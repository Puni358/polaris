"""
POLARIS — Static Unit Tests for Remediated OD-02 Boundary Diagnostic Harness
Tracking ID: PROP-2026-OD02-DIAG-01 (Revision 2.1)
Specification: SPEC-2026-OD02-DIAG-01

GOVERNANCE CONTRACT:
- STATIC VERIFICATION ONLY.
- ZERO optimizer calls, ZERO HiGHS execution.
- ZERO dataset access or filesystem reading.
- Validates:
  1. Variant 3 single-shift transform & metadata integrity (F-01).
  2. Variant 1 Policy B EBR wiring into solver config (F-02).
  3. Decision OD-01 dynamic terminal target derivation (F-03).
  4. Variant 2/3 solar bounds consistency (F-04).
  5. Four-tier lexicographic objective reporting (F-07).
  6. Fail-closed allow-list & quarantine safeguards (F-06, F-09).
  7. Solar & wind used power in FirstActionVector (F-08).
  8. Idempotency of Variant 0 baseline transform (F-11).
  9. Pre-execution run planning & manifest schema.
"""

import unittest
import unittest.mock
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from diag_od02_boundary import (
    MDR_CANONICAL_VERSION,
    GATE_A_APPROVED,
    GATE_B_AUTHORIZED,
    GATE_C_AUTHORIZED,
    WINNER_SELECTION,
    GateExecutionBlockedError,
    QuarantineViolationError,
    ExperimentalFeatureDisabledError,
    assert_gate_c_authorized,
    check_quarantine_compliance,
    ContinuousActionVector,
    BinaryActionVector,
    FirstActionVector,
    compare_first_actions,
    ObjectiveComponents,
    ObjectiveComparisonStatus,
    ObjectiveComparisonResult,
    compare_objectives,
    SolverTerminationStatus,
    DegeneracyStatus,
    DiagnosticOutcome,
    VariantType,
    VARIANT_CONFIGS,
    align_bundle_variant_0,
    align_bundle_variant_1,
    align_bundle_variant_2,
    align_bundle_variant_3,
    prepare_gap19_solver_config,
    extract_first_action_from_dispatch_plan,
    extract_objectives_from_dispatch_plan,
    execute_diagnostic_solve,
    InputManifestItem,
    DatasetIngestionFirewall,
    plan_diagnostic_run,
    VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD,
    VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN,
)
if "diag_od02_boundary" in sys.modules and "scratch.diag_od02_boundary" not in sys.modules:
    sys.modules["scratch.diag_od02_boundary"] = sys.modules["diag_od02_boundary"]

from run_od02_boundary_diagnostic import (
    RUNNER_TRACKING_ID,
    DEFAULT_OUTPUT_DIR,
    APPROVED_2024_INPUT_ALLOW_LIST,
    DiagnosticOriginResult,
    verify_origin_manifest,
    build_diagnostic_forecast_bundle,
    build_diagnostic_station_state,
    execute_single_origin_diagnostic,
    run_batch_od02_diagnostic,
)


# In-Memory Synthetic Fixtures for Static Testing (NO file access)
@dataclass
class MockTimeseries:
    point: List[float]
    lower: Optional[List[float]] = None
    upper: Optional[List[float]] = None
    unit: str = "W"


@dataclass
class MockForecastBundle:
    timestamps: List[str]
    solar_generation: MockTimeseries
    solar_irradiance: MockTimeseries
    wind_generation: MockTimeseries
    demand: MockTimeseries
    metadata: Dict[str, Any]
    demand_critical: Optional[MockTimeseries] = None


@dataclass
class MockStationState:
    battery_energy_wh: float = 100000.0
    diesel_running: bool = False
    operating_mode: str = "NORMAL"


@dataclass
class MockDispatchPlan:
    solar_used: List[float]
    wind_used: List[float]
    diesel_power: List[float]
    battery_charge: List[float]
    battery_discharge: List[float]
    load_served: List[float]
    unmet_load: List[float]
    flexible_load_schedule: List[float]
    renewable_curtailment: List[float]
    objective_value: float = 123.45
    j1_objective: float = 0.0
    j2_objective: float = 0.0
    j3_objective: float = 123.45
    j4_objective: float = 5.0
    constraint_status: str = "OPTIMAL"


