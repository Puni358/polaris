"""
Local System Orchestration Runner
Coordinates end-to-end local execution of LocalDataProvider, ForecastEngine, EnergyOptimizer, DigitalTwinSimulator, and EvaluationEngine.
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.forecasting.implementations.s81_solar import Stage81ForecastEngine
from system.optimization.implementations.rule_based import LocalRuleBasedEnergyOptimizer
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.optimization.implementations.reactive_hybrid_a2 import ReactiveHybridA2Optimizer
from system.control.router import EMSControlRouter
from system.optimization.implementations.option_d import OptionDFallbackSolver
from system.simulation.simulator import DigitalTwinSimulator
from system.evaluation.evaluator import EvaluationEngine

class FaultEvent:
    def __init__(self, timestep: int, fault_class: str, source: str, severity: str, response: str, state_advanced: bool, message: str):
        self.timestep = timestep
        self.fault_class = fault_class
        self.source = source
        self.severity = severity
        self.response = response
        self.state_advanced = state_advanced
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestep": self.timestep,
            "fault_class": self.fault_class,
            "source": self.source,
            "severity": self.severity,
            "response": self.response,
            "state_advanced": self.state_advanced,
            "message": self.message
        }

class PolarisLocalRunner:
    def __init__(
        self,
        system_dir: Path,
        scenario_filename: str = "demo_scenario.json",
        optimizer_type: str = "milp",
        forecast_engine_type: str = "baseline"
    ):
        self.system_dir = system_dir
        self.config_dir = system_dir / "config"
        self.data_dir = system_dir / "data"
        self.artifacts_dir = system_dir / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.scenario_path = self.data_dir / "scenarios" / scenario_filename
        self.data_provider = LocalDataProvider(self.scenario_path)

        # Load configs
        self.configs = {}
        for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
            cfg_file = self.config_dir / f"{cfg_name}.yaml"
            if cfg_file.exists():
                with open(cfg_file, "r") as f:
                    self.configs[cfg_name] = yaml.safe_load(f)
            else:
                self.configs[cfg_name] = {}

        # Instantiate components
        self.forecast_engine_type = forecast_engine_type.lower()
        if self.forecast_engine_type in ("stage81_solar", "stage81", "s81_solar", "s81"):
            self.forecast_engine = Stage81ForecastEngine(self.config_dir / "solar_pv.yaml")
        else:
            self.forecast_engine = LocalBaselineForecastEngine(self.config_dir / "solar_pv.yaml")

        self.optimizer_type = optimizer_type.lower()
        if self.optimizer_type == "rule_based":
            self.optimizer = LocalRuleBasedEnergyOptimizer()
        elif self.optimizer_type in ("highs_native", "gap19_highs_native"):
            self.optimizer = GAP19HighsNativeOptimizer()
        elif self.optimizer_type == "reactive_hybrid_a2":
            self.optimizer = ReactiveHybridA2Optimizer()
        else:
            self.optimizer = LocalMILPEnergyOptimizer()

        self.router = EMSControlRouter()
        self.option_d_solver = OptionDFallbackSolver()
        self.simulator = DigitalTwinSimulator(self.configs)

    def run_pipeline(self, steps_to_run: int = 24, v2_telemetry_collector: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes receding horizon MPC loop for steps_to_run timesteps with D4-C1 failure containment.
        Supports optional passive V2 telemetry collection.
        """
        # Initial Station State at t=0
        first_step = self.data_provider.timesteps[0]
        initial_state = StationState(
            timestamp=first_step["timestamp"],
            battery_soc_pct=self.configs.get("battery", {}).get("initial_soc_pct", 50.0),
            battery_energy_wh=self.configs.get("battery", {}).get("capacity_wh", 200000.0) * (self.configs.get("battery", {}).get("initial_soc_pct", 50.0) / 100.0),
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=first_step["actual_SW_IN"],
            last_observed_demand=first_step["actual_demand"],
            last_observed_wind_generation=first_step["actual_wind_generation"],
            diesel_fuel_remaining_liters=self.configs.get("diesel", {}).get("initial_fuel_l", 100.0)
        )

        current_state = initial_state
        forecast_bundles = []
        dispatch_plans = []
        actual_scenarios = []
        fault_events: List[FaultEvent] = []

        max_steps = min(steps_to_run, self.data_provider.total_timesteps)
        completed_steps = 0
        execution_status = "SUCCESS_CLEAN"
        termination_reason = None

        import time

        for step_idx in range(max_steps):
            # 1. Observable runtime state
            runtime_context = self.data_provider.get_runtime_state(step_idx)

            # 2. ForecastEngine predicts 24h horizon & validates ForecastBundle
            try:
                bundle = self.forecast_engine.predict(current_state, runtime_context)
            except Exception as e:
                ev = FaultEvent(
                    timestep=step_idx,
                    fault_class="INVALID_FORECAST_BUNDLE",
                    source="ForecastEngine",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=str(e)
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"INVALID_FORECAST_BUNDLE: {e}"
                break

            # 3. EMS Control Router Policy Assessment & Optimizer Invocation
            t0 = time.perf_counter()
            try:
                assessment, route = self.router.evaluate_and_route(current_state, bundle, self.configs)
                if route == "NORMAL":
                    plan = self.optimizer.optimize(bundle, current_state, self.configs)
                elif route == "EMERGENCY":
                    plan = self.option_d_solver.solve(assessment, bundle, current_state, self.configs)
                else:  # UNKNOWN_INVALID
                    ev = FaultEvent(
                        timestep=step_idx,
                        fault_class=assessment.validity_status.value if assessment.validity_status else "UNKNOWN_INVALID",
                        source="EMSControlRouter",
                        severity="CRITICAL_TERMINATION",
                        response="FAILED_TERMINATED",
                        state_advanced=False,
                        message=assessment.failure_reason or "Fail-closed UNKNOWN_INVALID operating mode"
                    )
                    fault_events.append(ev)
                    execution_status = "FAILED_TERMINATED"
                    termination_reason = f"FAIL_CLOSED_UNKNOWN_INVALID: {assessment.failure_reason}"
                    break
            except Exception as e:
                ev = FaultEvent(
                    timestep=step_idx,
                    fault_class="OPTIMIZATION_RUNTIME_FAILURE",
                    source="EnergyOptimizer",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=str(e)
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"OPTIMIZATION_RUNTIME_FAILURE: {e}"
                break

            t1 = time.perf_counter()
            solve_time_ms = (t1 - t0) * 1000.0

            # Check for genuine OPTIMIZATION_INFEASIBLE governed response
            if plan.constraint_status and plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
                ev = FaultEvent(
                    timestep=step_idx,
                    fault_class="OPTIMIZATION_INFEASIBLE",
                    source="EnergyOptimizer",
                    severity="GOVERNED_DEGRADED",
                    response="GOVERNED_ZERO_DISPATCH",
                    state_advanced=False,
                    message=plan.constraint_status
                )
                fault_events.append(ev)
                execution_status = "GOVERNANCE_DECISION_REQUIRED"
                termination_reason = f"OPTIMIZATION_INFEASIBLE: {plan.constraint_status}"
                break

            # Validate DispatchPlan
            try:
                plan_dict = plan.to_dict()
                plan_dict["solve_time_ms"] = solve_time_ms
            except Exception as e:
                ev = FaultEvent(
                    timestep=step_idx,
                    fault_class="INVALID_DISPATCH_PLAN",
                    source="DispatchPlanValidation",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=str(e)
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"INVALID_DISPATCH_PLAN: {e}"
                break

            # 4. Hidden ground truth for simulation
            future_actuals = self.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
            next_actual = future_actuals[0]

            # 5. Step simulator with step 1 dispatch decision
            state_before = current_state
            try:
                current_state = self.simulator.step(current_state, plan, next_actual)
                completed_steps += 1
                forecast_bundles.append(bundle.to_dict())
                dispatch_plans.append(plan_dict)
                actual_scenarios.append(future_actuals)
            except Exception as e:
                f_class = "FAILED_STATE_VIOLATION" if "FAILED_STATE_VIOLATION" in str(e) else "UNHANDLED_FAILURE"
                ev = FaultEvent(
                    timestep=step_idx,
                    fault_class=f_class,
                    source="DigitalTwinSimulator",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=str(e)
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"{f_class}: {e}"
                break

            # 6. Passive Observational Telemetry Capture (Isolated Failure Boundary)
            if v2_telemetry_collector is not None:
                try:
                    v2_telemetry_collector.record_step(
                        origin_id=0,
                        origin_timestamp=first_step["timestamp"],
                        mpc_timestep_idx=step_idx,
                        timestamp=state_before.timestamp,
                        treatment_forecast_vector_24=bundle.solar_irradiance.point,
                        control_forecast_vector_24=bundle.solar_irradiance.point,
                        actual_solar_truth=next_actual["actual_SW_IN"],
                        soc_before=state_before.battery_soc_pct,
                        diesel_state_before=state_before.diesel_running,
                        cumulative_diesel_fuel_before=getattr(state_before, "cumulative_diesel_fuel_l", 0.0),
                        cumulative_diesel_energy_before=getattr(state_before, "cumulative_diesel_energy_kwh", 0.0),
                        optimizer_status=plan.constraint_status,
                        objective_value=plan.objective_value,
                        diesel_commitment=plan.diesel_power[0] > 0,
                        battery_charge_decision=plan.battery_charge[0] / 1000.0,
                        battery_discharge_decision=plan.battery_discharge[0] / 1000.0,
                        reserve_status="NORMAL",
                        constraint_status=plan.constraint_status,
                        h1_diesel_power=plan.diesel_power[0] / 1000.0,
                        h1_battery_charge_power=plan.battery_charge[0] / 1000.0,
                        h1_battery_discharge_power=plan.battery_discharge[0] / 1000.0,
                        h1_renewable_dispatch=(plan.solar_used[0] + plan.wind_used[0]) / 1000.0,
                        h1_renewable_curtailment=plan.renewable_curtailment[0] / 1000.0,
                        h1_served_load=plan.load_served[0] / 1000.0,
                        h1_unmet_load=plan.unmet_load[0] / 1000.0,
                        soc_after=current_state.battery_soc_pct,
                        diesel_state_after=current_state.diesel_running,
                        cumulative_diesel_fuel_after=getattr(current_state, "cumulative_diesel_fuel_l", 0.0),
                        cumulative_diesel_energy_after=getattr(current_state, "cumulative_diesel_energy_kwh", 0.0),
                        cumulative_battery_throughput_after=getattr(current_state, "cumulative_battery_throughput_kwh", 0.0),
                    )
                except Exception as te:
                    # Isolated telemetry failure diagnostic - does NOT alter EMS execution status or state
                    if not hasattr(self, "_telemetry_faults"):
                        self._telemetry_faults = []
                    self._telemetry_faults.append({
                        "timestep": step_idx,
                        "error_class": te.__class__.__name__,
                        "error_message": str(te)
                    })

        # Post-execution status calculation
        governed_fault_count = sum(1 for e in fault_events if e.severity == "GOVERNED_DEGRADED")
        fault_count = len(fault_events)

        if execution_status not in ("FAILED_TERMINATED", "GOVERNANCE_DECISION_REQUIRED"):
            if governed_fault_count > 0:
                execution_status = "SUCCESS_WITH_GOVERNED_FAULTS"
            else:
                execution_status = "SUCCESS_CLEAN"

        # Evaluate performance if any steps were executed
        forecast_eval = EvaluationEngine.evaluate_forecasts(forecast_bundles, actual_scenarios) if forecast_bundles else {}
        ems_eval = EvaluationEngine.evaluate_ems_performance(dispatch_plans, self.configs) if dispatch_plans else {}

        run_report = {
            "run_id": f"polaris_run_d2_offline_{first_step['timestamp']}",
            "schema_version": "1.0.0",
            "environment": "LOCAL_OFFLINE_PC",
            "network_connectivity": "DISCONNECTED (100% OFFLINE)",
            "optimizer_type": self.optimizer_type.upper(),
            "data_mode": "DEMO / SMOKE-TEST SCENARIO (PROTOTYPE ASSUMPTIONS)",
            "execution_status": execution_status,
            "completed_steps": completed_steps,
            "requested_steps": max_steps,
            "fault_count": fault_count,
            "governed_fault_count": governed_fault_count,
            "fault_classes": sorted(list(set(e.fault_class for e in fault_events))),
            "termination_reason": termination_reason,
            "fault_events": [e.to_dict() for e in fault_events],
            "timesteps_executed": completed_steps,
            "forecast_evaluation": forecast_eval,
            "ems_evaluation": ems_eval,
            "research_qualification": "POLARIS research branch is frozen (ABC2). Operational 24h pipeline is a local system skeleton."
        }

        # Save artifacts
        if forecast_bundles:
            with open(self.artifacts_dir / "latest_forecast_bundle.json", "w") as f:
                json.dump(forecast_bundles[0], f, indent=2)

        if dispatch_plans:
            with open(self.artifacts_dir / "latest_dispatch_plan.json", "w") as f:
                json.dump(dispatch_plans[0], f, indent=2)

        with open(self.artifacts_dir / "run_report.json", "w") as f:
            json.dump(run_report, f, indent=2)

        return run_report

    def run_demo_comparison(self, steps_to_run: int = 24) -> Dict[str, Any]:
        """
        Runs both MILP and Rule-Based optimizers on the synthetic demo scenario for engineering comparison.
        Lables result strictly as DEMO / SMOKE-TEST RESULT.
        """
        # Save current optimizer
        orig_opt = self.optimizer
        orig_type = self.optimizer_type

        # 1. Run MILP Optimizer
        self.optimizer_type = "milp"
        self.optimizer = LocalMILPEnergyOptimizer()
        milp_report = self.run_pipeline(steps_to_run=steps_to_run)

        # 2. Run Rule-Based Optimizer
        self.optimizer_type = "rule_based"
        self.optimizer = LocalRuleBasedEnergyOptimizer()
        rule_report = self.run_pipeline(steps_to_run=steps_to_run)

        # Restore
        self.optimizer = orig_opt
        self.optimizer_type = orig_type

        comparison_report = {
            "disclaimer": "DIGITAL TWIN / SYNTHETIC ENGINEERING EVALUATION — Not evidence of real-world operational performance or scientific benchmark.",
            "milp_formal_optimizer": milp_report["ems_evaluation"],
            "rule_based_baseline_optimizer": rule_report["ems_evaluation"]
        }

        with open(self.artifacts_dir / "demo_comparison_report.json", "w") as f:
            json.dump(comparison_report, f, indent=2)

        return comparison_report

    def run_multi_scenario_suite(self, steps_to_run: int = 24) -> Dict[str, Any]:
        """
        Executes multi-scenario stress testing suite across Normal, Renewable Stress, Demand Stress, and Battery Stress scenarios.
        """
        orig_scenario = self.scenario_path
        scenarios = {
            "normal_demo": "demo_scenario.json",
            "renewable_stress": "renewable_stress_scenario.json",
            "demand_stress": "demand_stress_scenario.json",
            "battery_stress": "battery_stress_scenario.json"
        }

        suite_results = {
            "disclaimer": "DIGITAL TWIN / SYNTHETIC ENGINEERING EVALUATION — Synthetic scenarios for closed-loop stress validation.",
            "scenarios": {}
        }

        for key, s_file in scenarios.items():
            self.scenario_path = self.data_dir / "scenarios" / s_file
            if not self.scenario_path.exists():
                continue
            self.data_provider = LocalDataProvider(self.scenario_path)

            comp = self.run_demo_comparison(steps_to_run=steps_to_run)
            suite_results["scenarios"][key] = comp

        self.scenario_path = orig_scenario
        self.data_provider = LocalDataProvider(orig_scenario)

        with open(self.artifacts_dir / "multi_scenario_evaluation_report.json", "w") as f:
            json.dump(suite_results, f, indent=2)

        return suite_results

    def run_endurance_experiment(self, steps_to_run: int = 168) -> Dict[str, Any]:
        """
        Executes long-duration closed-loop MPC endurance experiment (168 timesteps) with per-iteration telemetry.
        """
        orig_scenario = self.scenario_path
        self.scenario_path = self.data_dir / "scenarios" / "synthetic_168h_endurance_scenario.json"
        self.data_provider = LocalDataProvider(self.scenario_path)

        report = self.run_pipeline(steps_to_run=steps_to_run)

        self.scenario_path = orig_scenario
        self.data_provider = LocalDataProvider(orig_scenario)
        return report

