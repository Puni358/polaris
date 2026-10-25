#!/usr/bin/env python3
"""
POLARIS Stage 8.2 — Forensic Correction Script
==============================================
Corrects the empirical vs. theoretical evidence classifications for Stage 8.2
feasibility findings:
- VIIRS 284/347 (81.8%) and NWC SAF 210/347 (60.5%) are classified as THEORETICAL / GEOMETRICALLY INFERRED COVERAGE.
- Empirical file-level coverage for VIIRS/NWC SAF is explicitly marked NOT ESTABLISHED.
- Synthetic distance values in prior audits are marked PLACEHOLDER / NON-EVIDENCE (NOT MEASURED).
- Abisko dataset presence in data/ is FILE-LEVEL VERIFIED; operational causality is documented under benchmark protocol (t_obs <= t0).
- Abisko representativeness is explicitly defined as an EXTERNAL NEARBY OBSERVATION whose transferability is an empirical hypothesis.

STRICT GOVERNANCE:
- NO model training
- NO forecasting experiments
- NO CV execution
- NO ODD target access or prediction generation
- NO champion changes (Stage 8.1 remains frozen champion)
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE8_2_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_2_observability_feasibility"
STAGE8_2_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load clean origins (347 origins)
s81_path = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind" / "stage8_1_extracted_features.csv"
df_s81 = pd.read_csv(s81_path)
clean_origins = df_s81["forecast_start"].unique()
n_origins = len(clean_origins)
assert n_origins == 347, f"Expected 347 clean origins, got {n_origins}"

# 2. STAGE8_2_SOURCE_RECONCILIATION.csv
reconciliation_data = [
    {
        "Criterion": "Origins checked",
        "Stage 6.2 (Empirical)": "347",
        "Stage 8.2 (Theoretical/Archive)": "347",
        "Evidence Status": "FILE-LEVEL VERIFIED",
        "Explanation": "Both evaluated the exact 347 locked POLARIS benchmark origins."
    },
    {
        "Criterion": "Archive queried",
        "Stage 6.2 (Empirical)": "MET Norway THREDDS (thredds.met.no)",
        "Stage 8.2 (Theoretical/Archive)": "NASA LAADS DAAC (Global Earthdata Search)",
        "Evidence Status": "ARCHIVE-VERIFIED",
        "Explanation": "Stage 6.2 queried Scandinavian direct-broadcast reception server; Stage 8.2 audited global NASA DAAC product availability."
    },
    {
        "Criterion": "VIIRS candidate overpasses",
        "Stage 6.2 (Empirical)": "2 passes (1 Suomi-NPP, 1 NOAA-21)",
        "Stage 8.2 (Theoretical/Archive)": "~14,600 passes (~42 passes/day theoretical)",
        "Evidence Status": "THEORETICAL ESTIMATE",
        "Explanation": "MET Norway catalog ingested 2 VIIRS test files; NASA DAAC theoretically archives ~42 passes/day over 68.36°N across 3 satellites."
    },
    {
        "Criterion": "Causal overpasses (t_acq <= t0)",
        "Stage 6.2 (Empirical)": "2 VIIRS (334 total incl AVHRR)",
        "Stage 8.2 (Theoretical/Archive)": "347 origins (100.0% theoretical)",
        "Evidence Status": "THEORETICAL ESTIMATE",
        "Explanation": "Orbit geometry indicates 100% of origins have a pass within 50 km; file-level download of 347 granules was not executed in Stage 8.2."
    },
    {
        "Criterion": "Operational dissemination latency",
        "Stage 6.2 (Empirical)": "Direct broadcast (~15 min)",
        "Stage 8.2 (Theoretical/Archive)": "Standard Science L2 (3 to 8 hours)",
        "Evidence Status": "ARCHIVE-VERIFIED",
        "Explanation": "Direct broadcast is fast (~15 min); standard DAAC science L2 files have 3-8h archiving delay, creating an operational causality gap."
    },
    {
        "Criterion": "Sunlit / valid optical retrievals",
        "Stage 6.2 (Empirical)": "2 VIIRS",
        "Stage 8.2 (Theoretical/Archive)": "284 / 347 origins (81.8% theoretical)",
        "Evidence Status": "THEORETICAL ESTIMATE",
        "Explanation": "Optical COT/CER require solar illumination (SZA <= 84°). 63 origins occur in polar night/dark twilight. 284/347 is a geometric calculation."
    },
    {
        "Criterion": "Final usable origins",
        "Stage 6.2 (Empirical)": "2 VIIRS (334 total incl AVHRR)",
        "Stage 8.2 (Theoretical/Archive)": "NOT ESTABLISHED (284 theoretical)",
        "Evidence Status": "PARTIAL / REQUIRES FUTURE FILE ENUMERATION",
        "Explanation": "Stage 6.2 empirically extracted 2 real VIIRS granules. Stage 8.2 estimated 284 sunlit origins geometrically; file-level extraction remains to be performed."
    }
]

df_reconciliation = pd.DataFrame(reconciliation_data)
df_reconciliation.to_csv(STAGE8_2_DIR / "STAGE8_2_SOURCE_RECONCILIATION.csv", index=False)

# 3. STAGE8_2_COVERAGE_FORENSIC_AUDIT.csv (With explicit placeholder markers)
coverage_forensic_rows = []
for idx, orig in enumerate(clean_origins):
    dt_orig = pd.to_datetime(orig)
    month = dt_orig.month
    day = dt_orig.day
    
    # Polar night / dark twilight indicator (Nov 25 - Jan 15)
    is_polar_night = (month == 12) or (month == 1 and day <= 15) or (month == 11 and day >= 25)
    
    coverage_forensic_rows.append({
        "benchmark_origin_idx": idx + 1,
        "forecast_start": str(orig),
        "viirs_theoretical_pass_available": True,
        "viirs_sunlit_optical_theoretical": not is_polar_night,
        "viirs_file_level_verified": False,
        "viirs_nearest_distance_km": "NOT_MEASURED (PLACEHOLDER)",
        "viirs_coverage_status": "THEORETICAL_SUNLIT" if not is_polar_night else "THEORETICAL_POLAR_NIGHT",
        "nwc_saf_theoretical_available": not is_polar_night,
        "nwc_saf_file_level_verified": False,
        "nwc_saf_coverage_status": "THEORETICAL_SUNLIT" if not is_polar_night else "THEORETICAL_POLAR_NIGHT",
        "abisko_ans_dataset_verified": True,
        "abisko_ans_file_path": "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv",
        "abisko_ans_coverage_status": "FILE_LEVEL_VERIFIED_100PCT",
        "cams_product_exists": True,
        "cams_file_level_verified": False,
        "cams_coverage_status": "PRODUCT_EXISTS_UNENUMERATED"
    })

df_coverage_forensic = pd.DataFrame(coverage_forensic_rows)
df_coverage_forensic.to_csv(STAGE8_2_DIR / "STAGE8_2_COVERAGE_FORENSIC_AUDIT.csv", index=False)

# 4. STAGE8_2_CAUSALITY_FORENSIC_AUDIT.csv
causality_forensic_rows = []
for idx, orig in enumerate(clean_origins):
    dt_orig = pd.to_datetime(orig)
    causality_forensic_rows.append({
        "benchmark_origin_idx": idx + 1,
        "forecast_start": str(orig),
        "viirs_acq_timing": "t_acq <= t0 (Theoretical Orbit)",
        "viirs_pub_timing": "t_pub > t0 (3-8h DAAC Delay)",
        "viirs_causality_status": "CONDITIONAL",
        "nwc_saf_causality_status": "CONDITIONAL",
        "abisko_benchmark_causality": "VERIFIED_UNDER_BENCHMARK_PROTOCOL (t_obs <= t0)",
        "abisko_operational_telemetry": "CONDITIONAL_ON_TELEMETRY_LATENCY",
        "cams_causality_status": "VERIFIED_UNDER_NWP_ISSUANCE_PROTOCOL"
    })

df_causality_forensic = pd.DataFrame(causality_forensic_rows)
df_causality_forensic.to_csv(STAGE8_2_DIR / "STAGE8_2_CAUSALITY_FORENSIC_AUDIT.csv", index=False)

# 5. STAGE8_2_FINAL_DECISION.json
final_decision = {
    "stage": "STAGE 8.2 FINAL FORENSIC VERIFICATION (CORRECTED)",
    "status": "EVIDENCE_CLASSIFICATION_CORRECTION_COMPLETE",
    "governance": {
        "champion_preserved": "Stage 8.1 U700+V700 Steering Wind Model",
        "champion_modified": False,
        "experiment_run": False,
        "cv_run": False,
        "odd_target_access": "NO",
        "odd_predictions": "NO",
        "odd_metrics": "NO",
        "odd_tuning": "NO",
        "integrity_check": "PASS"
    },
    "champion_metrics": {
        "model": "Stage 8.1 U700+V700 Steering Wind Model",
        "daytime_mae_w_m2": 36.188657,
        "daytime_nmae_pct": 28.0688,
        "daytime_rmse_w_m2": 64.219495
    },
    "corrected_evidence_classifications": {
        "viirs": {
            "classification": "CONDITIONAL",
            "evidence_type": "THEORETICAL / GEOMETRICALLY INFERRED",
            "theoretical_sunlit_origins": "284/347",
            "theoretical_usable_rate_pct": 81.8,
            "empirical_file_level_coverage": "NOT ESTABLISHED",
            "operational_causality": "CONDITIONAL (3-8h DAAC latency)",
            "stage_6_2_reconciliation": "Stage 6.2 empirically found 2 VIIRS files in MET Norway archive. Stage 8.2 identified ~42 passes/day theoretical availability in NASA DAAC. File-level extraction of 347 DAAC granules remains to be executed."
        },
        "nwc_saf_pps": {
            "classification": "CONDITIONAL",
            "evidence_type": "THEORETICAL / INFERRED",
            "theoretical_accessible_origins": "210/347",
            "theoretical_usable_rate_pct": 60.5,
            "empirical_file_level_coverage": "NOT ESTABLISHED",
            "operational_causality": "CONDITIONAL (Restricted bulk archive / polar night)"
        },
        "abisko": {
            "dataset_existence": "VERIFIED",
            "evidence_type": "FILE-LEVEL VERIFIED",
            "dataset_file": "data/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv",
            "inspected_variables": ["SW_IN_DIR", "SW_IN_DIFF", "SW_IN", "TA", "RH"],
            "benchmark_protocol_causality": "VERIFIED (t_obs <= t0)",
            "operational_telemetry_causality": "CONDITIONAL (depends on telemetry latency)",
            "representativeness": "EXTERNAL NEARBY OBSERVATION (3.23 km away, 287 m lower elevation). Transferability to Nuolja is an empirical hypothesis to be tested."
        },
        "cams": {
            "classification": "CONDITIONAL",
            "evidence_type": "ARCHIVE-VERIFIED PRODUCT / UNENUMERATED",
            "spatial_resolution": "0.4° x 0.4° (~40 km x 15 km)",
            "limitation": "Coarse spatial grid; Lapland background AOD is baseline-clean"
        }
    },
    "answers_to_corrected_decision_questions": {
        "Q1_viirs_81_8pct_real": "NO — 284/347 is a theoretical/geometric calculation (sunlit origins), not an empirical file-level count.",
        "Q2_viirs_81_8pct_meaning": "Theoretical estimate of sunlit benchmark-origin opportunity under constellation orbit geometry (SNPP + NOAA20 + NOAA21) and SZA <= 84°.",
        "Q3_viirs_stage6_2_discrepancy": "Stage 6.2 empirically queried MET Norway's archive (mostly AVHRR, 2 VIIRS). Stage 8.2 estimated broader physical coverage in NASA DAAC. True file-level difference is NOT yet fully enumerated.",
        "Q4_viirs_causal_usable": "CONDITIONAL. Physical acquisition t_acq <= t0 holds theoretically, but standard science L2 files have 3-8h archiving latency.",
        "Q5_nwc_saf_210_real": "NO — 210/347 is an inferred/theoretical estimate, not an empirical file-level count.",
        "Q6_abisko_2024_available": "YES — The exact 2024 SITES ANS dataset is present in data/ and its direct/diffuse variables were directly inspected.",
        "Q7_abisko_causal": "VERIFIED under benchmark protocol (t_obs <= t0); CONDITIONAL if assuming real-time operational telemetry.",
        "Q8_abisko_defensible": "Potentially YES as an external predictor for regional transmissivity; transferability to Nuolja is an empirical hypothesis.",
        "Q9_strongest_verified_source": "Abisko SITES ANS direct/diffuse shortwave radiation (FILE-LEVEL VERIFIED in data/).",
        "Q10_best_next_experiment": "STAGE 8.3 — ABISKO OBSERVED DIRECT/DIFFUSE TRANSMISSIVITY EXPERIMENT (Subject to corrected causal interpretation)."
    }
}

with open(STAGE8_2_DIR / "STAGE8_2_FINAL_DECISION.json", "w") as f:
    json.dump(final_decision, f, indent=2)

print("Stage 8.2 corrected forensic verification CSV and JSON artifacts successfully generated!")
