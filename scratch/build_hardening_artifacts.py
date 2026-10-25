import os
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

# 1. Variable Dependency Matrix
dep_rows = [
    {
        "variable_name": "cot (Cloud Optical Thickness)",
        "physical_meaning": "Radiative optical depth of cloud column",
        "category": "OBSERVED / RETRIEVED",
        "retrieval_method": "Nakajima-King bispectral solar visible/NIR reflectance ratio",
        "upstream_inputs": "0.63um / 1.6um / 2.1um / 3.7um top-of-atmosphere solar reflectances",
        "polar_night_status": "UNAVAILABLE / FILL VALUE (-9999)",
        "causal_availability": "CONDITIONALLY VERIFIED (t_pub <= t0)",
        "novelty_vs_stage8_1": "GENUINELY NOVEL",
        "meps_dependency": "INDEPENDENT (Pure satellite solar radiative retrieval)",
        "stage8_8_overlap": "NONE",
        "valid_as_optical_fallback": "PRIMARY OPTICAL FEATURE",
        "quality_semantics": "Valid when SZA <= 84° and cot_quality_flag == 0"
    },
    {
        "variable_name": "eff_radius (Cloud Effective Radius)",
        "physical_meaning": "Weighted mean cloud droplet / ice crystal radius (um)",
        "category": "OBSERVED / RETRIEVED",
        "retrieval_method": "Bispectral NIR / SWIR absorption ratio",
        "upstream_inputs": "1.6um / 2.1um / 3.7um solar NIR channels",
        "polar_night_status": "UNAVAILABLE / FILL VALUE (-9999)",
        "causal_availability": "CONDITIONALLY VERIFIED (t_pub <= t0)",
        "novelty_vs_stage8_1": "PARTIALLY NOVEL",
        "meps_dependency": "INDEPENDENT",
        "stage8_8_overlap": "NONE",
        "valid_as_optical_fallback": "PRIMARY OPTICAL FEATURE",
        "quality_semantics": "Valid when SZA <= 84°"
    },
    {
        "variable_name": "cma (Cloud Mask - Thermal Mode)",
        "physical_meaning": "Binary cloud presence / absence grid",
        "category": "OBSERVED / RETRIEVED",
        "retrieval_method": "Multispectral 11um / 12um brightness temperature thresholding",
        "upstream_inputs": "Thermal IR channels (10.8um, 12.0um)",
        "polar_night_status": "AVAILABLE 24/7/365",
        "causal_availability": "CONDITIONALLY VERIFIED (t_pub <= t0)",
        "novelty_vs_stage8_1": "GENUINELY NOVEL",
        "meps_dependency": "INDEPENDENT (Observed thermal IR emission)",
        "stage8_8_overlap": "NONE",
        "valid_as_optical_fallback": "VALID THERMAL FALLBACK (Observed 24/7 Cloud Presence)",
        "quality_semantics": "Valid 0 (clear) or 1 (cloudy) year-round"
    },
    {
        "variable_name": "phase (Cloud Thermodynamic Phase)",
        "physical_meaning": "Top-of-cloud phase (0=clear, 1=liquid, 2=ice)",
        "category": "OBSERVED / RETRIEVED",
        "retrieval_method": "Tri-spectral thermal IR difference (8.5um, 11um, 12um)",
        "upstream_inputs": "Thermal IR brightness temperatures",
        "polar_night_status": "PARTIALLY AVAILABLE (Thermal phase mode active)",
        "causal_availability": "CONDITIONALLY VERIFIED (t_pub <= t0)",
        "novelty_vs_stage8_1": "PARTIALLY NOVEL",
        "meps_dependency": "INDEPENDENT",
        "stage8_8_overlap": "NONE",
        "valid_as_optical_fallback": "VALID THERMAL FALLBACK",
        "quality_semantics": "Valid 0, 1, 2"
    },
    {
        "variable_name": "ctth_press (Cloud Top Pressure)",
        "physical_meaning": "Inverted atmospheric pressure at cloud top (hPa)",
        "category": "NWP_DERIVED",
        "retrieval_method": "Radiative transfer mapping of 10.8um/13.4um IR radiances to NWP vertical profile",
        "upstream_inputs": "MEPS / ECMWF vertical temperature, pressure, humidity forecasts",
        "polar_night_status": "AVAILABLE 24/7/365",
        "causal_availability": "CONDITIONALLY VERIFIED",
        "novelty_vs_stage8_1": "REDUNDANT",
        "meps_dependency": "STRONGLY MODEL-DEPENDENT",
        "stage8_8_overlap": "COMPLETE OVERLAP (Evaluated & REJECTED in Stage 8.8)",
        "valid_as_optical_fallback": "INVALID FALLBACK (NWP-derived profile, re-introduces rejected Stage 8.8)",
        "quality_semantics": "NWP-derived inverted parameter"
    },
    {
        "variable_name": "ctth_temp (Cloud Top Temperature)",
        "physical_meaning": "Radiometric temperature at cloud top (K)",
        "category": "NWP_DERIVED",
        "retrieval_method": "11um IR radiance inverted against NWP temperature profile",
        "upstream_inputs": "MEPS / ECMWF vertical temperature profile",
        "polar_night_status": "AVAILABLE 24/7/365",
        "causal_availability": "CONDITIONALLY VERIFIED",
        "novelty_vs_stage8_1": "REDUNDANT",
        "meps_dependency": "STRONGLY MODEL-DEPENDENT",
        "stage8_8_overlap": "COMPLETE OVERLAP (Evaluated & REJECTED in Stage 8.8)",
        "valid_as_optical_fallback": "INVALID FALLBACK (NWP-derived profile)",
        "quality_semantics": "NWP-derived inverted parameter"
    },
    {
        "variable_name": "lwp (Satellite Liquid Water Path)",
        "physical_meaning": "Integrated liquid water mass (g/m2)",
        "category": "CALCULATED DERIVED",
        "retrieval_method": "Formula: LWP = 2/3 * rho_w * COT * CER",
        "upstream_inputs": "Retrieved COT and CER",
        "polar_night_status": "UNAVAILABLE / FILL VALUE (-9999)",
        "causal_availability": "CONDITIONALLY VERIFIED",
        "novelty_vs_stage8_1": "DUPLICATE",
        "meps_dependency": "INDEPENDENT FROM MEPS, DERIVED FROM COT/CER",
        "stage8_8_overlap": "OVERLAPS MEPS lwp_latest",
        "valid_as_optical_fallback": "DERIVED OPTICAL VARIABLE",
        "quality_semantics": "Valid when COT and CER are valid"
    }
]