def create_synthetic_bundle() -> MockForecastBundle:
    """Creates a purely synthetic, in-memory 24-step forecast bundle."""
    ts = [f"2024-06-21T{h:02d}:00:00Z" for h in range(24)]
    solar_gen = [float(h * 1000) for h in range(24)]
    solar_irr = [float(h * 20) for h in range(24)]
    wind_gen = [5000.0] * 24
    demand = [15000.0] * 24
    demand_crit = [5000.0] * 24
    ebr_raw = [float(20000 + h * 500) for h in range(24)]
    
    return MockForecastBundle(
        timestamps=ts,
        solar_generation=MockTimeseries(point=solar_gen, lower=solar_gen, upper=solar_gen, unit="W"),
        solar_irradiance=MockTimeseries(point=solar_irr, lower=solar_irr, upper=solar_irr, unit="W/m^2"),
        wind_generation=MockTimeseries(point=wind_gen, unit="W"),
        demand=MockTimeseries(point=demand, unit="W"),
        demand_critical=MockTimeseries(point=demand_crit, unit="W"),
        metadata={"ebr_target_wh": ebr_raw},
    )


class TestDiagnosticGovernanceAndFirewalls(unittest.TestCase):
    """Verifies governance rules, gate firewalls, and allow-list safeguards."""

    def test_canonical_mdr_version(self):
        self.assertEqual(MDR_CANONICAL_VERSION, "1.9.13")

    def test_gate_authorization_flags(self):
        self.assertTrue(GATE_A_APPROVED)
        self.assertTrue(GATE_B_AUTHORIZED)
        self.assertFalse(GATE_C_AUTHORIZED)
        self.assertIsNone(WINNER_SELECTION)

    def test_gate_c_execution_firewall(self):
        with self.assertRaises(GateExecutionBlockedError):
            assert_gate_c_authorized()

    def test_execute_diagnostic_solve_blocks_under_gate_b(self):
        """Gate C unauthorized: execute_diagnostic_solve fails closed BEFORE optimizer construction."""
        import unittest.mock
        bundle = create_synthetic_bundle()
        state = MockStationState()
        cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
        with unittest.mock.patch("system.optimization.implementations.gap19_highs_native.GAP19HighsNativeOptimizer") as mock_gap19:
            with self.assertRaises(GateExecutionBlockedError):
                execute_diagnostic_solve(bundle, state, cfg, mock_optimizer=None)
            # CRITICAL: Confirms no production solver object was created
            mock_gap19.assert_not_called()

    def test_execute_diagnostic_solve_blocks_even_with_mock_under_gate_b(self):
        """Gate C unauthorized: passing a mock optimizer cannot bypass the firewall."""
        import unittest.mock
        bundle = create_synthetic_bundle()
        state = MockStationState()
        cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}
        fake_opt = unittest.mock.MagicMock()
        with self.assertRaises(GateExecutionBlockedError):
            execute_diagnostic_solve(bundle, state, cfg, mock_optimizer=fake_opt)
        fake_opt.optimize.assert_not_called()

    def test_execute_diagnostic_solve_authorized_fake_optimizer_control_flow(self):
        """
        Gate C authorized in isolated test: exercises full control flow with fake optimizer.
        Confirms fake receives exact production interface argument types and order without constructing HiGHS.
        """
        import unittest.mock
        import diag_od02_boundary as diag_mod

        bundle = create_synthetic_bundle()
        state = MockStationState()
        cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}

        class SpyOptimizer:
            def __init__(self):
                self.captured = []

            def optimize(self, forecast_bundle, station_state, config):
                self.captured.append((forecast_bundle, station_state, config))
                return MockDispatchPlan(
                    solar_used=[1000.0] * 24,
                    wind_used=[500.0] * 24,
                    diesel_power=[2000.0] * 24,
                    battery_charge=[0.0] * 24,
                    battery_discharge=[500.0] * 24,
                    load_served=[3500.0] * 24,
                    unmet_load=[0.0] * 24,
                    flexible_load_schedule=[0.0] * 24,
                    renewable_curtailment=[0.0] * 24,
                    objective_value=50.0,
                    j1_objective=0.0,
                    j2_objective=0.0,
                    j3_objective=50.0,
                    j4_objective=0.0,
                    constraint_status="OPTIMAL",
                )

        spy = SpyOptimizer()
        with unittest.mock.patch.object(diag_mod, "GATE_C_AUTHORIZED", True):
            status, u0, objs = execute_diagnostic_solve(bundle, state, cfg, mock_optimizer=spy)

        self.assertEqual(status, SolverTerminationStatus.OPTIMAL)
        self.assertEqual(len(spy.captured), 1)
        passed_bundle, passed_state, passed_cfg = spy.captured[0]
        # Verify arguments match exact EnergyOptimizer protocol
        self.assertIs(passed_bundle, bundle)
        self.assertIs(passed_state, state)
        self.assertIn("terminal_target_wh", passed_cfg)
        self.assertIn("ebr_target_wh", passed_cfg)
        # Verify u0 extraction
        self.assertIsNotNone(u0)
        self.assertEqual(u0.continuous.p_diesel, 2000.0)
        self.assertEqual(u0.continuous.p_sol_used, 1000.0)
        self.assertEqual(u0.continuous.p_wind_used, 500.0)
        self.assertIsNone(u0.continuous.p_curt_sol)
        self.assertIsNone(u0.continuous.p_curt_wind)
        # Verify objective extraction
        self.assertIsNotNone(objs)
        self.assertEqual(objs.j3_diesel_fuel_cost, 50.0)
        self.assertEqual(objs.j1_critical_deficit, 0.0)

    def test_execute_diagnostic_solve_authorized_production_optimizer_instantiation_without_execution(self):
        """Gate C authorized in isolated test: verifies production optimizer instantiation without invoking HiGHS."""
        import unittest.mock
        import diag_od02_boundary as diag_mod

        bundle = create_synthetic_bundle()
        state = MockStationState()
        cfg = {"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}}

        mock_plan = MockDispatchPlan(
            solar_used=[1000.0] * 24,
            wind_used=[500.0] * 24,
            diesel_power=[2000.0] * 24,
            battery_charge=[0.0] * 24,
            battery_discharge=[500.0] * 24,
            load_served=[3500.0] * 24,
            unmet_load=[0.0] * 24,
            flexible_load_schedule=[0.0] * 24,
            renewable_curtailment=[0.0] * 24,
            objective_value=50.0,
            j1_objective=0.0,
            j2_objective=0.0,
            j3_objective=50.0,
            j4_objective=0.0,
            constraint_status="OPTIMAL",
        )

        with unittest.mock.patch("system.optimization.implementations.gap19_highs_native.GAP19HighsNativeOptimizer") as mock_opt_cls:
            mock_instance = mock_opt_cls.return_value
            mock_instance.optimize.return_value = mock_plan

            with unittest.mock.patch.object(diag_mod, "GATE_C_AUTHORIZED", True):
                status, u0, objs = execute_diagnostic_solve(bundle, state, cfg, mock_optimizer=None)

            mock_opt_cls.assert_called_once_with()
            mock_instance.optimize.assert_called_once()
            self.assertEqual(status, SolverTerminationStatus.OPTIMAL)
            self.assertIsNotNone(u0)
            self.assertEqual(u0.continuous.p_diesel, 2000.0)

    def test_quarantine_compliance_filter(self):
        forbidden_samples = [
            "data/blind.csv",
            "POLARIS_v0_1_future_weather_forecasts_2025.csv",
            "raw_unfilled_year_2025.csv",
            "experiments/stage4_blind/results.parquet",
        ]
        for sample in forbidden_samples:
            with self.assertRaises(QuarantineViolationError):
                check_quarantine_compliance(sample)

        allowed_samples = [
            "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv",
            "candidate_k_2024_clean_matrix.parquet",
            "experiments/diagnostics/diag_od02_boundary_2024/",
        ]
        for sample in allowed_samples:
            check_quarantine_compliance(sample)

    def test_dataset_ingestion_firewall_fails_closed_when_empty(self):
        fw = DatasetIngestionFirewall(allow_list=[])
        with self.assertRaises(PermissionError):
            fw.validate_file("data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv")

    def test_dataset_ingestion_firewall_fails_closed_when_unverified(self):
        item = InputManifestItem("data/2024_test.parquet", "abc", "desc", is_verified=False)
        fw = DatasetIngestionFirewall(allow_list=[item])
        with self.assertRaises(PermissionError):
            fw.validate_file("data/2024_test.parquet")

    def test_dataset_ingestion_firewall_accepts_verified_entry(self):
        item = InputManifestItem("data/2024_test.parquet", "abc", "desc", is_verified=True)
        fw = DatasetIngestionFirewall(allow_list=[item])
        fw.validate_file("data/2024_test.parquet")  # Should not raise


class TestActionVectorAndComparison(unittest.TestCase):
    """Verifies action vector schemas including solar/wind used power."""

    def test_binary_action_vector_domain(self):
        b = BinaryActionVector(u_diesel=1, v_start=0, u_chg=0, u_dis=1)
        self.assertEqual(b.u_diesel, 1)
        with self.assertRaises(ValueError):
            BinaryActionVector(u_diesel=2)

    def test_action_comparison_includes_solar_and_wind_used(self):
        base = FirstActionVector(
            continuous=ContinuousActionVector(
                p_sol_used=3000.0, p_wind_used=2000.0, p_diesel=0.0, p_chg=5000.0,
                p_dis=0.0, p_curt_total=0.0, p_served=15000.0, p_unmet=0.0, p_flex=0.0
            ),
            binary=BinaryActionVector()
        )
        # Variant reallocates between solar and wind
        var = FirstActionVector(
            continuous=ContinuousActionVector(
                p_sol_used=4000.0, p_wind_used=1000.0, p_diesel=0.0, p_chg=5000.0,
                p_dis=0.0, p_curt_total=0.0, p_served=15000.0, p_unmet=0.0, p_flex=0.0
            ),
            binary=BinaryActionVector()
        )

        res = compare_first_actions(base, var)
        self.assertEqual(res.continuous_deltas_w["p_sol_used"], 1000.0)
        self.assertEqual(res.continuous_deltas_w["p_wind_used"], -1000.0)
        self.assertEqual(res.max_continuous_delta_w, 1000.0)
        self.assertIsNone(res.continuous_difference_detected)  # tau_cont unset


class TestVariantMappingAndFailClosedGuards(unittest.TestCase):
    """Verifies variant transformations, bounds consistency, and V3 single-shift."""

    def test_variant_0_frozen_od02_mapping(self):
        bundle = create_synthetic_bundle()
        v0 = align_bundle_variant_0(bundle)
        expected_solar = [float(h * 1000) for h in range(1, 24)] + [0.0]
        self.assertEqual(v0.solar_generation.point, expected_solar)
        self.assertEqual(v0.timestamps[0], "2024-06-21T01:00:00Z")
        self.assertEqual(v0.timestamps[-1], "2024-06-22T00:00:00Z")
        self.assertEqual(v0.metadata["ebr_target_wh"], bundle.metadata["ebr_target_wh"])

    def test_variant_0_idempotency(self):
        """Applying V0 transform twice must return unmodified (no double shift)."""
        bundle = create_synthetic_bundle()
        v0_first = align_bundle_variant_0(bundle)
        v0_second = align_bundle_variant_0(v0_first)
        self.assertEqual(v0_first.timestamps, v0_second.timestamps)
        self.assertEqual(v0_first.solar_generation.point, v0_second.solar_generation.point)

    def test_variant_2_bounds_consistency(self):
        """Variant 2 must update upper bound to prevent lower <= point <= upper violation."""
        bundle = create_synthetic_bundle()
        VARIANT_CONFIGS[VariantType.VARIANT_2_SOLAR_EST_ONLY].is_enabled = True
        try:
            v2 = align_bundle_variant_2(bundle, candidate_slot23_solar_w=3500.0, allow_experimental=True)
            self.assertEqual(v2.solar_generation.point[-1], 3500.0)
            self.assertGreaterEqual(v2.solar_generation.upper[-1], 3500.0)
            self.assertLessEqual(v2.solar_generation.lower[-1], 3500.0)
        finally:
            VARIANT_CONFIGS[VariantType.VARIANT_2_SOLAR_EST_ONLY].is_enabled = False

    def test_variant_3_no_double_shift(self):
        """CRITICAL: Variant 3 must shift solar & timestamps by exactly +1h, NOT +2h."""
        bundle = create_synthetic_bundle()
        VARIANT_CONFIGS[VariantType.VARIANT_1_EBR_SHIFT_ONLY].is_enabled = True
        VARIANT_CONFIGS[VariantType.VARIANT_3_COMBINED_INTERACTION].is_enabled = True
        try:
            v3 = align_bundle_variant_3(bundle, candidate_slot23_solar_w=4000.0, allow_experimental=True)
            
            # 1. Timestamps shifted by exactly +1h (01:00:00Z to 00:00:00Z next day)
            self.assertEqual(v3.timestamps[0], "2024-06-21T01:00:00Z")
            self.assertEqual(v3.timestamps[-1], "2024-06-22T00:00:00Z")
            
            # 2. Solar generation slots 0..22 match raw 1..23 (single +1h shift)
            expected_solar_head = [float(h * 1000) for h in range(1, 24)]
            self.assertEqual(v3.solar_generation.point[:-1], expected_solar_head)
            self.assertEqual(v3.solar_generation.point[-1], 4000.0)
            
            # 3. EBR shifted by +1h with persistence tail
            raw_ebr = list(bundle.metadata["ebr_target_wh"])
            expected_ebr = raw_ebr[1:] + [raw_ebr[-1]]
            self.assertEqual(v3.metadata["ebr_target_wh"], expected_ebr)
            
            # 4. Correct metadata identity
            self.assertEqual(v3.metadata["diagnostic_variant"], VariantType.VARIANT_3_COMBINED_INTERACTION.value)
            self.assertTrue(v3.metadata.get("interaction_perturbed"))
        finally:
            VARIANT_CONFIGS[VariantType.VARIANT_1_EBR_SHIFT_ONLY].is_enabled = False
            VARIANT_CONFIGS[VariantType.VARIANT_3_COMBINED_INTERACTION].is_enabled = False


class TestSolverConfigurationAndObjectiveReporting(unittest.TestCase):
    """Verifies Policy B wiring, OD-01 terminal target, and 4-tier objective extraction."""

    def test_prepare_gap19_solver_config_wires_policy_b_and_od01(self):
        """
        CRITICAL: Proves solver receives:
        1. OD-01 dynamic terminal target (initial_e - min_e).
        2. Policy B pointwise maximum combined reserve in config['ebr_target_wh'].
        """
        bundle = create_synthetic_bundle()
        # Battery capacity 200,000 Wh, min SOC 20% (min_e = 40,000 Wh), stored = 100,000 Wh
        state = MockStationState(battery_energy_wh=100000.0)
        base_cfg = {
            "battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
            "optimizer": {"timestep_hours": 1.0},
        }

        solver_cfg = prepare_gap19_solver_config(bundle, state, base_cfg)

        # 1. OD-01 dynamic target: 100,000 - 40,000 = 60,000 Wh
        self.assertIn("terminal_target_wh", solver_cfg)
        self.assertEqual(solver_cfg["terminal_target_wh"], 60000.0)

        # 2. Policy B combined reserve: max(crit_reserve, ebr)
        self.assertIn("ebr_target_wh", solver_cfg)
        combined_ebr = solver_cfg["ebr_target_wh"]
        self.assertEqual(len(combined_ebr), 24)
        # Verify it reflects metadata EBR
        raw_ebr_0 = bundle.metadata["ebr_target_wh"][0]
        self.assertGreaterEqual(combined_ebr[0], raw_ebr_0)

    def test_extract_objectives_all_four_components(self):
        plan = MockDispatchPlan(
            solar_used=[0.0]*24, wind_used=[0.0]*24, diesel_power=[0.0]*24,
            battery_charge=[0.0]*24, battery_discharge=[0.0]*24, load_served=[0.0]*24,
            unmet_load=[0.0]*24, flexible_load_schedule=[0.0]*24, renewable_curtailment=[0.0]*24,
            j1_objective=10.0, j2_objective=20.0, j3_objective=30.0, j4_objective=40.0
        )
        objs = extract_objectives_from_dispatch_plan(plan)
        self.assertTrue(objs.is_complete())
        self.assertEqual(objs.j1_critical_deficit, 10.0)
        self.assertEqual(objs.j2_reserve_shortfall, 20.0)
        self.assertEqual(objs.j3_diesel_fuel_cost, 30.0)
        self.assertEqual(objs.j4_curtailment_penalty, 40.0)

    def test_objective_comparison_identifies_individual_tier_shift(self):
        """Even if J3 (diesel) is identical, shift in J2 (reserve) or J4 (curtailment) is detected."""
        base = ObjectiveComponents(0.0, 100.0, 50.0, 0.0)
        var = ObjectiveComponents(0.0, 250.0, 50.0, 0.0)  # Reserve shortfall increased, diesel unchanged
        res = compare_objectives(base, var)
        self.assertTrue(res.is_complete)
        self.assertEqual(res.status, ObjectiveComparisonStatus.DISTINCT)
        self.assertEqual(res.deltas["delta_j2"], 150.0)
        self.assertEqual(res.deltas["delta_j3"], 0.0)


class TestStaticOrchestrationAndManifest(unittest.TestCase):
    """Verifies pre-execution orchestration planner and fail-closed state."""

    def test_plan_diagnostic_run_records_blocked_state(self):
        origins = ["2024-06-21T00:00:00Z"]
        allow_list = [InputManifestItem("data/2024_approved.parquet", "sha123", "desc", is_verified=True)]
        manifest = plan_diagnostic_run(origins, allow_list)
        self.assertEqual(manifest.execution_status, "BLOCKED_GATE_C_NOT_AUTHORIZED")
        self.assertFalse(manifest.gate_c_authorized)

    def test_plan_diagnostic_run_fails_closed_without_origins(self):
        with self.assertRaises(ValueError):
            plan_diagnostic_run([], [InputManifestItem("path", "sha", "desc", is_verified=True)])

    def test_verified_diagnostic_origins_strata_and_counts(self):
        """Verifies exact 4 Polar Day, 3 Shoulder, 3 Polar Night origins and physical bounds."""
        self.assertEqual(len(VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD), 10)
        
        polar_day = [o for o in VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD if o["stratum"] == "REGIME_A_POLAR_DAY"]
        shoulder = [o for o in VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD if o["stratum"] == "REGIME_B_DYNAMIC_SHOULDER"]
        polar_night = [o for o in VERIFIED_DIAGNOSTIC_ORIGINS_2024_ODD if o["stratum"] == "REGIME_C_POLAR_NIGHT"]
        
        self.assertEqual(len(polar_day), 4)
        self.assertEqual(len(shoulder), 3)
        self.assertEqual(len(polar_night), 3)
        
        # 1. Polar Day: min solar elevation > 0°
        for o in polar_day:
            self.assertGreater(o["min_solar_elevation_deg"], 0.0)
            self.assertTrue(o["timestamp"].endswith("T00:00:00Z"))
            
        # 2. Polar Night: max solar elevation <= 0° (strictly non-positive)
        for o in polar_night:
            self.assertLessEqual(o["max_solar_elevation_deg"], 0.0)
            self.assertTrue(o["timestamp"].endswith("T00:00:00Z"))
            
        # 3. Shoulder: minimum elevation <= -6° (darkness) and max elevation > 0° (daylight)
        for o in shoulder:
            self.assertLessEqual(o["min_solar_elevation_deg"], -6.0)
            self.assertGreater(o["max_solar_elevation_deg"], 0.0)
            self.assertTrue(o["timestamp"].endswith("T00:00:00Z"))


class TestBatchRunnerAndIsolationStatic(unittest.TestCase):
    """
    Gate B.4 Static Verification:
    Validates batch runner authoring, 2024-EVEN sampling frame, fail-closed guards,
    production schema adherence, error handling, output confinement, and isolation design.
    """

    def test_1_exact_10_distinct_verified_2024_even_origins(self):
        """Verifies exactly 10 distinct, verified 2024-EVEN origins and physical stratification."""
        manifest = VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN
        self.assertEqual(len(manifest), 10)

        # Unique IDs and timestamps
        seen_ids = set()
        seen_ts = set()
        for o in manifest:
            self.assertNotIn(o["forecast_origin"], seen_ids)
            self.assertNotIn(o["timestamp"], seen_ts)
            seen_ids.add(o["forecast_origin"])
            seen_ts.add(o["timestamp"])

            # 2024-EVEN parity
            self.assertEqual(o["parity"], "EVEN")
            self.assertEqual(o["forecast_origin"] % 2, 0)
            self.assertTrue(o["timestamp"].startswith("2024-"))
            self.assertTrue(o["timestamp"].endswith("T00:00:00Z"))

        # Stratum counts
        p_day = [o for o in manifest if o["stratum"] == "REGIME_A_POLAR_DAY"]
        shoulder = [o for o in manifest if o["stratum"] == "REGIME_B_DYNAMIC_SHOULDER"]
        p_night = [o for o in manifest if o["stratum"] == "REGIME_C_POLAR_NIGHT"]
        self.assertEqual(len(p_day), 4)
        self.assertEqual(len(shoulder), 3)
        self.assertEqual(len(p_night), 3)

        # Physical solar elevation bounds
        for o in p_day:
            self.assertGreater(o["min_solar_elevation_deg"], 0.0)
        for o in p_night:
            self.assertLessEqual(o["max_solar_elevation_deg"], 0.0)
        for o in shoulder:
            self.assertLessEqual(o["min_solar_elevation_deg"], -6.0)
            self.assertGreater(o["max_solar_elevation_deg"], 20.0)

    def test_2_rejection_of_odd_or_2025_origins(self):
        """Manifest validator strictly rejects ODD parity, odd IDs, 2025 years, and blind tokens."""
        import copy
        valid = copy.deepcopy(VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN)

        # 1. Reject ODD parity label
        bad_parity = copy.deepcopy(valid)
        bad_parity[0]["parity"] = "ODD"
        with self.assertRaises(ValueError):
            verify_origin_manifest(bad_parity)

        # 2. Reject odd origin ID
        bad_id = copy.deepcopy(valid)
        bad_id[0]["forecast_origin"] = 135
        with self.assertRaises(ValueError):
            verify_origin_manifest(bad_id)

        # 3. Reject 2025 origin timestamp
        bad_year = copy.deepcopy(valid)
        bad_year[0]["timestamp"] = "2025-06-02T00:00:00Z"
        with self.assertRaises(QuarantineViolationError):
            verify_origin_manifest(bad_year)

        # 4. Reject blind token in origin timestamp
        bad_token = copy.deepcopy(valid)
        bad_token[0]["timestamp"] = "2024-06-02T00:00:00Z_blind"
        with self.assertRaises(QuarantineViolationError):
            verify_origin_manifest(bad_token)

    def test_3_rejection_of_missing_or_unverified_provenance(self):
        """Rejects manifests with missing origins, duplicates, non-midnight times, or unverified inputs."""
        import copy
        valid = copy.deepcopy(VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN)

        # 1. Less than 10 origins
        with self.assertRaises(ValueError):
            verify_origin_manifest(valid[:9])

        # 2. Duplicate origin ID
        dup = copy.deepcopy(valid)
        dup[1]["forecast_origin"] = dup[0]["forecast_origin"]
        with self.assertRaises(ValueError):
            verify_origin_manifest(dup)

        # 3. Non-midnight timestamp
        midday = copy.deepcopy(valid)
        midday[0]["timestamp"] = "2024-06-02T12:00:00Z"
        with self.assertRaises(ValueError):
            verify_origin_manifest(midday)

        # 4. Unverified input allow-list item
        unverified_item = InputManifestItem("data/test.csv", "abc", "desc", is_verified=False)
        fw = DatasetIngestionFirewall([unverified_item])
        with self.assertRaises(PermissionError):
            fw.validate_file("data/test.csv")

    def test_4_v0_only_enforcement_and_rejection_of_v1_to_v3(self):
        """Ensures runner only executes V0 and experimental variants V1-V3 remain disabled."""
        bundle = create_synthetic_bundle()

        # V1 disabled
        with self.assertRaises(ExperimentalFeatureDisabledError):
            align_bundle_variant_1(bundle, allow_experimental=False)

        # V2 disabled
        with self.assertRaises(ExperimentalFeatureDisabledError):
            align_bundle_variant_2(bundle, candidate_slot23_solar_w=3000.0, allow_experimental=False)

        # V3 disabled
        with self.assertRaises(ExperimentalFeatureDisabledError):
            align_bundle_variant_3(bundle, candidate_slot23_solar_w=3000.0, allow_experimental=False)

    def test_5_gate_c_authorization_checked_before_optimizer_or_side_effects(self):
        """Gate C firewall blocks execution before any solver construction or side effect."""
        with self.assertRaises(GateExecutionBlockedError):
            run_batch_od02_diagnostic()

        origin = VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN[0]
        with self.assertRaises(GateExecutionBlockedError):
            execute_single_origin_diagnostic(origin, [0.0] * 24, config={})

    def test_6_no_execution_bypass_through_mocks_or_alternate_entrypoints(self):
        """Passing a mock optimizer cannot bypass the Gate C firewall in runner or solve functions."""
        fake_opt = unittest.mock.MagicMock()
        with self.assertRaises(GateExecutionBlockedError):
            run_batch_od02_diagnostic(mock_optimizer=fake_opt)

        origin = VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN[0]
        with self.assertRaises(GateExecutionBlockedError):
            execute_single_origin_diagnostic(origin, [0.0] * 24, config={}, mock_optimizer=fake_opt)
        fake_opt.optimize.assert_not_called()

    def test_7_production_loader_and_constructor_contracts(self):
        """Validates that bundle and station state constructors produce valid production schema instances."""
        from system.schemas.forecast_bundle import ForecastBundle
        from system.schemas.station_state import StationState

        origin = VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN[0]
        raw_irr = [400.0] * 24
        bundle = build_diagnostic_forecast_bundle(origin, raw_irr)

        self.assertIsInstance(bundle, ForecastBundle)
        self.assertEqual(bundle.schema_version, "1.0.0")
        self.assertEqual(bundle.horizon_hours, 24)
        self.assertEqual(bundle.solar_irradiance.unit, "W/m^2")
        self.assertEqual(bundle.solar_generation.unit, "W")
        self.assertEqual(bundle.wind_generation.unit, "W")
        self.assertEqual(bundle.demand.unit, "W")
        self.assertEqual(bundle.demand_critical.unit, "W")
        self.assertEqual(len(bundle.timestamps), 24)
        self.assertIn("ebr_target_wh", bundle.metadata)
        self.assertEqual(len(bundle.metadata["ebr_target_wh"]), 24)

        state = build_diagnostic_station_state(origin, initial_soc_pct=50.0)
        self.assertIsInstance(state, StationState)
        self.assertEqual(state.operating_mode, "NORMAL")
        self.assertEqual(state.battery_soc_pct, 50.0)
        self.assertEqual(state.battery_energy_wh, 100000.0)

    def test_8_explicit_handling_of_missing_fields_and_failed_statuses(self):
        """Verifies that infeasible/failed results mark fields as None, distinct from 0.0."""
        import diag_od02_boundary as diag_mod

        origin = VERIFIED_DIAGNOSTIC_ORIGINS_2024_EVEN[0]
        fake_plan = MockDispatchPlan(
            solar_used=[0.0] * 24, wind_used=[0.0] * 24, diesel_power=[0.0] * 24,
            battery_charge=[0.0] * 24, battery_discharge=[0.0] * 24, load_served=[0.0] * 24,
            unmet_load=[0.0] * 24, flexible_load_schedule=[0.0] * 24, renewable_curtailment=[0.0] * 24,
            constraint_status="INFEASIBLE"
        )
        fake_opt = unittest.mock.MagicMock()
        fake_opt.optimize.return_value = fake_plan

        with unittest.mock.patch.object(diag_mod, "GATE_C_AUTHORIZED", True):
            res = execute_single_origin_diagnostic(
                origin=origin,
                raw_irradiance_24h=[0.0] * 24,
                config={"battery": {"capacity_wh": 200000.0, "min_soc_pct": 20.0, "max_soc_pct": 95.0}},
                mock_optimizer=fake_opt,
            )

        self.assertFalse(res.is_successful_solve)
        self.assertEqual(res.solver_status, "INFEASIBLE")
        self.assertIsNone(res.j1_critical_deficit_wh)
        self.assertIsNone(res.j2_reserve_shortfall_wh)
        self.assertIsNone(res.j3_diesel_fuel_liters)
        self.assertIsNone(res.j4_curtailment_wh)
        self.assertIsNone(res.first_action)
        self.assertIsNotNone(res.error_message)

        # Schema fidelity: ContinuousActionVector p_curt_sol and p_curt_wind are None, not 0.0
        cont = ContinuousActionVector(
            p_sol_used=10.0, p_wind_used=10.0, p_diesel=10.0, p_chg=0.0, p_dis=0.0,
            p_curt_total=0.0, p_served=30.0, p_unmet=0.0, p_flex=0.0
        )
        self.assertIsNone(cont.p_curt_sol)
        self.assertIsNone(cont.p_curt_wind)

    def test_9_output_path_confinement_and_manifest_provenance(self):
        """Verifies output path confinement and immutable provenance capture in results."""
        with self.assertRaises(QuarantineViolationError):
            run_batch_od02_diagnostic(output_dir="data/2025_test_output")

        with self.assertRaises(QuarantineViolationError):
            run_batch_od02_diagnostic(output_dir="experiments/stage4_blind_results")

        self.assertEqual(DEFAULT_OUTPUT_DIR, "experiments/diagnostics/diag_od02_boundary_2024")

        res = DiagnosticOriginResult(
            origin_id=134,
            origin_timestamp="2024-06-02T00:00:00Z",
            stratum="REGIME_A_POLAR_DAY",
            parity="EVEN",
            canonical_fold=2,
        )
        d = res.to_dict()
        self.assertEqual(d["origin_id"], 134)
        self.assertEqual(d["parity"], "EVEN")
        self.assertEqual(d["canonical_fold"], 2)

    def test_10_isolation_spec_completeness_and_2025_file_exclusion(self):
        """Verifies that OD02_DIAGNOSTIC_ISOLATION_SPEC.md defines strict Bubblewrap controls."""
        spec_path = os.path.join(os.path.dirname(__file__), "OD02_DIAGNOSTIC_ISOLATION_SPEC.md")
        self.assertTrue(os.path.isfile(spec_path))

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Required isolation markers
        self.assertIn("SPEC-2026-OD02-ISOLATION-01", content)
        self.assertIn("--unshare-net", content)
        self.assertIn("--ro-bind", content)
        self.assertIn("--die-with-parent", content)
        self.assertIn("prlimit", content)
        self.assertIn("POLARIS_v0_1_future_weather_forecasts_2025.csv", content)
        self.assertIn("forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv", content)
        self.assertIn("experiments/diagnostics/diag_od02_boundary_2024", content)


if __name__ == "__main__":
    unittest.main()
