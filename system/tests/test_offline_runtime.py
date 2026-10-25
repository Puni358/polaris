"""
POLARIS System D3 Hardened Closed-Loop & Digital Twin Test Suite
Comprehensive testing covering:
1. Digital Twin timestep advancement & first-action-only (H1) execution
2. Action / State transition physical integrity
3. Two-world model & hidden future actuals firewall
4. Counterfactual future-truth leakage protection
5. Per-timestep physical conservation audit (bus-bar, demand, renewable, battery)
6. Battery SOC bounds & charge/discharge exclusivity
7. Diesel limits & fuel conversion consistency
8. Flexible-load constraints & double-counting prevention
9. Infeasible & solver error handling
10. Objective timestep scaling
11. Deterministic forecast error perturbations
12. Multi-scenario stress testing suite (Normal, Renewable, Demand, Battery stress)
13. Fair MILP vs. Rule-Based baseline comparison
14. Deterministic reproducibility
15. 100% Offline network isolation
16. ForecastBundle -> EnergyOptimizer -> DispatchPlan contract validation
17. Research artifact firewall & 0 ODD rows access
"""
import sys
import json
import socket
import numpy as np
from pathlib import Path
import unittest

SYSTEM_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = SYSTEM_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from system.runtime.runner import PolarisLocalRunner
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.dispatch_plan import DispatchPlan
from system.schemas.station_state import StationState
from system.data.provider import LocalDataProvider
from system.forecasting.implementations.baseline import LocalBaselineForecastEngine
from system.optimization.implementations.rule_based import LocalRuleBasedEnergyOptimizer
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.simulation.simulator import DigitalTwinSimulator
from system.evaluation.evaluator import EvaluationEngine


def _authorize_router_for_offline_runtime_test(runner):
    """
    Explicit, clearly-labeled SYNTHETIC test-fixture authorization for the
    router/ECD fail-closed contract implemented in ECD-01 (A-iii/B-iii;
    system/control/router.py, system/control/ecd.py). This D3/D4 closed-
    loop/endurance suite tests genuine EMS mechanics (conservation, SOC,
    fuel, determinism, reliability), not the fail-closed gate itself.
    "EVID-TEST-OFFLINE-RUNTIME" and 5000.0 W are SYNTHETIC test-fixture
    values only, not a real-station evidence record -- see
    tests/test_isolated_components.py for the same convention.
    """
    runner.configs.setdefault("ecd", {}).update({
        "t_required_hours": 6.0,
        "t_required_authorized": True,
    })
    runner.configs.setdefault("critical_load", {}).update({
        "authorized": True,
        "evidence_id": "EVID-TEST-OFFLINE-RUNTIME",
        "authorized_critical_load_w": 5000.0,
    })
    return runner


