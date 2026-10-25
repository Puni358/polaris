import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import os, sys, json, time, signal, hashlib, traceback
from pathlib import Path
from typing import Dict, Any, Optional

from system.adapters.h10_runtime_adapter import H10RuntimeAdapter
from system.schemas.station_state import StationState
from system.simulation.simulator import DigitalTwinSimulator
from system.control.router import EMSControlRouter
from system.optimization.implementations.rule_based import LocalRuleBasedEnergyOptimizer
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.s81_solar import Stage81ForecastEngine
from system.forecasting.implementations.wind_arx import WindSpeedARXForecastEngine
from system.orchestration.checkpoint import CheckpointManager, CHECKPOINT_SCHEMA_VERSION
from system.safety import reserve_policy_guard

class CampaignWorker:
    def __init__(
        self,
        run_id: str,
        cell_id: str,
        worker_id: str,
        system_dir: Path,
        run_dir: Path,
        start_step: int = 0,
        end_step: int = 8784,
        checkpoint_interval: int = 500,
        resume_checkpoint_path: Optional[Path] = None
    ):
        self.run_id = run_id
        self.cell_id = cell_id
        self.worker_id = worker_id
        self.system_dir = system_dir
        self.run_dir = run_dir
        self.start_step = start_step
        self.end_step = end_step
        self.checkpoint_interval = checkpoint_interval
        
        self.worker_dir = run_dir / "workers" / worker_id
        self.worker_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = run_dir / "logs" / f"{worker_id}.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.cell_dir = run_dir / "cells" / cell_id
        self.cell_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir = run_dir / "checkpoints" / cell_id
        
        self.interrupted = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        # Load system configs
        self.configs = {}
        for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
            cfg_file = system_dir / "config" / f"{cfg_name}.yaml"
            if cfg_file.exists():
                import yaml
                with open(cfg_file, "r") as f:
                    self.configs[cfg_name] = yaml.safe_load(f)

        # Initialize Adapter & Twin Simulator
        fixture_dir = system_dir.parent / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0" if (system_dir.parent / "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0").exists() else Path("ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0")
        self.adapter = H10RuntimeAdapter(str(fixture_dir))
        self.simulator = DigitalTwinSimulator(self.configs)
        self.router = EMSControlRouter()
        self.option_d_solver = OptionDFallbackSolver()
        
        # Instantiate cell-specific components according to 2-cell primary matrix
        # Cell A: Simple Diesel-Only Baseline (Direct load coverage, no forecasting/optimization)
        # Cell B: Complete POLARIS Closed-Loop System (Option B Native HiGHS MILP / Router)
        if self.cell_id in ("cell_a", "SIMPLE_DIESEL_ONLY_BASELINE"):
            self.optimizer = None
            self.forecast_engine = None
        elif self.cell_id in ("cell_a2", "REACTIVE_HYBRID_NO_FORECAST_BASELINE"):
            from system.optimization.implementations.reactive_hybrid_a2 import ReactiveHybridA2Optimizer
            self.optimizer = ReactiveHybridA2Optimizer()
            self.forecast_engine = None
        else:
            self.optimizer = GAP19HighsNativeOptimizer()
            self.forecast_engine = LocalBaselineForecastEngine(system_dir / "config" / "solar_pv.yaml")

        self.resume_checkpoint_path = resume_checkpoint_path

    def _log(self, message: str):
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        line = f"[{ts}] [{self.worker_id}] [{self.cell_id}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def _handle_signal(self, signum, frame):
        self._log(f"Received interruption signal {signum}. Triggering graceful worker shutdown...")
        self.interrupted = True

    def _evaluate_step_dispatch_safety(self, plan) -> Dict[str, Any]:
        """
        Additive, out-of-band safety check (system/safety/reserve_policy_guard.py) run
        against the H1 (physically executed) action of this step's DispatchPlan. Does
        NOT alter GAP19's formulation, the governed reserve policy, or any protected
        file -- it independently re-derives the same governed hard-SOC bound GAP19
        itself uses (min_e_wh = capacity_wh * min_soc_pct/100 from battery.yaml) and
        checks the already-produced plan against it, and surfaces GAP19's own
        internally-computed critical-unmet/reserve-shortfall fields, which were
        previously computed but never read downstream (see
        forecasting/n6/reports/N6_OPERATIONAL_READINESS_REMEDIATION_REPORT.md Section 4 /
        ems/reports/rt01_runtime_fixes/SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md).

        NOTE on units: DispatchPlan.battery_soc is a PERCENT (0-100), not Wh. It is
        converted to Wh here before being passed to
        reserve_policy_guard.validate_hard_soc_floor (which expects Wh, the same unit
        as min_e_wh) -- passing the raw percentage would silently corrupt this check.
        """
        plan_dict = plan.to_dict()
        capacity_wh = float(self.configs.get("battery", {}).get("capacity_wh", 200000.0))
        min_soc_pct_cfg = float(self.configs.get("battery", {}).get("min_soc_pct", 20.0))
        min_e_wh = capacity_wh * (min_soc_pct_cfg / 100.0)

        unmet_essential = plan_dict.get("unmet_essential")
        reserve_shortfall = plan_dict.get("reserve_shortfall")
        battery_soc = plan_dict.get("battery_soc")
        # NOTE: a schema-valid DispatchPlan always carries unmet_load (a required
        # constructor argument), so this is normally non-None. It is read
        # defensively via .get() rather than a hard subscript so that the
        # "unavailable" (neither unmet_essential nor unmet_load present) branch
        # below -- which represents that case as unknown, not a verified 0.0 --
        # is actually reachable rather than raising first.
        unmet_load = plan_dict.get("unmet_load")

        safety_plan = {
            "constraint_status": plan_dict.get("constraint_status"),
            "unmet_load": [unmet_load[0]] if unmet_load is not None else None,
            "unmet_essential": [unmet_essential[0]] if unmet_essential is not None else None,
            "reserve_shortfall": [reserve_shortfall[0]] if reserve_shortfall is not None else None,
            "battery_soc": [(battery_soc[0] / 100.0) * capacity_wh] if battery_soc is not None else None,
        }

        hard_soc_violation = False
        failure_reasons: list = []
        notes: list = []
        result = None
        try:
            result = reserve_policy_guard.evaluate_dispatch_safety(
                safety_plan,
                min_e_wh=min_e_wh,
                # AUTHORIZATION_REQUIRED: no numeric reserve-shortfall ceiling has been
                # authorized by the project owner; shortfall is surfaced for visibility
                # only (see ems/reports/rt01_runtime_fixes/SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md).
                reserve_shortfall_authorization_wh=None,
            )
        except reserve_policy_guard.ReservePolicyViolation as exc:
            # Hard SOC floor violated. The guard raises unconditionally for this case
            # (an unconditionally enforced physical constraint). This worker converts
            # it into a visible, structured finding rather than crashing the campaign
            # step loop -- the step's dispatch already executed physically via the
            # simulator; hiding or resetting this finding afterward is prohibited.
            hard_soc_violation = True
            failure_reasons.append(str(exc))

        if unmet_essential is not None:
            critical_unmet_source = "unmet_essential"
            critical_unmet_wh = float(unmet_essential[0])
        elif plan_dict.get("unmet_load") is not None:
            critical_unmet_source = "fallback_total_unmet_load"
            critical_unmet_wh = float(plan_dict["unmet_load"][0])
        else:
            # Neither a critical-specific nor a total unmet-load signal is available on
            # this plan. This must be represented as unknown, not as a verified zero --
            # a missing measurement is not evidence of "no unmet load" (Policy D).
            critical_unmet_source = "unavailable"
            critical_unmet_wh = None

        reserve_shortfall_wh = float(reserve_shortfall[0]) if reserve_shortfall is not None else None

        if result is not None:
            hard_soc_violation = hard_soc_violation or result.hard_soc_violation
            failure_reasons.extend(result.failure_reasons)
            notes.extend(result.notes)

        solver_infeasible = bool(
            plan_dict.get("constraint_status")
            and str(plan_dict["constraint_status"]).startswith("OPTIMIZATION_INFEASIBLE")
        )
        # NOTE: (critical_unmet_wh or 0.0) here only affects this LOCAL boolean flag,
        # never the reported critical_unmet_wh value itself (which stays None/unknown
        # below when unavailable) -- an unknown measurement is not asserted to be safe,
        # it simply cannot positively contribute to this derived "unsafe" flag.
        optimal_but_unsafe = (
            plan_dict.get("constraint_status") == "OPTIMAL"
            and ((critical_unmet_wh or 0.0) > 0.0 or (reserve_shortfall_wh or 0.0) > 0.0 or hard_soc_violation)
        )

        return {
            "applicable": True,
            "constraint_status": plan_dict.get("constraint_status"),
            "critical_unmet_wh": critical_unmet_wh if critical_unmet_wh is not None else "UNKNOWN_NOT_VERIFIED",
            "critical_unmet_source": critical_unmet_source,
            "reserve_shortfall_wh": reserve_shortfall_wh if reserve_shortfall_wh is not None else "UNKNOWN_NOT_VERIFIED",
            "hard_soc_violation": hard_soc_violation,
            "solver_infeasible": solver_infeasible,
            "optimal_but_unsafe": optimal_but_unsafe,
            "failure_reasons": failure_reasons,
            "notes": notes,
        }

    def execute(self) -> dict:
        self._log(f"Worker starting execution from step {self.start_step} to {self.end_step}...")
        
        current_step = self.start_step
        current_state = self.adapter.get_station_state(0, battery_soc_pct=50.0)
        cumulative_fuel_l = 0.0
        cumulative_diesel_kwh = 0.0
        cumulative_battery_throughput_kwh = 0.0
        last_checkpoint_hash = "GENESIS"
        
        integrity_counters = {
            "truth_leakage_count": 0,
            "state_reset_count": 0,
            "fuel_reset_count": 0,
            "soc_reset_count": 0,
            "infeasibility_count": 0,
            "unmet_critical_load_wh": 0.0,
            "power_balance_max_error_w": 0.0,
            # Dispatch-safety guard counters (system/safety/reserve_policy_guard.py).
            # Additive; see SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md.
            "reserve_shortfall_total_wh": 0.0,
            "hard_soc_violation_count": 0,
            "solver_infeasible_safety_flagged_count": 0,
            "optimal_but_unsafe_step_count": 0,
            "unmet_critical_load_source_fallback_count": 0,
            "unmet_critical_load_source_unavailable_count": 0
        }

        # Check for resume checkpoint
        if self.resume_checkpoint_path and self.resume_checkpoint_path.exists():
            cp_data = CheckpointManager.verify_and_load(
                self.resume_checkpoint_path, self.run_id, self.cell_id
            )
            current_step = cp_data["cycle_index"] + 1
            st = cp_data["station_state"]
            current_state = StationState(
                timestamp=st["timestamp"],
                battery_soc_pct=st["battery_soc_pct"],
                battery_energy_wh=st["battery_energy_wh"],
                diesel_running=st["diesel_running"],
                diesel_hours_running=st["diesel_hours_running"],
                last_observed_solar_irradiance=st["last_observed_solar_irradiance"],
                last_observed_demand=st["last_observed_demand"],
                last_observed_wind_generation=st["last_observed_wind_generation"]
            )
            cumulative_fuel_l = cp_data["cumulative_fuel_l"]
            cumulative_diesel_kwh = cp_data["cumulative_diesel_energy_kwh"]
            cumulative_battery_throughput_kwh = cp_data["cumulative_battery_throughput_kwh"]
            integrity_counters = cp_data["integrity_counters"]
            # Backfill safety-guard counters for resume from a checkpoint written before
            # this remediation pass (additive keys; never silently drop a resumed run's
            # pre-existing counters).
            for _k, _v in {
                "reserve_shortfall_total_wh": 0.0,
                "hard_soc_violation_count": 0,
                "solver_infeasible_safety_flagged_count": 0,
                "optimal_but_unsafe_step_count": 0,
                "unmet_critical_load_source_fallback_count": 0,
                "unmet_critical_load_source_unavailable_count": 0
            }.items():
                integrity_counters.setdefault(_k, _v)
            last_checkpoint_hash = cp_data["current_checkpoint_hash"]
            self._log(f"Resumed successfully from checkpoint step {cp_data['cycle_index']} (next step: {current_step})")

        records = []
        status = "COMPLETED"
        # Bounded correctness fix: structured diagnostics for an uncaught Cell B
        # optimizer/router exception (see try/except below). Stays None for every
        # run that does not hit that path; never silently dropped once populated.
        worker_failure_diagnostics: Optional[Dict[str, Any]] = None

        is_baseline_cell = self.cell_id in ("cell_a", "cell_1", "SIMPLE_DIESEL_ONLY_BASELINE")
        is_reactive_a2_cell = self.cell_id in ("cell_a2", "REACTIVE_HYBRID_NO_FORECAST_BASELINE")

        for k in range(current_step, self.end_step):
            if self.interrupted:
                self._log(f"Worker gracefully interrupted at step {k}.")
                status = "INTERRUPTED"
                break

            st_k = self.adapter.get_station_state(k, battery_soc_pct=current_state.battery_soc_pct)
            st_k.diesel_running = current_state.diesel_running
            st_k.diesel_hours_running = current_state.diesel_hours_running
            st_k.battery_energy_wh = current_state.battery_energy_wh
            
            future_actuals = self.adapter.get_future_ground_truth(k, horizon_hours=24)
            next_actual = future_actuals[0]

            # Default safety finding for paths with no MILP DispatchPlan to evaluate
            # (Cell A: direct demand coverage, no optimizer). Overwritten below for
            # Cell A2/Cell B once a DispatchPlan exists.
            step_safety: Dict[str, Any] = {
                "applicable": False,
                "reason": "No MILP DispatchPlan produced for this cell/path (SIMPLE_DIESEL_ONLY_BASELINE)."
            }

            if is_baseline_cell:
                # Cell A: Simple Diesel-Only Reference Execution Path (Direct demand coverage)
                p_demand_actual = float(next_actual["actual_demand"])
                p_diesel = p_demand_actual
                p_chg = 0.0
                p_dis = 0.0
                
                diesel_running = p_diesel > 0.0
                base_lph = self.configs.get("diesel", {}).get("base_fuel_consumption_l_per_h", 5.0)
                marg_lpwh = self.configs.get("diesel", {}).get("marginal_fuel_consumption_l_per_wh", 0.00025)
                step_fuel_l = ((base_lph if diesel_running else 0.0) + (marg_lpwh * p_diesel)) * 1.0
                cumulative_fuel_l += step_fuel_l
                cumulative_diesel_kwh += (p_diesel / 1000.0) * 1.0

                current_state = StationState(
                    timestamp=next_actual["timestamp"],
                    battery_soc_pct=current_state.battery_soc_pct,
                    battery_energy_wh=current_state.battery_energy_wh,
                    diesel_running=diesel_running,
                    diesel_hours_running=current_state.diesel_hours_running + (1.0 if diesel_running else 0.0),
                    last_observed_solar_irradiance=next_actual["actual_SW_IN"],
                    last_observed_demand=next_actual["actual_demand"],
                    last_observed_wind_generation=next_actual["actual_wind_generation"]
                )
            elif is_reactive_a2_cell:
                # Cell A2: Reactive Hybrid Baseline Execution Path (No forecast, no router, no MILP)
                from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
                from datetime import datetime, timedelta
                
                p_sol = float(next_actual["actual_solar_PV_power"])
                p_wnd = float(next_actual["actual_wind_generation"])
                p_dem = float(next_actual["actual_demand"])
                crit_dem = min(11600.0, p_dem)

                start_dt = datetime.fromisoformat(st_k.timestamp.replace("Z", "+00:00"))
                ts_24 = [(start_dt + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]

                bundle = ForecastBundle(
                    schema_version="1.0.0",
                    origin_timestamp=st_k.timestamp,
                    horizon_hours=24,
                    timestamps=ts_24,
                    solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
                    solar_generation=TimeseriesForecast([p_sol]*24, [p_sol]*24, [p_sol]*24, "W"),
                    wind_generation=TimeseriesForecast([p_wnd]*24, [p_wnd]*24, [p_wnd]*24, "W"),
                    demand=TimeseriesForecast([p_dem]*24, [p_dem]*24, [p_dem]*24, "W"),
                    metadata={"source": "instantaneous_observation"},
                    demand_critical=TimeseriesForecast([crit_dem]*24, [crit_dem]*24, [crit_dem]*24, "W")
                )

                plan = self.optimizer.optimize(bundle, st_k, self.configs)
                step_safety = self._evaluate_step_dispatch_safety(plan)

                p_chg = plan.battery_charge[0]
                p_dis = plan.battery_discharge[0]
                p_diesel = plan.diesel_power[0]

                next_state = self.simulator.step(st_k, plan, next_actual)
                current_state = next_state

                diesel_running = p_diesel > 0
                base_lph = self.configs.get("diesel", {}).get("base_fuel_consumption_l_per_h", 5.0)
                marg_lpwh = self.configs.get("diesel", {}).get("marginal_fuel_consumption_l_per_wh", 0.00025)
                step_fuel_l = ((base_lph if diesel_running else 0.0) + (marg_lpwh * p_diesel)) * 1.0
                cumulative_fuel_l += step_fuel_l
                cumulative_diesel_kwh += (p_diesel / 1000.0) * 1.0
                cumulative_battery_throughput_kwh += ((p_chg + p_dis) / 1000.0) * 1.0
            else:
                # Cell B: POLARIS Closed-Loop Strategy Execution Path
                runtime_ctx = self.adapter.get_runtime_context(k)
                bundle = self.forecast_engine.predict(st_k, runtime_ctx)

                # GAP19 requires an explicit protected critical-load trajectory
                # (demand_critical); no ForecastEngine (baseline or Stage 8.1) sets
                # bundle.demand_critical, so supply GAP19's top-level critical_demand_w
                # fallback from the canonical governed value in loads.yaml
                # (critical_load.baseline_power_w), clipped per-horizon against this
                # step's own forecasted demand so it can never exceed total demand --
                # same min() pattern already used by the Cell A2 path above. This is
                # engine-agnostic: identical for baseline and Stage 8.1.
                critical_load_baseline_w = float(
                    self.configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 11600.0)
                )
                self.configs["critical_demand_w"] = [min(critical_load_baseline_w, d) for d in bundle.demand.point]

                # Bounded correctness fix (ems/reports/rt01_runtime_fixes/BOUNDED_CORRECTNESS_FIXES_REPORT.md item 2b):
                # an uncaught exception from the optimizer/router here previously
                # propagated out of execute() and crashed the worker subprocess with
                # no persisted explanation (see ems/reports/rt01_runtime_fixes/SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md
                # Section 3, cases 7/9). This mirrors the equivalent try/except already
                # present in system/runtime/runner.py around the same
                # router.evaluate_and_route / optimizer.optimize call sequence: any
                # exception is converted into a structured, persisted, non-success
                # worker status rather than labeling it as solver infeasibility (which
                # has its own distinct, already-correct BLOCKED_INFEASIBLE handling
                # below) and rather than crashing silently.
                try:
                    assessment, route = self.router.evaluate_and_route(st_k, bundle, self.configs)
                    if route == "NORMAL":
                        plan = self.optimizer.optimize(bundle, st_k, self.configs)
                    elif route == "EMERGENCY":
                        plan = self.option_d_solver.solve(assessment, bundle, st_k, self.configs)
                    else:
                        self._log(f"Fail-closed UNKNOWN_INVALID at step {k}!")
                        status = "FAILED_UNKNOWN_INVALID"
                        break

                    if plan.constraint_status and plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
                        self._log(f"Initial MILP Infeasibility at step {k}: {plan.constraint_status}. Executing Gate-02 Option C governed relaxation re-solve...")

                        # Option C governed relaxation pass: preserve hard critical load, relax noncritical flexible demand bounds
                        relaxed_config = dict(self.configs)
                        opt_cfg = dict(relaxed_config.get("optimizer", {}))
                        opt_cfg["allow_flexible_load_relaxation"] = True
                        relaxed_config["optimizer"] = opt_cfg

                        relaxed_plan = self.optimizer.optimize(bundle, st_k, relaxed_config)

                        if relaxed_plan.constraint_status == "OPTIMAL":
                            # Re-solve FEASIBLE -> emit machine-readable operator relaxation event
                            operator_event = {
                                "event_id": f"GATE02_EVT_{self.run_id}_{self.cell_id}_k{k}",
                                "cycle_index": k,
                                "timestamp": st_k.timestamp,
                                "original_solver_status": plan.constraint_status,
                                "relaxed_constraint_class": "NONCRITICAL_FLEXIBLE_LOAD",
                                "re_solve_status": "OPTIMAL",
                                "operator_notification_status": "DELIVERED",
                                "dispatch_adopted": True
                            }
                            self._log(f"Gate-02 Option C re-solve FEASIBLE at step {k}. Event generated: {operator_event['event_id']}")

                            # Save operator event to cell logs
                            evt_file = self.cell_dir / "gate02_operator_events.json"
                            events = []
                            if evt_file.exists():
                                try:
                                    with open(evt_file, "r") as ef:
                                        events = json.load(ef)
                                except Exception:
                                    pass
                            events.append(operator_event)
                            with open(evt_file, "w") as ef:
                                json.dump(events, ef, indent=2)

                            plan = relaxed_plan
                            integrity_counters["gate02_relaxation_events"] = integrity_counters.get("gate02_relaxation_events", 0) + 1
                        else:
                            # Re-solve STILL INFEASIBLE -> halt fail-closed without zero-dispatch or Twin step
                            self._log(f"Gate-02 Option C re-solve STILL INFEASIBLE at step {k}: {relaxed_plan.constraint_status}. Halting fail-closed.")
                            integrity_counters["infeasibility_count"] += 1
                            status = "BLOCKED_INFEASIBLE"
                            break
                except Exception as exc:
                    # Structured, persisted, non-success failure -- NOT relabeled as
                    # OPTIMIZATION_INFEASIBLE (that status is reserved for the genuine
                    # Gate-02 "still infeasible after relaxation" case above, which is a
                    # governed solver outcome, not a Python exception). The original
                    # exception type/message/traceback are preserved verbatim in
                    # worker_failure_diagnostics for operator/debugging visibility.
                    self._log(
                        f"Unhandled exception in Cell B router/optimizer path at step {k}: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    worker_failure_diagnostics = {
                        "cycle_index": k,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                    status = "FAILED_OPTIMIZATION_EXCEPTION"
                    break

                # Evaluate the FINAL adopted plan (post Gate-02 relaxation if applicable)
                # against the safety guard before it is executed/recorded.
                step_safety = self._evaluate_step_dispatch_safety(plan)

                p_chg = plan.battery_charge[0]
                p_dis = plan.battery_discharge[0]
                p_diesel = plan.diesel_power[0]

                if "actual_SW_IN" in bundle.solar_irradiance.point:
                    integrity_counters["truth_leakage_count"] += 1

                next_state = self.simulator.step(st_k, plan, next_actual)
                current_state = next_state

                diesel_running = p_diesel > 0
                base_lph = self.configs.get("diesel", {}).get("base_fuel_consumption_l_per_h", 5.0)
                marg_lpwh = self.configs.get("diesel", {}).get("marginal_fuel_consumption_l_per_wh", 0.00025)
                step_fuel_l = ((base_lph if diesel_running else 0.0) + (marg_lpwh * p_diesel)) * 1.0
                cumulative_fuel_l += step_fuel_l
                cumulative_diesel_kwh += (p_diesel / 1000.0) * 1.0
                cumulative_battery_throughput_kwh += ((p_chg + p_dis) / 1000.0) * 1.0

            # Dispatch-safety guard bookkeeping (system/safety/reserve_policy_guard.py).
            # Surfaces GAP19's own internally-computed critical-unmet/reserve-shortfall
            # fields and the independent hard-SOC-floor check into the integrity
            # counters and the persisted per-step record; never suppressed/reset below.
            if step_safety.get("applicable"):
                if isinstance(step_safety["critical_unmet_wh"], (int, float)):
                    integrity_counters["unmet_critical_load_wh"] += step_safety["critical_unmet_wh"]
                if step_safety["critical_unmet_source"] == "fallback_total_unmet_load":
                    integrity_counters["unmet_critical_load_source_fallback_count"] += 1
                elif step_safety["critical_unmet_source"] == "unavailable":
                    integrity_counters["unmet_critical_load_source_unavailable_count"] += 1
                if isinstance(step_safety["reserve_shortfall_wh"], (int, float)):
                    integrity_counters["reserve_shortfall_total_wh"] += step_safety["reserve_shortfall_wh"]
                if step_safety["hard_soc_violation"]:
                    integrity_counters["hard_soc_violation_count"] += 1
                if step_safety["solver_infeasible"]:
                    integrity_counters["solver_infeasible_safety_flagged_count"] += 1
                if step_safety["optimal_but_unsafe"]:
                    integrity_counters["optimal_but_unsafe_step_count"] += 1

            # Step Record
            rec = {
                "cycle_index": k,
                "timestamp": st_k.timestamp,
                "p_solar_actual": next_actual["actual_solar_PV_power"],
                "p_wind_actual": next_actual["actual_wind_generation"],
                "p_demand_actual": next_actual["actual_demand"],
                "p_chg": p_chg,
                "p_dis": p_dis,
                "p_diesel": p_diesel,
                "soc_after": current_state.battery_soc_pct,
                "step_fuel_l": round(step_fuel_l, 4),
                "cumulative_fuel_l": round(cumulative_fuel_l, 4),
                "safety": step_safety
            }
            records.append(rec)

            # Update worker status file
            with open(self.worker_dir / "status.json", "w") as sf:
                json.dump({
                    "cell_id": self.cell_id,
                    "worker_id": self.worker_id,
                    "current_cycle": k,
                    "target_cycle": self.end_step,
                    "progress_pct": round((k + 1) / self.end_step * 100.0, 1),
                    "status": "RUNNING",
                    "cumulative_fuel_l": round(cumulative_fuel_l, 2)
                }, sf, indent=2)

            # Checkpoint saving
            if (k + 1) % self.checkpoint_interval == 0 or (k + 1) == self.end_step:
                cp_path = CheckpointManager.create_checkpoint(
                    checkpoint_dir=self.checkpoint_dir,
                    run_id=self.run_id,
                    cell_id=self.cell_id,
                    worker_id=self.worker_id,
                    cycle_index=k,
                    timestamp=current_state.timestamp,
                    station_state_dict={
                        "timestamp": current_state.timestamp,
                        "battery_soc_pct": current_state.battery_soc_pct,
                        "battery_energy_wh": current_state.battery_energy_wh,
                        "diesel_running": current_state.diesel_running,
                        "diesel_hours_running": current_state.diesel_hours_running,
                        "last_observed_solar_irradiance": current_state.last_observed_solar_irradiance,
                        "last_observed_demand": current_state.last_observed_demand,
                        "last_observed_wind_generation": current_state.last_observed_wind_generation
                    },
                    cumulative_fuel_l=cumulative_fuel_l,
                    cumulative_diesel_energy_kwh=cumulative_diesel_kwh,
                    cumulative_battery_throughput_kwh=cumulative_battery_throughput_kwh,
                    integrity_counters=integrity_counters,
                    protected_hashes={},
                    fixture_hash="H1.0",
                    previous_checkpoint_hash=last_checkpoint_hash
                )
                last_checkpoint_hash = CheckpointManager.compute_file_hash(str(cp_path))
                self._log(f"Saved checkpoint at step {k} -> {cp_path.name}")

        # Aggregate dispatch-safety guard summary (system/safety/reserve_policy_guard.py).
        # Kept visible in both the persisted trajectory record and the worker's final
        # result; never suppressed, reset, or overwritten after this point (protocol
        # item 8 of ems/reports/rt01_runtime_fixes/SAFETY_GUARD_WIRING_REMEDIATION_REPORT.md).
        safety_summary = {
            "unmet_critical_load_wh": round(integrity_counters["unmet_critical_load_wh"], 2),
            "unmet_critical_load_source_fallback_count": integrity_counters["unmet_critical_load_source_fallback_count"],
            "unmet_critical_load_source_unavailable_count": integrity_counters["unmet_critical_load_source_unavailable_count"],
            "reserve_shortfall_total_wh": round(integrity_counters["reserve_shortfall_total_wh"], 2),
            "hard_soc_violation_count": integrity_counters["hard_soc_violation_count"],
            "solver_infeasible_safety_flagged_count": integrity_counters["solver_infeasible_safety_flagged_count"],
            "optimal_but_unsafe_step_count": integrity_counters["optimal_but_unsafe_step_count"],
            "reserve_shortfall_authorization_wh": None,
            "reserve_shortfall_authorization_status": (
                "AUTHORIZATION_REQUIRED: no numeric reserve-shortfall ceiling has been authorized "
                "by the project owner. Totals above are reported for visibility only."
            ),
            "safety_gate_formally_authorized": False,
            "any_safety_finding": (
                integrity_counters["hard_soc_violation_count"] > 0
                or integrity_counters["optimal_but_unsafe_step_count"] > 0
                or integrity_counters["unmet_critical_load_wh"] > 0.0
            )
        }

        # Save records to cell output file
        records_file = self.cell_dir / "trajectory_records.json"
        with open(records_file, "w", encoding="utf-8") as rf:
            json.dump({
                "cell_id": self.cell_id,
                "run_id": self.run_id,
                "status": status,
                "total_records": len(records),
                "cumulative_fuel_l": round(cumulative_fuel_l, 4),
                "cumulative_diesel_energy_kwh": round(cumulative_diesel_kwh, 4),
                "integrity_counters": integrity_counters,
                "safety_summary": safety_summary,
                "failure_diagnostics": worker_failure_diagnostics,
                "records": records
            }, rf, indent=2)

        self._log(f"Worker finished execution with status: {status}. Total fuel: {cumulative_fuel_l:.2f} L")
        return {
            "cell_id": self.cell_id,
            "worker_id": self.worker_id,
            "status": status,
            "completed_cycles": len(records),
            "cumulative_fuel_l": round(cumulative_fuel_l, 4),
            "safety_summary": safety_summary,
            "failure_diagnostics": worker_failure_diagnostics
        }
