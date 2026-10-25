#!/usr/bin/env python3
"""
Post-hoc reconstruction of curtailment (kWh) and battery cycling loss (kWh)
for Scenarios 2/3/4, using the EXACT clamp/efficiency formulas from
run_continuous_ui_rhc_scenario2.py's run_continuous_rhc() (the shared
function Scenarios 2/3/4 all ran through). This is a deterministic replay,
not an estimate -- it reproduces the per-step battery-energy update using
only the already-saved CSV columns (battery_net_kw, battery_soc_pct), so no
rerun of the MILP/N6 pipeline is needed.

Reactive baseline is handled separately (run_reactive_baseline_clean.py was
re-run with direct instrumentation, since it's an 8-second rule-based loop
with no ML/MILP cost).
"""
import pandas as pd
import json

BATT_CAPACITY_WH = 200_000.0
BATT_MIN_WH = BATT_CAPACITY_WH * 0.20
BATT_MAX_WH = BATT_CAPACITY_WH * 0.95
CHARGE_EFF = 0.92
DISCHARGE_EFF = 0.92
FUEL_COST_PER_L = 2.50


def reconstruct(csv_path, label):
    df = pd.read_csv(csv_path)
    prev_wh = BATT_CAPACITY_WH * 0.50  # initial SOC used by all scenario2/3/4 runs

    total_curtailed_wh = 0.0
    total_cycling_loss_wh = 0.0
    total_charge_wh = 0.0
    total_discharge_wh = 0.0

    for _, row in df.iterrows():
        net_w = row["battery_net_kw"] * 1000.0
        actual_next_wh = (row["battery_soc_pct"] / 100.0) * BATT_CAPACITY_WH

        if net_w >= 0:
            headroom_gross_wh = max(0.0, (BATT_MAX_WH - prev_wh) / CHARGE_EFF)
            charged_gross_wh = min(net_w, headroom_gross_wh)
            curtailed_wh = net_w - charged_gross_wh
            cycling_loss_wh = charged_gross_wh * (1.0 - CHARGE_EFF)
            total_charge_wh += charged_gross_wh * CHARGE_EFF
        else:
            gross_discharge_wh = -net_w
            drawn_gross_wh = min(gross_discharge_wh / DISCHARGE_EFF, max(0.0, prev_wh - BATT_MIN_WH))
            curtailed_wh = 0.0
            cycling_loss_wh = drawn_gross_wh * (1.0 - DISCHARGE_EFF)
            total_discharge_wh += drawn_gross_wh * DISCHARGE_EFF

        total_curtailed_wh += curtailed_wh
        total_cycling_loss_wh += cycling_loss_wh
        prev_wh = actual_next_wh  # resync to the actually-recorded (clamped) value each step

    fuel_cost_total = df["diesel_fuel_cost"].sum() if "diesel_fuel_cost" in df.columns else None
    equivalent_cycles = (total_charge_wh + total_discharge_wh) / 2.0 / BATT_CAPACITY_WH

    return {
        "label": label,
        "renewable_curtailed_kwh": round(total_curtailed_wh / 1000.0, 1),
        "battery_cycling_loss_kwh": round(total_cycling_loss_wh / 1000.0, 1),
        "equivalent_battery_cycles": round(equivalent_cycles, 2),
        "total_fuel_cost_eur": round(fuel_cost_total, 2) if fuel_cost_total is not None else None,
        "rows": len(df),
    }


if __name__ == "__main__":
    results = []
    for path, label in [
        ("scratch/ui_dashboard_scenario3.csv", "Scenario 3 (EBR, no deadband)"),
        ("scratch/ui_dashboard_scenario2.csv", "Scenario 2 (EBR + 10kWh deadband)"),
    ]:
        results.append(reconstruct(path, label))

    for r in results:
        print(json.dumps(r, indent=2))
