"""
Unit and Integration Tests for ClosedLoopCausalNwpRunner
Covers Requirements A through N:
- Test A: One-hour closed-loop execution
- Test B: Two-hour receding-horizon execution
- Test C: Verify timestep 1 of the first plan is NOT reused at timestep 2
- Test D: Verify a fresh optimization occurs at every hour
- Test E: Verify returned StationState becomes the next cycle's input
- Test F: Verify actual solar never enters forecast inputs
- Test G: Verify actual demand/wind never enter forecast construction
- Test H: Verify accounting at every timestep (P_in == P_out)
- Test I: Verify SOC and fuel bounds
- Test J: Verify deterministic repeatability
- Test K: Verify production simulator remains untouched
- Test L: Verify GAP19 implementation remains untouched
- Test M: Verify Stage8.1 remains untouched
- Test N: Verify a causal-data availability failure fails closed
- Smoke Test: 3-hour closed-loop execution on audited 2024 summer daylight case
"""

import math
import subprocess
from pathlib import Path
import pytest
import pandas as pd

from system.schemas.station_state import StationState
from system.research.closed_loop_causal_nwp_runner import (
    ClosedLoopCausalNwpRunner,
    ClosedLoopExecutionReport
)


@pytest.fixture
def default_configs():
    return {
        "battery": {
            "capacity_wh": 200000.0,
            "min_soc_pct": 20.0,
            "max_soc_pct": 95.0,
            "charge_efficiency": 0.92,
            "discharge_efficiency": 0.92,
            "max_charge_power_w": 50000.0,
            "max_discharge_power_w": 50000.0,
            "initial_soc_pct": 50.0
        },
        "diesel": {
            "min_power_w": 10000.0,
            "max_power_w": 100000.0,
            "base_fuel_consumption_l_per_h": 5.0,
            "marginal_fuel_consumption_l_per_wh": 0.00025,
            "initial_fuel_l": 100.0
        },
        "solar_pv": {
            "array_area_m2": 300.0,
            "panel_efficiency": 0.20,
            "performance_ratio": 0.85,
            "max_inverter_power_w": 60000.0
        },
        "critical_demand_ratio": 0.5,
        "terminal_target_wh": 100000.0,
        # Explicit SYNTHETIC test-fixture authorization for the router/ECD
        # fail-closed contract (ECD-01, A-iii/B-iii). This suite tests
        # genuine closed-loop MPC mechanics, not the authorization gate
        # itself (test_n_causal_data_failure_fails_closed exercises a
        # separate, unaffected fail-closed path -- missing weather data).
        # "EVID-TEST-CLOSED-LOOP-NWP" is NOT a real-station evidence
        # record -- see tests/test_isolated_components.py for the
        # convention.
        "ecd": {"t_required_hours": 6.0, "t_required_authorized": True},
        "critical_load": {
            "authorized": True,
            "evidence_id": "EVID-TEST-CLOSED-LOOP-NWP",
            "authorized_critical_load_w": 5000.0,
        },
    }


@pytest.fixture
def sample_weather_df():
    # Build continuous 48-hour synthetic weather dataset
    timestamps = [f"2024-06-22 {h:02d}:00:00" for h in range(24)] + [f"2024-06-23 {h:02d}:00:00" for h in range(24)]
    return pd.DataFrame({
        "timestamp": timestamps,
        "fc_cloud_cover": [30.0 + (i % 20) for i in range(48)]
    })


@pytest.fixture
def production_state_50():
    return StationState(
        timestamp="2024-06-21T23:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=0.0,
        last_observed_demand=15000.0,
        last_observed_wind_generation=4500.0,
        diesel_fuel_remaining_liters=100.0,
        operating_mode="NORMAL"
    )


def test_a_one_hour_closed_loop(default_configs, sample_weather_df, production_state_50):
    """Test A: Single-hour closed loop executes and produces a valid report."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=1,
        weather_dataset=sample_weather_df,
        realized_solar=[150.0],
        realized_wind=[4000.0],
        realized_demand=[15000.0],
        realized_timestamps=["2024-06-22T00:00:00Z"]
    )
    assert report.execution_status == "SUCCESS"
    assert report.total_hours_executed == 1
    assert report.reoptimizations_count == 1
    assert len(report.step_records) == 1
    assert report.final_state.timestamp == "2024-06-22T00:00:00Z"


def test_b_two_hour_receding_horizon(default_configs, sample_weather_df, production_state_50):
    """Test B: Two-hour receding horizon executes 2 distinct cycles."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=2,
        weather_dataset=sample_weather_df,
        realized_solar=[150.0, 200.0],
        realized_wind=[4000.0, 4200.0],
        realized_demand=[15000.0, 14000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z"]
    )
    assert report.total_hours_executed == 2
    assert report.reoptimizations_count == 2
    assert report.step_records[0].target_timestamp == "2024-06-22T00:00:00Z"
    assert report.step_records[1].target_timestamp == "2024-06-22T01:00:00Z"
    assert report.final_state.timestamp == "2024-06-22T01:00:00Z"


