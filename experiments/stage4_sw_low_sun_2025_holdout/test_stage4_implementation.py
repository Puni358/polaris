"""
Unit and Integration Test Suite for Stage 4 SW Low-Sun Protection
Module: experiments.stage4_sw_low_sun_2025_holdout.test_stage4_implementation

Validates all 13 pre-execution requirements from EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md
and prompt section 8 before any 2025 candidate campaign execution.
"""

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import pytest

REPO = Path("/home/punith-bs/01polaris (Copy)")
OUT_DIR = REPO / "experiments/stage4_sw_low_sun_2025_holdout"

import sys
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/candidate_s_sw_campaign_2024"))
sys.path.insert(0, str(OUT_DIR))

import stage4_low_sun_adapter as s4a
from research_numerical_extractor import extract_and_correct_flows, TAU_RESIDUE_W
from system.forecasting.implementations.causal_nwp_physics import (
    CausalNwpPhysicsForecastEngine,
    check_causal_firewall
)


# ==============================================================================
# 1. THRESHOLD BEHAVIOR TEST
# ==============================================================================
def test_strict_threshold_behavior():
    """
    Test 1:
    e < 15.0 deg => L_k = 1 (protection active)
    e == 15.0 deg => L_k = 0 (protection inactive)
    e > 15.0 deg => L_k = 0 (protection inactive)
    """
    crit_w = [10000.0] * 24
    solar_w = [5000.0] * 24
    wind_w = [2000.0] * 24

    # Case A: exactly 15.000000 deg -> L_k = 0 everywhere
    el_15 = [15.0] * 24
    ebr_sl_15 = s4a.compute_variant_sl_ebr(crit_w, solar_w, el_15, threshold_deg=15.0)
    ebr_s = s4a.compute_variant_s_ebr(crit_w, solar_w)
    assert np.allclose(ebr_sl_15, ebr_s, atol=1e-12), "e == 15.0 must give protection inactive (L=0)"

    ebr_swl_15 = s4a.compute_variant_swl_ebr(crit_w, solar_w, wind_w, el_15, threshold_deg=15.0)
    ebr_sw = s4a.compute_variant_sw_ebr(crit_w, solar_w, wind_w)
    assert np.allclose(ebr_swl_15, ebr_sw, atol=1e-12), "e == 15.0 must give protection inactive (L=0)"

    # Case B: just below 15.0 deg (14.999999 deg) -> L_k = 1 everywhere
    el_below = [14.999999] * 24
    ebr_sl_below = s4a.compute_variant_sl_ebr(crit_w, solar_w, el_below, threshold_deg=15.0)
    ebr_b = s4a.compute_governed_ebr(crit_w)
    assert np.allclose(ebr_sl_below, ebr_b, atol=1e-12), "e < 15.0 must give protection active (L=1)"

    ebr_swl_below = s4a.compute_variant_swl_ebr(crit_w, solar_w, wind_w, el_below, threshold_deg=15.0)
    assert np.allclose(ebr_swl_below, ebr_b, atol=1e-12), "e < 15.0 must give protection active (L=1)"

    # Case C: above 15.0 deg (15.000001 deg) -> L_k = 0 everywhere
    el_above = [15.000001] * 24
    ebr_sl_above = s4a.compute_variant_sl_ebr(crit_w, solar_w, el_above, threshold_deg=15.0)
    assert np.allclose(ebr_sl_above, ebr_s, atol=1e-12), "e > 15.0 must give protection inactive (L=0)"


# ==============================================================================
# 2. S-L PROTECTION OFF REPRODUCES S
# ==============================================================================
def test_sl_protection_off_reproduces_s():
    """
    Test 2:
    S-L with protection OFF (or L_k = 0 everywhere) reproduces S exactly.
    """
    crit_w = [8000.0 + 100.0 * i for i in range(24)]
    solar_w = [max(0.0, 6000.0 * math.sin(i * math.pi / 24)) for i in range(24)]
    elevations = [float(i * 2.0) for i in range(24)]

    # Explicit protection_enabled=False
    ebr_sl_off = s4a.compute_variant_sl_ebr(
        crit_w, solar_w, elevations, threshold_deg=15.0, protection_enabled=False
    )
    ebr_s = s4a.compute_variant_s_ebr(crit_w, solar_w)
    assert np.allclose(ebr_sl_off, ebr_s, atol=1e-12), "S-L with protection OFF must equal S bit-identically"

    # All elevations >= 15.0
    el_high = [20.0 + i for i in range(24)]
    ebr_sl_high = s4a.compute_variant_sl_ebr(
        crit_w, solar_w, el_high, threshold_deg=15.0, protection_enabled=True
    )
    assert np.allclose(ebr_sl_high, ebr_s, atol=1e-12), "S-L with el >= 15.0 must equal S bit-identically"


