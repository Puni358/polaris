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

def create_final_closeout_checkpoint():
    print("==================================================")
    print("BUILDING POLARIS POST-ABC2 MECHANISM IDENTIFICATION LIMIT CHECKPOINT")
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
        "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md"),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"),
        "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md")
    }

    closeout_payload = {
        "artifact_name": "POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "governance_status": "POLARIS PROJECT MECHANISM DISCRIMINATION CLOSED UNDER CURRENT GOVERNANCE",
        "odd_firewall": "SEALED_0_ROWS_ACCESSED",
        "summary_of_evidence": {
            "signal_existence": "DEMONSTRATED — Frozen P1 contains nonlinear predictive information extractable by GBDT for aggregate transmission (Phase A), individual hourly transmission k(t+h) (Phase C-1), and physical SW_IN(t+h) irradiance (Phase C-2).",
            "mechanism_identification": "UNIDENTIFIED — Direct observational discrimination among M2 (Readout/Model Utilization), M3 (Point-Loss/Uncertainty), and Event-Timing Uncertainty is NOT IDENTIFIABLE under current frozen artifacts, protocols, and permitted information sources.",
            "c3_temporal_aggregation_status": "REJECTED_AS_NON_IDENTIFYING — Target aggregation changes task difficulty and variance; cannot uniquely discriminate M2 vs Event-Timing.",
            "c3_direct_timing_audit_status": "NON_DISCRIMINATING — Timing targets do not resolve whether Stage8.1 error gap was caused by timing uncertainty vs model/loss limitations.",
            "stage8_1_oof_limitation": "Direct paired OOF comparison unavailable because Stage8.1 champion lacks canonical GroupKFold EVEN OOF prediction artifact. Reconstruction is strictly prohibited."
        },
        "evidence_matrix": [
            {
                "phase": "Phase A",
                "question": "Does frozen P1 contain incremental predictive info for aggregate future transmission statistics beyond P0?",
                "main_result": "GBDT ΔR² = +0.305 to +0.599 across T1-T3 (p < 0.0001)",
                "demonstrated": "P1 contains substantial nonlinear predictive info for aggregate future transmission statistics.",
                "supported": "Inconsistent with M1 (information absent) for tested aggregate targets.",
                "not_established": "M2, M3, event timing, or Stage8.1 hourly error cause.",
                "governance_status": "FROZEN / CLOSED"
            },
            {
                "phase": "Phase B",
                "question": "Are Stage8.1 point predictions positioned central to local causal state neighbours?",
                "main_result": "Normalized rank = 0.4459; Pinball loss Δ = +0.0209 (p < 0.0001, unclustered)",
                "demonstrated": "Champion point forecasts concentrate near 5-neighbour local median.",
                "supported": "Consistent with conditional-median / hedging behavior under L1/pinball loss.",
                "not_established": "Proof of M3, proof of event timing, or B3 threshold validation (B3 compromised).",
                "governance_status": "FROZEN / CLOSED"
            },
            {
                "phase": "Phase C-1",
                "question": "Does frozen P1 provide incremental OOF predictive info for individual transmission targets k(t+h) beyond P0?",
                "main_result": "GBDT ΔR² = +0.3037 to +0.7013 (p = 0.0010 at all horizons)",
                "demonstrated": "Frozen P1 contains extractable predictive info for individual hourly transmission targets k(t+h).",
                "supported": "Inconsistent with M1 for individual transmission targets.",
                "not_established": "Stage8.1 representation inadequacy, head failure, M2, M3, timing, or physical SW_IN MAE reduction.",
                "governance_status": "FROZEN / CLOSED"
            },
            {
                "phase": "Phase C-2",
                "question": "Can a downstream readout on frozen P1 extract predictive info for physical SW_IN(t+h) beyond P0?",
                "main_result": "GBDT ΔMAE = +19.51 to +63.05 W/m² (all 95% CIs exclude 0)",
                "demonstrated": "Frozen P1 contains extractable predictive info for physical SW_IN(t+h) beyond P0 under specified GBDT readout.",
                "supported": "Information demonstrated in C-1 for k(t+h) transfers into physical irradiance prediction.",
                "not_established": "Stage8.1 representation failure, head failure, loss failure, M2, M3, timing, or ODD performance.",
                "governance_status": "FROZEN / CLOSED"
            },
            {
                "phase": "C-3 Audit",
                "question": "Can M2, M3, and Event-Timing be observationally discriminated using current frozen artifacts?",
                "main_result": "Hard Identification Limit Encountered",
                "demonstrated": "Signal existence is proven, but mechanism discrimination is non-identifiable under current frozen artifacts.",
                "supported": "Confirms necessity of explicit governance amendments for any future mechanism-attribution work.",
                "not_established": "Unique causal mechanism explaining Stage8.1 performance gap.",
                "governance_status": "CLOSED / REJECTED AS NON-IDENTIFYING"
            }
        ],
        "final_contribution_statement": [
            "1. Systematically evaluated the solar irradiance forecasting problem under a locked, causally rigorous benchmark.",
            "2. Evaluated candidate information sources and baseline architectures across canonical 5-fold cross-validation.",
            "3. Demonstrated that the frozen Stage8.1 causal state P1 contains substantial extractable predictive information for aggregate transmission and individual hourly targets.",
            "4. Showed that this predictive information is recoverable by a specified downstream GBDT readout for both normalized transmission index k(t+h) and physical surface irradiance SW_IN(t+h) (Phase C-2 ΔMAE +19.51 to +63.05 W/m²).",
            "5. Established that available empirical evidence does NOT identify the specific mechanism (M2, M3, or Event-Timing) responsible for the performance discrepancy with the original Stage8.1 system.",
            "6. Identified the absence of a canonical GroupKFold Stage8.1 OOF prediction artifact as a hard identification limitation for direct paired attribution.",
            "7. Maintained 100% strict Out-of-Distribution (ODD) data isolation throughout the entire research and diagnostic program (0 rows accessed)."
        ],
        "closed_routes": [
            "Generic neural-network experimentation",
            "Arbitrary GBDT/model variants",
            "Feature sweeps",
            "Hyperparameter sweeps",
            "Additional spatial/NWP/satellite feature searches",
            "Temporal aggregation as a mechanism test",
            "Direct timing probes that cannot discriminate mechanisms",
            "Stage8.1 OOF reconstruction",
            "ODD experimentation"
        ],
        "authoritative_hashes": hashes
    }

    json_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.json"
    with open(json_path, "w") as f:
        json.dump(closeout_payload, f, indent=2)

    md_path = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.md"
    with open(md_path, "w") as f:
        f.write("# POLARIS — POST-ABC2 MECHANISM IDENTIFICATION LIMIT CHECKPOINT & SCIENTIFIC CLOSEOUT\n\n")
        f.write(f"**Date (UTC):** {closeout_payload['timestamp_utc']}  \n")
        f.write("**Governance Status:** FINAL SCIENTIFIC CLOSEOUT & IDENTIFICATION LIMIT CHECKPOINT  \n")
        f.write("**Phases A, B, C-1, C-2 Status:** COMPLETE, FORENSICALLY AUDITED, AND FROZEN  \n")
        f.write("**C-3 Status:** REJECTED AS NON-IDENTIFYING / NOT AUTHORIZED  \n")
        f.write("**ODD Status:** SEALED (0 rows accessed)  \n\n---\n\n")

        f.write("## 1. Final Scientific State: Signal Existence vs. Mechanism Identification\n\n")
        f.write("The POLARIS research project has established a rigorous, forensically audited evidence chain across four completed phases:\n\n")
        f.write("- **Phase A:** $P1 \\to \\text{GBDT} \\to \\text{Aggregate Future Transmission } (T1, T2, T3)$\n")
        f.write("  - *Result:* Demonstrated nonlinear predictive information in $P1$ beyond $P0$ ($p < 0.0001$).\n")
        f.write("- **Phase C-1:** $P1 \\to \\text{GBDT} \\to k(t+h) \\text{ Transmission Index } (H7\\text{--}H12)$\n")
        f.write("  - *Result:* Demonstrated incremental out-of-fold predictive information for individual transmission targets ($p = 0.0010$).\n")
        f.write("- **Phase C-2:** $P1 \\to \\text{GBDT} \\to \\text{Physical } SW\\_IN(t+h) \\text{ Irradiance } (H7\\text{--}H12)$\n")
        f.write("  - *Result:* Demonstrated incremental out-of-fold predictive information for physical irradiance across all six horizons ($\\Delta MAE = +19.51 \\text{ to } +63.05 \\text{ W/m}^2$, all 95% CIs exclude 0).\n\n")
        f.write("> **Authoritative Core Finding:** *Useful predictive information exists in the frozen P1 causal state and is extractable under the specified downstream GBDT readout for both normalized transmission and physical surface irradiance.*\n\n")
        f.write("### Critical Distinction\n")
        f.write("$$\\text{Signal Existence / Extractability} \\quad \\neq \\quad \\text{Mechanism Identification}$$\n\n")
        f.write("The evidence proves that $P1$ contains extractable predictive information, but it **does NOT identify the mechanism** explaining why that information was not previously demonstrated through the Stage8.1 forecasting system itself.\n\n---\n\n")

        f.write("## 2. What ABC2 Does NOT Identify\n\n")
        f.write("The successful GBDT probe results in Phase C-1 and C-2 do **NOT** establish:\n")
        f.write("- Stage8.1 representation failure\n")
        f.write("- Stage8.1 readout-head failure\n")
        f.write("- Loss-function failure\n")
        f.write("- Capacity limitations\n")
        f.write("- **M2** (Model/Readout Utilization Limitation)\n")
        f.write("- **M3** (Point-Estimation / Uncertainty Limitation)\n")
        f.write("- **Event-Timing Uncertainty** as the cause of Stage8.1's performance gap\n")
        f.write("- Superiority on the official Out-of-Distribution (ODD) benchmark\n\n")
        f.write("The GBDT probes and Stage8.1 are distinct modeling systems with different architectures, objectives, losses, optimization procedures, and training dynamics. Probe extractability cannot be converted into a claim of Stage8.1 architectural failure.\n\n---\n\n")

        f.write("## 3. Signal Existence $\\neq$ Mechanism Identification\n\n")
        f.write("$$\\text{P1 contains info} \\implies \\text{GBDT extracts info} \\implies \\text{Info transfers to physical } SW\\_IN \\implies \\mathbf{Mechanism \\, Unidentified}$$\n\n")
        f.write("The competing candidate mechanisms remain:\n")
        f.write("1. **M2 — Model / Readout Utilization Limitation:** Downstream head, loss, or optimization under-extracts represented state info.\n")
        f.write("2. **M3 — Point-Estimation / Uncertainty Limitation:** Distributional/hedging dynamics under L1 loss obscure expected point error reduction.\n")
        f.write("3. **Event-Timing Uncertainty:** Cloud transition timing phase noise limits instantaneous 1-hour point error reduction.\n\n")
        f.write("None of these hypotheses are ranked, selected, or proven under the current evidence.\n\n---\n\n")

        f.write("## 4. Rejection of C-3 Temporal Aggregation & Direct Timing Probes\n\n")
        f.write("### C-3 Temporal Aggregation Rejection\n")
        f.write("The proposed *Temporal Window Aggregation Diagnostic* is formally **REJECTED AS NON-IDENTIFYING**. Target aggregation changes regression difficulty, target variance, and signal-to-noise ratio. Both M2 and Event-Timing Uncertainty predict greater relative improvement on aggregated targets; therefore, temporal aggregation cannot uniquely discriminate between them.\n\n")
        f.write("### Direct Timing Target Audit Rejection\n")
        f.write("Direct timing targets (e.g., $h^* = \\text{argmin}_h k(t+h)$) evaluate whether transition timing is extractable from $P1$. However, successful or unsuccessful timing prediction does not establish whether timing uncertainty was the causal mechanism responsible for Stage8.1's point forecast gap.\n\n---\n\n")

        f.write("## 5. Precise Identification-Limit Statement\n\n")
        f.write("> **\"Direct observational discrimination among M2 (Model/Readout Utilization), M3 (Point-Loss/Uncertainty), and Event-Timing Uncertainty is not identifiable under the current frozen POLARIS artifacts, protocols, and permitted information sources.\"**\n\n")
        f.write("*Note: This statement defines a limitation of the current frozen artifacts and protocols. It does not make an unproven universal claim about all conceivable future experiments under potential future governance amendments.*\n\n---\n\n")

        f.write("## 6. Hard Limitation: Missing Stage8.1 OOF Artifact\n\n")
        f.write("The official Stage8.1 champion model was fit on all 174 EVEN origins and lacks an exact valid 5-fold canonical GroupKFold EVEN OOF prediction artifact.\n")
        f.write("- Direct paired Stage8.1 OOF comparison is **unavailable**.\n")
        f.write("- Stage8.1 OOF reconstruction is **prohibited**.\n")
        f.write("- In-sample Stage8.1 predictions **cannot substitute** for OOF predictions.\n")
        f.write("- No synthetic or approximate Stage8.1 OOF artifact may be created.\n\n---\n\n")

        f.write("## 7. Final Evidence Matrix\n\n")
        f.write("| Phase | Question | Main Result | What is DEMONSTRATED | What is SUPPORTED / CONSISTENT WITH | What remains NOT ESTABLISHED | Governance Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :---: |\n")
        for row in closeout_payload["evidence_matrix"]:
            f.write(f"| **{row['phase']}** | {row['question']} | {row['main_result']} | {row['demonstrated']} | {row['supported']} | {row['not_established']} | **{row['governance_status']}** |\n")
        f.write("\n---\n\n")

        f.write("## 8. Final Contribution Statement\n\n")
        for stmt in closeout_payload["final_contribution_statement"]:
            f.write(f"{stmt}\n")
        f.write("\n---\n\n")

        f.write("## 9. Future-Work Boundary & Closed Routes\n\n")
        f.write("Future work may theoretically revisit mechanism discrimination **only through a new, explicit governance amendment** that demonstrates a mathematically valid, non-confounded controlled comparison.\n\n")
        f.write("The following routes are **EXPLICITLY CLOSED** under current governance:\n")
        for route in closeout_payload["closed_routes"]:
            f.write(f"- {route}\n")
        f.write("\n---\n\n")

        f.write("## 10. Authoritative Artifact Provenance & SHA-256 Hashes\n\n")
        f.write("### Authoritative Project Artifacts\n")
        f.write("| Artifact File | SHA-256 Hash |\n")
        f.write("| :--- | :--- |\n")
        for fn, h in hashes.items():
            if "HISTORICAL" not in fn and "C1_HORIZON_DIAGNOSTIC.j" not in fn and "C1_HORIZON_DIAGNOSTIC.m" not in fn:
                f.write(f"| `{fn}` | `{h}` |\n")

        f.write("\n### Historical Invalid Artifacts (Preserved Strictly for Auditability)\n")
        f.write("| Artifact File | SHA-256 Hash |\n")
        f.write("| :--- | :--- |\n")
        for fn in ["forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.json", "forecasting/reports/information_probe_and_causal/PHASE_C1_HORIZON_DIAGNOSTIC.md", "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json", "forecasting/reports/information_probe_and_causal/PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md"]:
            f.write(f"| `{fn}` | `{hashes[fn]}` |\n")

        f.write("\n---\n\n")
        f.write("POST-ABC2 MECHANISM IDENTIFICATION LIMIT = FROZEN.\n")
        f.write("C-3 TEMPORAL AGGREGATION = REJECTED AS NON-IDENTIFYING.\n")
        f.write("NO EXPERIMENT EXECUTED.\n")
        f.write("ABC2 REMAINS FROZEN.\n")
        f.write("ODD REMAINS SEALED.\n")
        f.write("MECHANISM-DISCRIMINATION WORK = CLOSED UNDER CURRENT GOVERNANCE.\n")
        f.write("AWAITING HUMAN DECISION ON ANY FUTURE GOVERNANCE AMENDMENT.\n")

    final_hashes = {
        "forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.json": sha256_file(json_path),
        "forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.md": sha256_file(md_path)
    }

    print("\nFinal Closeout Checkpoint Hashes:")
    print("Closeout JSON Hash:", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.json"])
    print("Closeout MD Hash:  ", final_hashes["forecasting/reports/information_probe_and_causal/POLARIS_POST_ABC2_MECHANISM_IDENTIFICATION_LIMIT_CHECKPOINT.md"])

if __name__ == "__main__":
    create_final_closeout_checkpoint()
