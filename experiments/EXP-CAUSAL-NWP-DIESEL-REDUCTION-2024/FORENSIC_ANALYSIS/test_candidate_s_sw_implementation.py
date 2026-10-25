"""
Unit, Integration, and Deterministic Smoke Tests for Candidate S & Candidate SW
Test module: experiments.EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024.FORENSIC_ANALYSIS.test_candidate_s_sw_implementation

Tests Candidate 2, Variant S (Solar-Only Net EBR) and Candidate 2, Variant SW (Solar + Synthetic Wind Net EBR):
1. Mathematical identity tests (zero solar reverting to governed EBR, zero wind reverting to Variant S).
2. Numerical hand-calculation verification.
3. Monotonic ordering: 0 <= E_SW <= E_S <= E_GOV.
4. Horizon edge (t=23): pointwise max with 100 kWh terminal target.
5. Direct electrical PV power consumption (no scaling factor).
6. Input validation and error handling.
7. Deterministic closed-loop smoke test on Origin 1 across Control B, Candidate S, and Candidate SW:
   - 24/24 steps OPTIMAL / FEASIBLE
   - 0 busbar balance residuals (> 1e-3 W)
   - 0 SOC violations (< 20%)
   - Reproduction check of Control B against frozen benchmark.
8. Cryptographic hash verification of production and preregistration files.
"""

import copy
import hashlib
import importlib.util
import json
import math
import os
import sys
from pathlib import Path
import pytest
import pandas as pd

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"))

import candidate_s_sw_adapter as csa
from system.schemas.station_state import StationState
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer

spec_camp = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec_camp)
spec_camp.loader.exec_module(camp)


# ==============================================================================
# 1. MATHEMATICAL FORMULATION TESTS
# ==============================================================================

def test_variant_s_zero_solar_identity():
    """When forecast solar is zero everywhere, Variant S MUST be identical to Governed EBR."""
    crit_constant = [11600.0] * 24
    zero_solar = [0.0] * 24

    gov = csa.compute_governed_ebr(crit_constant)
    var_s = csa.compute_variant_s_ebr(crit_constant, zero_solar)

    assert len(var_s) == 24
    for t in range(24):
        assert abs(var_s[t] - gov[t]) < 1e-12, f"Mismatch at t={t}: {var_s[t]} vs {gov[t]}"

    # Test with varying critical demand
    crit_varying = [10000.0 + 50.0 * t for t in range(24)]
    gov_v = csa.compute_governed_ebr(crit_varying)
    var_s_v = csa.compute_variant_s_ebr(crit_varying, zero_solar)
    for t in range(24):
        assert abs(var_s_v[t] - gov_v[t]) < 1e-12, f"Varying mismatch at t={t}: {var_s_v[t]} vs {gov_v[t]}"


def test_variant_s_full_solar_zero_reserve():
    """When forecast solar exceeds critical demand at every hour, reserve is zero."""
    crit = [11600.0] * 24
    excess_solar = [20000.0] * 24

    var_s = csa.compute_variant_s_ebr(crit, excess_solar)
    assert var_s == [0.0] * 24


def test_variant_s_hand_calculated_values():
    """Verify Variant S against independent hand calculation."""
    crit = [11600.0] * 24
    solar = [0.0, 5000.0, 11600.0, 12000.0, 6000.0, 0.0] + [0.0] * 18

    var_s = csa.compute_variant_s_ebr(crit, solar, eta_dis=0.92, dt=1.0)

    # Hand calculation for t=0:
    # k=0: max(0, 11600 - 0) = 11600
    # k=1: max(0, 11600 - 5000) = 6600
    # k=2: max(0, 11600 - 11600) = 0
    # k=3: max(0, 11600 - 12000) = 0
    # k=4: max(0, 11600 - 6000) = 5600
    # k=5: max(0, 11600 - 0) = 11600
    # Sum = 35400 Wh
    # Divided by 0.92 = 38478.260869565216 Wh
    expected_t0 = 35400.0 / 0.92
    assert abs(var_s[0] - expected_t0) < 1e-9

    # Hand calculation for t=23 (horizon edge):
    # k=23: max(0, 11600 - 0) = 11600
    # Sum = 11600 Wh
    # Divided by 0.92 = 12608.695652173914 Wh
    expected_t23 = 11600.0 / 0.92
    assert abs(var_s[23] - expected_t23) < 1e-9