# ==============================================================================
# 3. SW-L PROTECTION OFF REPRODUCES SW
# ==============================================================================
def test_swl_protection_off_reproduces_sw():
    """
    Test 3:
    SW-L with protection OFF (or L_k = 0 everywhere) reproduces SW exactly.
    """
    crit_w = [8000.0 + 100.0 * i for i in range(24)]
    solar_w = [max(0.0, 6000.0 * math.sin(i * math.pi / 24)) for i in range(24)]
    wind_w = [max(0.0, 3000.0 * math.cos(i * math.pi / 12)) for i in range(24)]
    elevations = [float(i * 2.0) for i in range(24)]

    # Explicit protection_enabled=False
    ebr_swl_off = s4a.compute_variant_swl_ebr(
        crit_w, solar_w, wind_w, elevations, threshold_deg=15.0, protection_enabled=False
    )
    ebr_sw = s4a.compute_variant_sw_ebr(crit_w, solar_w, wind_w)
    assert np.allclose(ebr_swl_off, ebr_sw, atol=1e-12), "SW-L with protection OFF must equal SW bit-identically"

    # All elevations >= 15.0
    el_high = [20.0 + i for i in range(24)]
    ebr_swl_high = s4a.compute_variant_swl_ebr(
        crit_w, solar_w, wind_w, el_high, threshold_deg=15.0, protection_enabled=True
    )
    assert np.allclose(ebr_swl_high, ebr_sw, atol=1e-12), "SW-L with el >= 15.0 must equal SW bit-identically"


# ==============================================================================
# 4. STRUCTURAL PROPERTIES AND MONOTONICITY
# ==============================================================================
def test_structural_properties_and_monotonicity():
    """
    Test 4:
    - If L_k = 1 everywhere => E_SL = E_SWL = E_B exactly.
    - Pointwise ordering: E_SW <= E_SWL <= E_B and E_S <= E_SL <= E_B.
    """
    np.random.seed(42)
    for _ in range(50):
        crit_w = list(np.random.uniform(2000.0, 11600.0, size=24))
        solar_w = list(np.random.uniform(0.0, 30000.0, size=24))
        wind_w = list(np.random.uniform(0.0, 10000.0, size=24))
        elevations = list(np.random.uniform(-10.0, 45.0, size=24))

        ebr_b = s4a.compute_governed_ebr(crit_w)
        ebr_s = s4a.compute_variant_s_ebr(crit_w, solar_w)
        ebr_sw = s4a.compute_variant_sw_ebr(crit_w, solar_w, wind_w)
        ebr_sl = s4a.compute_variant_sl_ebr(crit_w, solar_w, elevations, threshold_deg=15.0)
        ebr_swl = s4a.compute_variant_swl_ebr(crit_w, solar_w, wind_w, elevations, threshold_deg=15.0)

        # Monotonicity check
        for t in range(24):
            assert ebr_sw[t] <= ebr_swl[t] + 1e-9, f"E_SW <= E_SWL violated at t={t}: {ebr_sw[t]} > {ebr_swl[t]}"
            assert ebr_swl[t] <= ebr_b[t] + 1e-9, f"E_SWL <= E_B violated at t={t}: {ebr_swl[t]} > {ebr_b[t]}"
            assert ebr_s[t] <= ebr_sl[t] + 1e-9, f"E_S <= E_SL violated at t={t}: {ebr_s[t]} > {ebr_sl[t]}"
            assert ebr_sl[t] <= ebr_b[t] + 1e-9, f"E_SL <= E_B violated at t={t}: {ebr_sl[t]} > {ebr_b[t]}"

        # Check full protection (L=1 everywhere)
        el_low = list(np.random.uniform(-10.0, 14.9, size=24))
        ebr_sl_low = s4a.compute_variant_sl_ebr(crit_w, solar_w, el_low, threshold_deg=15.0)
        ebr_swl_low = s4a.compute_variant_swl_ebr(crit_w, solar_w, wind_w, el_low, threshold_deg=15.0)
        assert np.allclose(ebr_sl_low, ebr_b, atol=1e-12), "E_SL must equal E_B when L=1 everywhere"
        assert np.allclose(ebr_swl_low, ebr_b, atol=1e-12), "E_SWL must equal E_B when L=1 everywhere"


