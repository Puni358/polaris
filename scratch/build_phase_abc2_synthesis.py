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

def create_abc2_synthesis():
    print("==================================================")
    print("BUILDING PHASE A+B+C1+C2 SCIENTIFIC SYNTHESIS CHECKPOINT")
    print("==================================================")

    hashes = {
        "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv": sha256_file(BASE_DIR / "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md")
    }

    synthesis_payload = {
        "checkpoint_name": "POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "purpose": "Consolidated, forensically audited scientific synthesis checkpoint spanning Phase A, Phase B, Phase C-1, and Phase C-2",
        "governance_status": {
            "phase_a": "COMPLETE_AND_FROZEN",
            "phase_b": "COMPLETE_AND_FROZEN",
            "phase_c1": "COMPLETE_AND_FROZEN",
            "phase_c2": "COMPLETE_AND_FROZEN",
            "odd_firewall": "SEALED_0_ROWS_ACCESSED",
            "phase_c3_authorization": "NOT_AUTHORIZED"
        },
        "phase_a_summary": {
            "total_even_origins": 174,
            "eligible_even_origins": 104,
            "daytime_hours_evaluated": 604,
            "p0_features": 22,
            "p1_features": 147,
            "gbdt_aggregate_targets": {
                "T1_volatility": {"delta_R2": 0.309826, "bootstrap_95ci": [0.0506, 0.5886], "p_val": "< 0.0001"},
                "T2_max_transition": {"delta_R2": 0.305179, "bootstrap_95ci": [0.0470, 0.5837], "p_val": "< 0.0001"},
                "T3_mean_kt": {"delta_R2": 0.598801, "bootstrap_95ci": [0.3639, 0.8421], "p_val": "< 0.0001"},
                "T4_target": "DROPPED_UNAVAILABLE"
            },
            "section_9_rule": "Original 2-of-4 Section 9 rule remains unchanged",
            "established_finding": "M1 (information absent) is inconsistent with tested aggregate targets T1-T3."
        },
        "phase_b_summary": {
            "b1_rank": {"mean_normalized_rank": 0.4459, "mean_raw_rank": 2.2219},
            "b2_pinball_loss": {
                "champion_q05_loss": 0.105774,
                "neighbour_median_q05_loss": 0.126686,
                "difference": 0.020912,
                "dependence_caveat": "Reported p < 0.0001 treated 604 hourly observations as independent without origin clustering."
            },
            "b3_procedural_compromise": "B3 threshold was NOT frozen before computation. B3 is procedurally compromised and remains exploratory only."
        },
        "phase_c1_summary": {
            "initial_execution": "INVALID_HISTORICAL_ONLY (canonical fold indexing loop mismatch range(5) vs 1..5)",
            "corrected_execution": "VALID_AUTHORITATIVE (scratch/run_phase_c1_horizon_diagnostic_corrected.py)",
            "forensic_audit": "PASS (All 15 checks verified)",
            "parent_eligible_origins": 104,
            "aggregate_valid_target_cells": 609,
            "gbdt_transmission_targets": {
                "H7": {"N_h": 89, "delta_R2": 0.5146, "bootstrap_95ci": [0.2639, 0.7858], "permutation_p": 0.0010},
                "H8": {"N_h": 104, "delta_R2": 0.5317, "bootstrap_95ci": [0.3024, 0.7740], "permutation_p": 0.0010},
                "H9": {"N_h": 104, "delta_R2": 0.7013, "bootstrap_95ci": [0.4795, 0.9302], "permutation_p": 0.0010},
                "H10": {"N_h": 104, "delta_R2": 0.4718, "bootstrap_95ci": [0.2216, 0.7408], "permutation_p": 0.0010},
                "H11": {"N_h": 104, "delta_R2": 0.6373, "bootstrap_95ci": [0.3904, 0.8996], "permutation_p": 0.0010},
                "H12": {"N_h": 104, "delta_R2": 0.3037, "bootstrap_95ci": [0.0276, 0.5850], "permutation_p": 0.0010}
            },
            "controlled_finding": "Across all six H7-H12 horizons, the specified GBDT probe extracted positive incremental OOF predictive information for transmission index k(t+h) from P1 relative to P0."
        },
        "phase_c2_summary": {
            "status": "VALID_AUTHORITATIVE (scratch/run_phase_c2_frozen_p1_physical_sw_in_diagnostic.py)",
            "forensic_audit": "PASS (All 15 checks verified)",
            "parent_eligible_origins": 104,
            "aggregate_valid_target_cells": 609,
            "p0_features": 22,
            "p1_features": 147,
            "gbdt_physical_sw_in_targets": {
                "H7": {"N_h": 89, "p0_mae": 77.8171, "p1_mae": 58.3098, "delta_mae": 19.5073, "bootstrap_95ci_delta_mae": [5.2768, 34.0464], "p0_r2": 0.2322, "p1_r2": 0.5525, "delta_r2": 0.3203},
                "H8": {"N_h": 104, "p0_mae": 96.3352, "p1_mae": 61.2160, "delta_mae": 35.1192, "bootstrap_95ci_delta_mae": [20.9595, 49.8938], "p0_r2": 0.1483, "p1_r2": 0.6341, "delta_r2": 0.4858},
                "H9": {"N_h": 104, "p0_mae": 111.5761, "p1_mae": 74.9105, "delta_mae": 36.6656, "bootstrap_95ci_delta_mae": [19.5594, 53.9874], "p0_r2": 0.1049, "p1_r2": 0.5484, "delta_r2": 0.4435},
                "H10": {"N_h": 104, "p0_mae": 123.0241, "p1_mae": 91.7396, "delta_mae": 31.2846, "bootstrap_95ci_delta_mae": [12.2142, 50.6929], "p0_r2": 0.1382, "p1_r2": 0.5009, "delta_r2": 0.3627},
                "H11": {"N_h": 104, "p0_mae": 147.2473, "p1_mae": 84.1945, "delta_mae": 63.0528, "bootstrap_95ci_delta_mae": [44.2354, 82.0850], "p0_r2": -0.0522, "p1_r2": 0.6027, "delta_r2": 0.6550},
                "H12": {"N_h": 104, "p0_mae": 137.1815, "p1_mae": 93.1950, "delta_mae": 43.9865, "bootstrap_95ci_delta_mae": [25.2811, 62.7872], "p0_r2": 0.0734, "p1_r2": 0.4516, "delta_r2": 0.3782}
            },
            "statistical_protocol": {
                "bootstrap": "Origin-level 10,000 paired block bootstrap with ordinary percentile 95% CIs",
                "degenerate_replicates": 0,
                "permutation_test": "REMOVED due to statistical incoherence of feature/prediction swapping",
                "stage8_1_direct_comparison": "UNAVAILABLE (Stage8.1 champion lacks canonical GroupKFold EVEN OOF artifact)"
            },
            "controlled_finding": "The specified GBDT readout trained on frozen P1 extracted positive incremental OOF predictive information for physical SW_IN(t+h) relative to P0 across all six horizons, with ΔMAE ranging from +19.51 W/m² to +63.05 W/m²."
        },
        "scientific_evidence_matrix": [
            {
                "phase": "Phase A",
                "question": "Does frozen P1 contain incremental predictive info for aggregate future transmission statistics beyond P0?",
                "population": "104 EVEN origins (604 daytime hours)",
                "main_result": "GBDT ΔR² = +0.305 to +0.599 across T1-T3 (p < 0.0001)",
                "demonstrated": "P1 contains substantial nonlinear predictive info for aggregate future transmission statistics.",
                "supported": "Inconsistent with M1 (information absent) for tested aggregate targets.",
                "not_established": "M2, M3, event timing, or Stage8.1 hourly error cause.",
                "governance_status": "FROZEN"
            },
            {
                "phase": "Phase B",
                "question": "Are Stage8.1 point predictions positioned central to local causal state neighbours?",
                "population": "104 EVEN origins (604 daytime hours)",
                "main_result": "Normalized rank = 0.4459; Pinball loss Δ = +0.0209 (p < 0.0001, unclustered)",
                "demonstrated": "Champion point forecasts concentrate near 5-neighbour local median.",
                "supported": "Consistent with conditional-median / hedging behavior under L1/pinball loss.",
                "not_established": "Proof of M3, proof of event timing, or B3 threshold validation (B3 compromised).",
                "governance_status": "FROZEN"
            },
            {
                "phase": "Phase C-1",
                "question": "Does frozen P1 provide incremental OOF predictive info for individual transmission targets k(t+h) beyond P0?",
                "population": "104 EVEN origins (609 valid target cells)",
                "main_result": "GBDT ΔR² = +0.3037 to +0.7013 (p = 0.0010 at all horizons)",
                "demonstrated": "Frozen P1 contains extractable predictive info for individual hourly transmission targets k(t+h).",
                "supported": "Inconsistent with M1 for individual transmission targets.",
                "not_established": "Stage8.1 representation inadequacy, head failure, M2, M3, timing, or physical SW_IN MAE reduction.",
                "governance_status": "FROZEN"
            },
            {
                "phase": "Phase C-2",
                "question": "Can a downstream readout on frozen P1 extract predictive info for physical SW_IN(t+h) beyond P0?",
                "population": "104 EVEN origins (609 valid target cells)",
                "main_result": "GBDT ΔMAE = +19.51 to +63.05 W/m² (all 95% CIs exclude 0)",
                "demonstrated": "Frozen P1 contains extractable predictive info for physical SW_IN(t+h) beyond P0 under the specified GBDT readout.",
                "supported": "Information demonstrated in C-1 for k(t+h) transfers into physical irradiance prediction.",
                "not_established": "Stage8.1 representation failure, head failure, loss failure, M2, M3, timing, or ODD performance.",
                "governance_status": "FROZEN"
            }
        ],
        "resulting_scientific_question": "The unresolved problem is no longer whether frozen P1 contains useful extractable predictive information (Phase A, C-1, and C-2 establish that it does). The unresolved problem is WHICH MECHANISM explains why that information has not been demonstrated through the existing Stage8.1 forecasting system itself. M2, M3, and event timing remain competing unproven hypotheses.",
        "stage8_1_oof_limitation": "Direct paired OOF comparison with Stage8.1 is unavailable under existing frozen artifacts because no exact valid frozen Stage8.1 canonical GroupKFold OOF artifact exists. Reconstruction is strictly prohibited.",
        "next_step_governance": {
            "phase_a": "FROZEN / CLOSED",
            "phase_b": "FROZEN / CLOSED",
            "phase_c1": "FROZEN / CLOSED",
            "phase_c2": "FROZEN / CLOSED",
            "phase_c3_authorized": False,
            "odd_status": "SEALED (0 rows accessed)",
            "rules": [
                "No follow-up experiment automatically authorized.",
                "ODD firewall remains absolute.",
                "Any future experiment requires a separate design and explicit authorization.",
                "Future work must discriminate a specific mechanism rather than perform generic model/feature experimentation."
            ]
        },
        "artifact_hashes": hashes
    }

    synthesis_json_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"
    with open(synthesis_json_path, "w") as f:
        json.dump(synthesis_payload, f, indent=2)

    synthesis_md_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"
    with open(synthesis_md_path, "w") as f:
        f.write("# POLARIS — PHASE A + PHASE B + PHASE C-1 + PHASE C-2 SCIENTIFIC SYNTHESIS CHECKPOINT\n\n")
        f.write(f"**Date (UTC):** {synthesis_payload['timestamp_utc']}  \n")
        f.write("**Governance Status:** CONSOLIDATED SCIENTIFIC SYNTHESIS CHECKPOINT (ABC2)  \n")
        f.write("**Phases A, B, C-1, C-2 Status:** COMPLETE AND FROZEN  \n")
        f.write("**Phase C-3 Status:** NOT AUTHORIZED  \n")
        f.write("**ODD Status:** SEALED (0 rows accessed)  \n\n---\n\n")

        f.write("## 1. Executive Summary & Governance Record\n\n")
        f.write("This document provides the consolidated, forensically audited scientific synthesis checkpoint spanning **Phase A** (Information Probe), **Phase B** (Local Causal-State Diagnostics), **Phase C-1** (Horizon-Decomposed Transmission Diagnostic), and **Phase C-2** (Frozen P1 Physical SW_IN Diagnostic).\n\n")
        f.write("- **Phase A:** COMPLETE + FORENSICALLY AUDITED (Frozen)  \n")
        f.write("- **Phase B:** COMPLETE + FORENSICALLY AUDITED (Frozen)  \n")
        f.write("- **Phase C-1:** COMPLETE + FORENSICALLY AUDITED (Authoritative Corrected Execution, Frozen)  \n")
        f.write("- **Phase C-2:** COMPLETE + FORENSICALLY AUDITED (Authoritative Execution, Frozen)  \n")
        f.write("- **ODD Firewall:** SEALED (0 rows accessed)  \n")
        f.write("- **Phase C-3 Authorization:** NOT AUTHORIZED  \n\n---\n\n")

        f.write("## 2. Phase Summaries & Established Results\n\n")

        f.write("### Phase A — Information Probe\n")
        f.write("- **Population:** 104 eligible EVEN origins (604 daytime hours evaluated).\n")
        f.write("- **Inputs:** $P0$ (22 features) vs $P1$ (147 features).\n")
        f.write("- **Results:** $T1$ Volatility ($\Delta R^2 = +0.3098$, CI $[+0.0506, +0.5886]$), $T2$ Max Transition ($\Delta R^2 = +0.3052$, CI $[+0.0470, +0.5837]$), $T3$ Mean Transmission ($\Delta R^2 = +0.5988$, CI $[+0.3639, +0.8421]$), $T4$ Dropped/Unavailable.\n")
        f.write("- **Finding:** *M1 (information absent) is inconsistent with tested aggregate targets T1–T3. Frozen P1 contains nonlinear predictive information for aggregate future transmission statistics beyond P0.*\n\n")

        f.write("### Phase B — Local Causal-State Diagnostics\n")
        f.write("- **B1 Rank Diagnostic:** Champion point forecasts concentrate near the 5-neighbour local median (mean normalized rank $0.4459$, raw $2.2219/5$).\n")
        f.write("- **B2 Pinball Loss:** Champion $q=0.5$ loss ($0.1058$) is lower than crude 5-neighbour empirical median loss ($0.1267$, $\Delta = +0.0209$). *Dependence Caveat:* Reported $p < 0.0001$ treated 604 hourly observations as independent without origin clustering.\n")
        f.write("- **B3 Procedural Compromise:** B3 threshold was NOT frozen before computation. B3 is procedurally compromised and remains exploratory only.\n\n")

        f.write("### Phase C-1 — Horizon-Decomposed Transmission Diagnostic\n")
        f.write("- **Initial Execution:** Invalidated due to canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved as historical invalid artifact (`forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json`).\n")
        f.write("- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with PASS status (104 parent origins, 609 valid target cells).\n")
        f.write("- **Results ($k(t+h)$ GBDT $\Delta R^2$):** H7 ($+0.5146$), H8 ($+0.5317$), H9 ($+0.7013$), H10 ($+0.4718$), H11 ($+0.6373$), H12 ($+0.3037$). All 95% CIs exclude 0, permutation $p = 0.0010$ at all horizons.\n")
        f.write("- **Finding:** *Frozen P1 contains extractable predictive information for individual hourly transmission targets k(t+h) beyond P0.*\n\n")

        f.write("### Phase C-2 — Frozen P1 Physical SW_IN Diagnostic\n")
        f.write("- **Authoritative Execution:** Executed via `scratch/run_phase_c2_frozen_p1_physical_sw_in_diagnostic.py`, forensically audited with PASS status (15/15 checks).\n")
        f.write("- **Population & Targets:** 104 parent origins, 609 valid daytime target cells, physical $SW\\_IN(t+h)$ in $\\text{W/m}^2$.\n")
        f.write("- **Readout Specification:** $P0$ (22 features) vs $P1$ (147 features), GBDT (`max_depth=3`, `max_iter=200`, `learning_rate=0.05`, `min_samples_leaf=10`, `random_state=42`), canonical 5-fold OOF.\n")
        f.write("- **Results (Physical $SW\\_IN$ $\Delta MAE$ in $\\text{W/m}^2$):**\n")
        f.write("  - **H7:** $P0 \\text{ MAE} = 77.82$, $P1 \\text{ MAE} = 58.31$, $\\Delta MAE = \\mathbf{+19.51 \\text{ W/m}^2}$, 95% Bootstrap CI $[+5.28, +34.05]$, $\\Delta R^2 = +0.3203$\n")
        f.write("  - **H8:** $P0 \\text{ MAE} = 96.34$, $P1 \\text{ MAE} = 61.22$, $\\Delta MAE = \\mathbf{+35.12 \\text{ W/m}^2}$, 95% Bootstrap CI $[+20.96, +49.89]$, $\\Delta R^2 = +0.4858$\n")
        f.write("  - **H9:** $P0 \\text{ MAE} = 111.58$, $P1 \\text{ MAE} = 74.91$, $\\Delta MAE = \\mathbf{+36.67 \\text{ W/m}^2}$, 95% Bootstrap CI $[+19.56, +53.99]$, $\\Delta R^2 = +0.4435$\n")
        f.write("  - **H10:** $P0 \\text{ MAE} = 123.02$, $P1 \\text{ MAE} = 91.74$, $\\Delta MAE = \\mathbf{+31.28 \\text{ W/m}^2}$, 95% Bootstrap CI $[+12.21, +50.69]$, $\\Delta R^2 = +0.3627$\n")
        f.write("  - **H11:** $P0 \\text{ MAE} = 147.25$, $P1 \\text{ MAE} = 84.19$, $\\Delta MAE = \\mathbf{+63.05 \\text{ W/m}^2}$, 95% Bootstrap CI $[+44.24, +82.09]$, $\\Delta R^2 = +0.6550$\n")
        f.write("  - **H12:** $P0 \\text{ MAE} = 137.18$, $P1 \\text{ MAE} = 93.20$, $\\Delta MAE = \\mathbf{+43.99 \\text{ W/m}^2}$, 95% Bootstrap CI $[+25.28, +62.79]$, $\\Delta R^2 = +0.3782$\n")
        f.write("- **Inference & Audit:** 10,000 origin-level paired block bootstrap resamples, ordinary percentile CIs, 0 degenerate replicates. Permutation test removed due to statistical incoherence. Forensic audit **PASS**.\n\n---\n\n")

        f.write("## 3. Comprehensive Scientific Evidence Matrix\n\n")
        f.write("| Phase | Scientific Question | Data / Population | Main Result | What is DEMONSTRATED | What is SUPPORTED / CONSISTENT WITH | What remains NOT ESTABLISHED | Governance Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
        for row in synthesis_payload["scientific_evidence_matrix"]:
            f.write(f"| **{row['phase']}** | {row['question']} | {row['population']} | {row['main_result']} | {row['demonstrated']} | {row['supported']} | {row['not_established']} | **{row['governance_status']}** |\n")
        f.write("\n---\n\n")

        f.write("## 4. Evidence Chain Synthesis\n\n")
        f.write("1. **Phase A:** Established that frozen $P1$ contains nonlinear predictive information about aggregate future transmission statistics ($T1$–$T3$) beyond deterministic $P0$.\n")
        f.write("2. **Phase B:** Showed local causal-state diagnostics consistent with central positioning / conditional-median hedging under L1/pinball loss, but did not prove M3 or event timing.\n")
        f.write("3. **Phase C-1:** Demonstrated that the specified GBDT probe extracts incremental out-of-fold predictive information for individual normalized transmission targets $k(t+h)$ from $P1$ beyond $P0$.\n")
        f.write("4. **Phase C-2:** Demonstrated that the specified downstream GBDT readout also extracts incremental out-of-fold predictive information for physical surface solar irradiance $SW\\_IN(t+h)$ from $P1$ beyond $P0$, achieving positive $\\Delta MAE$ ($+19.51 \\text{ to } +63.05 \\text{ W/m}^2$) across all six horizons with bootstrap 95% CIs strictly excluding zero.\n\n---\n\n")

        f.write("## 5. Critical Scientific Boundary & Firewall Statements\n\n")
        f.write("Phase C-2 demonstrates extractable physical $SW\\_IN$ information in frozen $P1$ under the specified downstream GBDT readout.\n\n")
        f.write("It does **NOT** establish:\n")
        f.write("- Stage8.1 representation failure\n")
        f.write("- Stage8.1 readout head failure\n")
        f.write("- Loss-function failure\n")
        f.write("- Capacity limitations\n")
        f.write("- M2 (Model-Utilization Limitation)\n")
        f.write("- M3 (Point-Loss / Uncertainty Limitation)\n")
        f.write("- Event-timing uncertainty\n")
        f.write("- Out-of-distribution (ODD) performance improvements\n")
        f.write("- Superiority of any model on the official ODD benchmark\n\n")
        f.write("> **Direct Stage8.1 OOF Comparison Limitation:** Direct paired OOF comparison with Stage8.1 remains unavailable under existing frozen artifacts because no exact valid frozen Stage8.1 canonical GroupKFold OOF prediction artifact exists. Reconstruction is strictly prohibited.\n\n---\n\n")

        f.write("## 6. The Resulting Scientific Question\n\n")
        f.write("The unresolved problem is no longer whether frozen $P1$ contains useful extractable predictive information (Phase A, C-1, and C-2 establish that it does).\n\n")
        f.write("The unresolved problem is **WHICH MECHANISM** explains why that information has not been demonstrated through the existing Stage8.1 forecasting system itself.\n\n")
        f.write("M2, M3, and event timing remain competing, unproven hypotheses. No hypothesis is selected or ranked as the explanation prior to explicit mechanistic discrimination.\n\n---\n\n")

        f.write("## 7. Artifact Integrity & SHA-256 Provenance\n\n")
        f.write("### Authoritative Frozen Artifacts\n")
        f.write("| Artifact File | Description | SHA-256 Hash |\n")
        f.write("| :--- | :--- | :--- |\n")

        auth_files = [
            ("forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv", "Frozen Canonical Fold Assignments"),
            ("forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv", "Frozen Eligible EVEN Origins"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json", "Authoritative Corrected C-1 Results (JSON)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md", "Authoritative Corrected C-1 Results (MD)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json", "Authoritative Corrected C-1 Audit (JSON)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md", "Authoritative Corrected C-1 Audit (MD)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.json", "C-1 Correction & Closeout Record (JSON)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_CORRECTION_AND_CLOSEOUT.md", "C-1 Correction & Closeout Record (MD)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.json", "Authoritative C-2 Results (JSON)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.md", "Authoritative C-2 Results (MD)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.json", "Authoritative C-2 Audit (JSON)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md", "Authoritative C-2 Audit (MD)")
        ]
        for fn, desc in auth_files:
            f.write(f"| `{fn}` | {desc} | `{hashes[fn]}` |\n")

        f.write("\n### Historical Invalid Artifacts (Preserved Strictly for Auditability)\n")
        f.write("| Artifact File | Description | SHA-256 Hash |\n")
        f.write("| :--- | :--- | :--- |\n")

        hist_files = [
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json", "Initial Invalid C-1 Results (Range(5) loop defect)"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md", "Initial Invalid C-1 Report"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json", "Initial Invalid C-1 Audit"),
            ("forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md", "Initial Invalid C-1 Audit Report")
        ]
        for fn, desc in hist_files:
            f.write(f"| `{fn}` | {desc} | `{hashes[fn]}` |\n")

        f.write("\n---\n\n")

        f.write("## 8. Next-Step Governance\n\n")
        f.write("- **Phase A:** FROZEN / CLOSED  \n")
        f.write("- **Phase B:** FROZEN / CLOSED  \n")
        f.write("- **Phase C-1:** FROZEN / CLOSED  \n")
        f.write("- **Phase C-2:** FROZEN / CLOSED  \n")
        f.write("- **Phase C-3 Authorization:** NOT AUTHORIZED  \n")
        f.write("- **ODD Firewall:** SEALED (0 rows accessed)  \n\n")
        f.write("1. No follow-up experiment is automatically authorized.\n")
        f.write("2. The ODD firewall remains 100% absolute.\n")
        f.write("3. Any future scientific experiment requires a separate pre-registered design and explicit human authorization.\n")
        f.write("4. Future work must focus on discriminating a specific mechanism rather than performing generic model or feature experimentation.\n\n---\n\n")
        f.write("POLARIS PHASE A + PHASE B + PHASE C-1 + PHASE C-2 SYNTHESIS COMPLETE.\nNO SECONDARY ANALYSIS AUTHORIZED.\nODD REMAINS SEALED.\n")

    final_hashes = {
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json": sha256_file(synthesis_json_path),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md": sha256_file(synthesis_md_path)
    }

    print("\nCheckpoint Hashes:")
    print("Synthesis JSON Hash:", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"])
    print("Synthesis MD Hash:  ", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md"])

if __name__ == "__main__":
    create_abc2_synthesis()
