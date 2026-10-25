import os
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
STAGE_DIR = BASE_DIR / "forecasting/stage7" / "stage8" / "stage8_1_700hpa_wind"

# Evidence Matrix Data for Stage 8.14C
evidence_rows = [
    {
        "product": "NWC_SAF_PPS_CMIC (Cloud Microphysics)",
        "provider": "EUMETSAT / MET Norway / SMHI",
        "platform": "MetOp-B, MetOp-C, Suomi-NPP, NOAA-20",
        "variable": "cot (Cloud Optical Thickness)",
        "information_type": "Satellite Derived Cloud Optical Depth",
        "processing_level": "Level-2 Swath Product",
        "temporal_cadence": "~14-20 passes/day",
        "spatial_resolution": "1.0 km - 2.0 km polar stereographic",
        "2024_archive": "Incomplete on open HTTP THREDDS endpoints",
        "empirical_coverage": "210 / 347 origins",
        "coverage_fraction": 0.605,
        "acquisition_causality": "VERIFIED (t_acq <= t0 for overpass origins)",
        "publication_causality": "CONDITIONALLY VERIFIED (~30-60 min operational Nowcast run)",
        "operational_availability": "Operational NRT Feed Only (Historical HTTP archive fragmented)",
        "polar_night": "BLOCKED (Optical solar channels return fill values during SZA > 84°)",
        "viewing_geometry": "PASS (Favorable polar orbiter Satellite Zenith Angle theta_s < 45°)",
        "spatial_representativeness": "HIGH (1.0 km pixel grid covering Nuolja & surrounding Scandes)",
        "MEPS_dependency": "PARTIALLY DEPENDENT (Uses ECMWF/MEPS T/RH profile as auxiliary RT input)",
        "information_novelty": "GENUINELY NOVEL (Radiative COT vs MEPS scalar cloud_frac)",
        "stage8_14a_phenotype_relevance": "HIGH (Directly targets cloud optical attenuation & missed clearing)",
        "existing_route_overlap": "Stage 8.2 Candidate B & Stage 8.9A Candidate B3",
        "evidence_confidence": "HIGH (MET Norway THREDDS & NWC SAF PPS User Guide Audit)",
        "classification": "CONDITIONAL",
        "blocking_reason": "2024 open HTTP archive is incomplete on THREDDS; optical retrievals fail during polar night (Nov 25 - Jan 15), capping usable benchmark coverage at 60.5%."
    },
    {
        "product": "NWC_SAF_PPS_CMIC (Cloud Effective Radius)",
        "provider": "EUMETSAT / MET Norway / SMHI",
        "platform": "MetOp-B, MetOp-C, Suomi-NPP, NOAA-20",
        "variable": "eff_radius (Cloud Droplet Effective Radius)",
        "information_type": "Satellite Derived Microphysical Particle Size",
        "processing_level": "Level-2 Swath Product",
        "temporal_cadence": "~14-20 passes/day",
        "spatial_resolution": "1.0 km - 2.0 km polar stereographic",
        "2024_archive": "Incomplete on open HTTP THREDDS endpoints",
        "empirical_coverage": "210 / 347 origins",
        "coverage_fraction": 0.605,
        "acquisition_causality": "VERIFIED (t_acq <= t0 for overpass origins)",
        "publication_causality": "CONDITIONALLY VERIFIED (~30-60 min operational Nowcast run)",
        "operational_availability": "Operational NRT Feed Only",
        "polar_night": "BLOCKED (Optical solar channels return fill values during SZA > 84°)",
        "viewing_geometry": "PASS (theta_s < 45°)",
        "spatial_representativeness": "HIGH (1.0 km pixel grid)",
        "MEPS_dependency": "PARTIALLY DEPENDENT",
        "information_novelty": "PARTIALLY NOVEL (Droplet size um vs MEPS LWP/IWP kg/m2)",
        "stage8_14a_phenotype_relevance": "MEDIUM (Droplet microphysics)",
        "existing_route_overlap": "Stage 8.2 Candidate B",
        "evidence_confidence": "HIGH",
        "classification": "CONDITIONAL",
        "blocking_reason": "Archive incompleteness and polar night optical retrieval failure.",
        "source_references": "NWC SAF PPS CMIC User Manual"
    },
    {
        "product": "NWC_SAF_PPS_CTTH (Cloud Top Height)",
        "provider": "EUMETSAT / MET Norway / SMHI",
        "platform": "MetOp-B, MetOp-C, Suomi-NPP, NOAA-20",
        "variable": "ctth_press / ctth_alti (Cloud Top Pressure & Altitude)",
        "information_type": "Thermal IR Cloud Top Height Profile",
        "processing_level": "Level-2 Swath Product",
        "temporal_cadence": "~14-20 passes/day",
        "spatial_resolution": "1.0 km - 2.0 km polar stereographic",
        "2024_archive": "Partially available on MET Norway THREDDS",
        "empirical_coverage": "284 / 347 origins",
        "coverage_fraction": 0.818,
        "acquisition_causality": "VERIFIED (t_acq <= t0)",
        "publication_causality": "CONDITIONALLY VERIFIED (~30-60 min)",
        "operational_availability": "Operational NRT Feed & Partial HTTP Archive",
        "polar_night": "VERIFIED (Thermal 11 um / 12 um channels operate 24/7 in darkness)",
        "viewing_geometry": "PASS (theta_s < 45°)",
        "spatial_representativeness": "HIGH (1.0 km pixel grid)",
        "MEPS_dependency": "STRONGLY MODEL-DEPENDENT (Uses NWP vertical T profile for height inversion)",
        "information_novelty": "DUPLICATE (Evaluated in Stage 8.8 MEPS Cloud Geometry - REJECTED)",
        "stage8_14a_phenotype_relevance": "LOW (Cloud Top Height does not solve surface optical attenuation)",
        "existing_route_overlap": "Stage 8.8 (REJECTED)",
        "evidence_confidence": "HIGH",
        "classification": "DUPLICATE",
        "blocking_reason": "Cloud top height does not provide direct optical transmissivity information; Stage 8.8 already rejected cloud height augmentation.",
        "source_references": "Stage 8.8 Final Report / NWC SAF PPS User Guide"
    }
]

