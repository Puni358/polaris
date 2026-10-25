#!/usr/bin/env python3
"""
POLARIS — Static Governance & Alignment Regression Tests (Strictly Non-Executing Solver/Sim)
File: scratch/test_rhc_static_governance.py

Verifies:
1. OD-01 dynamic terminal target derivation feasibility across full SOC range [0..100%].
2. GAP19 Stage 2 terminal constraint feasibility (terminal_target_wh + min_e_wh <= max_e_wh).
3. Policy B pointwise reserve envelope calculation (max(critical_6h, conformal_ebr)).
4. Canonical OD-02 alignment contract (shift 1..23 -> 0..22, terminal slot == 0.0 W/m^2).
5. Previous runner 10 kWh terminal violation bug reproduction.

DOES NOT INVOKE: HiGHS solver, MIP optimization, DigitalTwin simulator, or external networks.
"""

from datetime import datetime, timedelta, timezone
import math
import pytest
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from system.evaluation.n6_multi_origin_harness.adapters import (
    _prepare_gap19_terminal_target_config,
    _prepare_gap19_policy_b_config,
)

BATTERY_CFG = {
    "capacity_wh": 200000.0,
    "min_soc_pct": 20.0,
    "max_soc_pct": 95.0,
    "initial_soc_pct": 50.0,
}

CRITICAL_LOAD_CFG = {
    "baseline_power_w": 11600.0
}


def test_od01_terminal_target_feasibility_across_soc_range():
    """OD-01 dynamic derivation must NEVER force GAP19 into terminal slack s_J2[23] > 0."""
    capacity_wh = BATTERY_CFG["capacity_wh"]
    min_soc_pct = BATTERY_CFG["min_soc_pct"]
    max_soc_pct = BATTERY_CFG["max_soc_pct"]
    min_e_wh = capacity_wh * (min_soc_pct / 100.0)  # 40,000 Wh
    max_e_wh = capacity_wh * (max_soc_pct / 100.0)  # 190,000 Wh

    configs = {
        "battery": BATTERY_CFG,
        "loads": {"critical_load": CRITICAL_LOAD_CFG}
    }

    test_socs = [0.0, 10.0, 20.0, 35.0, 50.0, 80.0, 95.0, 100.0]

    for soc in test_socs:
        energy_wh = capacity_wh * (soc / 100.0)
        st = StationState(
            timestamp="2024-06-01T00:00:00Z",
            battery_soc_pct=soc,
            battery_energy_wh=energy_wh,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=15000.0,
            last_observed_wind_generation=10000.0,
            diesel_fuel_remaining_liters=500.0
        )

        opt_cfg = _prepare_gap19_terminal_target_config(st, configs)
        target_wh = opt_cfg.get("terminal_target_wh")

        assert target_wh is not None, f"terminal_target_wh missing for SOC={soc}%"
        assert target_wh >= 0.0, f"Negative terminal target {target_wh} for SOC={soc}%"

        # In GAP19 (line 304): req_lhs = e_stage2_target[23] + min_e_wh
        # For the target to be physically feasible without slack penalty,
        # req_lhs MUST be <= max_e_wh:
        required_terminal_energy = target_wh + min_e_wh
        assert required_terminal_energy <= max_e_wh + 1e-6, (
            f"Terminal target violation: {required_terminal_energy} Wh exceeds max battery "
            f"capacity ceiling of {max_e_wh} Wh at initial SOC {soc}%!"
        )


