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

def build_synthesis():
    print("==================================================")
    print("BUILDING SCIENTIFIC SYNTHESIS CHECKPOINT ARTIFACTS")
    print("==================================================")
    
    artifacts = {
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.json"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_RESULTS.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_A_FORENSIC_INTEGRITY_AUDIT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_A_FORENSIC_INTEGRITY_AUDIT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_A_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_A_FORENSIC_INTEGRITY_AUDIT.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_B_HEDGING_DIAGNOSTIC.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_B_HEDGING_DIAGNOSTIC.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_B_HEDGING_DIAGNOSTIC.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_B_HEDGING_DIAGNOSTIC.md"),
        "forecasting/reports/information_probe_and_causal/PHASE_B_FORENSIC_INTEGRITY_AUDIT.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_B_FORENSIC_INTEGRITY_AUDIT.json"),
        "forecasting/reports/information_probe_and_causal/PHASE_B_FORENSIC_INTEGRITY_AUDIT.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/PHASE_B_FORENSIC_INTEGRITY_AUDIT.md"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_FREEZE_RECORD.json": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_FREEZE_RECORD.json"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_FREEZE_RECORD.md": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_FREEZE_RECORD.md"),
        "forecasting/reports/candidates/T4_RECONSTRUCTION_BLOCKER.md": sha256_file(BASE_DIR / "forecasting/reports/candidates/T4_RECONSTRUCTION_BLOCKER.md"),
        "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv": sha256_file(BASE_DIR / "forecasting/reports/stage8/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv"),
        "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_OOF_PREDICTIONS.csv": sha256_file(BASE_DIR / "forecasting/reports/information_probe_and_causal/INFORMATION_PROBE_OOF_PREDICTIONS.csv")
    }
    
    payload = {
        "checkpoint_name": "POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "purpose": "Consolidated scientific synthesis of audited Phase A and Phase B findings",
        "governance_status": {
            "phase_a": "COMPLETE_AND_FORENSICALLY_AUDITED",
            "phase_b": "COMPLETE_AND_FORENSICALLY_AUDITED",
            "b3_procedural_status": "PROCEDURALLY_COMPROMISED_EXPLORATORY_ONLY",
            "t4_status": "DROPPED_UNAVAILABLE",
            "section_9_decision_rule": "ORIGINAL_2_OF_4_RULE_UNCHANGED",
            "odd_firewall": "SEALED_0_ROWS_ACCESSED",
            "phase_c_authorization": "NOT_AUTHORIZED"
        },
        "phase_a_summary": {
            "total_even_origins": 174,
            "eligible_even_origins": 104,
            "excluded_even_origins": 70,
            "daytime_hours_evaluated": 604,
            "p0_feature_count": 22,
            "p1_feature_count": 147,
            "gbdt_results": {
                "T1_volatility": {"delta_R2": 0.309826, "bootstrap_95ci": [0.0506, 0.5886]},
                "T2_max_transition": {"delta_R2": 0.305179, "bootstrap_95ci": [0.0470, 0.5837]},
                "T3_mean_kt": {"delta_R2": 0.598801, "bootstrap_95ci": [0.3639, 0.8421]}
            },
            "established_m1_finding": "M1 (information absent) is inconsistent with the tested targets. The frozen Stage8.1 causal state contains nonlinear predictive information about the tested future H7-H12 transmission statistics beyond the deterministic P0 state."
        },
        "phase_b_summary": {
            "b1_rank": {"mean_normalized_rank": 0.4459, "mean_raw_rank": 2.2219},
            "b2_pinball_loss": {
                "champion_q05_loss": 0.105774,
                "neighbour_median_q05_loss": 0.126686,
                "difference": 0.020912,
                "win_rate_pct": 42.88,
                "p_value": 0.000001,
                "dependence_caveat": "The reported p < 0.0001 treats all 604 hourly observations as independent, rather than accounting for origin-level clustering across the 104 origins."
            },
            "b3_procedural_limitation": "The B3 combined threshold (B > 0.555 OR range > 0.40) was NOT demonstrably fixed in a frozen artifact prior to Phase B computation. B3 is procedurally compromised as confirmatory evidence and remains exploratory only. The 82.78% prevalence and 1.09x MAE elevation are descriptive associations, not confirmed physical or causal properties."
        },
        "demonstrated_supported_unresolved": {
            "A_demonstrated": [
                "P1 contains substantial nonlinear predictive information about targets T1-T3.",
                "M1 (information absent) is inconsistent with the tested targets.",
                "The champion point forecasts have a mean normalized rank of 0.4459 within the tested five-neighbour ensembles.",
                "Champion q=.5 pinball loss (0.1058) is lower than the crude five-neighbour empirical median loss (0.1267).",
                "B3 provides an exploratory association between the implemented high-spread/bimodal classification and elevated MAE, subject to its procedural limitation."
            ],
            "B_supported_consistent_with": [
                "Conditional-median hedging is a plausible explanation for part of the point-forecast behavior.",
                "The observed local-neighbour diagnostics are consistent with multiple locally plausible future transmission outcomes.",
                "Point-MAE optimization may fail to express some of the information available in the causal state.",
                "Representation and loss/uncertainty limitations may both contribute to point forecast error."
            ],
            "C_not_established": [
                "M3 is not proven.",
                "M2 is not ruled out.",
                "M2 and M3 are not mutually resolved.",
                "Bimodality is not established as a physical population property.",
                "Bimodality has not been shown to cause MAE elevation.",
                "Distributional forecasting has not been shown to improve SW_IN point MAE.",
                "Any ODD improvement remains completely untested.",
                "Exact cloud-event timing remains unresolved.",
                "Phase A does not demonstrate that the information can be converted into better 24-hour point forecasts.",
                "B1 proximity to a central rank does not prove conditional-median behavior.",
                "B2 p < 0.0001 must not be interpreted as fully origin-independent evidence because it treated nested hourly observations as independent."
            ]
        },
        "artifact_hashes": artifacts
    }
    
    out_json = BASE_DIR / "forecasting/reports/information_probe_and_causal/POLARIS_PHASE_AB_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json"
    with open(out_json, "w") as f:
        json.dump(payload, f, indent=2)
        
    print(f"Synthesis JSON saved to {out_json}")

if __name__ == "__main__":
    build_synthesis()