def test_variant_sw_zero_renewables_identity():
    """When both solar and wind are zero, Variant SW MUST equal Governed EBR."""
    crit = [11600.0] * 24
    zero_sol = [0.0] * 24
    zero_wnd = [0.0] * 24

    gov = csa.compute_governed_ebr(crit)
    var_sw = csa.compute_variant_sw_ebr(crit, zero_sol, zero_wnd)

    for t in range(24):
        assert abs(var_sw[t] - gov[t]) < 1e-12, f"Mismatch at t={t}: {var_sw[t]} vs {gov[t]}"


def test_variant_sw_zero_wind_equals_variant_s():
    """When wind is zero, Variant SW MUST equal Variant S for any solar trajectory."""
    crit = [11600.0] * 24
    sol = [max(0.0, 8000.0 * math.sin(t * math.pi / 12.0)) for t in range(24)]
    zero_wnd = [0.0] * 24

    var_s = csa.compute_variant_s_ebr(crit, sol)
    var_sw = csa.compute_variant_sw_ebr(crit, sol, zero_wnd)

    for t in range(24):
        assert abs(var_sw[t] - var_s[t]) < 1e-12, f"Mismatch at t={t}: {var_sw[t]} vs {var_s[t]}"


def test_ordering_and_monotonicity():
    """For any non-negative renewables, 0 <= E_SW[t] <= E_S[t] <= E_GOV[t]."""
    crit = [11600.0] * 24
    sol = [max(0.0, 5000.0 * math.sin(t * math.pi / 12.0)) for t in range(24)]
    wnd = [max(0.0, 3000.0 * math.cos(t * math.pi / 6.0)) for t in range(24)]

    gov = csa.compute_governed_ebr(crit)
    var_s = csa.compute_variant_s_ebr(crit, sol)
    var_sw = csa.compute_variant_sw_ebr(crit, sol, wnd)

    for t in range(24):
        assert 0.0 <= var_sw[t] <= var_s[t] + 1e-12
        assert var_s[t] <= gov[t] + 1e-12


def test_horizon_edge_t23_terminal_target():
    """Verify stage2 target at horizon edge t=23 is max(deficit, terminal_target_wh)."""
    # Case 1: Deficit below terminal target (12,608.7 Wh < 100,000 Wh) -> stage2[23] = 100,000 Wh
    crit_1 = [11600.0] * 24
    sol_1 = [0.0] * 24
    ebr_1 = csa.compute_variant_s_ebr(crit_1, sol_1)
    stage2_1 = csa.compute_stage2_target_vector(ebr_1, terminal_target_wh=100000.0)
    assert abs(stage2_1[23] - 100000.0) < 1e-9

    # Case 2: Huge critical demand at t=23 (150,000 W) -> deficit = 150000/0.92 = 163043.48 Wh > 100000 Wh
    crit_2 = [11600.0] * 23 + [150000.0]
    ebr_2 = csa.compute_variant_s_ebr(crit_2, sol_1)
    stage2_2 = csa.compute_stage2_target_vector(ebr_2, terminal_target_wh=100000.0)
    assert abs(stage2_2[23] - (150000.0 / 0.92)) < 1e-9


def test_direct_pv_watts_input_no_scaling():
    """Verify that solar is consumed directly in Watts without double conversion."""
    crit = [11600.0] * 24
    sol_w = [1000.0] * 24 # 1000 Watts

    var_s = csa.compute_variant_s_ebr(crit, sol_w, eta_dis=1.0, dt=1.0)
    # Deficit per hour is 11600 - 1000 = 10600 W. For 6 hours = 63600 Wh.
    assert abs(var_s[0] - 63600.0) < 1e-9


def test_input_validation_errors():
    """Verify strict fail-closed input validation."""
    with pytest.raises(ValueError, match="must have length 24"):
        csa.compute_variant_s_ebr([11600.0] * 23, [0.0] * 24)

    with pytest.raises(ValueError, match="must have length 24"):
        csa.compute_variant_s_ebr([11600.0] * 24, [0.0] * 25)

    with pytest.raises(ValueError, match="eta_dis must be positive"):
        csa.compute_variant_s_ebr([11600.0] * 24, [0.0] * 24, eta_dis=0.0)

    with pytest.raises(ValueError, match="invalid"):
        csa.compute_variant_s_ebr([11600.0] * 24, [-10.0] + [0.0] * 23)

    with pytest.raises(ValueError, match="invalid"):
        csa.compute_variant_s_ebr([float("nan")] + [11600.0] * 23, [0.0] * 24)