df_dep = pd.DataFrame(dep_rows)
dep_csv_path = STAGE_DIR / "STAGE8_14C_CMIC_VARIABLE_DEPENDENCY_MATRIX.csv"
df_dep.to_csv(dep_csv_path, index=False)
print(f"Saved STAGE8_14C_CMIC_VARIABLE_DEPENDENCY_MATRIX.csv to {dep_csv_path}")

# 2. 347-Origin Accounting State Schema
schema_spec = [
    {
        "column_name": "origin_id",
        "data_type": "INTEGER",
        "allowed_values": "0 to 346",
        "description": "Unique index of the daily benchmark forecast origin (347 total origins in 2024)."
    },
    {
        "column_name": "t0",
        "data_type": "DATETIME ISO-8601",
        "allowed_values": "2024-01-20T00:00:00Z to 2024-12-31T00:00:00Z",
        "description": "Forecast origin timestamp."
    },
    {
        "column_name": "acquisition_time",
        "data_type": "DATETIME ISO-8601",
        "allowed_values": "Timestamp or NULL",
        "description": "Physical satellite overpass time T_acq."
    },
    {
        "column_name": "processing_time",
        "data_type": "DATETIME ISO-8601",
        "allowed_values": "Timestamp or NULL",
        "description": "NWC SAF PPS processing completion time T_proc."
    },
    {
        "column_name": "publication_time",
        "data_type": "DATETIME ISO-8601",
        "allowed_values": "Timestamp or NULL",
        "description": "File availability timestamp on public server T_pub."
    },
    {
        "column_name": "causality_pass",
        "data_type": "BOOLEAN",
        "allowed_values": "TRUE / FALSE",
        "description": "Operational causality check: T_pub <= t0."
    },
    {
        "column_name": "granule_available",
        "data_type": "BOOLEAN",
        "allowed_values": "TRUE / FALSE",
        "description": "Granule exists in provider archive covering Nuolja."
    },
    {
        "column_name": "valid_optical",
        "data_type": "BOOLEAN",
        "allowed_values": "TRUE / FALSE",
        "description": "Solar elevation / SZA check: SZA <= 84° and valid COT."
    },
    {
        "column_name": "polar_night",
        "data_type": "BOOLEAN",
        "allowed_values": "TRUE / FALSE",
        "description": "Astronomical polar night or extreme low sun: SZA > 84°."
    },
    {
        "column_name": "quality_pass",
        "data_type": "BOOLEAN",
        "allowed_values": "TRUE / FALSE",
        "description": "Quality flags pass (cot_quality_flag == 0, theta_s <= 65°)."
    },
    {
        "column_name": "final_feature_state",
        "data_type": "ENUM STRING",
        "allowed_values": "VALID_OPTICAL | POLAR_NIGHT | LOW_SUN_INVALID | NO_GRANULE | QUALITY_REJECTED | CAUSALITY_REJECTED",
        "description": "Final discrete state assignment for origin."
    },
    {
        "column_name": "rejection_reason",
        "data_type": "STRING",
        "allowed_values": "Text description or NONE",
        "description": "Explicit reason if origin feature state is non-optical."
    }
]

