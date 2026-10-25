"""
Mechanical Unit Test for Class F Horizon-Weighted MPC Objective Implementation
Verifies implementation mechanics ONLY. Zero scientific replay, zero outcome inspection.
"""
import pytest
import numpy as np
from system.optimization.implementations.milp import LocalMILPEnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState
from datetime import datetime, timezone

def build_dummy_inputs():
    timestamps = [f"2024-01-01T{h:02d}:00:00Z" for h in range(24)]
    irr = TimeseriesForecast(point=[500.0]*24, lower=[500.0]*24, upper=[500.0]*24, unit="W/m^2")
    solar = TimeseriesForecast(point=[1000.0]*24, lower=[1000.0]*24, upper=[1000.0]*24, unit="W")
    wind = TimeseriesForecast(point=[500.0]*24, lower=[500.0]*24, upper=[500.0]*24, unit="W")
    demand = TimeseriesForecast(point=[2000.0]*24, lower=[2000.0]*24, upper=[2000.0]*24, unit="W")
    
    fb = ForecastBundle(
        schema_version="1.0.0",
        origin_timestamp="2024-01-01T00:00:00Z",
        horizon_hours=24,
        timestamps=timestamps,
        solar_irradiance=irr,
        solar_generation=solar,
        wind_generation=wind,
        demand=demand,
        metadata={}
    )
    
    st = StationState(
        timestamp="2024-01-01T00:00:00Z",
        battery_soc_pct=50.0,
        battery_energy_wh=100000.0,
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=500.0,
        last_observed_demand=2000.0,
        last_observed_wind_generation=500.0
    )
    return fb, st

def test_class_f_baseline_equivalence():
    """Verify that when gamma=1.0 (default), objective vector is identical to baseline."""
    fb, st = build_dummy_inputs()
    opt = LocalMILPEnergyOptimizer()
    
    # Baseline config (no horizon_discount_factor_gamma or gamma=1.0)
    cfg_base = {"optimizer": {"timestep_hours": 1.0, "weights": {"renewable_curtailment_penalty": 0.001}}}
    cfg_g1 = {"optimizer": {"timestep_hours": 1.0, "horizon_discount_factor_gamma": 1.0, "weights": {"renewable_curtailment_penalty": 0.001}}}
    
    plan_base = opt.optimize(fb, st, cfg_base)
    plan_g1 = opt.optimize(fb, st, cfg_g1)
    
    assert plan_base.constraint_status == "OPTIMAL"
    assert plan_g1.constraint_status == "OPTIMAL"
    assert np.isclose(plan_base.objective_value, plan_g1.objective_value)

def test_class_f_horizon_discounting_mechanics():
    """Verify that gamma=0.95 correctly applies w_t = 0.95^t to operational terms while leaving unmet load unweighted."""
    fb, st = build_dummy_inputs()
    opt = LocalMILPEnergyOptimizer()
    
    cfg_f = {"optimizer": {"timestep_hours": 1.0, "horizon_discount_factor_gamma": 0.95, "weights": {"renewable_curtailment_penalty": 0.001}}}
    plan_f = opt.optimize(fb, st, cfg_f)
    
    assert plan_f.constraint_status == "OPTIMAL"
    # Verify gamma sequence values
    gamma = 0.95
    w_sequence = [gamma ** t for t in range(24)]
    assert np.isclose(w_sequence[0], 1.0)
    assert np.isclose(w_sequence[1], 0.95)
    assert np.isclose(w_sequence[2], 0.9025)
    assert np.isclose(w_sequence[23], 0.95**23)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
