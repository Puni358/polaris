#!/usr/bin/env python3
"""
TERMINAL-TARGET ABLATION. RESEARCH-ONLY SIMULATION. NOT a production run.
NOT a governance-authorized experiment.

Tests the hypothesis identified in STAGE81_FORECAST_VALUE_TRANSLATION_INVESTIGATION.md
(§3/§4): that the Stage8.1-vs-baseline diesel delta is dominated by `terminal_target_wh`
being solar-forecast-sensitive (via the R1/R2 research formula
`40000 + max(0, 6h trailing deficit) * 1.10`), not by GAP19 itself or by the direct bus-bar
balance alone.

Change made, and ONLY this change: `terminal_target_wh` is forced to a SOLAR-INSENSITIVE
CONSTANT equal to the existing R1/R2 floor (40,000 Wh), for BOTH arms, at every origin. This
is done by monkeypatching the `compute_terminal_target_wh` name inside THIS SCRIPT's own
imported copy of `run_full_experiment`'s module namespace -- it does not edit
run_full_experiment.py, run_research_simulation.py, or any other file on disk. Those files
remain byte-identical to their frozen R1/R2 hashes (verified below, via the same
verify_frozen_manifest() R1/R2 already use, unmodified).

Everything else is reused UNCHANGED from the frozen R1/R2 harness: build_components(),
run_one_cycle() (same function object, same code), final_smoke_test(), the same 347 origins,
same GAP19HighsNativeOptimizer, same config YAMLs, same warmed-up StationState construction,
same two forecast engines (baseline, Stage 8.1 corrected).

No production code, config, or frozen artifact is modified by this script.
"""
import sys
import json
import time
from pathlib import Path

import pandas as pd

BASE = Path("/home/punith-bs/01polaris (Copy)")
sys.path.insert(0, str(BASE))
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

import run_full_experiment as rfe  # frozen R1/R2 module, imported not copied; not modified on disk

CHECKPOINT_EVERY = rfe.CHECKPOINT_EVERY
ABLATED_TERMINAL_TARGET_WH = 40000.0  # == the existing R1/R2 TERMINAL_FLOOR_WH constant


def _ablated_compute_terminal_target_wh(bundle):
    """Solar-insensitive constant, replacing the R1/R2 research formula for this run ONLY.
    In-process monkeypatch of rfe's module-level name; no file on disk is changed."""
    return ABLATED_TERMINAL_TARGET_WH


def main():
    print("=" * 80)
    print("TERMINAL-TARGET ABLATION -- terminal_target_wh forced to solar-insensitive")
    print(f"constant = {ABLATED_TERMINAL_TARGET_WH} Wh (== existing R1/R2 floor), both arms.")
    print("Everything else: same frozen R1/R2 harness, GAP19, configs, 347 origins, unchanged.")
    print("NOT a production run. NOT governance-authorized. RESEARCH-SIMULATION ONLY.")
    print("=" * 80)

    # Same frozen-manifest verification R1/R2 already use -- confirms no file on disk changed.
    rfe.verify_frozen_manifest()

    # The ONE change: monkeypatch the name run_one_cycle() actually calls, inside rfe's own
    # module namespace. run_one_cycle's body is unmodified; only which function the name
    # `compute_terminal_target_wh` resolves to, for this process only, changes.
    original_fn = rfe.compute_terminal_target_wh
    rfe.compute_terminal_target_wh = _ablated_compute_terminal_target_wh
    print(f"Monkeypatched compute_terminal_target_wh -> constant {ABLATED_TERMINAL_TARGET_WH} "
          f"Wh (original formula object preserved at {original_fn}, restored at exit; "
          f"run_research_simulation.py and run_full_experiment.py are unmodified on disk).\n")

    try:
        components = rfe.build_components()
        rfe.final_smoke_test(components)

        (df, configs_base, adapter, baseline_engine, stage81_engine, router, optimizer,
         option_d_solver, simulator, base_fuel_lph, marginal_fuel_lpwh, _cap) = components

        origins = sorted(df["forecast_start"].unique())
        origins = [pd.Timestamp(o) for o in origins]
        print(f"Established evaluation window (same as R1/R2): {len(origins)} daily origins, "
              f"{origins[0]} .. {origins[-1]}\n")

        results = []
        t_start = time.time()
        for i, origin in enumerate(origins):
            index = int((origin - pd.Timestamp("2024-01-01T00:00:00Z")).total_seconds() // 3600)
            for engine_label, engine in [("baseline", baseline_engine), ("stage8_1_corrected", stage81_engine)]:
                r = rfe.run_one_cycle(engine_label, engine, adapter, router, optimizer, option_d_solver,
                                       simulator, configs_base, df, origin, index, base_fuel_lph, marginal_fuel_lpwh)
                assert abs(r["terminal_target_wh"] - ABLATED_TERMINAL_TARGET_WH) < 1e-6, (
                    f"STOP: ablation did not take effect at origin {origin}, engine {engine_label} "
                    f"(terminal_target_wh={r['terminal_target_wh']})"
                )
                results.append(r)

            if (i + 1) % CHECKPOINT_EVERY == 0 or (i + 1) == len(origins):
                elapsed = time.time() - t_start
                print(f"Checkpoint: {i+1}/{len(origins)} origins done ({len(results)} cycles), "
                      f"elapsed={elapsed:.1f}s")

        out_path = THIS_DIR / "TERMINAL_ABLATION_RAW_RESULTS.json"
        with open(out_path, "w") as f:
            json.dump({
                "disclaimer": (
                    "TERMINAL-TARGET ABLATION. RESEARCH-SIMULATION OUTPUT ONLY. The ONLY "
                    "change from frozen R1/R2: terminal_target_wh forced to a solar-"
                    "insensitive constant (40000.0 Wh, == the existing floor) for BOTH arms "
                    "at every origin. GAP19, configs, StationState, 347-origin window, and "
                    "both forecast engines are byte-identical to R1/R2. Not stakeholder-"
                    "authorized, not a performance claim, not a production run."
                ),
                "ablated_terminal_target_wh": ABLATED_TERMINAL_TARGET_WH,
                "origins_total": len(origins), "cycles_total": len(results),
                "elapsed_s": round(time.time() - t_start, 1),
                "results": results,
            }, f, indent=2)
        print(f"\nTerminal-ablation raw results written to {out_path}")
        print(f"Total: {len(origins)} origins, {len(results)} cycles, "
              f"{round(time.time() - t_start, 1)}s elapsed.")
        print("\nTERMINAL-TARGET ABLATION COMPLETE. No production code, config, or frozen "
              "artifact was modified on disk.")
    finally:
        rfe.compute_terminal_target_wh = original_fn  # restore, in-process only


if __name__ == "__main__":
    main()
