"""
PHASE10_CANDIDATE_A TRAINING — CORRECTED PYTORCH IMPLEMENTATION
Bidirectional GRU, real torch.nn.GRU, EVEN-only, nested 5-fold GroupKFold CV.

This replaces the invalid prior script, which defined a NumPy GRU class but
actually trained a flattened sklearn MLPRegressor instead. This version uses
torch.nn.GRU(bidirectional=True) and preserves [origin, 24, 39] sequence
structure throughout (no flattening across horizons at any point).

Expected parameter count: 6,113 (CORRECTED from the design doc's original
6,049 figure — see PHASE10_CANDIDATE_A_DESIGN_CHECKPOINT_CORRECTED_6113.md
for the full explanation). The architecture itself is unchanged; only the
hand-computed parameter total was wrong in the original design doc.

USAGE (from ~/01polaris (Copy)):
    python scripts/forecasting_research/phase10_candidate_a_train.py            # audit only, no training
    python scripts/forecasting_research/phase10_candidate_a_train.py --train    # audit, then train

Do not run --train until you have reviewed the audit output printed by the
first mode, per the design-checkpoint requirement that no training proceeds
without explicit authorization after the audit is inspected.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

# ============================================================================
# 0. CONFIG — FROZEN, DO NOT CHANGE
# ============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind" / "stage8_1_full_37_feature_matrix_2024.csv"

STATIC_FEATURES = [
    "ctx_std_3h", "ctx_std_6h", "ctx_std_12h", "ctx_std_24h",
    "ctx_abs_change_1h", "ctx_abs_change_3h", "ctx_abs_change_6h",
    "ctx_max_diff_6h", "ctx_mean_diff_6h", "ctx_slope_6h", "ctx_kt_std_6h",
    "ctx_last_obs", "ctx_mean_24h", "ctx_max_24h",
]  # 14

HORIZON_VARYING_FEATURES = [
    "horizon_hour", "month", "hour",
    "solar_elevation", "solar_zenith", "clearsky_ghi", "clearsky_ghi_terrain_adjusted",
    "fc_cloud_cover", "fc_temperature_2m", "fc_relative_humidity_2m", "cloud_frac",
    "lwp_latest", "iwp_latest", "lwp_x_cloud",
    "terrain_horizon_elevation_deg", "terrain_elevation_margin_deg", "terrain_solar_obstruction_flag",
    "u700", "v700",
    "pred_stage3b_cloud_nwp", "phys_pred_fold", "pred_stage4_fold", "disagreement_fold",
    "is_daytime", "is_night_causal",
]  # 25

ALL_FEATURES = STATIC_FEATURES + HORIZON_VARYING_FEATURES  # 39, static-first ordering per frozen design doc
assert len(STATIC_FEATURES) == 14
assert len(HORIZON_VARYING_FEATURES) == 25
assert len(ALL_FEATURES) == 39
assert len(set(ALL_FEATURES)) == 39, "Duplicate feature name in frozen feature list"

TARGET_COL = "actual_SW_IN"
EXPECTED_TOTAL_ORIGINS = 347
EXPECTED_EVEN_ORIGINS = 173
EXPECTED_ODD_ORIGINS = 174
EXPECTED_HORIZONS = 24
EXPECTED_PARAM_COUNT = 6113  # CORRECTED per PHASE10_CANDIDATE_A_DESIGN_CHECKPOINT_CORRECTED_6113.
# The original design doc's 6,049 figure was a manual arithmetic error: it assumed
# a single tied bias per GRU gate (real torch.nn.GRU stores separate bias_ih and
# bias_hh per gate) and miscounted the 32->1 output Dense layer as 65 params
# instead of the correct 33. The architecture itself is UNCHANGED — only the
# expected parameter count is corrected to match the real, standard nn.GRU math.

# Deterministic inner 80/20 validation split.
# Seed formula (fixed, recorded here for reproducibility): seed = INNER_SPLIT_BASE_SEED + fold_idx
# fold_idx runs 1..N_OUTER_FOLDS. Selection uses np.random.RandomState(seed).choice
# over the training-origin index array for that fold, without replacement.
INNER_SPLIT_BASE_SEED = 42

DENSE1_DIM = 32
GRU_HIDDEN = 16
DROPOUT_P = 0.2

BATCH_ORIGINS = 8
LR = 1e-3
BETAS = (0.9, 0.999)
EPS = 1e-7
WEIGHT_DECAY = 1e-4
MAX_EPOCHS = 300
PATIENCE = 20
N_OUTER_FOLDS = 5
INNER_VAL_FRACTION = 0.2

torch.set_num_threads(max(1, torch.get_num_threads()))
DEVICE = torch.device("cpu")  # CUDA unavailable per environment report


# ============================================================================
# 1. MODEL — real torch.nn.GRU, bidirectional, no proxy
# ============================================================================

class CandidateA(nn.Module):
    def __init__(self, input_dim=39, dense_dim=32, gru_hidden=16, dropout_p=0.2):
        super().__init__()
        self.dense1 = nn.Linear(input_dim, dense_dim)
        self.relu = nn.ReLU()
        self.drop1 = nn.Dropout(dropout_p)
        self.gru = nn.GRU(
            input_size=dense_dim,
            hidden_size=gru_hidden,
            num_layers=1,
            batch_first=True,
            bidirectional=True,
        )
        self.drop2 = nn.Dropout(dropout_p)
        self.dense_out = nn.Linear(gru_hidden * 2, 1)

    def forward(self, x):
        # x: [batch, 24, 39]
        h = self.relu(self.dense1(x))          # [batch, 24, 32]
        h = self.drop1(h)
        h, _ = self.gru(h)                     # [batch, 24, 32]  (return_sequences equivalent: batch_first output at every step)
        h = self.drop2(h)
        out = self.dense_out(h)                # [batch, 24, 1]
        return out.squeeze(-1)                 # [batch, 24]


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())


def parameter_breakdown(model):
    breakdown = {}
    for name, p in model.named_parameters():
        breakdown[name] = tuple(p.shape) + (p.numel(),)
    return breakdown


# ============================================================================
# 2. DATA LOADING + AUDIT
# ============================================================================

def load_and_audit():
    print("=" * 80)
    print("PHASE10_CANDIDATE_A — ASSERTION AUDIT")
    print("=" * 80)

    if not CSV_PATH.exists():
        print(f"\n[FATAL] CSV not found at: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    print(f"\n[1] Loaded CSV: {CSV_PATH}")
    print(f"    shape = {df.shape}")

    # --- duplicate horizon_hour column check -------------------------------
    # pandas will have already deduped the header into 'horizon_hour' and
    # 'horizon_hour.1'. We are told to use the plain 'horizon_hour' column
    # and ignore 'horizon_hour.1'. Verify that the column we are about to use
    # actually contains 1..24 per origin before trusting it — the earlier
    # (invalid) script assumed the opposite mapping.
    assert "horizon_hour" in df.columns, "horizon_hour column missing"
    if "horizon_hour.1" in df.columns:
        print("    NOTE: duplicate column 'horizon_hour.1' present in CSV — excluded per instruction, using 'horizon_hour' only.")

    # --- origin / horizon structure -----------------------------------------
    origins_all = sorted(df["origin_id"].unique().tolist())
    n_origins = len(origins_all)
    print(f"\n[2] Total unique origins: {n_origins} (expected {EXPECTED_TOTAL_ORIGINS})")
    ok_total_origins = n_origins == EXPECTED_TOTAL_ORIGINS
    print(f"    {'PASS' if ok_total_origins else 'FAIL'}")

    origin_counts = df.groupby("origin_id").size()
    ok_24_per_origin = bool((origin_counts == EXPECTED_HORIZONS).all())
    print(f"\n[3] Rows per origin: min={origin_counts.min()}, max={origin_counts.max()} (expected all == {EXPECTED_HORIZONS})")
    print(f"    {'PASS' if ok_24_per_origin else 'FAIL'}")

    # --- horizon_hour content check (1..24 per origin) ----------------------
    sample_origin_id = origins_all[0]
    sample = df[df["origin_id"] == sample_origin_id].sort_values("horizon_hour")
    hh_values = sorted(sample["horizon_hour"].unique().tolist())
    ok_horizon_hour_values = hh_values == list(range(1, 25))
    print(f"\n[4] 'horizon_hour' values for sample origin {sample_origin_id}: {hh_values[:3]}...{hh_values[-3:]}")
    print(f"    Expected exactly 1..24. {'PASS' if ok_horizon_hour_values else 'FAIL — CHECK COLUMN MAPPING, see note in script header'}")

    # --- split counts ---------------------------------------------------------
    assert "split" in df.columns, "split column missing"
    split_by_origin = df.drop_duplicates("origin_id")[["origin_id", "split"]]
    even_origins = sorted(split_by_origin.loc[split_by_origin["split"] == "EVEN", "origin_id"].tolist())
    odd_origins = sorted(split_by_origin.loc[split_by_origin["split"] == "ODD", "origin_id"].tolist())
    print(f"\n[5] EVEN origins: {len(even_origins)} (expected {EXPECTED_EVEN_ORIGINS})")
    ok_even = len(even_origins) == EXPECTED_EVEN_ORIGINS
    print(f"    {'PASS' if ok_even else 'FAIL'}")
    print(f"    ODD origins: {len(odd_origins)} (expected {EXPECTED_ODD_ORIGINS})")
    ok_odd = len(odd_origins) == EXPECTED_ODD_ORIGINS
    print(f"    {'PASS' if ok_odd else 'FAIL'}")

    # --- feature presence ------------------------------------------------------
    missing_feats = [f for f in ALL_FEATURES if f not in df.columns]
    print(f"\n[6] Frozen feature columns present: {39 - len(missing_feats)}/39")
    if missing_feats:
        print(f"    MISSING: {missing_feats}")
    ok_features_present = len(missing_feats) == 0
    print(f"    {'PASS' if ok_features_present else 'FAIL'}")

    # --- static-feature constancy per origin -----------------------------------
    static_ok = True
    for feat in STATIC_FEATURES:
        n_unique = sample[feat].nunique()
        if n_unique != 1:
            static_ok = False
            print(f"    Static feature '{feat}' has {n_unique} unique values for sample origin (expected 1)")
    print(f"\n[7] Static features constant per origin (sampled on origin {sample_origin_id}): {'PASS' if static_ok else 'FAIL'}")

    # --- NaN check on required columns -----------------------------------------
    needed_cols = ALL_FEATURES + [TARGET_COL, "origin_id", "split"]
    n_nan = int(df[needed_cols].isna().sum().sum())
    print(f"\n[8] NaN count across required columns: {n_nan} (expected 0)")
    ok_no_nan = n_nan == 0
    print(f"    {'PASS' if ok_no_nan else 'FAIL'}")

    # --- build EVEN tensor & check shape ----------------------------------------
    feature_data = {}
    target_data = {}
    for origin in even_origins:
        odf = df[df["origin_id"] == origin].sort_values("horizon_hour")
        feature_data[origin] = odf[ALL_FEATURES].values.astype(np.float64)  # [24, 39]
        target_data[origin] = odf[TARGET_COL].values.astype(np.float64)     # [24]

    even_tensor = np.stack([feature_data[o] for o in even_origins], axis=0)  # [173, 24, 39]
    print(f"\n[9] EVEN input tensor shape: {even_tensor.shape} (expected ({EXPECTED_EVEN_ORIGINS}, {EXPECTED_HORIZONS}, 39))")
    ok_shape = even_tensor.shape == (EXPECTED_EVEN_ORIGINS, EXPECTED_HORIZONS, 39)
    print(f"    {'PASS' if ok_shape else 'FAIL'}")

    # --- model parameter count ----------------------------------------------------
    model = CandidateA(input_dim=39, dense_dim=DENSE1_DIM, gru_hidden=GRU_HIDDEN, dropout_p=DROPOUT_P)
    actual_params = count_parameters(model)
    print(f"\n[10] Model parameter count (real torch.nn.GRU): {actual_params} (corrected expected: {EXPECTED_PARAM_COUNT})")
    ok_param_count = actual_params == EXPECTED_PARAM_COUNT
    print(f"     {'PASS' if ok_param_count else 'FAIL'}")

    breakdown = parameter_breakdown(model)
    print("\n     Parameter breakdown:")
    for name, shape_and_n in breakdown.items():
        *shape, n = shape_and_n
        print(f"       {name}: shape={tuple(shape)} n={n}")

    audit = {
        "csv_path": str(CSV_PATH),
        "csv_shape": list(df.shape),
        "total_origins": n_origins,
        "total_origins_pass": ok_total_origins,
        "rows_per_origin_pass": ok_24_per_origin,
        "horizon_hour_values_pass": ok_horizon_hour_values,
        "even_origins": len(even_origins),
        "even_origins_pass": ok_even,
        "odd_origins": len(odd_origins),
        "odd_origins_pass": ok_odd,
        "features_present_pass": ok_features_present,
        "static_features_constant_pass": static_ok,
        "nan_count": n_nan,
        "no_nan_pass": ok_no_nan,
        "even_tensor_shape": list(even_tensor.shape),
        "even_tensor_shape_pass": ok_shape,
        "model_param_count_actual": actual_params,
        "model_param_count_expected": EXPECTED_PARAM_COUNT,
        "model_param_count_pass": ok_param_count,
        "inner_split_seed_formula": "INNER_SPLIT_BASE_SEED + fold_idx",
        "inner_split_base_seed": INNER_SPLIT_BASE_SEED,
    }

    all_pass = all([
        ok_total_origins, ok_24_per_origin, ok_horizon_hour_values, ok_even, ok_odd,
        ok_features_present, static_ok, ok_no_nan, ok_shape, ok_param_count,
    ])
    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: {'ALL PASS' if all_pass else 'FAILED — DO NOT TRAIN'}")
    print(f"Inner 80/20 validation split: deterministic, seed = {INNER_SPLIT_BASE_SEED} + fold_idx (RandomState, no-replacement choice)")
    print("=" * 80)

    return df, even_origins, odd_origins, feature_data, target_data, audit, all_pass


# ============================================================================
# 3. TRAINING (nested GroupKFold, per-origin sequences preserved throughout)
# ============================================================================

def train_one_fold(fold_idx, train_inner_origins, val_inner_origins, test_origins,
                    feature_data, target_data, inner_split_seed):
    # Fit scaler on inner-training origins only, flattened over [n*24, 39] ONLY
    # for the purpose of computing mean/std — the resulting transform is still
    # applied per-origin and the [origin, 24, 39] structure is preserved for
    # every tensor that touches the model.
    train_stack = np.concatenate([feature_data[o] for o in train_inner_origins], axis=0)  # [n_train*24, 39]
    scaler = StandardScaler()
    scaler.fit(train_stack)

    def to_tensor_set(origin_list):
        X = np.stack([scaler.transform(feature_data[o]) for o in origin_list], axis=0)  # [n, 24, 39]
        y = np.stack([target_data[o] for o in origin_list], axis=0)                       # [n, 24]
        return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

    X_train, y_train = to_tensor_set(train_inner_origins)
    X_val, y_val = to_tensor_set(val_inner_origins)
    X_test, y_test = to_tensor_set(test_origins)

    model = CandidateA(input_dim=39, dense_dim=DENSE1_DIM, gru_hidden=GRU_HIDDEN, dropout_p=DROPOUT_P).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, betas=BETAS, eps=EPS, weight_decay=WEIGHT_DECAY)
    loss_fn = nn.L1Loss()  # MAE

    n_train = X_train.shape[0]
    best_val_loss = float("inf")
    best_state = None
    patience_counter = 0

    for epoch in range(MAX_EPOCHS):
        model.train()
        perm = torch.randperm(n_train)
        epoch_loss = 0.0
        n_batches = 0
        for start in range(0, n_train, BATCH_ORIGINS):
            idx = perm[start:start + BATCH_ORIGINS]
            xb, yb = X_train[idx].to(DEVICE), y_train[idx].to(DEVICE)
            optimizer.zero_grad()
            pred = model(xb)                 # [batch, 24]
            loss = loss_fn(pred, yb)          # MAE averaged over all 24 horizons (and batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * xb.shape[0]
            n_batches += 1
        train_mae = epoch_loss / n_train

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val.to(DEVICE))
            val_mae = loss_fn(val_pred, y_val.to(DEVICE)).item()

        if val_mae < best_val_loss - 1e-6:
            best_val_loss = val_mae
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1

        if (epoch + 1) % 10 == 0 or patience_counter == 0:
            print(f"      epoch {epoch+1:3d}  train_mae={train_mae:.4f}  val_mae={val_mae:.4f}  patience={patience_counter}")

        if patience_counter >= PATIENCE:
            print(f"      early stopping at epoch {epoch+1} (best val_mae={best_val_loss:.4f})")
            break

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test.to(DEVICE)).cpu().numpy()
    test_true = y_test.numpy()

    test_mae = float(np.mean(np.abs(test_pred - test_true)))
    test_rmse = float(np.sqrt(np.mean((test_pred - test_true) ** 2)))
    test_bias = float(np.mean(test_pred - test_true))

    return {
        "fold": fold_idx,
        "n_test_origins": len(test_origins),
        "mae": test_mae,
        "rmse": test_rmse,
        "bias": test_bias,
        "best_val_mae": best_val_loss,
        "inner_split_seed": inner_split_seed,
        "train_inner_origins": list(train_inner_origins),
        "val_inner_origins": list(val_inner_origins),
        "test_origins": list(test_origins),
        "predictions": {o: test_pred[i].tolist() for i, o in enumerate(test_origins)},
    }


def run_training(even_origins, feature_data, target_data):
    print("\n" + "=" * 80)
    print("CANDIDATE A TRAINING — nested 5-fold GroupKFold, EVEN only")
    print("=" * 80)

    gkf = GroupKFold(n_splits=N_OUTER_FOLDS)
    group_array = np.arange(len(even_origins))

    fold_results = []
    for fold_idx, (train_idx, test_idx) in enumerate(
        gkf.split(np.zeros(len(even_origins)), groups=group_array), start=1
    ):
        train_origins = [even_origins[i] for i in train_idx]
        test_origins = [even_origins[i] for i in test_idx]

        inner_seed = INNER_SPLIT_BASE_SEED + fold_idx
        rng = np.random.RandomState(inner_seed)
        n_val = max(1, int(len(train_origins) * INNER_VAL_FRACTION))
        val_pos = rng.choice(len(train_origins), n_val, replace=False)
        train_pos = np.setdiff1d(np.arange(len(train_origins)), val_pos)

        train_inner_origins = [train_origins[i] for i in train_pos]
        val_inner_origins = [train_origins[i] for i in val_pos]

        print(f"\n  Fold {fold_idx}/{N_OUTER_FOLDS}: "
              f"train={len(train_inner_origins)}  val={len(val_inner_origins)}  test={len(test_origins)}  "
              f"(inner_split_seed={inner_seed})")

        result = train_one_fold(fold_idx, train_inner_origins, val_inner_origins, test_origins,
                                 feature_data, target_data, inner_seed)
        print(f"    Fold {fold_idx} TEST: MAE={result['mae']:.4f}  RMSE={result['rmse']:.4f}  bias={result['bias']:.4f}")
        fold_results.append(result)

    return fold_results


# ============================================================================
# 4. MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Proceed to training after audit passes.")
    args = parser.parse_args()

    df, even_origins, odd_origins, feature_data, target_data, audit, all_pass = load_and_audit()

    audit_out_path = BASE_DIR / "forecasting/reports/candidates/PHASE10_CANDIDATE_A_AUDIT.json"
    with open(audit_out_path, "w") as f:
        json.dump(audit, f, indent=2)
    print(f"\nAudit written to: {audit_out_path}")

    if not args.train:
        print("\nAudit-only run complete. Re-run with --train to proceed to model training,")
        print("after reviewing the audit output above (especially the parameter-count WARNING).")
        return

    if not all_pass:
        print("\n[FATAL] Structural audit checks failed. Refusing to train. Fix data/config and re-run.")
        sys.exit(1)

    fold_results = run_training(even_origins, feature_data, target_data)

    maes = [r["mae"] for r in fold_results]
    rmses = [r["rmse"] for r in fold_results]
    n_test_total = sum(r["n_test_origins"] for r in fold_results)
    agg_mae = float(np.average(maes, weights=[r["n_test_origins"] for r in fold_results]))
    agg_rmse = float(np.sqrt(np.average(np.array(rmses) ** 2, weights=[r["n_test_origins"] for r in fold_results])))

    print("\n" + "=" * 80)
    print("CANDIDATE A — AGGREGATE EVEN-OOF RESULTS")
    print("=" * 80)
    print(f"  Aggregate MAE:  {agg_mae:.4f} W/m^2  (n={n_test_total})")
    print(f"  Aggregate RMSE: {agg_rmse:.4f} W/m^2")
    for r in fold_results:
        print(f"  Fold {r['fold']}: MAE={r['mae']:.4f}  RMSE={r['rmse']:.4f}  bias={r['bias']:.4f}  n={r['n_test_origins']}")

    results_path = BASE_DIR / "forecasting/reports/candidates/PHASE10_CANDIDATE_A_RESULTS_REAL.json"
    with open(results_path, "w") as f:
        json.dump({
            "checkpoint": "PHASE10_CANDIDATE_A_RESULTS_CHECKPOINT_CORRECTED",
            "date": datetime.now().isoformat(),
            "implementation": "torch.nn.GRU(bidirectional=True), real training loop, no proxy",
            "model_param_count": audit["model_param_count_actual"],
            "inner_split_seed_formula": f"{INNER_SPLIT_BASE_SEED} + fold_idx",
            "fold_results": [
                {k: v for k, v in r.items() if k != "predictions"} for r in fold_results
            ],
            "aggregate_mae_wm2": agg_mae,
            "aggregate_rmse_wm2": agg_rmse,
            "note": "This checkpoint contains ONLY Candidate A EVEN-OOF metrics. "
                    "Control (HGB) comparison and gate evaluation (G1-G6) still need "
                    "to be computed against the official/reconstructed control before "
                    "any accept/reject verdict is issued.",
        }, f, indent=2)
    print(f"\nResults written to: {results_path}")
    print("\nODD was not accessed at any point in this run.")


if __name__ == "__main__":
    main()
