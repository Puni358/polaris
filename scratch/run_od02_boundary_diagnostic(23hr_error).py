#!/usr/bin/env python3
"""
POLARIS — Read-Only Gate C Diagnostic: OFAT Sensitivity Solve (V0 vs V2)
Tracking ID: DIAG-GATEC-U0-SENSITIVITY-2026-10-20
File: scratch/run_od02_boundary_diagnostic.py
"""

import sys
import datetime
import numpy as np

try:
    from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
    from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
    from system.schemas.station_state import StationState
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

def build_timeseries(values, unit="W"):
    """Instantiate TimeseriesForecast with required probabilistic bounds."""
    return TimeseriesForecast(
        point=values,
        lower=values,
        upper=values,
        unit=unit
    )

def extract_u0(plan):
    """Safely extract Step 0 diesel (kW) and net battery discharge (kW)."""
    # The solver operates in Watts, so we divide by 1000 to get kW
    diesel_kw = plan.diesel_power[0] / 1000.0
    
    # Net battery action = discharge - charge
    batt_discharge = plan.battery_discharge[0] / 1000.0
    batt_charge = plan.battery_charge[0] / 1000.0
    batt_net_kw = batt_discharge - batt_charge
    
    return diesel_kw, batt_net_kw

def run_ofat_sensitivity():
    print("=" * 80)
    print("POLARIS — GATE C: OFAT SENSITIVITY SOLVE (V0 vs V2)")
    print("=" * 80)

    horizon = 24
    base_time = datetime.datetime(2024, 6, 21, 0, 0, 0, tzinfo=datetime.timezone.utc)
    timestamps = [(base_time + datetime.timedelta(hours=i)).isoformat() for i in range(horizon)]

    # 1. Base Profiles (Flat demand/wind, Polar Day solar)
    demand_kw = [500.0] * horizon
    demand_critical_kw = [100.0] * horizon
    wind_kw = [150.0] * horizon
    
    solar_v0_wm2 = list(np.linspace(800, 50, horizon))
    solar_v0_wm2[23] = 0.0  # V0: Step 23 is forced to 0.0 (Current OD-02)
    
    solar_v2_wm2 = list(solar_v0_wm2)
    solar_v2_wm2[23] = solar_v2_wm2[22]  # V2: Persist step 22

    # 2. Build Typed Station State
    state = StationState(
        timestamp=timestamps[0],
        battery_soc_pct=10.0,
        battery_energy_wh=100_000.0, 
        diesel_running=False,
        diesel_hours_running=0.0,
        last_observed_solar_irradiance=800.0,
        last_observed_demand=500.0,
        last_observed_wind_generation=150.0,
        operating_mode='NORMAL',
        ebr_target_wh_override=None,
        terminal_target_wh_override=250_000.0 
    )

    # 3. Build Typed Forecast Bundles
    def build_bundle(solar_vals):
        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=timestamps[0],
            horizon_hours=horizon,
            timestamps=timestamps,
            solar_irradiance=build_timeseries(solar_vals, "W/m^2"),
            solar_generation=build_timeseries([v * 0.2 * 1000 for v in solar_vals], "W"), 
            wind_generation=build_timeseries([v * 1000 for v in wind_kw], "W"),           
            demand=build_timeseries([v * 1000 for v in demand_kw], "W"),                  
            demand_critical=build_timeseries([v * 1000 for v in demand_critical_kw], "W"), 
            metadata={"diagnostic": "gate_c"}
        )

    bundle_v0 = build_bundle(solar_v0_wm2)
    bundle_v2 = build_bundle(solar_v2_wm2)
    config = {"solver": "highs", "verbosity": 0}

    # 4. Execute Solves
    print("\n[INFO] Instantiating GAP19HighsNativeOptimizer...")
    opt_v0 = GAP19HighsNativeOptimizer()
    opt_v2 = GAP19HighsNativeOptimizer()

    print("[EXEC] Solving Variant V0 (OD-02: Step 23 = 0.0 W/m2)...")
    res_v0 = opt_v0.optimize(forecast_bundle=bundle_v0, station_state=state, config=config)

    print("[EXEC] Solving Variant V2 (Candidate C.1: Step 23 = Step 22)...")
    res_v2 = opt_v2.optimize(forecast_bundle=bundle_v2, station_state=state, config=config)

    # 5. Extract and Compare u_0
    u0_v0_diesel, u0_v0_batt = extract_u0(res_v0)
    u0_v2_diesel, u0_v2_batt = extract_u0(res_v2)

    delta_diesel = u0_v2_diesel - u0_v0_diesel
    delta_batt   = u0_v2_batt - u0_v0_batt

    print("\n--- Gate C Diagnostic Results (u_0 Step 0 Action) ---")
    print(f"Variant V0 (0.0 W/m2) -> Diesel: {u0_v0_diesel:.2f} kW | Battery: {u0_v0_batt:.2f} kW")
    print(f"Variant V2 (Persist)  -> Diesel: {u0_v2_diesel:.2f} kW | Battery: {u0_v2_batt:.2f} kW")
    print("-" * 55)
    print(f"Delta (V2 - V0)       -> Diesel: {delta_diesel:.2f} kW | Battery: {delta_batt:.2f} kW")

    print("\n--- Conclusion ---")
    if abs(delta_diesel) < 1e-4 and abs(delta_batt) < 1e-4:
        print("[PASS] NULL HYPOTHESIS RATIFIED: Delta u_0 == 0")
        print("The terminal zero at Step 23 is mathematically invariant in Receding-Horizon Control.")
        print("MDR Pass 24 should freeze OD-02 permanently and reject Candidate C.")
    else:
        print("[FAIL] BOUNDARY ARTIFACT DETECTED: Delta u_0 != 0")
        print("The terminal zero at Step 23 distorts Step 0 physical dispatch.")
        print("MDR Pass 24 must adopt Option C and integrate the fallback estimator.")
        
    print("=" * 80)

if __name__ == "__main__":
    run_ofat_sensitivity()