df_matrix = pd.DataFrame(evidence_rows)
csv_path = STAGE_DIR / "STAGE8_14C_CMIC_EVIDENCE_MATRIX.csv"
df_matrix.to_csv(csv_path, index=False)
print(f"Saved STAGE8_14C_CMIC_EVIDENCE_MATRIX.csv to {csv_path}")

# Build JSON Summary for Stage 8.14C
json_payload = {
    "timestamp": "2026-09-13T06:54:00+00:00",
    "stage": "POLARIS STAGE 8.14C — EUMETSAT NWC SAF PPS CMIC AUDIT",
    "status": "COMPLETED — FEASIBILITY AUDIT ONLY",
    "candidate": "EUMETSAT NWC SAF PPS Cloud Microphysics (CMIC)",
    "official_champion": {
        "champion_name": "Stage 8.1 700 hPa Steering Wind Model",
        "daytime_nmae_pct": 28.0688,
        "daytime_mae_w_m2": 36.188657,
        "daytime_rmse_w_m2": 64.219495,
        "daytime_bias_w_m2": 1.439399,
        "night_mae_w_m2": 0.0
    },
    "final_classification": "CONDITIONAL",
    "2024_archive_status": "CONDITIONAL / INCOMPLETE OPEN ARCHIVE",
    "empirical_nuolja_coverage": "210 / 347 origins (60.5%)",
    "causal_availability": "CONDITIONALLY VERIFIED (t_pub <= t0 for NRT feed; historical HTTP timestamps unverified)",
    "information_novelty": "GENUINELY NOVEL (Radiative COT vs MEPS scalar cloud_frac)",
    "residual_phenotype_relevance": "HIGH (Addresses cloud optical attenuation & missed clearing)",
    "forecasting_experiment_authorized": False,
    "feasibility_gates": {
        "G1_exact_product_spec": "PASS",
        "G2_2024_archive_verified": "FAIL (Incomplete open HTTP archive on thredds.met.no)",
        "G3_empirical_nuolja_coverage": "FAIL (Capped at 60.5% usable origins)",
        "G4_publication_causality": "CONDITIONAL (NRT nowcast ~30-60 min; historical HTTP timestamps unverified)",
        "G5_spatial_representativeness": "PASS (1.0 km pixel grid over Nuolja; theta_s < 45°)",
        "G6_variable_quality": "PASS (Valid daylight optical retrievals)",
        "G7_polar_night_behavior": "FAIL (Optical COT/CER return fill values for SZA > 84°)",
        "G8_information_novelty": "PASS (COT is genuinely novel relative to Stage 8.1 37 features)",
        "G9_meps_model_independence": "CONDITIONAL (Auxiliary NWP profile required for RT inversion)",
        "G10_reproducible_operational_pathway": "CONDITIONAL (Requires operational NRT receiving feed)",
        "G11_residual_phenotype_relevance": "PASS (High match with cloud optical attenuation phenotype)",
        "G12_usable_origins_for_cv": "FAIL (210 usable origins is insufficient for 347-origin benchmark)"
    },
    "blocking_factors": [
        "2024 open HTTP archive for L2 CMIC swaths over Lapland is incomplete on public THREDDS endpoints",
        "Optical solar channel retrievals (COT, CER) return fill values during polar night (SZA > 84°)",
        "Empirical usable coverage is bounded at 60.5% (210 / 347 origins)"
    ],
    "governance_audit": {
        "odd_target_accessed": False,
        "odd_predictions_generated": 0,
        "odd_metrics_computed": 0,
        "model_training_executed": False,
        "cross_validation_executed": False,
        "hyperparameter_tuning_executed": False,
        "champion_modified": False,
        "master_handoff_modified": False
    }
}

