"""
Control-only campaign driver (EXP-PLANNER-CF-CONSISTENCY-2025, §5 and §6.1: F_c = PC-Control fuel).

Runs ONLY the PC-Control arm over the governed 123-origin population (2,952 operating hours), using the
same runner, inputs, initialization, realization executor and accounting as the Planner-CF campaign
runner. No candidate arm is run. No oracle is run. Nothing in existing files is modified.

Refuses to run without explicit authorization and verifies the protected hashes first. Writes only to a
new timestamped directory and never overwrites an existing one. Stops and reports on the first optimizer
or step error (fail closed).
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
for _p in (str(REPO), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import planner_cf_campaign_runner as runner  # noqa: E402
import planner_cf_audit_gates as gates  # noqa: E402
import planner_cf_hash_guards as hg  # noqa: E402
import stage4_low_sun_adapter as s4a  # noqa: E402

CONTROL_ARM = "PC-Control"
N_ORIGINS = 123
HOURS = 24
SOC_FLOOR_PCT = 20.0


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_control(*, authorized: bool = False, timestamp: Optional[str] = None) -> Dict[str, Any]:
    if not authorized:
        raise PermissionError("Control-only campaign requires explicit authorization")
    pre = hg.verify_protected_hashes(REPO)
    if pre:
        return {"status": "BLOCKED", "reason": "protected hashes failed before run", "details": pre}

    ts = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = _HERE / f"control_only_{ts}"
    if out_dir.exists():
        raise FileExistsError(f"refusing to overwrite {out_dir}")

    configs, make_initial_state = runner._load_canonical_configs()
    weather = pd.read_csv(runner.WEATHER_2025_PATH)
    origins = runner.origin_population(weather)
    if len(origins) != N_ORIGINS:
        return {"status": "BLOCKED", "reason": f"population {len(origins)} != {N_ORIGINS}"}
    solar = s4a.SolarElevationProvider(runner.DECOMPOSITION_2025_PATH)

    rows = []
    fail: Optional[Dict[str, Any]] = None
    for oi, fs in enumerate(origins, start=1):
        t0 = (pd.to_datetime(fs) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rs, rw, rd, rts = runner.realized_inputs_for(weather, fs)
        try:
            hourly, _ = runner.PlannerCFArmRunner(configs, CONTROL_ARM, solar).run_origin(
                oi, make_initial_state(t0), weather, rs, rw, rd, rts)
        except Exception as e:  # fail closed: record and stop
            fail = {"origin_id": oi, "forecast_start": fs, "error": f"{type(e).__name__}: {e}"}
            break
        rows.extend(hourly)

    result: Dict[str, Any] = {"timestamp": ts, "arm": CONTROL_ARM, "origins_attempted": oi if fail is None else oi,
                              "rows": len(rows), "optimizer_or_step_failure": fail}
    if fail is not None:
        result["status"] = "CONTROL_RUN_FAILED"
        return result

    df = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=False)
    csv = out_dir / "PC_CONTROL_HOURLY.csv"
    df.to_csv(csv, index=False)

    # G7 repeat: one repeated PC-Control run on origin index 1 (earliest sorted origin)
    fs1 = origins[0]
    t01 = (pd.to_datetime(fs1) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rs1, rw1, rd1, rts1 = runner.realized_inputs_for(weather, fs1)
    rep, _ = runner.PlannerCFArmRunner(configs, CONTROL_ARM, solar).run_origin(
        1, make_initial_state(t01), weather, rs1, rw1, rd1, rts1)

    crit = float(df["critical_demand"].sum())
    fuel = float(df["diesel_fuel"].sum())
    per_origin_fuel = df.groupby("origin_id")["diesel_fuel"].sum()
    r_cf = 100.0 * float(df["critical_served_first"].sum()) / crit
    r_p = 100.0 * float(df["critical_served_prop"].sum()) / crit
    unmet_crit_wh = float((df["critical_demand"] - df["critical_served_first"]).sum())
    soc_viol = int((df["soc_after"] < SOC_FLOOR_PCT).sum())

    gate_results = {
        "G4": gates.g4_optimizer_status(df),
        "G6": gates.g6_busbar_soc_fuel(df),
        "G7": gates.g7_determinism(df[(df.origin_id == 1)], pd.DataFrame(rep)),
        "G9": gates.g9_accounting(df, [CONTROL_ARM]),
        "G10": gates.g10_route_propagation(df),
        "G11": gates.g11_old_telemetry_unmodified(REPO),
    }
    integrity_pass = all(v["PASS"] for v in gate_results.values())

    L = 1397.8482963577756
    threshold = L / 0.60
    if fuel <= threshold:
        verdict = "40% target ruled out by certified lower bound"
    else:
        verdict = "40% target NOT ruled out by certified lower bound"

    result.update({
        "status": "CONTROL_COMPLETE",
        "rows_expected": N_ORIGINS * HOURS,
        "origins_completed": int(df["origin_id"].nunique()),
        "F_c_total_fuel_L": fuel,
        "mean_fuel_per_origin_L": fuel / N_ORIGINS,
        "min_origin_fuel_L": float(per_origin_fuel.min()),
        "max_origin_fuel_L": float(per_origin_fuel.max()),
        "critical_first_reliability_pct": r_cf,
        "proportional_reliability_pct": r_p,
        "total_unmet_critical_Wh": unmet_crit_wh,
        "soc_floor_violations_below_20pct": soc_viol,
        "min_soc_pct": float(df["soc_after"].min()),
        "optimizer_failures": 0,
        "gates": {k: {"PASS": bool(v["PASS"])} for k, v in gate_results.items()},
        "control_integrity_gates_PASS": bool(integrity_pass),
        "lower_bound_gate": {"L_certified_L": L, "threshold_L_over_0p60": threshold,
                             "F_c_L": fuel, "verdict": verdict,
                             "note": "NG7 triggers iff L > 0.60 F_c (strict); equality is not a trigger"},
        "hashes": {
            "control_hourly_csv_sha256": _sha(csv),
            "driver_sha256": _sha(_HERE / "run_control_only.py"),
            "runner_sha256": _sha(_HERE / "planner_cf_campaign_runner.py"),
            "planner_sha256": _sha(_HERE / "research_numerical_extractor_planner_cf_v1.py"),
            "executor_sha256": _sha(REPO / "system/simulation/research_realization_executor.py"),
        },
        "protected_pre": pre,
        "protected_post": hg.verify_protected_hashes(REPO),
    })
    (out_dir / "CONTROL_RESULT.json").write_text(json.dumps(result, indent=2, default=str))
    result["out_dir"] = str(out_dir)
    return result