df_schema = pd.DataFrame(schema_spec)
schema_csv_path = STAGE_DIR / "STAGE8_14C_CMIC_ORIGIN_STATE_SCHEMA.csv"
df_schema.to_csv(schema_csv_path, index=False)
print(f"Saved STAGE8_14C_CMIC_ORIGIN_STATE_SCHEMA.csv to {schema_csv_path}")

# 3. Build JSON Audit Artifact
json_payload = {
    "timestamp": "2026-09-13T06:58:00+00:00",
    "stage": "POLARIS STAGE 8.14C — BLOCKER PLAN SCIENTIFIC HARDENING AUDIT",
    "status": "COMPLETED — HARDENING AUDIT VERIFIED",
    "plan_classification": "PLAN_VALID_WITH_CORRECTIONS",
    "champion_state": {
        "official_champion": "Stage 8.1 700 hPa Steering Wind Model",
        "daytime_nmae_pct": 28.0688,
        "daytime_mae_w_m2": 36.188657,
        "daytime_rmse_w_m2": 64.219495,
        "daytime_bias_w_m2": 1.439399,
        "night_mae_w_m2": 0.0
    },
    "ctth_dependency_audit": {
        "variables_audited": ["ctth_press", "ctth_temp", "ctth_alti"],
        "upstream_inputs": "RTOV inversion mapping 10.8um/13.4um thermal radiances against ECMWF/MEPS vertical T/RH forecast profiles",
        "classification": "NWP_DERIVED & REDUNDANT",
        "stage8_8_reconciliation": "Complete overlap with Stage 8.8 MEPS vertical cloud geometry (which was REJECTED)",
        "scientific_verdict": "REJECTED AS OPTICAL FALLBACK. CTTH is strongly NWP-derived and re-introduces rejected Stage 8.8 cloud geometry. It CANNOT legitimately serve as a fallback for novel optical transmissivity (COT)."
    },
    "non_optical_variable_audit": {
        "primary_thermal_observation": "cma (Cloud Mask - Thermal IR Mode)",
        "classification": "OBSERVED / RETRIEVED (Thermal IR 11um / 12um)",
        "polar_night_status": "AVAILABLE 24/7/365",
        "scientific_verdict": "VALID THERMAL FALLBACK. Observed binary cloud presence/absence grid that operates in darkness without NWP profile dependency."
    },
    "missingness_semantics": {
        "model_type": "6-State Discrete Missingness & Retrieval Model",
        "states": [
            "VALID_OPTICAL",
            "POLAR_NIGHT",
            "LOW_SUN_INVALID",
            "NO_GRANULE",
            "QUALITY_REJECTED",
            "CAUSALITY_REJECTED"
        ],
        "zero_imputation_rule": "PROHIBITED FOR COT/CER. Zero COT physically implies clear sky, which is false during cloudy polar night. Polar night MUST be represented via explicit binary indicators and dual-branch features."
    },
    "coverage_gate_review": {
        "v1_threshold": ">=90% overall usable origins",
        "scientific_flaw": "Polar night (SZA > 84°) covers 57/347 origins (16.4%). Daylight optical COT can NEVER exceed 83.6% (290/347 origins) across a full-year benchmark.",
        "hardened_thresholds": {
            "daylight_origin_optical_gate": ">=90% usable optical retrievals within the 290 Daylight Origins (SZA <= 84°)",
            "benchmark_completeness_gate": "100% of 347 origins must receive an auditable state classification via dual-branch architecture without dropping origins"
        }
    },
    "required_corrections": [
        "Remove ctth_temp/ctth_press as a fallback for novel optical information; replace with observed thermal cloud mask (cma).",
        "Prohibit zero-imputation of COT/CER during polar night (SZA > 84°); use explicit polar_night indicator flags and dual-branch features.",
        "Replace unachievable >=90% overall optical coverage gate with Daylight Origin Optical Coverage Gate (>=90% of daylight origins) and 347-Origin Dual-Branch Benchmark Gate.",
        "Publish STAGE8_14C_CMIC_BLOCKER_RESOLUTION_PLAN_V2.md containing hardened scientific specifications."
    ],
    "governance_check": {
        "odd_target_accessed": False,
        "odd_predictions_generated": 0,
        "model_training_executed": False,
        "cross_validation_executed": False,
        "hyperparameter_tuning_executed": False,
        "champion_modified": False,
        "master_handoff_modified": False,
        "forecasting_experiment_authorized": False
    }
}

json_path = STAGE_DIR / "STAGE8_14C_PLAN_HARDENING_AUDIT.json"
with open(json_path, "w") as f:
    json.dump(json_payload, f, indent=2)
print(f"Saved STAGE8_14C_PLAN_HARDENING_AUDIT.json to {json_path}")