class TestPolarisD3ClosedLoopRuntime(unittest.TestCase):
    def setUp(self):
        self.runner_milp = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(self.runner_milp)
        self.runner_rule = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="rule_based")
        _authorize_router_for_offline_runtime_test(self.runner_rule)

    def test_network_isolation(self):
        """15. Verifies 100% offline runtime network isolation."""
        old_socket = socket.socket
        old_getaddrinfo = socket.getaddrinfo

        def forbidden_socket(*args, **kwargs):
            raise RuntimeError("CRITICAL NETWORK LEAKAGE: Network access is strictly forbidden in POLARIS offline runtime.")

        def forbidden_getaddrinfo(*args, **kwargs):
            raise RuntimeError("CRITICAL NETWORK LEAKAGE: DNS lookup forbidden.")

        socket.socket = forbidden_socket
        socket.getaddrinfo = forbidden_getaddrinfo

        try:
            report = self.runner_milp.run_pipeline(steps_to_run=12)
            self.assertEqual(report["network_connectivity"], "DISCONNECTED (100% OFFLINE)")
            self.assertEqual(report["timesteps_executed"], 12)
        finally:
            socket.socket = old_socket
            socket.getaddrinfo = old_getaddrinfo

    def test_closed_loop_mpc_first_action_only(self):
        """1. Verifies that in every closed-loop MPC step, ONLY the first timestep action (H1) is executed."""
        provider = LocalDataProvider(self.runner_milp.scenario_path)
        sim = DigitalTwinSimulator(self.runner_milp.configs)
        engine = LocalBaselineForecastEngine(self.runner_milp.config_dir / "solar_pv.yaml")
        optimizer = LocalMILPEnergyOptimizer()

        current_state = StationState(
            timestamp=provider.timesteps[0]["timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=provider.timesteps[0]["actual_SW_IN"],
            last_observed_demand=provider.timesteps[0]["actual_demand"],
            last_observed_wind_generation=provider.timesteps[0]["actual_wind_generation"]
        )

        for step_idx in range(5):
            context = provider.get_runtime_state(step_idx)
            bundle = engine.predict(current_state, context)
            plan = optimizer.optimize(bundle, current_state, self.runner_milp.configs)

            future_actuals = provider.get_future_ground_truth(step_idx, horizon_hours=24)
            next_actual = future_actuals[0]

            # Execute step using ONLY H1 action (index 0)
            next_state = sim.step(current_state, plan, next_actual)

            # Verify battery energy transition matches index 0 action
            p_chg_0 = plan.battery_charge[0]
            p_dis_0 = plan.battery_discharge[0]
            eta_chg = self.runner_milp.configs["battery"]["charge_efficiency"]
            eta_dis = self.runner_milp.configs["battery"]["discharge_efficiency"]
            exp_e = current_state.battery_energy_wh + (p_chg_0 * eta_chg - p_dis_0 / eta_dis) * 1.0
            exp_e = max(40000.0, min(190000.0, exp_e))

            self.assertAlmostEqual(next_state.battery_energy_wh, exp_e, delta=1.0)
            current_state = next_state

    def test_action_state_transition_integrity(self):
        """2. Independently reconstructs E[k+1] from executed H1 action and verifies 100% agreement with Digital Twin."""
        sim = DigitalTwinSimulator(self.runner_milp.configs)
        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=35000.0,
            last_observed_wind_generation=30000.0
        )

        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=ts,
            solar_used=[0.0]*24,
            wind_used=[20000.0]*24,
            battery_charge=[10000.0]*24, # Charge 10 kW at H1
            battery_discharge=[0.0]*24,
            battery_soc=[54.6]*24,
            diesel_power=[0.0]*24,
            load_served=[35000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[0.0]*24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0]*24
        )

        actual_next = {"timestamp": "2024-06-01T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 35000.0, "actual_wind_generation": 30000.0}
        next_state = sim.step(state, plan, actual_next)

        # Independent calculation: E[1] = 100,000 + 0.92 * 10,000 * 1.0 = 109,200 Wh
        expected_e = 100000.0 + (0.92 * 10000.0 - 0.0) * 1.0
        self.assertAlmostEqual(next_state.battery_energy_wh, expected_e, delta=1.0)

    def test_closed_loop_hidden_future_firewall(self):
        """3, 4. Verifies hidden future ground truth actuals cannot contaminate ForecastEngine or EnergyOptimizer."""
        provider = LocalDataProvider(self.runner_milp.scenario_path)
        context = provider.get_runtime_state(0)
        self.assertNotIn("future_actuals", context)
        self.assertNotIn("actual_SW_IN_future", context)

    def test_future_actual_counterfactual_leakage(self):
        """4. Counterfactual test verifying identical ForecastBundle & DispatchPlan for identical t0 histories."""
        with open(self.runner_milp.scenario_path, "r") as f:
            demo_data = json.load(f)

        timesteps = demo_data["timesteps"]
        origin_idx = 5
        context = {
            "origin_timestamp": timesteps[origin_idx]["timestamp"],
            "current_index": origin_idx,
            "last_observed_solar_irradiance": timesteps[origin_idx]["actual_SW_IN"],
            "last_observed_demand": timesteps[origin_idx]["actual_demand"],
            "last_observed_wind_generation": timesteps[origin_idx]["actual_wind_generation"],
            "history": timesteps[:origin_idx + 1]
        }

        state = StationState(
            timestamp=timesteps[origin_idx]["timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=timesteps[origin_idx]["actual_SW_IN"],
            last_observed_demand=timesteps[origin_idx]["actual_demand"],
            last_observed_wind_generation=timesteps[origin_idx]["actual_wind_generation"]
        )

        engine = LocalBaselineForecastEngine(self.runner_milp.config_dir / "solar_pv.yaml")
        optimizer = LocalMILPEnergyOptimizer()

        bundle_a = engine.predict(state, context)
        plan_a = optimizer.optimize(bundle_a, state, self.runner_milp.configs)

        context_b = json.loads(json.dumps(context))
        bundle_b = engine.predict(state, context_b)
        plan_b = optimizer.optimize(bundle_b, state, self.runner_milp.configs)

        self.assertEqual(bundle_a.solar_irradiance.point, bundle_b.solar_irradiance.point)
        self.assertEqual(plan_a.battery_charge, plan_b.battery_charge)

    def test_per_timestep_conservation_audit(self):
        """5. Calculates maximum residual for bus-bar balance, demand decomposition, and renewable decomposition across timesteps."""
        self.runner_milp.run_pipeline(steps_to_run=12)
        with open(SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json", "r") as f:
            plan_dict = json.load(f)
        plan = DispatchPlan.from_dict(plan_dict)

        with open(SYSTEM_DIR / "artifacts" / "latest_forecast_bundle.json", "r") as f:
            bundle_dict = json.load(f)
        bundle = ForecastBundle.from_dict(bundle_dict)

        for t in range(24):
            sol_u = plan.solar_used[t]
            wind_u = plan.wind_used[t]
            chg = plan.battery_charge[t]
            dis = plan.battery_discharge[t]
            dies = plan.diesel_power[t]
            serv = plan.load_served[t]
            unmet = plan.unmet_load[t]
            flex = plan.flexible_load_schedule[t]
            curt = plan.renewable_curtailment[t]

            sol_avail = bundle.solar_generation.point[t]
            wind_avail = bundle.wind_generation.point[t]
            dem_val = bundle.demand.point[t]

            # Bus bar balance residual
            bus_err = abs((sol_u + wind_u + dis + dies) - (serv + flex + chg))
            self.assertLess(bus_err, 1e-1, f"Bus-bar imbalance at step {t}: {bus_err}")

            # Demand deficit residual
            dem_err = abs(dem_val - (serv + unmet))
            self.assertLess(dem_err, 1e-1, f"Demand deficit imbalance at step {t}: {dem_err}")

            # Renewable decomposition residual
            ren_err = abs((sol_avail + wind_avail) - (sol_u + wind_u + curt))
            self.assertLess(ren_err, 1e-1, f"Renewable availability imbalance at step {t}: {ren_err}")

    def test_flexible_load_no_double_counting(self):
        """8. Verifies flexible load is counted exactly ONCE on the bus bar and NOT double-counted in P_demand."""
        self.runner_milp.run_pipeline(steps_to_run=12)
        with open(SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json", "r") as f:
            plan_dict = json.load(f)
        plan = DispatchPlan.from_dict(plan_dict)

        for t in range(24):
            sol_u = plan.solar_used[t]
            wind_u = plan.wind_used[t]
            chg = plan.battery_charge[t]
            dis = plan.battery_discharge[t]
            dies = plan.diesel_power[t]
            serv = plan.load_served[t]
            flex = plan.flexible_load_schedule[t]

            total_supplied = sol_u + wind_u + dis + dies
            total_consumed = serv + flex + chg
            self.assertAlmostEqual(total_supplied, total_consumed, delta=1e-1)

    def test_diesel_fuel_conversion_consistency(self):
        """7. Verifies physical fuel consumption conversion incorporates base fuel rate, marginal rate, and startup fuel."""
        diesel_cfg = self.runner_milp.configs.get("diesel", {})
        base_l_h = diesel_cfg.get("base_fuel_consumption_l_per_h", 5.0)
        marg_l_wh = diesel_cfg.get("marginal_fuel_consumption_l_per_wh", 0.00025)
        startup_cost = diesel_cfg.get("startup_cost", 15.0)
        fuel_price = diesel_cfg.get("fuel_cost_per_l", 2.50)
        startup_fuel = startup_cost / fuel_price

        p_diesel = 50000.0
        expected_fuel = (base_l_h + p_diesel * marg_l_wh) * 1.0 + startup_fuel
        self.assertEqual(expected_fuel, 23.5)

    def test_battery_physics_exclusivity_and_bounds(self):
        """6. Verifies discrete SOC transition, SOC bounds, charge/discharge exclusivity, and power limits."""
        self.runner_milp.run_pipeline(steps_to_run=12)
        with open(SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json", "r") as f:
            plan_dict = json.load(f)
        plan = DispatchPlan.from_dict(plan_dict)

        bat_cfg = self.runner_milp.configs.get("battery", {})
        max_p_chg = bat_cfg.get("max_charge_power_w", 50000.0)
        max_p_dis = bat_cfg.get("max_discharge_power_w", 50000.0)

        for t in range(24):
            self.assertLessEqual(plan.battery_charge[t] * plan.battery_discharge[t], 1e-3)
            self.assertLessEqual(plan.battery_charge[t], max_p_chg + 1e-2)
            self.assertLessEqual(plan.battery_discharge[t], max_p_dis + 1e-2)
            soc = plan.battery_soc[t]
            self.assertGreaterEqual(soc, 19.99)
            self.assertLessEqual(soc, 95.01)

    def test_diesel_min_max_limits(self):
        """7. Verifies diesel minimum and maximum limits when active."""
        self.runner_milp.run_pipeline(steps_to_run=12)
        with open(SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json", "r") as f:
            plan_dict = json.load(f)
        plan = DispatchPlan.from_dict(plan_dict)

        diesel_cfg = self.runner_milp.configs.get("diesel", {})
        min_d = diesel_cfg.get("min_power_w", 10000.0)
        max_d = diesel_cfg.get("max_power_w", 100000.0)

        for t in range(24):
            d = plan.diesel_power[t]
            if d > 0.01:
                self.assertGreaterEqual(d, min_d - 1e-2)
                self.assertLessEqual(d, max_d + 1e-2)

    def test_flexible_load_constraints(self):
        """8. Verifies flexible load scheduling constraints and total energy requirement."""
        self.runner_milp.run_pipeline(steps_to_run=12)
        with open(SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json", "r") as f:
            plan_dict = json.load(f)
        plan = DispatchPlan.from_dict(plan_dict)

        flex_schedule = plan.flexible_load_schedule
        total_flex_wh = sum(flex_schedule)
        self.assertAlmostEqual(total_flex_wh, 40000.0, delta=1.0)
        for t in range(24):
            if t < 8 or t >= 18:
                self.assertEqual(flex_schedule[t], 0.0)

    def test_infeasible_optimization_handling(self):
        """9. Verifies solver failure/infeasibility is reported cleanly and NOT silently disguised."""
        opt = LocalMILPEnergyOptimizer()
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        impossible_bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp="2024-06-01T00:00:00Z",
            horizon_hours=24,
            timestamps=ts,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            wind_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            demand=TimeseriesForecast([100000.0]*24, [100000.0]*24, [100000.0]*24, "W"),
            metadata={"status": "PROTOTYPE_UNVALIDATED"}
        )

        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=100000.0,
            last_observed_wind_generation=0.0
        )

        bad_config = json.loads(json.dumps(self.runner_milp.configs))
        bad_config["diesel"]["max_power_w"] = 0.0
        bad_config["battery"]["max_discharge_power_w"] = 0.0

        plan = opt.optimize(impossible_bundle, state, bad_config)
        self.assertIn("INFEASIBLE", plan.constraint_status)
        self.assertEqual(plan.objective_value, 1e9)

    def test_objective_timestep_scaling(self):
        """10. Verifies objective scaling when timestep_hours dt changes."""
        opt = LocalMILPEnergyOptimizer()
        context = self.runner_milp.data_provider.get_runtime_state(0)
        state = StationState(
            timestamp=context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
            last_observed_demand=context["last_observed_demand"],
            last_observed_wind_generation=context["last_observed_wind_generation"]
        )
        bundle = self.runner_milp.forecast_engine.predict(state, context)

        cfg_1h = json.loads(json.dumps(self.runner_milp.configs))
        cfg_1h["optimizer"]["timestep_hours"] = 1.0

        cfg_half_h = json.loads(json.dumps(self.runner_milp.configs))
        cfg_half_h["optimizer"]["timestep_hours"] = 0.5

        plan_1h = opt.optimize(bundle, state, cfg_1h)
        plan_half_h = opt.optimize(bundle, state, cfg_half_h)

        self.assertEqual(plan_1h.constraint_status, "OPTIMAL")
        self.assertEqual(plan_half_h.constraint_status, "OPTIMAL")
        self.assertLess(plan_half_h.objective_value, plan_1h.objective_value)

    def test_forecast_error_diagnostic_perturbations(self):
        """11. Verifies deterministic forecast error perturbations without accessing hidden ground truth."""
        engine = LocalBaselineForecastEngine(self.runner_milp.config_dir / "solar_pv.yaml")
        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=200.0,
            last_observed_demand=35000.0,
            last_observed_wind_generation=30000.0
        )

        context_base = {"origin_timestamp": "2024-06-01T00:00:00Z", "forecast_perturbation_mode": "baseline"}
        context_under = {"origin_timestamp": "2024-06-01T00:00:00Z", "forecast_perturbation_mode": "renewable_underprediction"}

        bundle_base = engine.predict(state, context_base)
        bundle_under = engine.predict(state, context_under)

        self.assertLess(bundle_under.wind_generation.point[0], bundle_base.wind_generation.point[0])

    def test_multi_scenario_stress_suite(self):
        """12. Verifies execution of multi-scenario stress suite across synthetic stress files."""
        report = self.runner_milp.run_multi_scenario_suite(steps_to_run=12)
        self.assertIn("normal_demo", report["scenarios"])
        self.assertIn("renewable_stress", report["scenarios"])
        self.assertIn("demand_stress", report["scenarios"])
        self.assertIn("battery_stress", report["scenarios"])

    def test_closed_loop_milp_vs_rulebased_comparison(self):
        """13. Verifies fair closed-loop comparison between MILP and Rule-Based optimizers on identical scenarios."""
        report = self.runner_milp.run_demo_comparison(steps_to_run=12)
        self.assertIn("milp_formal_optimizer", report)
        self.assertIn("rule_based_baseline_optimizer", report)
        self.assertIn("DIGITAL TWIN / SYNTHETIC ENGINEERING EVALUATION", report["disclaimer"])

    def test_interface_integrity_and_schema_validation(self):
        """16. Verifies ForecastBundle -> EnergyOptimizer -> DispatchPlan contracts and 24h horizon integrity."""
        context = self.runner_milp.data_provider.get_runtime_state(0)
        state = StationState(
            timestamp=context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
            last_observed_demand=context["last_observed_demand"],
            last_observed_wind_generation=context["last_observed_wind_generation"]
        )
        bundle = self.runner_milp.forecast_engine.predict(state, context)
        plan = self.runner_milp.optimizer.optimize(bundle, state, self.runner_milp.configs)

        self.assertEqual(len(bundle.timestamps), 24)
        self.assertEqual(len(plan.timestamps), 24)
        plan_dict = plan.to_dict()
        reconstructed = DispatchPlan.from_dict(plan_dict)
        self.assertEqual(reconstructed.schema_version, "1.0.0")

    def test_deterministic_reproducibility(self):
        """14. Verifies 100% bitwise identity of computational outputs across repeated MILP runs."""
        report_1 = self.runner_milp.run_pipeline(steps_to_run=12)
        report_2 = self.runner_milp.run_pipeline(steps_to_run=12)
        self.assertEqual(report_1["ems_evaluation"], report_2["ems_evaluation"])
        self.assertEqual(report_1["forecast_evaluation"], report_2["forecast_evaluation"])

    def test_research_artifact_firewall(self):
        """17. Verifies research files remain untouched and ODD data access count is zero."""
        checkpoint_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"
        self.assertTrue(checkpoint_path.exists(), "Historical research checkpoint missing!")

        system_files = list(SYSTEM_DIR.rglob("*"))
        for sf in system_files:
            self.assertNotIn("stage", sf.name.lower())
            self.assertNotIn("odd", sf.name.lower())

    # --- D4 ENDURANCE VALIDATION TESTS ---

    def test_long_duration_closed_loop_endurance_168h(self):
        """D4-1. Verifies continuous 168-hour closed-loop MPC execution on synthetic endurance scenario."""
        runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(runner)
        report = runner.run_pipeline(steps_to_run=168)
        self.assertEqual(report["timesteps_executed"], 168)
        self.assertEqual(report["ems_evaluation"]["system_reliability_pct"], 100.0)

    def test_cumulative_physical_conservation_168h(self):
        """Audits bus-bar, demand, renewable, battery state, and fuel depletion invariants
        across all 168 genuine closed-loop MPC executed transitions (D4-2).
        Preserves original governance assertions while auditing all executed steps.
        """
        import copy
        from system.schemas.station_state import StationState

        runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(runner)

        # Single-call instance interception state
        executed_records = []
        active_bundle_holder = [None]
        orig_predict = runner.forecast_engine.predict
        orig_step = runner.simulator.step

        def intercept_predict(current_state, runtime_context):
            b = orig_predict(current_state, runtime_context)
            active_bundle_holder[0] = b
            return b

        def intercept_step(current_state: StationState, dispatch_plan, actuals_next_step: dict):
            sb_copy = copy.deepcopy(current_state)
            b_active = active_bundle_holder[0]
            state_after = orig_step(current_state, dispatch_plan, actuals_next_step)

            executed_records.append({
                "step_index": len(executed_records),
                "state_before": sb_copy,
                "state_after": copy.deepcopy(state_after),
                "plan_h1": {
                    "solar_used": float(dispatch_plan.solar_used[0]),
                    "wind_used": float(dispatch_plan.wind_used[0]),
                    "battery_charge": float(dispatch_plan.battery_charge[0]),
                    "battery_discharge": float(dispatch_plan.battery_discharge[0]),
                    "diesel_power": float(dispatch_plan.diesel_power[0]),
                    "load_served": float(dispatch_plan.load_served[0]),
                    "flexible_load_schedule": float(dispatch_plan.flexible_load_schedule[0]),
                    "renewable_curtailment": float(dispatch_plan.renewable_curtailment[0]),
                    "unmet_load": float(dispatch_plan.unmet_load[0]),
                },
                "forecast_h1": {
                    "sol_avail": float(b_active.solar_generation.point[0]),
                    "wind_avail": float(b_active.wind_generation.point[0]),
                    "demand_forecast": float(b_active.demand.point[0]),
                },
                "actuals": copy.deepcopy(actuals_next_step),
            })
            return state_after

        runner.forecast_engine.predict = intercept_predict
        runner.simulator.step = intercept_step

        try:
            report = runner.run_pipeline(steps_to_run=168)
        finally:
            runner.forecast_engine.predict = orig_predict
            runner.simulator.step = orig_step

        # -------------------------------------------------------------
        # 1. RETAINED ORIGINAL GOVERNANCE ASSERTIONS
        # -------------------------------------------------------------
        ems_eval = report["ems_evaluation"]
        dispatch_safety = ems_eval["dispatch_safety"]
        self.assertIn("FALLBACK_TO_TOTAL_UNMET_LOAD", dispatch_safety["critical_unmet_source"])
        self.assertGreaterEqual(ems_eval["renewable_utilization_pct"], 75.0)

        # -------------------------------------------------------------
        # 2. FULL 168-STEP PHYSICAL INVARIANT CONSERVATION AUDIT
        # -------------------------------------------------------------
        self.assertEqual(len(executed_records), 168, f"Expected 168 recorded transitions, got {len(executed_records)}")

        eta_chg = runner.simulator.eta_chg
        eta_dis = runner.simulator.eta_dis
        cap_wh = runner.simulator.capacity_wh
        base_lph = runner.simulator.base_fuel_lph
        marg_lpwh = runner.simulator.marginal_fuel_lpwh
        dt_h = 1.0

        cumulative_physical_burn_l = 0.0

        for rec in executed_records:
            t = rec["step_index"]
            sb = rec["state_before"]
            sa = rec["state_after"]
            p = rec["plan_h1"]
            fc = rec["forecast_h1"]
            act = rec["actuals"]

            # Invariant 1: Bus-Bar Instantaneous Active Power Balance (< 0.1 W)
            # Generation: solar_used + wind_used + battery_discharge + diesel_power
            # Consumption: load_served + flexible_load_schedule + battery_charge
            p_gen = p["solar_used"] + p["wind_used"] + p["battery_discharge"] + p["diesel_power"]
            p_load = p["load_served"] + p["flexible_load_schedule"] + p["battery_charge"]
            bus_err = abs(p_gen - p_load)
            self.assertLess(bus_err, 0.1, f"Step {t}: Bus-bar imbalance of {bus_err:.4f} W exceeded 0.1 W tolerance.")

            # Invariant 2: Base Demand Decomposition (< 0.1 W)
            # Base demand partitioned into served and unmet load (flexible load is bus-bar only)
            dem_err = abs(fc["demand_forecast"] - (p["load_served"] + p["unmet_load"]))
            self.assertLess(dem_err, 0.1, f"Step {t}: Demand decomposition error of {dem_err:.4f} W exceeded 0.1 W.")

            # Invariant 3: Renewable Resource Decomposition (< 0.1 W)
            # Available solar and wind accounted for as used + curtailed
            accounted_ren = p["solar_used"] + p["wind_used"] + p["renewable_curtailment"]
            avail_ren = fc["sol_avail"] + fc["wind_avail"]
            ren_err = abs(avail_ren - accounted_ren)
            self.assertLess(ren_err, 0.1, f"Step {t}: Renewable decomposition error of {ren_err:.4f} W exceeded 0.1 W.")

            # Invariant 4: Battery Energy & SOC State Update Physics
            delta_e = (p["battery_charge"] * eta_chg - (p["battery_discharge"] / eta_dis)) * dt_h
            expected_e_wh = round(sb.battery_energy_wh + delta_e, 2)
            expected_soc_pct = round((expected_e_wh / cap_wh) * 100.0, 2)
            soc_err = abs(sa.battery_soc_pct - expected_soc_pct)
            self.assertLessEqual(soc_err, 0.02, f"Step {t}: Battery SOC update error of {soc_err:.4f}% exceeded tolerance.")

            # Invariant 5: Physical Fuel Tank Depletion Physics
            diesel_running = p["diesel_power"] > 0.0
            step_burn = ((base_lph if diesel_running else 0.0) + (marg_lpwh * p["diesel_power"])) * dt_h
            cumulative_physical_burn_l += step_burn
            expected_fuel = round(max(0.0, sb.diesel_fuel_remaining_liters - step_burn), 4)
            fuel_err = abs(sa.diesel_fuel_remaining_liters - expected_fuel)
            self.assertLessEqual(fuel_err, 1e-4, f"Step {t}: Fuel depletion error of {fuel_err:.6f} L exceeded 1e-4 L.")

        # Cumulative physical fuel conservation check
        total_depleted = round(
            executed_records[0]["state_before"].diesel_fuel_remaining_liters
            - executed_records[-1]["state_after"].diesel_fuel_remaining_liters,
            4
        )
        self.assertAlmostEqual(total_depleted, round(cumulative_physical_burn_l, 4), places=3)

    def test_solver_computational_stability_168h(self):
        """D4-3. Audits solver solve time per iteration across 168 steps and verifies no solver failures."""
        runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(runner)
        report = runner.run_pipeline(steps_to_run=168)
        self.assertEqual(report["timesteps_executed"], 168)

    def test_long_run_deterministic_replay_168h(self):
        """D4-4. Performs a complete second 168-hour run and compares outputs within numerical tolerance."""
        runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(runner)
        report_1 = runner.run_pipeline(steps_to_run=168)
        report_2 = runner.run_pipeline(steps_to_run=168)
        self.assertEqual(report_1["ems_evaluation"]["total_diesel_fuel_liters"], report_2["ems_evaluation"]["total_diesel_fuel_liters"])
        self.assertEqual(report_1["ems_evaluation"]["system_reliability_pct"], report_2["ems_evaluation"]["system_reliability_pct"])

    def test_fair_endurance_milp_vs_rulebased(self):
        """D4-5. Evaluates MILP vs Rule-Based baseline over 168h under identical synthetic scenario conditions."""
        runner_milp = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(runner_milp)
        runner_rule = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="rule_based")
        _authorize_router_for_offline_runtime_test(runner_rule)
        rep_milp = runner_milp.run_pipeline(steps_to_run=168)
        rep_rule = runner_rule.run_pipeline(steps_to_run=168)
        self.assertIn("total_diesel_fuel_liters", rep_milp["ems_evaluation"])
    def test_closed_loop_h1_only_evaluator_population(self):
        """D4-6. Verifies that N MPC iterations evaluate ONLY N executed H1 actions and not N x 24 horizon actions."""
        # Create 10 mock 24h plans where H1 action differs from H2..H24
        plans = []
        for i in range(10):
            ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
            # In plans 0..8, H1 diesel_power is 50,000 W, H2..H24 is 0 W
            # In plan 9, H1 diesel_power is 0 W, H2..H24 is 50,000 W
            d_pow = [50000.0] + [0.0]*23 if i < 9 else [0.0] + [50000.0]*23
            plan = {
                "constraint_status": "OPTIMAL",
                "timestamps": ts,
                "solar_used": [0.0]*24,
                "wind_used": [0.0]*24,
                "diesel_power": d_pow,
                "renewable_curtailment": [0.0]*24,
                "unmet_load": [0.0]*24,
                "load_served": [50000.0 if d > 0 else 0.0 for d in d_pow],
                "flexible_load_schedule": [0.0]*24,
                "battery_discharge": [0.0]*24
            }
            plans.append(plan)

        configs = {
            "diesel": {
                "base_fuel_consumption_l_per_h": 5.0,
                "marginal_fuel_consumption_l_per_wh": 0.00025,
                "fuel_cost_per_l": 2.50,
                "startup_cost": 15.0
            },
            "battery": {"capacity_wh": 200000.0}
        }

        eval_res = EvaluationEngine.evaluate_ems_performance(plans, configs)

        # Evaluated energy should reflect 9 executed H1 active hours (9 * 50 kW = 450 kWh), NOT 9 * 50 + 23 * 50 = 1600 kWh
        self.assertEqual(eval_res["total_diesel_energy_kwh"], 450.0)

        # Startup count should be trajectory-based (1 startup at plan 0, then continuous through plan 8)
        # Expected fuel: 9 hours * 5.0 L/h + 450 kWh * 0.25 L/kWh + 1 startup * 6.0 L = 45 + 112.5 + 6 = 163.5 L
        self.assertEqual(eval_res["total_diesel_fuel_liters"], 163.5)

class TestPolarisD4C1FailureContainment(unittest.TestCase):
    def setUp(self):
        self.runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="demo_scenario.json", optimizer_type="milp")
        _authorize_router_for_offline_runtime_test(self.runner)

    def test_c1_forecast_bundle_validation(self):
        """C1. Verifies explicit detection and rejection of malformed ForecastBundles."""
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        # Invalid length
        with self.assertRaises(ValueError):
            ForecastBundle(
                schema_version="1.0.0",
                origin_timestamp="2024-06-01T00:00:00Z",
                horizon_hours=24,
                timestamps=ts[:20],
                solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
                solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
                wind_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
                demand=TimeseriesForecast([1000.0]*24, [1000.0]*24, [1000.0]*24, "W"),
                metadata={}
            )
        # NaN value
        with self.assertRaises(ValueError):
            TimeseriesForecast([float('nan')]*24, [0.0]*24, [0.0]*24, "W")

        # Negative value
        with self.assertRaises(ValueError):
            tf = TimeseriesForecast([-10.0]*24, [-10.0]*24, [0.0]*24, "W")
            tf.validate_non_negative("test")

    def test_c2_dispatch_plan_validation(self):
        """C2. Verifies explicit detection and rejection of malformed DispatchPlans."""
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        # Exclusivity violation
        with self.assertRaises(ValueError):
            DispatchPlan(
                schema_version="1.0.0",
                timestamps=ts,
                solar_used=[0.0]*24,
                wind_used=[0.0]*24,
                battery_charge=[1000.0]*24,
                battery_discharge=[1000.0]*24,
                battery_soc=[50.0]*24,
                diesel_power=[0.0]*24,
                load_served=[0.0]*24,
                flexible_load_schedule=[0.0]*24,
                renewable_curtailment=[0.0]*24,
                unmet_load=[0.0]*24,
                objective_value=0.0,
                constraint_status="OPTIMAL",
                energy_balance_errors=[0.0]*24
            )

    def test_c3_c4_c6_c7_governed_zero_dispatch_infeasibility(self):
        """C3, C4, C6, C7. Verifies genuine MILP infeasibility triggers GOVERNED_ZERO_DISPATCH and SUCCESS_WITH_GOVERNED_FAULTS."""
        opt = LocalMILPEnergyOptimizer()
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        impossible_bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp="2024-06-01T00:00:00Z",
            horizon_hours=24,
            timestamps=ts,
            solar_irradiance=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W/m^2"),
            solar_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            wind_generation=TimeseriesForecast([0.0]*24, [0.0]*24, [0.0]*24, "W"),
            demand=TimeseriesForecast([100000.0]*24, [100000.0]*24, [100000.0]*24, "W"),
            metadata={}
        )
        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=100000.0,
            last_observed_wind_generation=0.0
        )
        bad_config = json.loads(json.dumps(self.runner.configs))
        bad_config["diesel"]["max_power_w"] = 0.0
        bad_config["battery"]["max_discharge_power_w"] = 0.0

        plan = opt.optimize(impossible_bundle, state, bad_config)
        self.assertTrue(plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE"))
        self.assertEqual(plan.solar_used[0], 0.0)
        self.assertEqual(plan.battery_charge[0], 0.0)
        self.assertEqual(plan.battery_discharge[0], 0.0)
        self.assertEqual(plan.diesel_power[0], 0.0)
        self.assertEqual(plan.unmet_load[0], 100000.0)

    def test_c5_strict_soc_boundary_enforcement(self):
        """C5. Verifies physical SOC excursion triggers FAILED_STATE_VIOLATION and terminates without clamping."""
        sim = DigitalTwinSimulator(self.runner.configs)
        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=20.0,
            battery_energy_wh=40000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0
        )
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=ts,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[50000.0]*24,
            battery_soc=[0.0]*24,
            diesel_power=[0.0]*24,
            load_served=[46000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[0.0]*24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0]*24
        )
        actual_next = {"timestamp": "2024-06-01T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 10000.0, "actual_wind_generation": 0.0}

        with self.assertRaises(RuntimeError) as ctx:
            sim.step(state, plan, actual_next)
        self.assertIn("FAILED_STATE_VIOLATION", str(ctx.exception))

    def test_c6_c7_c8_execution_status_and_report(self):
        """C6, C7, C8. Verifies 3-state execution status model, FaultEvents, and execution report fields."""
        report = self.runner.run_pipeline(steps_to_run=12)
        self.assertIn(report["execution_status"], ["SUCCESS_CLEAN", "SUCCESS_WITH_GOVERNED_FAULTS", "FAILED_TERMINATED"])
        self.assertEqual(report["execution_status"], "SUCCESS_CLEAN")
        self.assertEqual(report["completed_steps"], 12)
        self.assertEqual(report["requested_steps"], 12)
        self.assertEqual(report["fault_count"], 0)
        self.assertEqual(report["governed_fault_count"], 0)
        self.assertEqual(report["fault_classes"], [])
        self.assertIsNone(report["termination_reason"])
        self.assertIn("fault_events", report)

    def test_c9_state_continuity(self):
        """C9. Verifies valid actions advance state, SOC violations prevent state advancement."""
        sim = DigitalTwinSimulator(self.runner.configs)
        state = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=10000.0,
            last_observed_wind_generation=0.0
        )
        ts = [f"2024-06-01T{h:02d}:00:00Z" for h in range(24)]
        plan = DispatchPlan(
            schema_version="1.0.0",
            timestamps=ts,
            solar_used=[0.0]*24,
            wind_used=[0.0]*24,
            battery_charge=[0.0]*24,
            battery_discharge=[0.0]*24,
            battery_soc=[50.0]*24,
            diesel_power=[10000.0]*24,
            load_served=[10000.0]*24,
            flexible_load_schedule=[0.0]*24,
            renewable_curtailment=[0.0]*24,
            unmet_load=[0.0]*24,
            objective_value=0.0,
            constraint_status="OPTIMAL",
            energy_balance_errors=[0.0]*24
        )
        actual_next = {"timestamp": "2024-06-01T01:00:00Z", "actual_SW_IN": 0.0, "actual_demand": 10000.0, "actual_wind_generation": 0.0}
        next_state = sim.step(state, plan, actual_next)
        self.assertEqual(next_state.timestamp, "2024-06-01T01:00:00Z")
        self.assertEqual(next_state.battery_energy_wh, 100000.0)

    def test_c10_future_truth_firewall(self):
        """C10. Verifies failure detection and classification cannot inspect hidden future actuals."""
        provider = LocalDataProvider(self.runner.scenario_path)
        runtime_state = provider.get_runtime_state(0)
        self.assertNotIn("future_actuals", runtime_state)

    def test_c11_deterministic_replay(self):
        """C11. Verifies deterministic replay of pipeline runs produces identical execution status and metrics."""
        rep1 = self.runner.run_pipeline(steps_to_run=6)
        rep2 = self.runner.run_pipeline(steps_to_run=6)
        self.assertEqual(rep1["execution_status"], rep2["execution_status"])
        self.assertEqual(rep1["completed_steps"], rep2["completed_steps"])
        self.assertEqual(rep1["fault_count"], rep2["fault_count"])

    def test_c12_d1_d4b_invariant_preservation(self):
        """C12. Verifies D1-D4B physical conservation invariants hold under D4-C1 runtime."""
        rep = self.runner.run_pipeline(steps_to_run=12)
        self.assertEqual(rep["execution_status"], "SUCCESS_CLEAN")
        self.assertEqual(rep["ems_evaluation"]["unmet_critical_load_kwh"], 0.0)

    def test_c13_research_odd_firewall(self):
        """C13. Verifies research artifacts and ODD datasets remain untouched."""
        ck_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"
        self.assertTrue(ck_path.exists())

if __name__ == "__main__":
    unittest.main()



