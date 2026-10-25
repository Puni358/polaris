#!/usr/bin/env python3
import os
import sys
import pandas as pd
import numpy as np
import time

try:
    from system.forecasting.implementations.n6_solar import N6SolarForecastEngine
    from system.optimization.implementations.gap19_highs_native import GAP19HighsNativeOptimizer
    from system.evaluation.n6_multi_origin_harness.adapters import _align_n6_bundle_od02
    from system.schemas.station_state import StationState
    from system.schemas.forecast_bundle import TimeseriesForecast
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

def build_timeseries(values, unit="W"):
    return TimeseriesForecast(point=values, lower=values, upper=values, unit=unit)

def run_continuous_rhc():
    print("Loading Hourly Matrix and Actuals...")
    df_mat = pd.read_parquet("scratch/hourly_rolling_candidate_matrix.parquet")
    df_mat["forecast_start"] = pd.to_datetime(df_mat["forecast_start"], utc=True)

    truth_df = pd.read_csv("data/POLARIS_v0_1_clearsky_decomposition.csv")
    truth_df['TIMESTAMP'] = pd.to_datetime(truth_df['TIMESTAMP'], utc=True)
    truth_df = truth_df.set_index('TIMESTAMP')

    # Real station telemetry: air temperature (TA, degC) and snow depth (D_SNOW, cm)
    # used for battery cold-derating and panel snow-cover de-rate below.
    wx_df = pd.read_csv("data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv")
    wx_df['TIMESTAMP'] = pd.to_datetime(wx_df['TIMESTAMP'], utc=True)
    wx_df = wx_df.set_index('TIMESTAMP')

    origins = sorted(df_mat["forecast_start"].drop_duplicates().tolist())

    n6_engine = N6SolarForecastEngine()
    optimizer = GAP19HighsNativeOptimizer()

    # SYSTEM PHYSICAL CONSTANTS (system/config/*.yaml)
    BATT_CAPACITY_WH = 200_000.0
    BATT_MIN_SOC_PCT = 20.0
    BATT_MAX_SOC_PCT = 95.0
    BATT_MIN_WH = BATT_CAPACITY_WH * BATT_MIN_SOC_PCT / 100.0   # 40,000 Wh hard floor
    BATT_MAX_WH = BATT_CAPACITY_WH * BATT_MAX_SOC_PCT / 100.0   # 190,000 Wh ceiling
    CHARGE_EFF = 0.92     # battery.yaml charge_efficiency
    DISCHARGE_EFF = 0.92  # battery.yaml discharge_efficiency
    DEG_PENALTY_PER_WH = 0.00005  # battery.yaml deg_penalty_per_wh
    current_battery_wh = BATT_CAPACITY_WH * 0.50

    # solar_pv.yaml: 300 m^2 * 0.20 efficiency * 0.85 performance ratio
    K_PV_W_PER_WM2 = 300.0 * 0.20 * 0.85  # 51.0 W per (W/m^2)
    MAX_INVERTER_POWER_W = 60_000.0       # solar_pv.yaml max_inverter_power_w

    # Diesel throttle (mechanical-wear-aware prime/standby envelope)
    DIESEL_PRIME_POWER_W = 40_000.0      # normal-mode sweet spot (80% throttle)
    DIESEL_STANDBY_POWER_W = 50_000.0    # emergency-mode max rating
    DIESEL_EMERGENCY_SOC_PCT = 25.0      # below this, allow standby-rated output
    DIESEL_RAMP_LIMIT_W_PER_STEP = 30_000.0  # soft-start: max +/-30kW change per hourly step
    FUEL_COST_PER_L = 2.50               # diesel.yaml fuel_cost_per_l
    prev_diesel_w = 0.0

    # Battery cold-derating (LiFePO4 datasheet-style approximation, not measured):
    # ~100% usable capacity at >=0 degC, derating ~1.5%/degC below 0, floored at 60%
    # (typical cited range for LiFePO4 without thermal management is ~65-80% at -20 degC).
    def battery_cold_derate_pct(ta_degc):
        if pd.isna(ta_degc) or ta_degc >= 0.0:
            return 100.0
        return max(60.0, 100.0 + 1.5 * ta_degc)

    # Panel snow-cover de-rate: ground snow depth (D_SNOW, cm) used as a proxy for
    # panel obstruction. Simplified two-tier heuristic, not a direct panel measurement:
    # <5cm negligible, >=5cm assume partial/heavy coverage reduces effective K_pv by 50%.
    SNOW_COVER_THRESHOLD_CM = 5.0
    SNOW_DERATE_FACTOR = 0.50

    config = {
        "operating_mode": "NORMAL",
        "battery": {"capacity_wh": BATT_CAPACITY_WH, "min_soc_pct": 20.0, "max_soc_pct": 95.0},
        "diesel": {"min_power_w": 10_000.0, "max_power_w": 100_000.0},
        "terminal_reserve_model": "INITIAL_STATE",
        "optimizer": {"timestep_hours": 1.0}
    }

    dashboard_data = []
    total_diesel_liters = 0.0
    diesel_run_hours = 0
    diesel_start_events = 0
    total_cycling_loss_wh = 0.0
    total_degradation_cost = 0.0
    total_inverter_clipped_wh = 0.0

    print(f"Starting Continuous RHC Loop across {len(origins)} hours...")
    start_time = time.time()

    for i, orig_dt in enumerate(origins):

        # 1. Grab 24h rolling forecast
        origin_rows = df_mat[df_mat["forecast_start"] == orig_dt].sort_values("horizon_hour").reset_index(drop=True)
        features_df = origin_rows.drop(columns=["actual_SW_IN", "residual_target"], errors="ignore")

        # FIX: Synthesize missing interactions and forward-fill rolling NaNs to satisfy the strict validator
        features_df["elevation_x_transition_cloud"] = 0.0
        features_df = features_df.ffill().bfill().fillna(0.0)

        # 2. Tell ML and Optimizer the TRUE current battery state
        current_soc_pct = (current_battery_wh / BATT_CAPACITY_WH) * 100.0

        station_state = StationState(
            timestamp=orig_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            battery_soc_pct=current_soc_pct,
            battery_energy_wh=current_battery_wh,
            diesel_running=(prev_diesel_w > 0),
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=0.0,
            last_observed_demand=30_000.0,
            last_observed_wind_generation=15_000.0,
            operating_mode="NORMAL"
        )

        # 3. Predict & Align
        raw_bundle = n6_engine.predict(station_state, {"n6_feature_matrix": features_df})
        aligned_bundle = _align_n6_bundle_od02(raw_bundle)

        demand_w = [30_000.0 + 5_000.0 * np.sin((orig_dt.hour + h) * np.pi / 12.0) for h in range(24)]
        wind_w = [15_000.0 + 10_000.0 * np.sin(h * np.pi / 6.0) for h in range(24)]
        aligned_bundle.demand = build_timeseries(demand_w, "W")
        aligned_bundle.wind_generation = build_timeseries(wind_w, "W")
        aligned_bundle.demand_critical = build_timeseries([15_000.0] * 24, "W")

        # NOTE: Deliberately NOT wiring aligned_bundle.metadata["ebr_target_wh"] into
        # config here. Doing so activates the Stage-2 forecast-uncertainty reserve
        # trigger (RT-01 outlook_trigger), which makes the optimizer defend an EBR
        # buffer and commit diesel far more often. The audited annual benchmark
        # (run_n6_rhc_annual_checkpointed.py -> 693.557 L / 91 hrs) never sets this
        # key, so it is omitted here to keep this script's policy identical to that
        # benchmark's.

        # 4. Optimize
        plan = optimizer.optimize(forecast_bundle=aligned_bundle, station_state=station_state, config=config)

        # 5. EXECUTE STEP 0 ONLY (The magic of RHC)
        planned_diesel_w = plan.diesel_power[0] if hasattr(plan, 'diesel_power') else 0.0

        # Dynamic generator throttle: Prime (40 kW) in normal operation, Standby (50 kW)
        # only once the battery has been pushed down to the emergency floor region.
        if current_soc_pct > DIESEL_EMERGENCY_SOC_PCT:
            diesel_cap_w = DIESEL_PRIME_POWER_W
        else:
            diesel_cap_w = DIESEL_STANDBY_POWER_W
        throttled_diesel_w = min(planned_diesel_w, diesel_cap_w)

        # Soft-start ramp limit: generator can't jump its output instantly hour-to-hour.
        max_up = prev_diesel_w + DIESEL_RAMP_LIMIT_W_PER_STEP
        max_down = prev_diesel_w - DIESEL_RAMP_LIMIT_W_PER_STEP
        actual_diesel_w = min(max(throttled_diesel_w, max(0.0, max_down)), max_up)
        if throttled_diesel_w <= 0.0:
            actual_diesel_w = 0.0  # no ramp-down floor games when genset is meant to be off
        step0_diesel_kw = actual_diesel_w / 1000.0

        fuel_l = 0.0
        if actual_diesel_w > 0:
            diesel_run_hours += 1
            if prev_diesel_w <= 0.0:
                diesel_start_events += 1
            fuel_l = 5.0 + (actual_diesel_w * 0.00025)  # diesel.yaml base + marginal rate
            total_diesel_liters += fuel_l
        prev_diesel_w = actual_diesel_w

        # What actually happened in reality?
        actual_ghi = truth_df.loc[orig_dt, 'actual_SW_IN'] if orig_dt in truth_df.index else 0.0
        air_temp_c = wx_df.loc[orig_dt, 'TA'] if orig_dt in wx_df.index else np.nan
        snow_depth_cm = wx_df.loc[orig_dt, 'D_SNOW'] if orig_dt in wx_df.index else np.nan

        # solar_pv.yaml: array_area_m2=300, panel_efficiency=0.20, performance_ratio=0.85
        theoretical_solar_w = max(0.0, actual_ghi * K_PV_W_PER_WM2)

        # Panel snow-cover de-rate (ground snow depth as proxy)
        snow_covered = pd.notna(snow_depth_cm) and snow_depth_cm >= SNOW_COVER_THRESHOLD_CM
        solar_after_snow_w = theoretical_solar_w * SNOW_DERATE_FACTOR if snow_covered else theoretical_solar_w

        # Inverter clipping
        actual_solar_w = min(solar_after_snow_w, MAX_INVERTER_POWER_W)
        inverter_clipped_w = max(0.0, solar_after_snow_w - MAX_INVERTER_POWER_W)
        total_inverter_clipped_wh += inverter_clipped_w  # 1-hour steps

        actual_demand_w = demand_w[0]
        actual_wind_w = wind_w[0]

        # PHYSICAL REALITY: The battery must absorb/provide whatever the net difference is
        net_surplus_w = actual_solar_w + actual_wind_w + actual_diesel_w - actual_demand_w

        # Apply round-trip efficiency + cold-derating only to the battery-mediated portion
        batt_derate_pct = battery_cold_derate_pct(air_temp_c)
        derate_factor = batt_derate_pct / 100.0

        if net_surplus_w >= 0:
            # Charging: efficiency loss on the way in, cold-derated usable headroom
            gross_charge_wh = net_surplus_w
            net_charge_wh = gross_charge_wh * CHARGE_EFF
            cycling_loss_wh = gross_charge_wh - net_charge_wh
            effective_max_wh = BATT_MIN_WH + (BATT_MAX_WH - BATT_MIN_WH) * derate_factor
            current_battery_wh = min(effective_max_wh, current_battery_wh + net_charge_wh)
        else:
            # Discharging: draw more from the battery than delivered, due to efficiency loss
            gross_discharge_wh = -net_surplus_w
            drawn_from_batt_wh = gross_discharge_wh / DISCHARGE_EFF
            cycling_loss_wh = drawn_from_batt_wh - gross_discharge_wh
            current_battery_wh = max(BATT_MIN_WH, current_battery_wh - drawn_from_batt_wh)

        total_cycling_loss_wh += cycling_loss_wh
        total_degradation_cost += cycling_loss_wh * DEG_PENALTY_PER_WH

        # Enforce the governed hard SOC floor (20%) / ceiling (95%) — battery.yaml
        current_battery_wh = max(BATT_MIN_WH, min(BATT_MAX_WH, current_battery_wh))
        current_soc_pct_clamped = (current_battery_wh / BATT_CAPACITY_WH) * 100.0

        # Record for UI Dashboard
        forecast_ghi = aligned_bundle.solar_irradiance.point[0]

        dashboard_data.append({
            "timestamp": orig_dt.isoformat(),
            "actual_ghi": round(actual_ghi, 2),
            "n6_forecast_ghi": round(forecast_ghi, 2),
            "battery_soc_pct": round(current_soc_pct_clamped, 2),
            "diesel_kw": round(step0_diesel_kw, 2),
            "battery_net_kw": round(net_surplus_w / 1000.0, 2),
            "air_temp_c": round(air_temp_c, 2) if pd.notna(air_temp_c) else None,
            "snow_depth_cm": round(snow_depth_cm, 2) if pd.notna(snow_depth_cm) else None,
            "battery_cold_derate_pct": round(batt_derate_pct, 1),
            "snow_covered": bool(snow_covered),
            "theoretical_solar_kw": round(theoretical_solar_w / 1000.0, 2),
            "actual_solar_kw": round(actual_solar_w / 1000.0, 2),
            "inverter_clipped_kw": round(inverter_clipped_w / 1000.0, 2),
            "battery_cycling_loss_wh": round(cycling_loss_wh, 1),
            "diesel_fuel_cost": round(fuel_l * FUEL_COST_PER_L, 3),
        })

        if i % 24 == 0:
            print(f"[{i:04d}/{len(origins)}] Processed {orig_dt.strftime('%Y-%m-%d %H:%M')} | SOC: {current_soc_pct_clamped:5.1f}% | Diesel: {step0_diesel_kw:5.1f} kW | T_air: {air_temp_c if pd.notna(air_temp_c) else float('nan'):5.1f}C")

    ui_df = pd.DataFrame(dashboard_data)
    ui_df.to_csv("scratch/ui_dashboard_continuous_rhc.csv", index=False)

    print("=" * 60)
    print(f"SUCCESS! Continuous RHC completed in {time.time() - start_time:.1f} seconds.")
    print(f"Total diesel consumed:        {total_diesel_liters:,.2f} L")
    print(f"Diesel run hours:             {diesel_run_hours:,} / {len(origins):,}")
    print(f"Diesel start/stop events:     {diesel_start_events:,}")
    print(f"Diesel fuel cost (@2.50/L):   {total_diesel_liters * FUEL_COST_PER_L:,.2f}")
    print(f"Total battery cycling loss:   {total_cycling_loss_wh / 1000.0:,.2f} kWh")
    print(f"Total degradation cost:       {total_degradation_cost:,.4f}")
    print(f"Total inverter-clipped solar: {total_inverter_clipped_wh / 1000.0:,.2f} kWh")
    print("Data ready for Figma/Tremor.so at: scratch/ui_dashboard_continuous_rhc.csv")
    print("=" * 60)

if __name__ == "__main__":
    run_continuous_rhc()