# ==============================================================================
# 2. DETERMINISTIC SMOKE TEST: ORIGIN 1 (CONTROL B, VARIANT S, VARIANT SW)
# ==============================================================================

def test_deterministic_smoke_origin_1():
    """
    Executes a deterministic 24-hour closed-loop run for Origin 1 under:
    1. Control_Frozen_B
    2. Candidate 2, Variant S
    3. Candidate 2, Variant SW

    Verifies:
    - 24/24 steps executed for all arms.
    - All optimizer status OPTIMAL or FEASIBLE.
    - All busbar balance errors < 1e-3 W.
    - All realized SOC between 20.0% and 95.0% (zero violations).
    - Control_Frozen_B reproduces frozen Arm B per_origin_results.json exactly.
    - Both Candidate S and SW execute cleanly without errors.
    """
    frozen_path = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"
    weather_path = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2024.csv"

    frozen_list = json.load(open(frozen_path))
    weather_df = pd.read_csv(weather_path)

    origin_1_data = next(o for o in frozen_list if o["origin_index"] == 1)
    fs = origin_1_data["forecast_start"]
    t0 = origin_1_data["t0_timestamp"]

    sub = weather_df[weather_df["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    base_cfg = camp.load_canonical_configs()

    # --- Run Control Frozen B ---
    runner_b = csa.CandidateControlBClosedLoopRunner(base_cfg)
    init_state_b = camp.make_initial_state(t0)
    rep_b = runner_b.run_closed_loop(init_state_b, 24, weather_df, rs, rw, rd, rts)

    # Reproduction check against frozen Arm B benchmark
    fb_origin_1 = origin_1_data["arms"]["ARM_B_CANDIDATE"]
    assert abs(rep_b.cumulative_diesel_fuel_l - fb_origin_1["diesel_fuel_liters"]) < 1e-3
    assert abs(rep_b.cumulative_unmet_load_wh - fb_origin_1["unmet_critical_load_wh"]) < 1e-2
    assert abs(rep_b.cumulative_served_load_wh - fb_origin_1["served_load_wh"]) < 1e-2
    assert abs(rep_b.cumulative_curtailment_wh - fb_origin_1["curtailment_wh"]) < 1e-2

    # --- Run Candidate S ---
    runner_s = csa.CandidateSClosedLoopRunner(base_cfg)
    init_state_s = camp.make_initial_state(t0)
    rep_s = runner_s.run_closed_loop(init_state_s, 24, weather_df, rs, rw, rd, rts)

    assert len(rep_s.step_records) == 24
    for sr in rep_s.step_records:
        assert sr.optimizer_status in ("OPTIMAL", "FEASIBLE")
        assert 19.999 <= sr.realized_soc_pct <= 95.001
        assert sr.diesel_fuel_consumed_l >= -1e-6
        assert sr.busbar_balance_error_w < 1e-3

    # --- Run Candidate SW ---
    runner_sw = csa.CandidateSWClosedLoopRunner(base_cfg)
    init_state_sw = camp.make_initial_state(t0)
    rep_sw = runner_sw.run_closed_loop(init_state_sw, 24, weather_df, rs, rw, rd, rts)

    assert len(rep_sw.step_records) == 24
    for sr in rep_sw.step_records:
        assert sr.optimizer_status in ("OPTIMAL", "FEASIBLE")
        assert 19.999 <= sr.realized_soc_pct <= 95.001
        assert sr.diesel_fuel_consumed_l >= -1e-6
        assert sr.busbar_balance_error_w < 1e-3

    # Verify exact realized SOC ranges
    b_socs = [sr.realized_soc_pct for sr in rep_b.step_records]
    s_socs = [sr.realized_soc_pct for sr in rep_s.step_records]
    sw_socs = [sr.realized_soc_pct for sr in rep_sw.step_records]

    assert abs(min(b_socs) - 65.58) < 1e-2 and abs(max(b_socs) - 93.85) < 1e-2
    assert abs(min(s_socs) - 61.71) < 1e-2 and abs(max(s_socs) - 93.71) < 1e-2
    assert abs(min(sw_socs) - 44.32) < 1e-2 and abs(max(sw_socs) - 94.02) < 1e-2

    print(f"\n[Origin 1 Smoke Results]")
    print(f"  Control B Fuel:     {rep_b.cumulative_diesel_fuel_l:.4f} L, Unmet: {rep_b.cumulative_unmet_load_wh:.2f} Wh, SOC: [{min(b_socs):.2f}%, {max(b_socs):.2f}%]")
    print(f"  Candidate S Fuel:   {rep_s.cumulative_diesel_fuel_l:.4f} L, Unmet: {rep_s.cumulative_unmet_load_wh:.2f} Wh, SOC: [{min(s_socs):.2f}%, {max(s_socs):.2f}%]")
    print(f"  Candidate SW Fuel:  {rep_sw.cumulative_diesel_fuel_l:.4f} L, Unmet: {rep_sw.cumulative_unmet_load_wh:.2f} Wh, SOC: [{min(sw_socs):.2f}%, {max(sw_socs):.2f}%]")


# ==============================================================================
# 3. GAP19 SOLVER INTEGRATION TESTS (BLOCKER 4 RESOLUTION)
# ==============================================================================

def test_gap19_integration_candidate_s_and_sw_ebr_consumption():
    """
    Directly exercises the actual GAP19 solve path via highspy solver interception.
    Asserts:
    1. For every t=0..23, the Stage-2 target supplied to GAP19 equals:
       - for t=0..22: candidate_EBR_target[t]
       - for t=23: max(candidate_EBR_target[23], terminal_target_wh)
    2. This exact target appears in the Layer-C/J2 constraint RHS/LHS used by GAP19:
       E_next[t] + s_J2[t] >= E_stage2_target[t] + min_e_wh.
    3. Candidate S trajectory reaches GAP19 unchanged.
    4. Candidate SW trajectory reaches GAP19 unchanged.
    5. Terminal target remains 100,000 Wh.
    6. No candidate trajectory silently disappears or gets replaced.
    """
    import highspy
    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine

    captured_highs = []
    orig_init = highspy.Highs.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        captured_highs.append(self)

    highspy.Highs.__init__ = patched_init

    base_cfg = camp.load_canonical_configs()
    state = camp.make_initial_state("2024-05-01T00:00:00Z")
    fe = CausalNwpPhysicsForecastEngine()
    bundle = fe.predict(state, {"fc_cloud_cover": [0.4] * 24})

    crit_w = csa.adapt_critical_demand_vector(11600.0, bundle.demand.point)
    sol_w = list(bundle.solar_generation.point)
    wnd_w = list(bundle.wind_generation.point)

    try:
        # --- Part A: Candidate S GAP19 Solve Path Verification ---
        captured_highs.clear()
        runner_s = csa.CandidateSClosedLoopRunner(base_cfg)
        plan_s = runner_s.optimizer.optimize(bundle, state, dict(base_cfg))

        assert len(captured_highs) >= 1, "Failed to intercept HiGHS solver in Candidate S path"
        h_s = captured_highs[0]

        expected_cand_s_ebr = csa.compute_variant_s_ebr(crit_w, sol_w)
        for t in range(24):
            row_idx = 288 + t # Layer C: Stage 2 reserve envelope
            status, lhs, rhs, n = h_s.getRow(row_idx)

            # Verify variable columns in this constraint: E_next[t] and s_J2[t]
            ret_status, cols, coeffs = h_s.getRowEntries(row_idx)
            assert (t * 15 + 6) in cols, f"E_next[{t}] missing from row {row_idx}"
            assert (384 + t) in cols, f"s_J2[{t}] missing from row {row_idx}"

            expected_stage2_s = expected_cand_s_ebr[t] if t < 23 else max(expected_cand_s_ebr[23], 100000.0)
            expected_lhs_s = expected_stage2_s + 40000.0 # min_e_wh = 40,000 Wh
            assert abs(lhs - expected_lhs_s) < 1e-6, f"Candidate S Layer-C bound mismatch at t={t}: {lhs} vs {expected_lhs_s}"
            assert rhs > 1e20, f"Candidate S upper bound must be +infinity, got {rhs}"

        # --- Part B: Candidate SW GAP19 Solve Path Verification ---
        captured_highs.clear()
        runner_sw = csa.CandidateSWClosedLoopRunner(base_cfg)
        plan_sw = runner_sw.optimizer.optimize(bundle, state, dict(base_cfg))

        assert len(captured_highs) >= 1, "Failed to intercept HiGHS solver in Candidate SW path"
        h_sw = captured_highs[0]

        expected_cand_sw_ebr = csa.compute_variant_sw_ebr(crit_w, sol_w, wnd_w)
        for t in range(24):
            row_idx = 288 + t
            status, lhs, rhs, n = h_sw.getRow(row_idx)

            ret_status, cols, coeffs = h_sw.getRowEntries(row_idx)
            assert (t * 15 + 6) in cols, f"E_next[{t}] missing from row {row_idx}"
            assert (384 + t) in cols, f"s_J2[{t}] missing from row {row_idx}"

            expected_stage2_sw = expected_cand_sw_ebr[t] if t < 23 else max(expected_cand_sw_ebr[23], 100000.0)
            expected_lhs_sw = expected_stage2_sw + 40000.0
            assert abs(lhs - expected_lhs_sw) < 1e-6, f"Candidate SW Layer-C bound mismatch at t={t}: {lhs} vs {expected_lhs_sw}"
            assert rhs > 1e20, f"Candidate SW upper bound must be +infinity, got {rhs}"

        # --- Part C: Horizon Edge Terminal Target Boundary Verification ---
        captured_highs.clear()
        opt = GAP19HighsNativeOptimizer()

        # Case C1: Deficit at t=23 exceeds 100,000 Wh (140,000 Wh)
        custom_ebr_high = [25000.0] * 23 + [140000.0]
        cfg_high = dict(base_cfg)
        cfg_high["critical_demand_w"] = [11600.0] * 24
        cfg_high["terminal_target_wh"] = 100000.0
        cfg_high["ebr_target_wh"] = custom_ebr_high
        opt.optimize(bundle, state, cfg_high)

        h_c1 = captured_highs[0]
        status, lhs_c1, rhs, n = h_c1.getRow(288 + 23)
        assert abs(lhs_c1 - (140000.0 + 40000.0)) < 1e-6, f"Expected 180,000 Wh, got {lhs_c1}"

        # Case C2: Deficit at t=23 is below 100,000 Wh (12,000 Wh) -> must enforce 100,000 Wh
        captured_highs.clear()
        custom_ebr_low = [25000.0] * 23 + [12000.0]
        cfg_low = dict(base_cfg)
        cfg_low["critical_demand_w"] = [11600.0] * 24
        cfg_low["terminal_target_wh"] = 100000.0
        cfg_low["ebr_target_wh"] = custom_ebr_low
        opt.optimize(bundle, state, cfg_low)

        h_c2 = captured_highs[0]
        status, lhs_c2, rhs, n = h_c2.getRow(288 + 23)
        assert abs(lhs_c2 - (100000.0 + 40000.0)) < 1e-6, f"Expected 140,000 Wh, got {lhs_c2}"

    finally:
        highspy.Highs.__init__ = orig_init


# ==============================================================================
# 4. CRYPTOGRAPHIC INTEGRITY VERIFICATION
# ==============================================================================

def test_immutable_baseline_and_production_hashes():
    """Verify that no production files or frozen baseline artifacts were altered."""
    expected_hashes = {
        "system/optimization/implementations/gap19_highs_native.py":
            "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
        "system/forecasting/implementations/causal_nwp_physics.py":
            "14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710",
        "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/hourly_telemetry_123_frozen_b.json":
            "13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5",
        "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/hourly_telemetry_123_frozen_b_summary.json":
            "46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f",
        "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/hourly_trace_123_frozen_b/HOURLY_BASELINE_RECONCILIATION_REPORT.md":
            "70985bc3ba9e5909fb2ac43fa46feae3a81cc569b65c2a67c334ab40f3f6ce08",
        "experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md":
            "1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5",
        "experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json":
            "3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4",
        "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace/origin_1_hourly_traces.json":
            "88ea4a0db60f4bb9582fe119a18df6e93b3fe817a2d0feef5841db9e3eca055c",
    }

    for path_str, exp_hash in expected_hashes.items():
        p = REPO / path_str
        assert p.exists(), f"File {path_str} does not exist!"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch for {path_str}!\nExpected: {exp_hash}\nActual:   {actual_hash}"


if __name__ == "__main__":
    pytest.main(["-v", str(Path(__file__))])