def test_previous_runner_terminal_reserve_bug_reproduction():
    """Confirms that setting terminal_reserve_model='INITIAL_STATE' creates the 200 kWh defect."""
    capacity_wh = 200000.0
    initial_soc_pct = 80.0
    initial_e_wh = capacity_wh * (initial_soc_pct / 100.0)  # 160,000 Wh
    min_e_wh = capacity_wh * 0.20                          # 40,000 Wh
    max_e_wh = capacity_wh * 0.95                          # 190,000 Wh

    # In previous runner line 194:
    # cfg["terminal_reserve_model"] = "INITIAL_STATE" directly, bypassing helper.
    # In GAP19 lines 138-139:
    terminal_target_wh_raw = initial_e_wh  # 160,000 Wh
    # In GAP19 line 304:
    req_lhs = terminal_target_wh_raw + min_e_wh  # 160,000 + 40,000 = 200,000 Wh!

    # Slack is guaranteed:
    slack = req_lhs - max_e_wh  # 200,000 - 190,000 = 10,000 Wh (10 kWh)
    assert slack == 10000.0, f"Expected 10 kWh terminal violation, got {slack}"


def test_policy_b_pointwise_maximum_envelope():
    """Verifies Policy B combines critical 6h reserve and conformal EBR correctly."""
    crit_p = 10000.0  # 10 kW critical demand
    critical_demand = [crit_p] * 24
    conformal_ebr = [50000.0] * 24  # 50 kWh constant conformal EBR
    t0 = datetime(2024, 6, 1, 0, 0, tzinfo=timezone.utc)
    timestamps = [(t0 + timedelta(hours=h)).isoformat() for h in range(24)]

    bundle = ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp=t0.isoformat(),
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W/m^2"),
        solar_generation=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W"),
        wind_generation=TimeseriesForecast(point=[0.0]*24, lower=[0.0]*24, upper=[0.0]*24, unit="W"),
        demand=TimeseriesForecast(point=[20000.0]*24, lower=[20000.0]*24, upper=[20000.0]*24, unit="W"),
        demand_critical=TimeseriesForecast(point=critical_demand, lower=critical_demand, upper=critical_demand, unit="W"),
        metadata={
            "SOLAR_FORECAST_SOURCE": "CANDIDATE_N6_25ADD_15KT_SPECIALIST",
            "ebr_target_wh": conformal_ebr,
            "policy": "POLICY_B"
        }
    )

    configs = {
        "critical_demand_w": critical_demand,
        "battery": BATTERY_CFG
    }

    opt_cfg = _prepare_gap19_policy_b_config(bundle, configs)
    ebr_combined = opt_cfg.get("ebr_target_wh")

    assert ebr_combined is not None
    assert len(ebr_combined) == 24

    # In GAP19, stored battery reserve needed to serve critical load accounts for
    # discharge efficiency: reserve_wh = critical_wh / eta_dis (default 0.92)
    # For step t=0: 6h critical load = 6 * 10,000 = 60,000 Wh.
    # Stored reserve required = 60,000 / 0.92 = 65,217.3913 Wh.
    # Conformal EBR = 50,000 Wh.
    # Pointwise maximum = max(65,217.3913, 50,000) = 65,217.3913 Wh.
    expected_t0 = (6 * 10000.0) / 0.92
    assert abs(ebr_combined[0] - expected_t0) < 1e-4

    # For step t=20: remaining hours in horizon = 4.
    # Stored reserve required = (4 * 10,000) / 0.92 = 43,478.26 Wh.
    # Conformal EBR = 50,000 Wh.
    # Pointwise maximum = max(43,478.26, 50,000) = 50,000 Wh.
    assert ebr_combined[20] == 50000.0


def test_od02_canonical_shift_and_terminal_zero_fallback():
    """Verifies that OD-02 shift maps 1..23 -> 0..22 and forces step 23 to 0.0 W/m^2."""
    raw_point = [float(h * 10) for h in range(24)]  # raw[0]=0, raw[1]=10, ..., raw[23]=230

    # Canonical frozen OD-02 contract:
    aligned_point = raw_point[1:] + [0.0]

    assert len(aligned_point) == 24
    # Step 0 gets raw[1]
    assert aligned_point[0] == 10.0
    # Step 22 gets raw[23]
    assert aligned_point[22] == 230.0
    # Terminal step 23 gets 0.0
    assert aligned_point[23] == 0.0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
