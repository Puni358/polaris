#!/usr/bin/env python3
"""
R2 SOLAR-FORECAST ABLATION. RESEARCH-ONLY SIMULATION. NOT a production run.
NOT a governance-authorized experiment. NOT a full renewable-forecast experiment --
wind and demand are deliberately held identical (both baseline-persistence) between arms;
only the solar forecast differs. See R2_SOLAR_ABLATION_MANIFEST.md.

Reuses R1's frozen verify_frozen_manifest / build_components / run_one_cycle /
final_smoke_test functions from run_full_experiment.py UNCHANGED (imported, not copied) so
R2 cannot silently diverge from R1's assumptions or mechanics. The only things this script
adds are: (1) the full-window identical-wind/demand precondition (already run separately as
verify_r2_identical_wind_demand.py; re-checked here against its JSON output before
proceeding), and (2) independent R2-named output artifacts so R1's results are never
overwritten.
"""
import sys
import json
import time
from pathlib import Path

import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent

from run_full_experiment import (
    verify_frozen_manifest, build_components, run_one_cycle, final_smoke_test, CHECKPOINT_EVERY,
)

R2_IDENTICAL_INPUT_CHECK = THIS_DIR / "R2_IDENTICAL_INPUT_VERIFICATION.json"


def verify_identical_input_precondition():
    print("--- Verifying R2 full-window identical wind/demand precondition ---")
    if not R2_IDENTICAL_INPUT_CHECK.exists():
        raise RuntimeError(
            "STOP: R2_IDENTICAL_INPUT_VERIFICATION.json not found. Run "
            "verify_r2_identical_wind_demand.py first; R2 must not proceed without it."
        )
    with open(R2_IDENTICAL_INPUT_CHECK) as f:
        result = json.load(f)
    if not result.get("all_identical") or result.get("origins_checked") != 347:
        raise RuntimeError(
            f"STOP: R2 identical-input precondition failed or incomplete: {result}"
        )
    print(f"Precondition OK: {result['origins_checked']}/{result['origins_total']} origins, "
          f"0 mismatches.\n")


def main():
    print("=" * 80)
    print("R2 SOLAR-FORECAST ABLATION -- reuses R1-frozen assumptions, unchanged.")
    print("NOT a production run. NOT governance-authorized. RESEARCH-SIMULATION ONLY.")
    print("NOT a full renewable-forecast experiment -- wind/demand held identical by design.")
    print("=" * 80)

    verify_frozen_manifest()
    verify_identical_input_precondition()
    components = build_components()
    final_smoke_test(components)

    (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
     option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, _cap) = components

    origins = sorted(df["forecast_start"].unique())
    origins = [pd.Timestamp(o) for o in origins]
    print(f"Established evaluation window (same as R1): {len(origins)} daily origins, "
          f"{origins[0]} .. {origins[-1]}\n")

    results = []
    t_start = time.time()
    try:
        for i, origin in enumerate(origins):
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
            for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
                r = run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                                   simulator, configs_base, df, origin, index, base_fuel_lph, marginal_fuel_lpwh)
                results.append(r)

            if (i + 1) % CHECKPOINT_EVERY == 0 or (i + 1) == len(origins):
                elapsed = time.time() - t_start
                print(f"Checkpoint: {i+1}/{len(origins)} origins done ({len(results)} cycles), "
                      f"elapsed={elapsed:.1f}s")
                ckpt_path = THIS_DIR / "R2_FULL_EXPERIMENT_CHECKPOINT.json"
                with open(ckpt_path, "w") as f:
                    json.dump({
                        "disclaimer": "R2 SOLAR-FORECAST ABLATION. RESEARCH-SIMULATION ONLY. In-progress checkpoint.",
                        "origins_done": i + 1, "origins_total": len(origins),
                        "cycles_done": len(results), "elapsed_s": round(elapsed, 1),
                        "results": results,
                    }, f, indent=2)
    except Exception as exc:
        print(f"\nSTOP: unexpected failure during R2 full run after {len(results)} cycles: {exc}")
        ckpt_path = THIS_DIR / "R2_FULL_EXPERIMENT_CHECKPOINT.json"
        with open(ckpt_path, "w") as f:
            json.dump({
                "disclaimer": "R2 SOLAR-FORECAST ABLATION. RESEARCH-SIMULATION ONLY. Run HALTED due to failure.",
                "halted": True, "error": str(exc),
                "cycles_done": len(results), "results": results,
            }, f, indent=2)
        raise

    out_path = THIS_DIR / "R2_FULL_EXPERIMENT_RAW_RESULTS.json"
    with open(out_path, "w") as f:
        json.dump({
            "disclaimer": "R2 SOLAR-FORECAST ABLATION. RESEARCH-SIMULATION OUTPUT ONLY. Wind and "
                           "demand are identical (baseline-persistence) between arms by design; "
                           "only solar differs. Not a full renewable-forecast experiment. Not "
                           "stakeholder-authorized, not a performance claim.",
            "manifest": "R2_SOLAR_ABLATION_MANIFEST.md",
            "origins_total": len(origins), "cycles_total": len(results),
            "elapsed_s": round(time.time() - t_start, 1),
            "results": results,
        }, f, indent=2)
    print(f"\nFull R2 raw results written to {out_path}")
    print(f"Total: {len(origins)} origins, {len(results)} cycles, "
          f"{round(time.time() - t_start, 1)}s elapsed.")
    print("\nR2 SOLAR-FORECAST ABLATION COMPLETE. No production code or config was modified. "
          "No assumption was tuned based on results.")


if __name__ == "__main__":
    main()