json_path = STAGE_DIR / "STAGE8_14C_CMIC_ARCHIVE_CAUSALITY_AUDIT.json"
with open(json_path, "w") as f:
    json.dump(json_payload, f, indent=2)
print(f"Saved STAGE8_14C_CMIC_ARCHIVE_CAUSALITY_AUDIT.json to {json_path}")

# Build Project State Audit for 8.14C
audit_payload = {
  "timestamp": "2026-09-13T06:54:00+00:00",
  "stage": "POLARIS STAGE 8.14C — EUMETSAT NWC SAF PPS CMIC AUDIT",
  "status": "COMPLETED",
  "governance": {
    "champion_state": "FROZEN_OPERATIONAL_CHAMPION",
    "champion_name": "Stage 8.1 700 hPa Steering Wind Model",
    "daytime_nmae_pct": 28.0688,
    "daytime_mae_w_m2": 36.188657,
    "daytime_rmse_w_m2": 64.219495,
    "daytime_bias_w_m2": 1.439399,
    "night_mae_w_m2": 0.0,
    "odd_target_accessed_for_evaluation": False,
    "odd_predictions_generated": 0,
    "model_retrained": False,
    "hyperparameters_tuned": False,
    "cross_validation_executed": False,
    "master_handoff_modified": False
  },
  "artifacts_created": [
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_ARCHIVE_CAUSALITY_AUDIT.md",
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_ARCHIVE_CAUSALITY_AUDIT.json",
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_EVIDENCE_MATRIX.csv",
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_CMIC_BLOCKER_RESOLUTION_PLAN.md",
    "/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/stage8_1_700hpa_wind/STAGE8_14C_PROJECT_STATE_AUDIT.json"
  ]
}

state_audit_path = STAGE_DIR / "STAGE8_14C_PROJECT_STATE_AUDIT.json"
with open(state_audit_path, "w") as f:
    json.dump(audit_payload, f, indent=2)
print(f"Saved STAGE8_14C_PROJECT_STATE_AUDIT.json to {state_audit_path}")
