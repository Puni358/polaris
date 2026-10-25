import json
from hashlib import sha256
from pathlib import Path
import pandas as pd

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")

def sha256_file(p):
    if not p.exists():
        return "FILE_NOT_FOUND"
    with open(p, "rb") as f:
        return sha256(f.read()).hexdigest()

def create_closeout_and_synthesis():
    print("==================================================")
    print("BUILDING PHASE C-1 CLOSEOUT & SYNTHESIS ARTIFACTS")
    print("==================================================")

    hashes = {
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md"),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"),
        "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv": sha256_file(BASE_DIR / "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv")
    }

    closeout_payload = {
        "artifact_name": "PHASE_C1_CORRECTION_AND_CLOSEOUT",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "governance_status": "PHASE C-1 OFFICIALLY CLOSED AND FROZEN",
        "initial_execution_record": {
            "status": "INVALID_HISTORICAL_ONLY",
            "root_cause_defect": "Canonical fold labels in forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv are 1-indexed (1,2,3,4,5), whereas initial script used range(5) (0,1,2,3,4). Fold 0 was empty, Fold 5 validation origins were omitted, Fold 5 origins leaked into training for Folds 1-4, and Fold 5 OOF predictions were unpredicted zero-fills.",
            "preserved_invalid_artifacts": [
                "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md"
            ]
        },
        "authoritative_corrected_execution": {
            "status": "VALID_AUTHORITATIVE",
            "execution_script": "scratch/run_phase_c1_horizon_diagnostic_corrected.py",
            "forensic_audit_verdict": "PASS — All 15 checks verified",
            "authoritative_artifacts": [
                "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json",
                "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md"
            ]
        },
        "corrected_results_summary": {
            "population_accounting": {
                "parent_eligible_origins": 104,
                "theoretical_max_cells": 624,
                "aggregate_valid_target_cells": 609,
                "total_omitted_cells": 15,
                "omitted_horizon_detail": "All 15 omitted cells occur at H7 due to clear-sky GHI < 20 W/m²"
            },
            "horizon_gbdt_results": {
                "H7": {"N_h": 89, "delta_R2": 0.5146, "bootstrap_95ci": [0.2639, 0.7858], "permutation_p": 0.0010, "folds_1_to_5": [18, 17, 18, 18, 18]},
                "H8": {"N_h": 104, "delta_R2": 0.5317, "bootstrap_95ci": [0.3024, 0.7740], "permutation_p": 0.0010, "folds_1_to_5": [21, 21, 21, 20, 21]},
                "H9": {"N_h": 104, "delta_R2": 0.7013, "bootstrap_95ci": [0.4795, 0.9302], "permutation_p": 0.0010, "folds_1_to_5": [21, 21, 21, 20, 21]},
                "H10": {"N_h": 104, "delta_R2": 0.4718, "bootstrap_95ci": [0.2216, 0.7408], "permutation_p": 0.0010, "folds_1_to_5": [21, 21, 21, 20, 21]},
                "H11": {"N_h": 104, "delta_R2": 0.6373, "bootstrap_95ci": [0.3904, 0.8996], "permutation_p": 0.0010, "folds_1_to_5": [21, 21, 21, 20, 21]},
                "H12": {"N_h": 104, "delta_R2": 0.3037, "bootstrap_95ci": [0.0276, 0.5850], "permutation_p": 0.0010, "folds_1_to_5": [21, 21, 21, 20, 21]}
            },
            "ridge_contrast_summary": {
                "H7": -0.7366, "H8": -0.4308, "H9": -0.2484, "H10": -0.3494, "H11": -0.2729, "H12": -0.4332
            }
        },
        "hypothesis_ledger": {
            "M1_information_absent": "DISFAVORED — Incremental out-of-fold predictive information extracted across all 6 daytime horizons.",
            "M2_representation_limitation": "NOT ESTABLISHED BY C-1 — Probe extraction does not establish Stage8.1 architecture inadequacy due to model-class, loss, and capacity confounders.",
            "M3_point_loss_uncertainty": "NOT ESTABLISHED BY C-1 — Phase B hedging diagnostics remain consistent with median hedging, but C-1 does not independently test M3.",
            "event_timing_uncertainty": "NOT ESTABLISHED BY C-1 — C-1 does not directly measure transition timing.",
            "odd_performance": "UNKNOWN — ODD data remains completely sealed (0 rows accessed)."
        },
        "governance_closure": {
            "phase_c1_status": "COMPLETE_AND_CLOSED",
            "odd_firewall": "SEALED_0_ROWS_ACCESSED",
            "secondary_analysis_authorized": False
        },
        "historical_hashes": hashes
    }

    closeout_json_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json"
    with open(closeout_json_path, "w") as f:
        json.dump(closeout_payload, f, indent=2)

    closeout_md_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md"
    with open(closeout_md_path, "w") as f:
        f.write("# POLARIS — PHASE C-1 CORRECTION AND CLOSEOUT REPORT\n\n")
        f.write(f"**Date (UTC):** {closeout_payload['timestamp_utc']}  \n")
        f.write("**Governance Status:** PHASE C-1 OFFICIALLY CLOSED AND FROZEN  \n")
        f.write("**ODD Status:** SEALED (0 rows accessed)  \n\n---\n\n")

        f.write("## 1. Executive Summary & Governance Closure\n\n")
        f.write("Phase C-1 (`POLARIS Horizon-Decomposed Transmission Diagnostic`) is officially **COMPLETE AND CLOSED**.\n\n")
        f.write("- **Initial Execution:** Invalidated due to a canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved strictly as historical invalid artifacts (`forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json` / `.md`).\n")
        f.write("- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with **PASS** status (`forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json` / `.md`).\n")
        f.write("- **ODD Firewall:** 100% sealed (0 rows accessed).\n")
        f.write("- **Secondary Analysis:** None authorized. Phase C-1 closes without triggering adaptive reruns or new feature/model sweeps.\n\n---\n\n")

        f.write("## 2. Historical Record of Initial Execution Defect\n\n")
        f.write("- **Root Cause:** Canonical fold labels in `forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` are 1-indexed (1, 2, 3, 4, 5). The initial script iterated over `0..4`.\n")
        f.write("- **Defect Impact:** Fold 0 was empty; Fold 5 (21 origins) was omitted from validation, leaked into training for Folds 1–4, and received unpredicted zero-filled placeholders.\n")
        f.write("- **Preservation Policy:** Initial invalid artifacts are retained for historical auditability and MUST NEVER be used as benchmarks, tuning references, or supporting evidence.\n\n---\n\n")

        f.write("## 3. Authoritative Corrected Results & Accounting\n\n")
        f.write("### Population & Fold Accounting\n")
        f.write("- **Parent EVEN Origins:** 104 Phase-A-eligible origins.\n")
        f.write("- **Theoretical Max Cells:** 624 cells ($104 \\times 6$).\n")
        f.write("- **Aggregate Valid Target Cells:** 609 cells (15 omitted cells at H7 due to clear-sky GHI $< 20\\text{ W/m}^2$).\n\n")

        f.write("| Horizon | Target | Valid $N_h$ | Omitted Cells | Canonical Fold 1–5 Breakdown | Sum |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for h, hr in closeout_payload["corrected_results_summary"]["horizon_gbdt_results"].items():
            fb = hr["folds_1_to_5"]
            f.write(f"| {h} | $k_{{t+{h[1:]}}}$ | {hr['N_h']} | {104 - hr['N_h']} | {fb[0]} / {fb[1]} / {fb[2]} / {fb[3]} / {fb[4]} | **{sum(fb)}** |\n")
        f.write("\n---\n\n")

        f.write("### Quantitative Results Table\n\n")
        f.write("| Horizon | Ridge $\\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        ridge_dict = closeout_payload["corrected_results_summary"]["ridge_contrast_summary"]
        for h, hr in closeout_payload["corrected_results_summary"]["horizon_gbdt_results"].items():
            ci = hr["bootstrap_95ci"]
            f.write(f"| {h} | {ridge_dict[h]:+.4f} | — | — | **{hr['delta_R2']:+.4f}** | [{ci[0]:+.4f}, {ci[1]:+.4f}] | {hr['permutation_p']:.4f} |\n")
        f.write("\n---\n\n")

        f.write("## 4. Controlled Scientific Interpretation\n\n")
        f.write("> \"Across all six H7–H12 horizons, the specified nonlinear GBDT probe extracted positive incremental out-of-fold predictive information from the frozen P1 causal state relative to P0. The GBDT ΔR² values ranged from +0.3037 to +0.7013, with the prespecified origin-level bootstrap 95% confidence intervals excluding zero at every horizon. The corresponding finite-sample within-month permutation p-values were 0.0010 at all six horizons.\n\n")
        f.write("> This demonstrates that the frozen P1 causal state contains information that the specified GBDT probe can extract for individual hourly transmission targets k(t+h) beyond the deterministic P0 state.\n\n")
        f.write("> This does NOT establish that the Stage8.1 representation itself is inadequate, because the GBDT probe and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure.\"\n\n---\n\n")

        f.write("## 5. Hypothesis Ledger Summary\n\n")
        f.write("- **M1 (Information Absent):** DISFAVORED for tested hourly transmission targets.\n")
        f.write("- **M2 (Representation Limitation):** NOT ESTABLISHED BY C-1 (probe extraction does not prove architecture inadequacy).\n")
        f.write("- **M3 (Point-Loss / Uncertainty Limitation):** NOT ESTABLISHED BY C-1 (Phase B hedging diagnostics remain consistent, but C-1 does not independently test M3).\n")
        f.write("- **Event-Timing Uncertainty:** NOT ESTABLISHED BY C-1 (timing error not directly isolated).\n")
        f.write("- **ODD Performance:** UNKNOWN (sealed).\n\n---\n\n")
        f.write("PHASE C-1 CORRECTION AND CLOSEOUT COMPLETE.\nNO SECONDARY ANALYSIS AUTHORIZED.\nODD REMAINS SEALED.\n")

    synthesis_payload = {
        "checkpoint_name": "POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "purpose": "Consolidated scientific synthesis of audited Phase A, Phase B, and Phase C-1 findings",
        "governance_status": {
            "phase_a": "COMPLETE_AND_FORENSICALLY_AUDITED",
            "phase_b": "COMPLETE_AND_FORENSICALLY_AUDITED",
            "phase_c1": "COMPLETE_AND_FORENSICALLY_AUDITED",
            "b3_procedural_status": "PROCEDURALLY_COMPROMISED_EXPLORATORY_ONLY",
            "t4_status": "DROPPED_UNAVAILABLE",
            "section_9_decision_rule": "ORIGINAL_2_OF_4_RULE_UNCHANGED",
            "odd_firewall": "SEALED_0_ROWS_ACCESSED",
            "phase_c2_authorization": "NOT_AUTHORIZED"
        },
        "phase_a_summary": {
            "total_even_origins": 174,
            "eligible_even_origins": 104,
            "daytime_hours_evaluated": 604,
            "p0_feature_count": 22,
            "p1_feature_count": 147,
            "gbdt_aggregate_targets": {
                "T1_volatility": {"delta_R2": 0.309826, "bootstrap_95ci": [0.0506, 0.5886]},
                "T2_max_transition": {"delta_R2": 0.305179, "bootstrap_95ci": [0.0470, 0.5837]},
                "T3_mean_kt": {"delta_R2": 0.598801, "bootstrap_95ci": [0.3639, 0.8421]}
            },
            "established_m1_finding": "M1 (information absent) is inconsistent with the tested aggregate targets. The frozen Stage8.1 causal state contains nonlinear predictive information about the tested future H7-H12 transmission statistics beyond P0."
        },
        "phase_b_summary": {
            "b1_rank": {"mean_normalized_rank": 0.4459, "mean_raw_rank": 2.2219},
            "b2_pinball_loss": {
                "champion_q05_loss": 0.105774,
                "neighbour_median_q05_loss": 0.126686,
                "difference": 0.020912,
                "win_rate_pct": 42.88,
                "p_value": 0.000001,
                "dependence_caveat": "The reported p < 0.0001 treats all 604 hourly observations as independent, without accounting for origin-level clustering."
            },
            "b3_procedural_limitation": "B3 combined threshold was NOT demonstrably frozen before computation. B3 is procedurally compromised and remains exploratory only."
        },
        "phase_c1_summary": {
            "initial_execution": "INVALID_HISTORICAL_ONLY (canonical fold indexing loop mismatch range(5) vs 1..5)",
            "corrected_execution": "VALID_AUTHORITATIVE (scratch/run_phase_c1_horizon_diagnostic_corrected.py)",
            "parent_eligible_origins": 104,
            "aggregate_valid_target_cells": 609,
            "gbdt_hourly_targets": {
                "H7": {"N_h": 89, "delta_R2": 0.5146, "bootstrap_95ci": [0.2639, 0.7858], "permutation_p": 0.0010},
                "H8": {"N_h": 104, "delta_R2": 0.5317, "bootstrap_95ci": [0.3024, 0.7740], "permutation_p": 0.0010},
                "H9": {"N_h": 104, "delta_R2": 0.7013, "bootstrap_95ci": [0.4795, 0.9302], "permutation_p": 0.0010},
                "H10": {"N_h": 104, "delta_R2": 0.4718, "bootstrap_95ci": [0.2216, 0.7408], "permutation_p": 0.0010},
                "H11": {"N_h": 104, "delta_R2": 0.6373, "bootstrap_95ci": [0.3904, 0.8996], "permutation_p": 0.0010},
                "H12": {"N_h": 104, "delta_R2": 0.3037, "bootstrap_95ci": [0.0276, 0.5850], "permutation_p": 0.0010}
            },
            "controlled_finding": "Across all six H7-H12 horizons, the specified GBDT probe extracted positive incremental out-of-fold predictive information from P1 relative to P0."
        },
        "evidence_classification": {
            "A_demonstrated": [
                "P1 contains substantial nonlinear predictive information about aggregate targets T1-T3 (Phase A).",
                "M1 (information absent) is inconsistent with tested aggregate targets (Phase A) and individual hourly transmission targets k(t+h) (Phase C-1).",
                "The champion point forecasts have a mean normalized rank of 0.4459 within tested five-neighbour ensembles (Phase B).",
                "Champion q=.5 pinball loss (0.1058) is lower than crude 5-neighbour empirical median loss (0.1267) (Phase B).",
                "GBDT probes achieve positive out-of-fold incremental predictive power (ΔR² from +0.3037 to +0.7013) for individual hourly targets k(t+7) to k(t+12) relative to P0 (Phase C-1)."
            ],
            "B_supported_consistent_with": [
                "Phase B diagnostics are consistent with conditional-median/hedging behavior.",
                "The Ridge vs GBDT contrast is consistent with nonlinear information structure, but does not establish inherent physical nonlinearity."
            ],
            "C_not_established": [
                "Stage8.1 representation limitation (M2 is not established by C-1 due to model-class, loss, and capacity confounders).",
                "M3 point-loss / uncertainty limitation (not established by C-1).",
                "Event-timing uncertainty as a sole mechanism (not established by C-1).",
                "Any unique mechanism explaining Stage8.1 hourly point forecast error.",
                "Any ODD performance implication."
            ]
        }
    }

    synthesis_json_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"
    with open(synthesis_json_path, "w") as f:
        json.dump(synthesis_payload, f, indent=2)

    synthesis_md_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"
    with open(synthesis_md_path, "w") as f:
        f.write("# POLARIS — PHASE A + PHASE B + PHASE C-1 SCIENTIFIC SYNTHESIS CHECKPOINT\n\n")
        f.write(f"**Date (UTC):** {synthesis_payload['timestamp_utc']}  \n")
        f.write("**Governance Status:** CONSOLIDATED SCIENTIFIC SYNTHESIS CHECKPOINT  \n")
        f.write("**Phase C-1 Status:** COMPLETE AND CLOSED  \n")
        f.write("**Phase C-2 Status:** NOT AUTHORIZED  \n")
        f.write("**ODD Status:** SEALED (0 rows accessed)  \n\n---\n\n")

        f.write("## 1. Executive Purpose & Governance Record\n\n")
        f.write("This document provides the consolidated, forensically audited scientific synthesis checkpoint spanning **Phase A** (Information Probe), **Phase B** (Local Causal-State Diagnostics), and **Phase C-1** (Horizon-Decomposed Transmission Diagnostic).\n\n")
        f.write("- **Phase A:** COMPLETE + FORENSICALLY AUDITED  \n")
        f.write("- **Phase B:** COMPLETE + FORENSICALLY AUDITED  \n")
        f.write("- **Phase C-1:** COMPLETE + FORENSICALLY AUDITED (Authoritative Corrected Execution)  \n")
        f.write("- **T4 Target:** DROPPED / UNAVAILABLE  \n")
        f.write("- **Section 9 Decision Rule:** ORIGINAL 2-OF-4 RULE UNCHANGED  \n")
        f.write("- **ODD Firewall:** SEALED (0 rows accessed)  \n")
        f.write("- **Phase C-2 Authorization:** NOT AUTHORIZED  \n\n---\n\n")

        f.write("## 2. Phase A — Established Findings\n\n")
        f.write("Phase A evaluated the incremental predictive information in the frozen Stage8.1 causal state $P1$ (147 features) vs deterministic astronomical state $P0$ (22 features) across 104 eligible EVEN origins.\n\n")
        f.write("- **T1 (Volatility):** GBDT $\\Delta R^2 = +0.3098$, 95% CI `[+0.0506, +0.5886]`, $p < 0.0001$\n")
        f.write("- **T2 (Max Transition):** GBDT $\\Delta R^2 = +0.3052$, 95% CI `[+0.0470, +0.5837]`, $p < 0.0001$\n")
        f.write("- **T3 (Mean Transmission):** GBDT $\\Delta R^2 = +0.5988$, 95% CI `[+0.3639, +0.8421]`, $p < 0.0001$\n\n")
        f.write("> **Established Finding:** *M1 (information absent) is inconsistent with the tested aggregate targets. The frozen Stage8.1 causal state contains nonlinear predictive information about future H7–H12 transmission statistics beyond P0.*\n\n---\n\n")

        f.write("## 3. Phase B — Established Findings & Limitations\n\n")
        f.write("- **B1 Rank Diagnostic:** Champion forecasts concentrate near the local 5-neighbour ensemble median (mean normalized rank $0.4459$, raw $2.2219/5$). Descriptively compatible with central positioning.\n")
        f.write("- **B2 Pinball Loss:** Champion $q=0.5$ loss ($0.1058$) is lower than crude 5-neighbour empirical median loss ($0.1267$, $\\Delta = +0.0209$, reported $p < 0.0001$).\n")
        f.write("  - *Dependence Caveat:* Reported $p < 0.0001$ treated 604 hourly observations as independent without origin-level clustering.\n")
        f.write("- **B3 Procedural Limitation:** B3 threshold was NOT frozen before computation. B3 is procedurally compromised and remains exploratory only.\n\n---\n\n")

        f.write("## 4. Phase C-1 — Horizon-Decomposed Transmission Diagnostic\n\n")
        f.write("- **Initial Execution:** Invalidated due to canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved as historical invalid artifact (`forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json`).\n")
        f.write("- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with PASS status.\n")
        f.write("- **Population:** 104 parent origins, 609 aggregate valid target cells (H7: 89 valid; H8–H12: 104 valid each; 15 omitted cells at H7).\n\n")

        f.write("### Authoritative Horizon Results Table\n\n")
        f.write("| Horizon | Target | Valid $N_h$ | Ridge $\\Delta R^2$ | GBDT $P0$ $R^2$ | GBDT $P1$ $R^2$ | GBDT $\\Delta R^2$ | GBDT 95% Bootstrap CI | Permutation $p$-value |\n")
        f.write("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for h, hr in synthesis_payload["phase_c1_summary"]["gbdt_hourly_targets"].items():
            ci = hr["bootstrap_95ci"]
            f.write(f"| {h} | $k_{{t+{h[1:]}}}$ | {hr['N_h']} | — | — | — | **{hr['delta_R2']:+.4f}** | [{ci[0]:+.4f}, {ci[1]:+.4f}] | {hr['permutation_p']:.4f} |\n")
        f.write("\n")
        f.write("> **Controlled Interpretation:** *Across all six H7–H12 horizons, the specified GBDT probe extracted positive incremental out-of-fold predictive information from P1 relative to P0 (ΔR² from +0.3037 to +0.7013, all 95% CIs exclude 0, permutation p = 0.0010). This demonstrates that P1 contains information extractable by the GBDT probe for individual hourly targets. It does NOT establish that the Stage8.1 representation itself is inadequate, because GBDT and Stage8.1 differ in model class, objective, loss, capacity, optimization, and training procedure.*\n\n---\n\n")

        f.write("## 5. Demonstrated / Supported / Not Established Hierarchy\n\n")
        f.write("### A. DEMONSTRATED\n")
        for item in synthesis_payload["evidence_classification"]["A_demonstrated"]:
            f.write(f"- {item}\n")
        f.write("\n### B. SUPPORTED / CONSISTENT WITH\n")
        for item in synthesis_payload["evidence_classification"]["B_supported_consistent_with"]:
            f.write(f"- {item}\n")
        f.write("\n### C. NOT ESTABLISHED\n")
        for item in synthesis_payload["evidence_classification"]["C_not_established"]:
            f.write(f"- {item}\n")
        f.write("\n---\n\n")
        f.write("PHASE A + PHASE B + PHASE C-1 SYNTHESIS CHECKPOINT COMPLETE.\nNO SECONDARY ANALYSIS AUTHORIZED.\nODD REMAINS SEALED.\n")

    final_hashes = {
        "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json": sha256_file(closeout_json_path),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md": sha256_file(closeout_md_path),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json": sha256_file(synthesis_json_path),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md": sha256_file(synthesis_md_path)
    }

    print("Closeout JSON Hash:", final_hashes["forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json"])
    print("Closeout MD Hash:  ", final_hashes["forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md"])
    print("Synthesis JSON Hash:", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"])
    print("Synthesis MD Hash:  ", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC1_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"])

if __name__ == "__main__":
    create_closeout_and_synthesis()