# ==============================================================================
# 5 & 6. CAUSAL FIREWALL AND LEAKAGE CONTROLS
# ==============================================================================
def test_causal_firewall_blocks_actual_sw_in():
    """
    Test 5 & 6:
    Verify that CausalNwpPhysicsForecastEngine fails closed if actual observations
    or ground truth are passed into the context.
    """
    forbidden_keys = [
        "actual_sw_in", "actual_solar", "actual_irradiance", "actual_ghi",
        "ground_truth", "future_actual", "future_state", "sites_actual"
    ]
    for key in forbidden_keys:
        bad_context = {key: [100.0] * 24}
        with pytest.raises(PermissionError):
            check_causal_firewall(bad_context)


# ==============================================================================
# 7 & 8. 2025 POPULATION & ORIGIN-HOURS COUNT
# ==============================================================================
def test_2025_population_and_hour_count():
    """
    Test 7 & 8:
    2025 holdout population must contain exactly 123 origins
    and 2,952 origin-hours from 2025-05-01 to 2025-08-31 inclusive.
    """
    weather_path = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
    assert weather_path.exists(), "2025 weather forecast file missing"

    df = pd.read_csv(weather_path)
    sub = df[(df["forecast_start"] >= "2025-05-01 00:00:00") & (df["forecast_start"] <= "2025-08-31 00:00:00")]

    unique_origins = sorted(sub["forecast_start"].unique())
    assert len(unique_origins) == 123, f"Expected exactly 123 origins, got {len(unique_origins)}"
    assert len(sub) == 2952, f"Expected exactly 2952 rows (123*24), got {len(sub)}"

    # Check each origin has exactly 24 horizons
    for orig in unique_origins:
        orig_rows = sub[sub["forecast_start"] == orig]
        assert len(orig_rows) == 24, f"Origin {orig} has {len(orig_rows)} rows, expected 24"


# ==============================================================================
# 9. INPUT COMPLETENESS (NO NANS)
# ==============================================================================
def test_2025_input_completeness():
    """
    Test 9:
    All required inputs must have 0 NaNs across the 2,952 window rows:
    - NWP 6 causal variables
    - SITES actual SW_IN
    - Solar elevation decomposition
    """
    weather_path = REPO / "data/POLARIS_v0_1_future_weather_forecasts_2025.csv"
    df = pd.read_csv(weather_path)
    sub = df[(df["forecast_start"] >= "2025-05-01 00:00:00") & (df["forecast_start"] <= "2025-08-31 00:00:00")]

    required_cols = [
        "actual_SW_IN", "fc_cloud_cover", "fc_temperature_2m",
        "fc_relative_humidity_2m", "fc_precipitation", "fc_surface_pressure", "fc_wind_speed_10m"
    ]
    for col in required_cols:
        assert col in sub.columns, f"Missing column {col} in 2025 weather dataset"
        nan_count = sub[col].isna().sum()
        assert nan_count == 0, f"Column {col} has {nan_count} NaNs in 2025 holdout window"

    cs_path = REPO / "data/POLARIS_v0_1_SITES_Nuolja_2025_clearsky_decomposition.csv"
    assert cs_path.exists(), "Clearsky decomposition file missing"
    cs_df = pd.read_csv(cs_path)
    assert len(cs_df) == 8760, f"Expected 8760 rows in clearsky decomposition, got {len(cs_df)}"
    assert cs_df["solar_elevation"].isna().sum() == 0, "Clearsky decomposition has NaNs in solar_elevation"


