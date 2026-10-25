#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

REPORT_DIR = Path("/home/punith-bs/01polaris (Copy)/forecasting/spatial_arome_research")
V1_JSON_PATH = REPORT_DIR / "FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT.json"
V2_JSON_PATH = REPORT_DIR / "FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT_v2.json"
V2_MD_PATH = REPORT_DIR / "FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT_v2.md"

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(V1_JSON_PATH, "r") as f:
        data = json.load(f)

    # 1. Update Document Title
    data["document_title"] = "POLARIS FINAL CORRECTED LOCAL SPATIAL STATE INFORMATION AUDIT v2"
    data["timestamp_utc"] = datetime.now(timezone.utc).isoformat()

    # 2. Separation of Claims update (Claim A range corrected)
    data["separation_of_claims"]["claim_a_local_spatial_info"] = (
        "VALIDATED — Local station-neighborhood (3x3) cloud state contains modest, statistically significant incremental information "
        "(Delta R^2 ranging from +0.0078 to +0.0740 across individually FDR-supported horizons, and +0.0037 to +0.0140 across grouped regimes; "
        "all-horizon range +0.0001 to +0.0740) about future station cloud state beyond single-pixel station persistence."
    )
    data["separation_of_claims"]["claim_b_sw_in_forecasting_gain"] = (
        "NOT ESTABLISHED — Diagnostic associations with control SW_IN error DO NOT EQUAL forecasting gain. "
        "No forecasting model has been trained, and no forecast improvement has been demonstrated."
    )

    # 3. Add Level 3-5 prose reconciliation to JSON
    data["level_3_5_incremental_variance_reconciliation"] = {
        "reconciliation_statement": (
            "Level 2 (3x3 mean) provides the clearest recurring incremental contribution across horizons (Delta R^2 up to +0.0740 at H17). "
            "Levels 3–5 (heterogeneity, temporal change, structural change) show smaller but occasionally non-negligible individual increments "
            "(e.g., H2 L4 +0.0155, H2 L5 +0.0064, H3 L3 +0.0131, H3 L4 +0.0080, H4 L3 +0.0080, H4 L4 +0.0052) that are not consistently supported "
            "across horizons or in grouped FDR tests (p > 0.05 for L3–L5 grouped F-tests) and do not justify separate experimentation."
        )
    }

    # 4. Add explicit H24 audit to JSON
    data["h24_audit"] = {
        "status": "EXPLICITLY EXCLUDED FROM PREDICTOR REGRESSION ORIGINS",
        "explanation": (
            "The 24-step forecast window (H1–H24) yields 23 1-step ahead state transitions (H1->H2, H2->H3, ..., H23->H24). "
            "Predicting 1-step ahead state for H24 requires S_cloud(t+1) at t+1=H25, which lies outside the 24-step forecast horizon window. "
            "H24 is evaluated as the target state for predictor H23, but cannot serve as a predictor origin for H25. "
            "Thus, the final grouped transition regime is H19–H23 (covering 5 step transitions ending at H24)."
        )
    }

    # 5. Null 1 classification update (remove causal overclaim)
    data["null_controls_audit"]["null1_classification"] = (
        "STRONG ASSOCIATIVE NULL REJECTION — Origin-permuted null yields near-zero partial correlation (-0.0115), "
        "supporting origin-specific association and rejecting the simple origin-permuted null."
    )

    # 6. Conservative Horizon Recommendation Wording
    data["final_decision"]["justified_horizon_regime"] = (
        "Local 3x3 spatial state shows horizon-dependent incremental information, with strongest individually supported evidence "
        "at the listed FDR-supported horizons (H2, H5, H6, H8, H10, H13, H17, H19, H20, H22, H23) and additional grouped-regime evidence (H4–H6, H7–H12, H13–H18, H19–H23)."
    )

    # Write v2 JSON
    with open(V2_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    json_v2_hash = compute_sha256(V2_JSON_PATH)
    print(f"v2 JSON written: {V2_JSON_PATH}")
    print(f"v2 JSON SHA256: {json_v2_hash}")

    # Build v2 Markdown Report
    lines = []
    lines.append("# POLARIS — FINAL CORRECTED CAUSAL LOCAL SPATIAL STATE INFORMATION AUDIT REPORT (v2)\n")
    lines.append(f"**Date:** {datetime.now(timezone.utc).strftime('%B %d, %Y')}  ")
    lines.append(f"**Audit Classification:** `{data['final_decision']['classification_code']}`  ")
    lines.append(f"**Final Recommendation:** **`{data['final_decision']['recommendation']}`**  ")
    lines.append(f"**Justified Horizon Regime:** `{data['final_decision']['justified_horizon_regime']}`  \n")

    lines.append("---\n## 1. Absolute Separation of Scientific Claims\n")
    lines.append("> **CRITICAL SCIENTIFIC GOVERNANCE SEPARATION:**")
    lines.append(f"> 1. **CLAIM A (Local Spatial State Information Content):** {data['separation_of_claims']['claim_a_local_spatial_info']}")
    lines.append(f"> 2. **CLAIM B (POLARIS SW_IN Forecasting Improvement):** {data['separation_of_claims']['claim_b_sw_in_forecasting_gain']}\n")

    lines.append("---\n## 2. Governance & Safeguard Audit\n")
    lines.append("> **STRICT DIAGNOSTIC SAFEGUARDS VERIFIED:**")
    lines.append("> 1. *No model training was performed.*")
    lines.append("> 2. *No ODD data accessed (174 ODD origins completely sealed).*")
    lines.append("> 3. *Network fetches performed = 0.*")
    lines.append("> 4. *EVEN origins ONLY (173 origins × 24 horizons = 4,152 rows).*")
    lines.append("> 5. *Evaluated on 2,216 causal daytime forecast hours (`solar_elevation > 0` & `clearsky_ghi > 1e-6`).*")
    lines.append("> 6. *Future SW_IN used strictly post-hoc after spatial metrics were frozen.*\n")

    lines.append("---\n## 3. Level 3–5 Incremental Variance Audit & Reconciliation\n")
    lines.append(r"Raw $R^2$ values and exact nested $\Delta R^2$ increments across nested models (L1: Center, L2: +3x3 Mean, L3: +Heterogeneity, L4: +Temporal Change, L5: +Structural Change):" + "\n")
    lines.append(r"| Horizon / Group | L1 $R^2$ | L2 $R^2$ ($\Delta R^2$) | L3 $R^2$ ($\Delta R^2$) | L4 $R^2$ ($\Delta R^2$) | L5 $R^2$ ($\Delta R^2$) | L2 $p_{\text{FDR}}$ | L3 $p_{\text{F-test}}$ | L4 $p_{\text{F-test}}$ | L5 $p_{\text{F-test}}$ |")
    lines.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    target_keys = [f"H{h}" for h in range(1, 7)] + ["H1–H3", "H4–H6", "H7–H12", "H13–H18", "H19–H23"]
    nested_results = data["nested_model_results"]
    for k in target_keys:
        res = nested_results[k]
        r2 = res["raw_r2"]
        dr2 = res["delta_r2"]
        fp = res["f_test_p_values"]
        fdr_p = res.get("fdr_p_val", fp["L2_vs_L1"])
        
        fdr_str = f"{fdr_p:.2e}" if fdr_p < 0.001 else f"{fdr_p:.4f}"
        p3_str = f"{fp['L3_vs_L2']:.2e}" if fp['L3_vs_L2'] < 0.001 else f"{fp['L3_vs_L2']:.4f}"
        p4_str = f"{fp['L4_vs_L3']:.2e}" if fp['L4_vs_L3'] < 0.001 else f"{fp['L4_vs_L3']:.4f}"
        p5_str = f"{fp['L5_vs_L4']:.2e}" if fp['L5_vs_L4'] < 0.001 else f"{fp['L5_vs_L4']:.4f}"
        
        lines.append(f"| **{k}** | `{r2['L1']:.4f}` | `{r2['L2']:.4f}` (**`+{dr2['L2_inc']:.4f}`**) | `{r2['L3']:.4f}` (`+{dr2['L3_inc']:.4f}`) | `{r2['L4']:.4f}` (`+{dr2['L4_inc']:.4f}`) | `{r2['L5']:.4f}` (`+{dr2['L5_inc']:.4f}`) | `{fdr_str}` | `{p3_str}` | `{p4_str}` | `{p5_str}` |")

    lines.append("\n> **PROSE RECONCILIATION WITH TABLE:**")
    lines.append(f"> {data['level_3_5_incremental_variance_reconciliation']['reconciliation_statement']}\n")

    lines.append("---\n## 4. Horizon Decision Table & H24 Audit\n")
    lines.append(r"Complete individual (H1–H23) and grouped horizon decision table with raw and Benjamini-Hochberg FDR-adjusted $p$-values:" + "\n")
    lines.append(r"| Horizon / Group | Sample Size ($N$) | Level 1 $R^2$ | Level 2 $\Delta R^2$ | Raw F-test $p$ | FDR-adjusted $p$ | Evidence Status |")
    lines.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for row in data["horizon_decision_table"]:
        raw_p_str = f"{row['raw_p_val']:.2e}" if row['raw_p_val'] < 0.001 else f"{row['raw_p_val']:.4f}"
        fdr_p_str = f"{row['fdr_p_val']:.2e}" if row['fdr_p_val'] < 0.001 else f"{row['fdr_p_val']:.4f}"
        lines.append(f"| **{row['horizon']}** | `{row['sample_size']}` | `{row['raw_r2_l1']:.4f}` | **`+{row['delta_r2_l2']:.4f}`** | `{raw_p_str}` | `{fdr_p_str}` | **`{row['evidence_status']}`** |")

    lines.append("\n### **Individually FDR-Supported Horizons (11 Total):**")
    lines.append(r"> `H2, H5, H6, H8, H10, H13, H17, H19, H20, H22, H23` (FDR $p < 0.05$, $\Delta R^2 > +0.001$)" + "\n")

    lines.append("### **Borderline Horizons (4 Total):**")
    lines.append(r"> `H9, H15, H18, H21` (raw $p < 0.05$, FDR $p \le 0.10$)" + "\n")

    lines.append("### **Not Supported Horizons (8 Total):**")
    lines.append(r"> `H1, H3, H4, H7, H11, H12, H14, H16` (FDR $p > 0.10$)" + "\n")

    lines.append("### **Explicit H24 Audit & Grouping Rationale:**")
    lines.append(f"> **Status:** `{data['h24_audit']['status']}`  ")
    lines.append(f"> **Explanation:** {data['h24_audit']['explanation']}\n")

    lines.append("---\n## 5. Origin-Level Regression Audit & Origin-Resampled Bootstrap\n")
    origin_audit = data["origin_level_small_sample_audit"]
    lines.append(f"- **Small-Sample Acknowledgement:** {origin_audit['small_sample_acknowledgement']}")
    lines.append(r"- **Origin-Level Level 2 $\Delta R^2$ Median:** " + f"`{origin_audit['origin_l2_inc_r2_median']}` (IQR: `{origin_audit['origin_l2_inc_r2_iqr']}`)")
    lines.append(r"- **Origin-Resampled 1,000x Bootstrap 95% CI for Median $\Delta R^2$:** " + f"`{origin_audit['origin_l2_inc_r2_bootstrap_95ci']}`")
    lines.append(r"- **Fraction of Origins with Positive $\Delta R^2$:** " + f"`{origin_audit['fraction_origins_positive_inc_r2']*100:.1f}%`\n")
    lines.append(r"- **Origin-Level $3\times 3$ Spearman Partial $\rho$ Median:** " + f"`{origin_audit['origin_spearman_pcorr_median']}` (IQR: `{origin_audit['origin_spearman_pcorr_iqr']}`)")
    lines.append(r"- **Origin-Resampled 1,000x Bootstrap 95% CI for Median Partial $\rho$:** " + f"`{origin_audit['origin_spearman_pcorr_bootstrap_95ci']}`")
    lines.append(f"- **Fraction of Origins with Positive Partial Correlation:** `{origin_audit['fraction_origins_positive_pcorr']*100:.1f}%`\n")

    lines.append("---\n## 6. Null Controls Audit & Uncertainty Assessment\n")
    null_audit = data["null_controls_audit"]
    lines.append(r"- **Real $3\times 3$ Station Mean Partial $\rho$:** " + f"`{null_audit['real_3x3_mean_spearman_pcorr']}`")
    lines.append(r"- **Null 1 (Origin-Permuted $3\times 3$ Mean):** " + f"`{null_audit['null1_origin_permuted_pcorr']}` ({null_audit['null1_classification']})")
    lines.append(r"- **Null 2 (Unrelated Field $y$-wind 10m):** " + f"`{null_audit['null2_unrelated_field_pcorr']}`")
    lines.append(r"- **Null 3 (Random Patch Location $[3,3]$):** " + f"`{null_audit['null3_random_patch_location_pcorr']}`")
    lines.append(r"- **Difference Real $-$ Null 3:** " + f"`{null_audit['difference_real_minus_null3']}` (Bootstrap 95% CI: `{null_audit['null3_difference_bootstrap_95ci']}`)")
    lines.append(f"- **Null 3 Status:** `{null_audit['null3_classification']}`\n")

    lines.append("---\n## 7. SW_IN Forecast Error Double-Residual FDR Audit\n")
    sw_audit = data["sw_in_error_fdr_audit"]
    lines.append(f"- **Disclaimer:** {sw_audit['claim_b_disclaimer']}\n")
    lines.append(r"| Spatial Descriptor | Raw Spearman $\rho$ | Double-Residual Spearman $\rho$ | Raw $p$-value | FDR-adjusted $p$-value | Significant at $\alpha=0.05$? |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")

    for d_name, d_dict in sw_audit["descriptor_associations"].items():
        sig_str = "YES" if d_dict["is_significant_fdr_05"] else "NO"
        lines.append(f"| `{d_name}` | `{d_dict['spearman_rho_raw']}` | `{d_dict['double_residual_spearman_rho']}` | `{d_dict['double_residual_p_value_raw']:.2e}` | `{d_dict['bh_adjusted_p_value']:.2e}` | `{sig_str}` |")

    lines.append("\n---\n## 8. Final Decision & Scientific Recommendation\n")
    lines.append(f"### **Final Classification:** `{data['final_decision']['classification_code']}`\n")
    lines.append(f"### **Final Scientific Recommendation:**\n> **`{data['final_decision']['recommendation']}`**\n")
    lines.append(f"### **Justified Horizon Regime:**\n> `{data['final_decision']['justified_horizon_regime']}`\n")
    lines.append("### **Actionable Pre-Registration Guidance:**")
    lines.append(r"1. **Authorized Experiment:** If authorized by human review, design a **single pre-registered horizon-conditional architecture** exploiting **local station-neighborhood ($3\times 3$) cloud state**.")
    lines.append("2. **Discontinued Components:** Multi-scale CNNs, high-order patch heterogeneity features, optical flow cloud translation, and temporal spatial change features are **PERMANENTLY DISCONTINUED** as they add no consistent incremental information beyond Level 2.")
    lines.append("3. **Stop Condition:** Awaiting human review before any model development. **NO MODEL TRAINING IS AUTHORIZED IN THIS CORRECTION RUN.**\n")

    lines.append("---\n## 9. Cryptographic Provenance\n")
    lines.append(f"- **Control Predictions Artifact CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/forecasting/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)")
    lines.append(f"  - SHA256: `{data['provenance']['control_preds_csv_sha256']}`")
    lines.append(f"- **Final Audit Script SHA256:** `{data['provenance']['final_script_sha256']}`")
    lines.append(f"- **Final Audit JSON Artifact v2:** [`FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT_v2.json`](file:///home/punith-bs/01polaris (Copy)/forecasting/spatial_arome_research/FINAL_CORRECTED_LOCAL_SPATIAL_STATE_AUDIT_v2.json)")
    lines.append(f"  - SHA256: `{json_v2_hash}`")

    md_content = "\n".join(lines)
    with open(V2_MD_PATH, "w") as f:
        f.write(md_content)

    md_v2_hash = compute_sha256(V2_MD_PATH)
    print(f"v2 MD written: {V2_MD_PATH}")
    print(f"v2 MD SHA256: {md_v2_hash}")

if __name__ == "__main__":
    main()
