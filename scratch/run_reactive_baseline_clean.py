#!/usr/bin/env python3
"""
"Legacy Reactive" baseline: ReactiveHybridA2Optimizer (zero forecast access,
zero MILP, current-timestep-only rule-based dispatch), run through the exact
same clean base physics as Scenarios 1-4 (K_pv=51.0, strict 20-95% SOC floor/
ceiling, 0.92/0.92 round-trip efficiency) and over the EXACT SAME 8,328-hour
window as Scenarios 2/3/4 (2024-01-20 00:00 onward, matching the N6 feature
matrix's warm-up-trimmed origin range), for a true apples-to-apples first rung
on the dashboard progression.

Unlike GAP19, this controller only ever sees the CURRENT hour's actual
conditions (that's the whole point of "zero forecast access"), so it is
called once per hour with a single-timestep bundle built directly from real
actual_SW_IN -- no N6 ML forecast, no rolling 24h horizon needed.

Output: scratch/ui_dashboard_reactive_baseline.csv
"""
import pandas as pd
import numpy as np
import time

from system.optimization.implementations.reactive_hybrid_a2 import ReactiveHybridA2Optimizer
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState


def build_ts(values, unit="W"):
    return TimeseriesForecast(point=values, lower=values, upper=values, unit=unit)


def run_reactive_baseline():
    print("Loading real telemetry and the Scenario 2/3/4 hourly origin window...")
    df_mat = pd.read_parquet("scratch/hourly_rolling_candidate_matrix.parquet")
    df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)
    origins = sorted(df_mat["forecast_start"].drop_duplicates().tolist())  # same 8,328 hours as Scenarios 2/3/4

    truth_df = pd.read_csv("data/POLARIS_v0_1_clearsky_decomposition.csv")
    truth_df['TIMESTAMP'] = pd.to_datetime(truth_df['TIMESTAMP'], utc=True)
    truth_df = truth_df.set_index('TIMESTAMP')

    optimizer = ReactiveHybridA2Optimizer()

    BATT_CAPACITY_WH = 200_000.0
    BATT_MIN_WH = BATT_CAPACITY_WH * 0.20
    BATT_MAX_WH = BATT_CAPACITY_WH * 0.95
    K_PV_W_PER_WM2 = 300.0 * 0.20 * 0.85  # 51.0 W per (W/m^2)
    FUEL_COST_PER_L = 2.50

    config = {
        "battery": {
            "capacity_wh": BATT_CAPACITY_WH, "min_soc_pct": 20.0, "max_soc_pct": 95.0,
            "charge_efficiency": 0.92, "discharge_efficiency": 0.92,
            "max_charge_power_w": 50_000.0, "max_discharge_power_w": 50_000.0,
        },
        "diesel": {
            "min_power_w": 10_000.0, "max_power_w": 100_000.0,
            "base_fuel_consumption_l_per_h": 5.0, "marginal_fuel_consumption_l_per_wh": 0.00025,
        },
    }

    current_battery_wh = BATT_CAPACITY_WH * 0.50
    dashboard_data = []
    total_diesel_liters = 0.0
    diesel_run_hours = 0
    diesel_start_events = 0
    prev_diesel_w = 0.0

    print(f"Starting Reactive Baseline loop across {len(origins)} hours...")
    start_time = time.time()

    for i, orig_dt in enumerate(origins):
        actual_ghi = truth_df.loc[orig_dt, 'actual_SW_IN'] if orig_dt in truth_df.index else 0.0
        actual_solar_w = max(0.0, actual_ghi * K_PV_W_PER_WM2)

        # Same synthetic demand/wind formulas as Scenarios 1-4 (identical inputs, fair comparison)
        demand_w = 30_000.0 + 5_000.0 * np.sin(orig_dt.hour * np.pi / 12.0)
        wind_w = 15_000.0 + 10_000.0 * np.sin(0 * np.pi / 6.0)  # h=0 term for this hour, matches scenario scripts

        # ForecastBundle requires exactly 24 horizon values. Padded with the
        # repeated current-hour value (indices 1..23 are never read -- only
        # plan.*[0] is used below, matching the step-0-only RHC convention of
        # Scenarios 1-4). t=0's result depends only on station_state's real
        # battery_energy_wh, not on this padding, so this is harmless and does
        # NOT give the "zero forecast access" controller any real lookahead.
        timestamps_24 = [(orig_dt + pd.Timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in range(24)]
        bundle = ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=orig_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            horizon_hours=24,
            timestamps=timestamps_24,
            solar_irradiance=build_ts([actual_ghi] * 24, "W/m^2"),
            solar_generation=build_ts([actual_solar_w] * 24, "W"),
            wind_generation=build_ts([wind_w] * 24, "W"),
            demand=build_ts([demand_w] * 24, "W"),
            demand_critical=build_ts([15_000.0] * 24, "W"),
            metadata={"source": "reactive_baseline_zero_forecast"},
        )

        station_state = StationState(
            timestamp=timestamps_24[0],
            battery_soc_pct=(current_battery_wh / BATT_CAPACITY_WH) * 100.0,
            battery_energy_wh=current_battery_wh,
            diesel_running=(prev_diesel_w > 0),
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=actual_ghi,
            last_observed_demand=demand_w,
            last_observed_wind_generation=wind_w,
            operating_mode="NORMAL",
        )

        plan = optimizer.optimize(forecast_bundle=bundle, station_state=station_state, config=config)

        diesel_w = plan.diesel_power[0]
        current_battery_wh = (plan.battery_soc[0] / 100.0) * BATT_CAPACITY_WH
        current_battery_wh = max(BATT_MIN_WH, min(BATT_MAX_WH, current_battery_wh))

        fuel_l = 0.0
        if diesel_w > 0:
            diesel_run_hours += 1
            if prev_diesel_w <= 0.0:
                diesel_start_events += 1
            fuel_l = 5.0 + (diesel_w * 0.00025)
            total_diesel_liters += fuel_l
        prev_diesel_w = diesel_w

        dashboard_data.append({
            "timestamp": orig_dt.isoformat(),
            "actual_ghi": round(actual_ghi, 2),
            "battery_soc_pct": round((current_battery_wh / BATT_CAPACITY_WH) * 100.0, 2),
            "diesel_kw": round(diesel_w / 1000.0, 2),
            "diesel_fuel_cost": round(fuel_l * FUEL_COST_PER_L, 3),
            "renewable_curtailment_wh": plan.renewable_curtailment[0],
            "battery_charge_wh": plan.battery_charge[0],
            "battery_discharge_wh": plan.battery_discharge[0],
            "demand_w": round(demand_w, 2),
            "unmet_load_w": plan.unmet_load[0],
        })

        if i % 400 == 0:
            print(f"[{i:05d}/{len(origins)}] {orig_dt.strftime('%Y-%m-%d %H:%M')} | SOC: {(current_battery_wh/BATT_CAPACITY_WH)*100:5.1f}% | Diesel: {diesel_w/1000.0:5.1f} kW")

    ui_df = pd.DataFrame(dashboard_data)
    ui_df.to_csv("scratch/ui_dashboard_reactive_baseline.csv", index=False)

    print("=" * 60)
    print(f"SUCCESS! Reactive Baseline completed in {time.time() - start_time:.1f} seconds.")
    print(f"Total diesel consumed:        {total_diesel_liters:,.2f} L")
    print(f"Diesel run hours:             {diesel_run_hours:,} / {len(origins):,}")
    print(f"Diesel start/stop events:     {diesel_start_events:,}")
    print(f"Diesel fuel cost (@2.50/L):   {total_diesel_liters * FUEL_COST_PER_L:,.2f}")
    print("Data ready at: scratch/ui_dashboard_reactive_baseline.csv")
    print("=" * 60)


if __name__ == "__main__":
    run_reactive_baseline()