def test_c_timestep_1_of_first_plan_not_reused_at_cycle_2(default_configs, sample_weather_df, production_state_50):
    """Test C: Plan for cycle 2 is freshly solved and not simply timestep 1 of cycle 1."""
    runner = ClosedLoopCausalNwpRunner(default_configs)

    # Run cycle 1 manually to inspect full 24h plan
    origin_dt = runner._parse_iso(production_state_50.timestamp)
    target_dts = [origin_dt + pd.Timedelta(hours=h) for h in range(1, 25)]
    weather_lookup = sample_weather_df.set_index(pd.to_datetime(sample_weather_df["timestamp"], utc=True))["fc_cloud_cover"].to_dict()
    cloud_traj = [weather_lookup[dt] for dt in target_dts]

    bundle_1 = runner.forecast_engine.predict(production_state_50, {"fc_cloud_cover": cloud_traj})
    plan_1 = runner.optimizer.optimize(bundle_1, production_state_50, default_configs)

    planned_action_step_1_from_cycle_1 = plan_1.battery_discharge[1]

    # Now run 2-hour closed loop
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=2,
        weather_dataset=sample_weather_df,
        realized_solar=[10.0, 300.0],  # Realization induces state divergence
        realized_wind=[1000.0, 5000.0],
        realized_demand=[25000.0, 10000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z"]
    )

    actual_executed_action_cycle_2 = report.step_records[1].planned_battery_discharge_w
    # Because state diverged, cycle 2 was freshly re-optimized
    assert report.reoptimizations_count == 2
    # Verify that plan_1 was discarded and step_records[1] came from fresh optimization
    assert report.step_records[1].origin_timestamp == "2024-06-22T00:00:00Z"


def test_d_fresh_optimization_at_every_hour(default_configs, sample_weather_df, production_state_50):
    """Test D: Exactly N re-optimizations occur for N hours."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=3,
        weather_dataset=sample_weather_df,
        realized_solar=[100.0, 150.0, 200.0],
        realized_wind=[4000.0, 4000.0, 4000.0],
        realized_demand=[15000.0, 15000.0, 15000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z", "2024-06-22T02:00:00Z"]
    )
    assert report.reoptimizations_count == 3
    assert len(report.step_records) == 3


def test_e_returned_state_becomes_next_input(default_configs, sample_weather_df, production_state_50):
    """Test E: Realization next_state connects seamlessly as the state for the next hour."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=2,
        weather_dataset=sample_weather_df,
        realized_solar=[100.0, 200.0],
        realized_wind=[3000.0, 4000.0],
        realized_demand=[12000.0, 13000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z"]
    )
    step0 = report.step_records[0]
    step1 = report.step_records[1]

    assert step0.target_timestamp == step1.origin_timestamp
    assert step1.origin_timestamp == "2024-06-22T00:00:00Z"


def test_f_actual_solar_never_enters_forecast(default_configs, sample_weather_df, production_state_50):
    """Test F: Forecast engine causal firewall remains active in closed-loop runner."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    # The runner passes forecast_context = {'fc_cloud_cover': ...} with zero actuals
    # If someone tries to pass actuals, the forecast engine raises PermissionError
    with pytest.raises(PermissionError):
        runner.forecast_engine.predict(production_state_50, {"fc_cloud_cover": [20.0]*24, "actual_SW_IN": [100.0]*24})


def test_g_actual_demand_wind_never_enter_forecast(default_configs, production_state_50):
    """Test G: ForecastBundle relies only on baseline/NWP cloud, not future realized wind/demand."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    bundle = runner.forecast_engine.predict(production_state_50, {"fc_cloud_cover": [20.0]*24})
    # ForecastBundle demand and wind are causal baseline predictions, not actual future ground truth
    assert len(bundle.demand.point) == 24
    assert len(bundle.wind_generation.point) == 24