# ==============================================================================
# 10. PRODUCTION AND GOVERNANCE HASH INTEGRITY
# ==============================================================================
def test_startup_hash_guards():
    """
    Test 10:
    Verifies that all 15 startup hash guards specified in the preregistration match bit-for-bit.
    """
    prereg_json_path = REPO / "experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json"
    with open(prereg_json_path, "r") as f:
        prereg_json = json.load(f)

    guards = prereg_json["implementation_boundary"]["startup_hash_guards"]
    assert len(guards) >= 11, f"Expected at least 11 guards in prereg json, found {len(guards)}"

    for name, info in guards.items():
        rel_path = info["path"]
        expected_hash = info["sha256"]
        full_path = REPO / rel_path
        assert full_path.exists(), f"Guarded file {rel_path} does not exist"
        actual_hash = hashlib.sha256(full_path.read_bytes()).hexdigest()
        assert actual_hash == expected_hash, (
            f"GUARD_HASH_MISMATCH for {name} ({rel_path}): "
            f"expected {expected_hash}, got {actual_hash}"
        )


# ==============================================================================
# 11. NO CANDIDATE-BASED ORIGIN EXCLUSION
# ==============================================================================
def test_no_candidate_based_exclusion():
    """
    Test 11:
    Population is strictly determined by calendar rule (2025-05-01 to 2025-08-31).
    All 123 origins must be present without any exclusion based on route, solar, or performance.
    """
    weather_df = pd.read_csv(REPO / "data/POLARIS_v0_1_future_weather_forecasts_2025.csv")
    summer_starts = sorted(
        weather_df[
            (weather_df["forecast_start"] >= "2025-05-01 00:00:00") &
            (weather_df["forecast_start"] <= "2025-08-31 00:00:00")
        ]["forecast_start"].unique()
    )
    assert len(summer_starts) == 123
    assert summer_starts[0] == "2025-05-01 00:00:00"
    assert summer_starts[-1] == "2025-08-31 00:00:00"


# ==============================================================================
# 12. NUMERICAL BOUNDARY RESIDUE COMPLIANCE
# ==============================================================================
def test_numerical_boundary_residue_handling():
    """
    Test 12:
    Verifies that extract_and_correct_flows adheres strictly to tau = 0.055 W.
    - Residue <= tau is zeroed on the smaller flow.
    - Simultaneous flow > tau raises ValueError.
    """
    tau = TAU_RESIDUE_W  # 0.055 W

    # Case 1: Residue on charge
    c_chg, c_dis, fired, mag = extract_and_correct_flows(raw_chg=0.012, raw_dis=1500.0, tau=tau)
    assert fired is True
    assert c_chg == 0.0
    assert c_dis == 1500.0
    assert mag == 0.012

    # Case 2: Residue on discharge
    c_chg, c_dis, fired, mag = extract_and_correct_flows(raw_chg=2000.0, raw_dis=0.038, tau=tau)
    assert fired is True
    assert c_chg == 2000.0
    assert c_dis == 0.0
    assert mag == 0.038

    # Case 3: Genuine violation (> tau)
    with pytest.raises(ValueError, match="GENUINE_SIMULTANEOUS_FLOW_VIOLATION"):
        extract_and_correct_flows(raw_chg=0.060, raw_dis=100.0, tau=tau)

    # Case 4: Zero flows
    c_chg, c_dis, fired, mag = extract_and_correct_flows(raw_chg=0.0, raw_dis=500.0, tau=tau)
    assert fired is False
    assert c_chg == 0.0
    assert c_dis == 500.0
    assert mag == 0.0


# ==============================================================================
# 13. ACCOUNTING AND TERMINAL INVARIANTS
# ==============================================================================
def test_stage2_terminal_target_invariant():
    """
    Test 13:
    Stage 2 target vector preserves ebr[t] for t in {0..22} and enforces
    max(ebr[23], 100,000 Wh) at t=23.
    """
    ebr = [50000.0 + 1000.0 * i for i in range(24)]
    stage2 = s4a.compute_stage2_target_vector(ebr, terminal_target_wh=100000.0)

    assert len(stage2) == 24
    for t in range(23):
        assert stage2[t] == ebr[t]
    assert stage2[23] == 100000.0  # max(73000.0, 100000.0)

    # If ebr[23] > 100000.0
    ebr_high = [120000.0] * 24
    stage2_high = s4a.compute_stage2_target_vector(ebr_high, terminal_target_wh=100000.0)
    assert stage2_high[23] == 120000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
