#!/usr/bin/env python3
"""Forensic-only pre-run. Extracts 4 seasonal EVEN origins, runs Section 13/14 checks, verifies architecture. Does NOT train."""
import sys
sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
import run_real_arome_21x21_experiment as exp

import pandas as pd
import numpy as np
import json

def main():
    print("="*80)
    print("PRE-RUN FORENSIC VALIDATION (4 SEASONAL ORIGINS ONLY)")
    print("Purpose: Validate pipeline correctness. NO ODD, NO TRAINING.")
    print("="*80)

    df_all, df_even, origin_meta_df = exp.load_feature_matrix_and_map_origins()
    seasonal = exp.pick_seasonal_origins(origin_meta_df, n=4)
    print(f"\nForensic test origins: {[s['origin_id'] for s in seasonal]}")

    # Build mini meta df
    mini_meta_df = pd.DataFrame(seasonal)
    spatial_dict = {}
    meta_dict = {}

    for _, row in mini_meta_df.iterrows():
        row_dict = row.to_dict()
        tensor, meta, cached = exp.extract_patch_for_origin(row_dict)
        if tensor is None:
            print(f"FAIL: origin {row_dict['origin_id']} no tensor")
            continue
        spatial_dict[int(row_dict['origin_id'])] = tensor
        meta_dict[int(row_dict['origin_id'])] = meta
        print(f"  origin {row_dict['origin_id']}: shape={list(tensor.shape)}, cached={cached}")

    # Tabular dicts needed for Section 13 (38 CSV reconstructability check)
    tabular_dict = {}
    target_dict = {}
    elev_dict = {}
    for oid in spatial_dict.keys():
        odf = df_even[df_even["origin_id"]==oid].sort_values("horizon_hour").reset_index(drop=True)
        tabular_dict[oid] = odf[exp.CONTEXT_38_FEATURES].iloc[0].values.astype(np.float32)
        target_dict[oid] = odf[exp.TARGET_COL].values.astype(np.float32)
        elev_dict[oid] = odf["solar_elevation"].values.astype(np.float32)

    # Section 13
    forensic = exp.run_pre_training_forensic_checks(df_even, mini_meta_df, spatial_dict, meta_dict)

    # Section 14
    recon = exp.run_independent_reconstruction_check(spatial_dict, meta_dict)

    # Arch
    exp.verify_architecture()

    # Control mini-run (6 folds not possible, but check folds reproducibility on 4 seasonal)
    sorted_ids = sorted(spatial_dict.keys())
    # Use 36 random EVEN origins for mini control reproduction to sanity check
    ctrl_ids = sorted([int(x) for x in df_even["origin_id"].unique()])[:40]
    from sklearn.model_selection import GroupKFold
    gkf = exp.GroupKFold(n_splits=5)
    ctrl_res = exp.run_control_reproduction(df_even[df_even["origin_id"].isin(ctrl_ids)], gkf, ctrl_ids)

    print()
    print("="*80)
    print("FORENSIC VALIDATION SUMMARY")
    print("="*80)
    print(f"Validity defects found: {len(exp.VALIDITY_DEFECTS)}")
    for i,d in enumerate(exp.VALIDITY_DEFECTS, 1):
        print(f"  DEFECT {i}: {d}")
    print()
    print(f"Section13 all_channels_real_arome = {forensic.get('all_channels_real_arome')}")
    print(f"Section13 any_spatial_variation     = {forensic.get('any_channel_has_spatial_variation')}")
    print(f"Section13 origins_different_patterns= {forensic.get('origins_produce_different_patterns')}")
    print(f"Section13 not_reconstructable_csv  = {forensic.get('not_reconstructable_from_csv_alone')}")
    print(f"Section14 independent_recon_pass    = {recon.get('pass')}")
    print(f"Control reproduced (40 EVEN oris)   = {ctrl_res.get('reproduced')}")
    print(f"  Ctrl MAE  = {ctrl_res['aggregate_metrics']['MAE_W_m2']:.4f} (ref {exp.CONTROL_REFERENCE['MAE_W_m2']:.4f})")
    print(f"  Ctrl nMAE = {ctrl_res['aggregate_metrics']['nMAE_pct']:.4f}% (ref {exp.CONTROL_REFERENCE['nMAE_pct']:.4f}%)")

    verdict = "PASS — PROCEED WITH FULL 173-ORIGIN RUN" if len(exp.VALIDITY_DEFECTS)==0 else "FAIL — DEFECTS MUST BE FIXED FIRST"
    print()
    print(f"*** PRE-RUN: {verdict} ***")

    with open("/tmp/polaris_forensic_prerun.json", "w") as f:
        json.dump({
            "defects": exp.VALIDITY_DEFECTS,
            "forensic": forensic,
            "recon": recon,
            "control_mini": {k:v for k,v in ctrl_res.items() if k != "fold_results"},
        }, f, indent=2, default=str)

if __name__ == "__main__":
    main()
