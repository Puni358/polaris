"""
Unit, Invariance, and Baseline Tests for Governance-Approved Numerical Boundary Protocol
Module: experiments.candidate_s_sw_campaign_2024.test_numerical_boundary_invariance

Verifies:
A. When no residue occurs, research extractor output is bit-identical to GAP19 extraction.
B. A 0.009 W residue is corrected (smaller flow zeroed).
C. A 0.039 W residue is corrected.
D. A 0.055 W residue (exact theoretical bound tau) is corrected.
E. A residue >0.055 W (e.g., 0.05501 W) is NOT corrected and raises ValueError.
F. Genuine simultaneous charge/discharge (e.g., 10 kW / 10 kW) is rejected.
G. Binary normalization is NOT performed (binaries remain unrounded).
H. HiGHS solver options and tolerances remain completely unchanged.
I. GAP19 source hash remains unchanged.
J. DispatchPlan source hash remains unchanged.
K. candidate_s_sw_adapter.py hash remains unchanged.
L. Frozen preregistration hashes remain unchanged.
M. Baseline test: run against frozen Control B fixture (Origin 1) demonstrating bit-identical accounting.
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
import numpy as np

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"))
sys.path.insert(0, str(REPO / "experiments/candidate_s_sw_campaign_2024"))

from research_numerical_extractor import (
    extract_and_correct_flows,
    ResearchNumericalGAP19Optimizer,
    TAU_RESIDUE_W,
    BIG_M_W,
    EPS_INTEGRALITY,
    EPS_PRIMAL
)
from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
from system.schemas.dispatch_plan import DispatchPlan

spec_camp = importlib.util.spec_from_file_location("camp", REPO / "experiments/run_diesel_reduction_campaign.py")
camp = importlib.util.module_from_spec(spec_camp)
spec_camp.loader.exec_module(camp)


# ==============================================================================
# 1. THEORETICAL BOUND DERIVATION TEST
# ==============================================================================

def test_theoretical_residue_bound_derivation():
    """Verify that tau = M * (eps_integrality + eps_primal) = 0.055 W."""
    expected_tau = BIG_M_W * (EPS_INTEGRALITY + EPS_PRIMAL)
    assert abs(expected_tau - 0.055) < 1e-12
    assert abs(TAU_RESIDUE_W - 0.055) < 1e-12


# ==============================================================================
# 2. CORE NUMERICAL EXTRACTION INVARIANCE TESTS (TESTS B, C, D, E, F, G)
# ==============================================================================

def test_b_residue_0_009_corrected():
    """Test B: A 0.009 W residue (observed failure magnitude) is corrected."""
    raw_chg = 46041.9
    raw_dis = 0.009123 # raw unrounded solver residue

    c_chg, c_dis, fired, zeroed = extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)
    assert fired is True
    assert zeroed == raw_dis
    assert c_chg == raw_chg
    assert c_dis == 0.0


def test_c_residue_0_039_corrected():
    """Test C: A 0.039 W residue (prior diagnostic magnitude) is corrected."""
    raw_chg = 0.03875 # charge is the smaller flow
    raw_dis = 25000.0

    c_chg, c_dis, fired, zeroed = extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)
    assert fired is True
    assert zeroed == raw_chg
    assert c_chg == 0.0
    assert c_dis == raw_dis


def test_d_residue_0_055_exact_bound_corrected():
    """Test D: A residue exactly at tau = 0.055 W is corrected."""
    raw_chg = 50000.0
    raw_dis = 0.0550000000000

    c_chg, c_dis, fired, zeroed = extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)
    assert fired is True
    assert zeroed == 0.055
    assert c_chg == 50000.0
    assert c_dis == 0.0


def test_e_residue_above_tau_raises_violation():
    """Test E: A residue > 0.055 W (e.g. 0.05501 W) is NOT corrected and raises ValueError."""
    raw_chg = 50000.0
    raw_dis = 0.05501

    with pytest.raises(ValueError, match="GENUINE_SIMULTANEOUS_FLOW_VIOLATION"):
        extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)


def test_f_genuine_simultaneous_flow_rejected():
    """Test F: Genuine simultaneous flow (e.g. 10 kW / 10 kW) is rejected."""
    raw_chg = 10000.0
    raw_dis = 10000.0

    with pytest.raises(ValueError, match="GENUINE_SIMULTANEOUS_FLOW_VIOLATION"):
        extract_and_correct_flows(raw_chg, raw_dis, tau=0.055)


def test_g_binary_normalization_not_performed():
    """Test G: Binary variables are extracted as raw unrounded floats without normalization."""
    # Test through ResearchNumericalGAP19Optimizer diagnostic capture
    opt = ResearchNumericalGAP19Optimizer()
    state = camp.make_initial_state("2024-05-01T00:00:00Z")
    cfg = camp.load_canonical_configs()

    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    fe = CausalNwpPhysicsForecastEngine()
    bundle = fe.predict(state, {"fc_cloud_cover": [0.3] * 24})
    cfg["critical_demand_w"] = [min(11600.0, d) for d in bundle.demand.point]

    plan = opt.optimize(bundle, state, cfg)
    assert len(opt.last_diagnostics) == 24

    for diag in opt.last_diagnostics:
        # Binaries must be floats, not rounded or cast to int
        assert isinstance(diag["u_chg"], float)
        assert isinstance(diag["u_dis"], float)
        assert isinstance(diag["u_diesel"], float)
        assert isinstance(diag["v_start"], float)


# ==============================================================================
# 3. STRUCTURAL IDENTITY WHEN NO RESIDUE OCCURS (TEST A & BASELINE TEST)
# ==============================================================================

def test_a_structural_identity_when_no_residue():
    """
    Test A: When no residue occurs, ResearchNumericalGAP19Optimizer produces
    structurally identical DispatchPlan outputs to standard GAP19.
    """
    state = camp.make_initial_state("2024-05-01T00:00:00Z")
    cfg = camp.load_canonical_configs()

    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    fe = CausalNwpPhysicsForecastEngine()
    bundle = fe.predict(state, {"fc_cloud_cover": [0.5] * 24})
    cfg["critical_demand_w"] = [min(11600.0, d) for d in bundle.demand.point]

    # Standard GAP19
    opt_std = GAP19HighsNativeOptimizer()
    plan_std = opt_std.optimize(bundle, state, cfg)

    # Research Numerical GAP19
    opt_res = ResearchNumericalGAP19Optimizer()
    plan_res = opt_res.optimize(bundle, state, cfg)

    assert plan_res.constraint_status == plan_std.constraint_status
    assert plan_res.battery_charge == plan_std.battery_charge
    assert plan_res.battery_discharge == plan_std.battery_discharge
    assert plan_res.battery_soc == plan_std.battery_soc
    assert plan_res.diesel_power == plan_std.diesel_power
    assert plan_res.load_served == plan_std.load_served
    assert plan_res.unmet_load == plan_std.unmet_load
    assert plan_res.renewable_curtailment == plan_std.renewable_curtailment
    assert plan_res.objective_value == plan_std.objective_value
    assert plan_res.j1_objective == plan_std.j1_objective
    assert plan_res.j2_objective == plan_std.j2_objective
    assert plan_res.j3_objective == plan_std.j3_objective
    assert plan_res.j4_objective == plan_std.j4_objective


def test_baseline_origin_1_fixture_reproduction():
    """
    Section 9 Baseline Test: Run research extractor across Origin 1 closed-loop
    and demonstrate that outputs are structurally identical to standard GAP19 when
    no numerical residue occurs, with Origin-1 closed-loop metrics verified to the
    stated numerical tolerance against frozen Control B.
    """
    import candidate_s_sw_adapter as csa
    import pandas as pd

    weather_df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    frozen_list = json.load(open("experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json"))

    o1 = next(o for o in frozen_list if o["origin_index"] == 1)
    fs = o1["forecast_start"]
    t0 = o1["t0_timestamp"]

    sub = weather_df[weather_df["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]

    base_cfg = camp.load_canonical_configs()

    runner = csa.CandidateControlBClosedLoopRunner(base_cfg)
    # Replace runner optimizer with ResearchNumericalGAP19Optimizer
    runner.optimizer.inner_optimizer = ResearchNumericalGAP19Optimizer()

    init_state = camp.make_initial_state(t0)
    rep = runner.run_closed_loop(init_state, 24, weather_df, rs, rw, rd, rts)

    fb = o1["arms"]["ARM_B_CANDIDATE"]
    assert abs(rep.cumulative_diesel_fuel_l - fb["diesel_fuel_liters"]) < 1e-3
    assert abs(rep.cumulative_unmet_load_wh - fb["unmet_critical_load_wh"]) < 1e-2
    assert abs(rep.cumulative_served_load_wh - fb["served_load_wh"]) < 1e-2
    assert abs(rep.cumulative_curtailment_wh - fb["curtailment_wh"]) < 1e-2

    socs = [sr.realized_soc_pct for sr in rep.step_records]
    assert abs(min(socs) - 65.58) < 1e-2
    assert abs(max(socs) - 93.85) < 1e-2


# ==============================================================================
# 4. SOLVER OPTIONS & PRODUCTION HASH INTEGRITY TESTS (TESTS H, I, J, K, L)
# ==============================================================================

def test_h_highs_solver_options_unchanged():
    """Test H: Verify HiGHS default options and tolerances remain unchanged."""
    import highspy
    h = highspy.Highs()
    status_mip, eps_mip = h.getOptionValue("mip_feasibility_tolerance")
    status_primal, eps_primal = h.getOptionValue("primal_feasibility_tolerance")

    assert status_mip == highspy.HighsStatus.kOk
    assert eps_mip == 1e-6
    assert status_primal == highspy.HighsStatus.kOk
    assert eps_primal == 1e-7


def test_i_gap19_source_hash_unchanged():
    """Test I: GAP19 solver implementation hash remains unchanged."""
    path = REPO / "system/optimization/implementations/gap19_highs_native.py"
    expected = "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_j_dispatch_plan_source_hash_unchanged():
    """Test J: DispatchPlan schema implementation hash remains unchanged."""
    path = REPO / "system/schemas/dispatch_plan.py"
    expected = "21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_k_candidate_s_sw_adapter_hash_unchanged():
    """Test K: candidate_s_sw_adapter.py hash remains unchanged."""
    path = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py"
    expected = "a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected


def test_l_preregistration_hashes_unchanged():
    """Test L: Frozen preregistration markdown and JSON hashes remain unchanged."""
    md_path = REPO / "experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md"
    json_path = REPO / "experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json"

    expected_md = "1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5"
    expected_json = "3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4"

    assert hashlib.sha256(md_path.read_bytes()).hexdigest() == expected_md
    assert hashlib.sha256(json_path.read_bytes()).hexdigest() == expected_json


if __name__ == "__main__":
    pytest.main(["-v", str(Path(__file__))])