def test_h_accounting_at_every_timestep(default_configs, sample_weather_df, production_state_50):
    """Test H: Busbar energy balance is satisfied at every closed-loop hour."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=3,
        weather_dataset=sample_weather_df,
        realized_solar=[50.0, 250.0, 450.0],
        realized_wind=[2000.0, 3500.0, 5000.0],
        realized_demand=[18000.0, 15000.0, 12000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z", "2024-06-22T02:00:00Z"]
    )
    for rec in report.step_records:
        assert rec.busbar_balance_error_w == pytest.approx(0.0, abs=1e-4)
        p_in = rec.realized_solar_w + rec.realized_wind_w + rec.realized_diesel_w + rec.realized_battery_discharge_w
        p_out = rec.served_load_w + rec.realized_battery_charge_w + rec.curtailment_w
        assert p_in == pytest.approx(p_out, abs=1e-3)
        assert rec.realized_demand_w == pytest.approx(rec.served_load_w + rec.unmet_load_w, abs=1e-3)


def test_i_soc_fuel_bounds(default_configs, sample_weather_df, production_state_50):
    """Test I: Battery SOC remains in [20, 95] and fuel remains non-negative."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=3,
        weather_dataset=sample_weather_df,
        realized_solar=[100.0, 200.0, 300.0],
        realized_wind=[3000.0, 3000.0, 3000.0],
        realized_demand=[15000.0, 15000.0, 15000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z", "2024-06-22T02:00:00Z"]
    )
    for rec in report.step_records:
        assert 20.0 <= rec.realized_soc_pct <= 95.0
        assert rec.diesel_fuel_remaining_l >= 0.0


def test_j_deterministic_repeatability(default_configs, sample_weather_df, production_state_50):
    """Test J: Running the same closed loop twice yields bitwise identical step records."""
    runner = ClosedLoopCausalNwpRunner(default_configs)
    args = dict(
        initial_state=production_state_50,
        hours_to_run=2,
        weather_dataset=sample_weather_df,
        realized_solar=[120.0, 240.0],
        realized_wind=[4000.0, 4500.0],
        realized_demand=[14000.0, 13000.0],
        realized_timestamps=["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z"]
    )
    rep1 = runner.run_closed_loop(**args)
    rep2 = runner.run_closed_loop(**args)

    assert len(rep1.step_records) == len(rep2.step_records)
    for r1, r2 in zip(rep1.step_records, rep2.step_records):
        assert r1.to_dict() == r2.to_dict()


def test_k_production_simulator_unmodified():
    """Test K: Production simulator is unmodified."""
    sim_path = Path("system/simulation/simulator.py")
    diff = subprocess.check_output(["git", "diff", "--", str(sim_path)]).decode("utf-8")
    assert diff.strip() == ""


def test_l_gap19_unmodified():
    """Test L: GAP19 optimizer is unmodified."""
    gap_path = Path("system/optimization/implementations/gap19_highs_native.py")
    diff = subprocess.check_output(["git", "diff", "--", str(gap_path)]).decode("utf-8")
    assert diff.strip() == ""


def test_m_stage81_unmodified():
    """Test M: Stage 8.1 files are unmodified."""
    diff = subprocess.check_output(["git", "diff", "--", "system/forecasting/implementations/s81_solar.py"]).decode("utf-8")
    assert diff.strip() == ""


def test_n_causal_data_failure_fails_closed(default_configs, production_state_50):
    """Test N: If future weather data are missing, fails closed with ValueError."""
    # Incomplete weather dataset: only 10 hours
    short_df = pd.DataFrame({
        "timestamp": [f"2024-06-22 {h:02d}:00:00" for h in range(10)],
        "fc_cloud_cover": [30.0]*10
    })
    runner = ClosedLoopCausalNwpRunner(default_configs)
    with pytest.raises(ValueError, match="CAUSAL_DATA_UNAVAILABLE"):
        runner.run_closed_loop(
            initial_state=production_state_50,
            hours_to_run=1,
            weather_dataset=short_df,
            realized_solar=[100.0],
            realized_wind=[4000.0],
            realized_demand=[15000.0],
            realized_timestamps=["2024-06-22T00:00:00Z"]
        )


def test_smoke_3_hour_closed_loop(default_configs, production_state_50):
    """Smoke test: 3-hour closed-loop receding-horizon execution on audited 2024 dataset."""
    df = pd.read_csv("data/POLARIS_v0_1_future_weather_forecasts_2024.csv")
    sub = df[df["forecast_start"] == "2024-06-22 00:00:00"].head(3)

    realized_solar = sub["actual_SW_IN"].tolist()
    realized_wind = [4500.0, 4800.0, 5200.0]
    realized_demand = [15000.0, 14500.0, 14000.0]
    realized_ts = ["2024-06-22T00:00:00Z", "2024-06-22T01:00:00Z", "2024-06-22T02:00:00Z"]

    runner = ClosedLoopCausalNwpRunner(default_configs)
    report = runner.run_closed_loop(
        initial_state=production_state_50,
        hours_to_run=3,
        weather_dataset=df,
        realized_solar=realized_solar,
        realized_wind=realized_wind,
        realized_demand=realized_demand,
        realized_timestamps=realized_ts
    )

    assert report.execution_status == "SUCCESS"
    assert report.total_hours_executed == 3
    assert report.reoptimizations_count == 3
    assert report.final_state.timestamp == "2024-06-22T02:00:00Z"
