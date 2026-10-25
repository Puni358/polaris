"""
D5Runner Orchestrator Module (D5 Implementation)
Implements paired closed-loop MPC orchestration under D5 forecast perturbation in strict compliance with the frozen D5 contract.

Enforces:
1. Closed-loop MPC semantics: 24h horizon per step, H1-only execution per step, N closed-loop iterations.
2. Two-World Causal Firewall: Perturbation applies to controller-visible ForecastBundle F_t without inspecting future actuals A_t.
3. Paired Control / Counterfactual comparison under 100% identical physical setup and exogenous provenance.
4. D4-C1 failure containment semantics (SUCCESS_CLEAN, SUCCESS_WITH_GOVERNED_FAULTS, FAILED_TERMINATED).
"""
import copy
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from system.data.provider import LocalDataProvider
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.optimization.implementations.rule_based import LocalRuleBasedEnergyOptimizer
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.robustness.perturbation import ForecastPerturber, ForecastBundleValidationError
from system.robustness.scenarios import D5ScenarioRegistry, D5ScenarioConfig
from system.robustness.metrics import D5MetricsCalculator


class D5FaultEvent:
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


class D5Runner:
    """
    Orchestrates D5 closed-loop MPC simulations and paired Control/Counterfactual evaluations.
    """

    def __init__(
        self,
        system_dir: Path,
        scenario_filename: str = "demo_scenario.json",
        optimizer_type: str = "milp",
        custom_data_provider: Optional[LocalDataProvider] = None
    ):
        self.system_dir = system_dir
        self.config_dir = system_dir / "config"
        self.data_dir = system_dir / "data"
        self.artifacts_dir = system_dir / "artifacts" / "d5"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        if custom_data_provider:
            self.data_provider = custom_data_provider
        else:
            self.scenario_path = self.data_dir / "scenarios" / scenario_filename
            self.data_provider = LocalDataProvider(self.scenario_path)

        # Load system configs
        self.configs = {}
        for cfg_name in ["station", "battery", "diesel", "solar_pv", "loads", "optimizer"]:
            cfg_file = self.config_dir / f"{cfg_name}.yaml"
            if cfg_file.exists():
                import yaml
                with open(cfg_file, "r") as f:
                    self.configs[cfg_name] = yaml.safe_load(f)
            else:
                self.configs[cfg_name] = {}

        self.forecast_engine = LocalBaselineForecastEngine(self.config_dir / "solar_pv.yaml")
        self.optimizer_type = optimizer_type.lower()
        if self.optimizer_type == "rule_based":
            self.optimizer = LocalRuleBasedEnergyOptimizer()
        else:
            self.optimizer = LocalMILPEnergyOptimizer()

        self.simulator = DigitalTwinSimulator(self.configs)

    def _create_initial_state(self) -> StationState:
        first_step = self.data_provider.timesteps[0]
        init_soc = self.configs.get("battery", {}).get("initial_soc_pct", 50.0)
        cap_wh = self.configs.get("battery", {}).get("capacity_wh", 200000.0)
        return StationState(
            timestamp=first_step["timestamp"],
            battery_soc_pct=init_soc,
            battery_energy_wh=cap_wh * (init_soc / 100.0),
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=first_step["actual_SW_IN"],
            last_observed_demand=first_step["actual_demand"],
            last_observed_wind_generation=first_step["actual_wind_generation"]
        )

    def run_single_simulation(
        self,
        steps_to_run: int = 24,
        solar_scale: float = 1.0,
        wind_scale: float = 1.0,
        demand_scale: float = 1.0,
        irradiance_scale: Optional[float] = None,
        scenario_id: str = "BASELINE"
    ) -> Dict[str, Any]:
        """
        Executes receding horizon MPC loop for steps_to_run timesteps with D5 perturbation applied to ForecastBundle at each step.
        Enforces D4-C1 failure containment semantics.
        """
        current_state = self._create_initial_state()
        forecast_bundles = []
        dispatch_plans = []
        station_states = [current_state.to_dict()]
        fault_events: List[D5FaultEvent] = []

        max_steps = min(steps_to_run, self.data_provider.total_timesteps)
        completed_steps = 0
        execution_status = "SUCCESS_CLEAN"
        termination_reason = None

        for step_idx in range(max_steps):
            runtime_context = self.data_provider.get_runtime_state(step_idx)

            # 1. Baseline Forecast Generation
            try:
                baseline_bundle = self.forecast_engine.predict(current_state, runtime_context)
            except Exception as e:
                ev = D5FaultEvent(
                    timestep=step_idx,
                    fault_class="INVALID_FORECAST_BUNDLE",
                    source="ForecastEngine",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=f"Baseline forecast generation failed: {e}"
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"BASELINE_FORECAST_FAILURE: {e}"
                break

            # 2. D5 Forecast Perturbation (Causal Firewall: operates strictly on baseline_bundle)
            try:
                perturbed_bundle = ForecastPerturber.apply_perturbation(
                    bundle=baseline_bundle,
                    solar_scale=solar_scale,
                    wind_scale=wind_scale,
                    demand_scale=demand_scale,
                    irradiance_scale=irradiance_scale,
                    scenario_id=scenario_id
                )
            except ForecastBundleValidationError as e:
                ev = D5FaultEvent(
                    timestep=step_idx,
                    fault_class="INVALID_FORECAST_BUNDLE",
                    source="ForecastPerturber",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=f"Forecast perturbation rejected as invalid: {e}"
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"INVALID_PERTURBED_FORECAST_BUNDLE: {e}"
                break
            except Exception as e:
                ev = D5FaultEvent(
                    timestep=step_idx,
                    fault_class="INVALID_FORECAST_BUNDLE",
                    source="ForecastPerturber",
                    severity="CRITICAL_TERMINATION",
                    response="FAILED_TERMINATED",
                    state_advanced=False,
                    message=str(e)
                )
                fault_events.append(ev)
                execution_status = "FAILED_TERMINATED"
                termination_reason = f"PERTURBATION_FAILURE: {e}"
                break

            # 3. EMS Optimization
            t0 = time.perf_counter()
            try:
                plan = self.optimizer.optimize(perturbed_bundle, current_state, self.configs)
            except Exception as e:
                ev = D5FaultEvent(
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

            # Governed Zero-Dispatch Infeasibility Handling
            if plan.constraint_status and plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"):
                ev = D5FaultEvent(
                    timestep=step_idx,
                    fault_class="OPTIMIZATION_INFEASIBLE",
                    source="EnergyOptimizer",
                    severity="GOVERNED_DEGRADED",
                    response="GOVERNED_ZERO_DISPATCH",
                    state_advanced=True,
                    message=plan.constraint_status
                )
                fault_events.append(ev)

            # Validate DispatchPlan
            try:
                plan_dict = plan.to_dict()
                plan_dict["solve_time_ms"] = solve_time_ms
            except Exception as e:
                ev = D5FaultEvent(
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

            # 4. Hidden Ground Truth Actuals for Digital Twin step
            future_actuals = self.data_provider.get_future_ground_truth(step_idx, horizon_hours=24)
            next_actual = future_actuals[0]

            # 5. H1 Step Execution on Digital Twin
            try:
                current_state = self.simulator.step(current_state, plan, next_actual)
                completed_steps += 1
                forecast_bundles.append(perturbed_bundle.to_dict())
                dispatch_plans.append(plan_dict)
                station_states.append(current_state.to_dict())
            except Exception as e:
                f_class = "FAILED_STATE_VIOLATION" if "FAILED_STATE_VIOLATION" in str(e) else "UNHANDLED_FAILURE"
                ev = D5FaultEvent(
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

        # Final Status Calculation
        governed_fault_count = sum(1 for e in fault_events if e.severity == "GOVERNED_DEGRADED")
        if execution_status != "FAILED_TERMINATED":
            if governed_fault_count > 0:
                execution_status = "SUCCESS_WITH_GOVERNED_FAULTS"
            else:
                execution_status = "SUCCESS_CLEAN"

        # Calculate Separated Metrics
        scenario_params = {
            "scenario_id": scenario_id,
            "solar_scale": solar_scale,
            "wind_scale": wind_scale,
            "demand_scale": demand_scale,
            "irradiance_scale": irradiance_scale or solar_scale,
            "requested_steps": max_steps,
            "completed_steps": completed_steps
        }

        metrics_report = D5MetricsCalculator.calculate_metrics(
            dispatch_plans=dispatch_plans,
            station_states=station_states,
            fault_events=[e.to_dict() for e in fault_events],
            station_configs=self.configs,
            scenario_config=scenario_params,
            execution_status=execution_status,
            termination_reason=termination_reason
        )

        metrics_report["run_metadata"] = {
            "optimizer_type": self.optimizer_type.upper(),
            "completed_steps": completed_steps,
            "max_steps": max_steps
        }

        return metrics_report

    def run_paired_d5_experiment(self, gate_or_scenario_id: str) -> Dict[str, Any]:
        """
        Executes strict paired Control (baseline gamma=1.0) vs Counterfactual (perturbed gamma) comparison under identical physical setup.
        """
        scfg = D5ScenarioRegistry.get_scenario(gate_or_scenario_id)

        # 1. Control Execution (Baseline forecast gamma = 1.0)
        control_report = self.run_single_simulation(
            steps_to_run=scfg.duration_iterations,
            solar_scale=1.0,
            wind_scale=1.0,
            demand_scale=1.0,
            irradiance_scale=1.0,
            scenario_id=f"{scfg.scenario_id}_CONTROL"
        )

        # 2. Counterfactual Execution (Perturbed forecast)
        counterfactual_report = self.run_single_simulation(
            steps_to_run=scfg.duration_iterations,
            solar_scale=scfg.solar_scale,
            wind_scale=scfg.wind_scale,
            demand_scale=scfg.demand_scale,
            irradiance_scale=scfg.irradiance_scale,
            scenario_id=scfg.scenario_id
        )

        return {
            "gate_id": scfg.gate_id,
            "scenario_id": scfg.scenario_id,
            "scenario_name": scfg.name,
            "duration_iterations": scfg.duration_iterations,
            "control_run": control_report,
            "counterfactual_run": counterfactual_report
        }
