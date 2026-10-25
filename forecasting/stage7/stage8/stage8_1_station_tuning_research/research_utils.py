#!/usr/bin/env python3
"""
Shared utilities for Candidates G/H/I (and onward), reused across scripts to avoid
re-deriving the same metric/bootstrap/night-zero/hash logic per candidate.

**Bootstrap CI fix** (per CANDIDATE_F_PRE_TRAINING_AUDIT.md item 5, disclosed non-blocking
issue): the original `bootstrap_mae_diff_ci()` in phase2_candidateF_additive_feature.py
resampled unique origins with replacement but selected rows via `np.isin(origins, sample)`,
which includes each sampled origin's rows **at most once per draw**, regardless of how many
times that origin was drawn in the resample (duplicates in `sample` collapse to a single
inclusion). This under-calibrates variance (narrower CI than a correct origin-level paired
bootstrap). `bootstrap_mae_diff_ci_corrected()` below fixes this: it duplicates an origin's
~24 rows once for each time that origin is drawn, by building an explicit row-index pool
per origin and concatenating indices per draw (so an origin drawn 3 times contributes its
rows 3 times, not once). This module performs NO training, NO .fit() calls, and modifies no
frozen artifact.
"""
import hashlib
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def metrics(actual, pred):
    actual = np.asarray(actual)
    pred = np.asarray(pred)
    e = pred - actual
    mae = float(mean_absolute_error(actual, pred))
    rmse = float(np.sqrt(mean_squared_error(actual, pred)))
    bias = float(np.mean(e))
    m = float(np.mean(actual))
    nmae = float((mae / m) * 100.0) if m > 0 else float("nan")
    return {"n": int(len(actual)), "mae": round(mae, 4), "rmse": round(rmse, 4),
            "bias": round(bias, 4), "nmae_pct": round(nmae, 4)}


def apply_night_zero(pred, night_causal_mask):
    out = np.asarray(pred).copy()
    out[np.asarray(night_causal_mask)] = 0.0
    return out


def bootstrap_mae_diff_ci_corrected(origins_series, actual, pred_candidate, pred_control,
                                     n_boot=2000, seed=42):
    """Origin-level paired bootstrap, CORRECTED: an origin drawn k times in a resample
    contributes its ~24 rows k times (row-index pool concatenation), not merely once via
    np.isin set membership. Same n_boot/seed convention as the original (disclosed-flawed)
    utility, for direct comparability of point estimates; the CI width differs (wider,
    correctly) as documented in the Candidate F audit."""
    rng = np.random.RandomState(seed)
    origins = np.asarray(origins_series)
    actual = np.asarray(actual)
    pred_candidate = np.asarray(pred_candidate)
    pred_control = np.asarray(pred_control)
    unique_origins, inverse = np.unique(origins, return_inverse=True)
    n_u = len(unique_origins)
    idx_by_origin = [np.where(inverse == i)[0] for i in range(n_u)]
    diffs = []
    for _ in range(n_boot):
        sample_idx = rng.randint(0, n_u, size=n_u)
        rows = np.concatenate([idx_by_origin[s] for s in sample_idx])
        if rows.size == 0:
            continue
        mae_c = float(np.mean(np.abs(pred_candidate[rows] - actual[rows])))
        mae_k = float(np.mean(np.abs(pred_control[rows] - actual[rows])))
        diffs.append(mae_c - mae_k)
    diffs = np.array(diffs)
    return {"mean_diff": round(float(diffs.mean()), 4),
            "ci95_lo": round(float(np.percentile(diffs, 2.5)), 4),
            "ci95_hi": round(float(np.percentile(diffs, 97.5)), 4),
            "n_boot": int(len(diffs)),
            "method": "corrected_row_duplication_per_draw_count"}


def horizon_breakdown(horizon_hour, actual, pred_control, pred_candidate):
    """Per-H1..H24 MAE/bias for control and candidate, plus candidate-minus-control MAE
    delta, keyed by the integer horizon_hour value observed in the data (H1..H24)."""
    horizon_hour = np.asarray(horizon_hour)
    actual = np.asarray(actual)
    pred_control = np.asarray(pred_control)
    pred_candidate = np.asarray(pred_candidate)
    out = {}
    for h in sorted(np.unique(horizon_hour)):
        mask = horizon_hour == h
        n = int(mask.sum())
        if n == 0:
            continue
        mae_ctrl = float(np.mean(np.abs(pred_control[mask] - actual[mask])))
        mae_cand = float(np.mean(np.abs(pred_candidate[mask] - actual[mask])))
        bias_ctrl = float(np.mean(pred_control[mask] - actual[mask]))
        bias_cand = float(np.mean(pred_candidate[mask] - actual[mask]))
        out[f"H{int(h)}"] = {
            "n": n,
            "control_mae": round(mae_ctrl, 4), "candidate_mae": round(mae_cand, 4),
            "delta_mae": round(mae_cand - mae_ctrl, 4),
            "control_bias": round(bias_ctrl, 4), "candidate_bias": round(bias_cand, 4),
        }
    return out
