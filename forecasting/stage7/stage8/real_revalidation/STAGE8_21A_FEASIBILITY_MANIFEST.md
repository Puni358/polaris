# POLARIS STAGE 8.21A FEASIBILITY & REPORT CORRECTION MANIFEST

## 1. Executive Summary & Audit Status

This manifest completes the workflow for:
1. **PART A:** Stage 8.17A Report & Postmortem Narrative Correction.
2. **PART B:** Stage 8.21A 3D Solar Slant-Path Hydrometeor Geometry Feasibility Audit & Targeted Correction.

---

## 2. Part A Summary — Stage 8.17A Report Correction

- **Degradation Verdict:** **VERIFIED_DEGRADED** (Control MAE = $36.211027\text{ W/m}^2$, Candidate MAE = $36.426418\text{ W/m}^2$, $\Delta = +0.215391\text{ W/m}^2$).
- **Report Correction:** Narrative correlation typos corrected directly from machine artifact `STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv`.
- **Model Resolution Correction:** Clarified that both AROME-Arctic and MEPS are $2.5\text{ km}$ HARMONIE-AROME family models. Disagreement stems from domain limits, boundary conditions, and data assimilation, not spatial resolution superiority.
- **Scientific Verdict Impact:** **NO CHANGE**. Raw scalar disagreement route remains closed.

---

## 3. Part B Summary — Stage 8.21A Feasibility Audit & Targeted Correction

- **Proposed Route:** Stage 8.21A 3D Solar Slant-Path Hydrometeor Geometry
- **Original Classification:** `A. FEASIBILITY VERIFIED — EXPERIMENT MAY BE DESIGNED`
- **Corrected Classification:** **`B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED`**
- **Decision & Gate Re-Evaluations:**
  - `F3_ORIGINAL`: `PASS` $\to$ `F3_CORRECTED`: **`CONDITIONAL`** ($25 \times 25$ window provides $30\text{ km}$ cardinal radius; $85^\circ$ zenith at $5\text{ km}$ cloud height requires $57.15\text{ km}$ displacement $\implies 47 \times 47$ window needed).
  - `F4_ORIGINAL`: `PASS` $\to$ `F4_CORRECTED`: **`CONDITIONAL`** (`meps_det_pl` provides pressure levels; height $z$ must be defensibly reconstructed via hydrostatic integration).
  - `F6_ORIGINAL`: `CONDITIONAL` $\to$ `F6_CORRECTED`: **`CONDITIONAL`** ($q_l/q_i$ directly observed, but droplet effective radii $r_e$ must be parameterized).

---

## 4. Manifest of Generated & Updated Artifacts

| Artifact Filename | Purpose | Target Directory |
|---|---|---|
| `STAGE8_21A_FEASIBILITY_CORRECTION_AUDIT.md` | Detailed geometry & physics correction audit report | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEASIBILITY_CORRECTION_AUDIT.json` | Machine-readable correction audit summary | `real_revalidation/` & Artifact Dir |
| `STAGE8_17A_REPORT_CORRECTION_AUDIT.md` | Detailed Part A narrative correction audit | `real_revalidation/` & Artifact Dir |
| `STAGE8_17A_REPORT_CORRECTION_AUDIT.json` | Machine-readable Part A correction audit | `real_revalidation/` & Artifact Dir |
| `STAGE8_17A_REAL_AROME_POSTMORTEM_CORRECTED.md` | Corrected postmortem markdown | `real_revalidation/` & Artifact Dir |
| `STAGE8_17A_REAL_AROME_POSTMORTEM_CORRECTED.json` | Corrected postmortem JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_3D_SLANT_PATH_FEASIBILITY.md` | Updated 10-gate feasibility report | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_3D_SLANT_PATH_FEASIBILITY.json` | Machine-readable feasibility evaluation | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEASIBILITY_MANIFEST.md` | Comprehensive audit manifest | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEASIBILITY_MANIFEST.json` | Machine-readable audit manifest | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEASIBILITY.log` | Feasibility audit script log | `real_revalidation/` |
| `run_stage8_21a_feasibility_correction.py` | Targeted geometry correction script | `real_revalidation/` |

---

## 5. Absolute Governance Verification

```
ORIGINAL_DECISION = A. FEASIBILITY VERIFIED — EXPERIMENT MAY BE DESIGNED
CORRECTED_DECISION = B. CONDITIONAL FEASIBILITY — SPECIFIC DATA/PHYSICS GAP MUST BE RESOLVED

F3_ORIGINAL = PASS
F3_CORRECTED = CONDITIONAL (25x25 window provides 30km cardinal radius; 85° zenith at 5km cloud height requires 57.15km displacement -> 47x47 window needed)

F4_ORIGINAL = PASS
F4_CORRECTED = CONDITIONAL (meps_det_pl provides pressure levels; height z must be defensibly reconstructed via hydrostatic equation)

F6_ORIGINAL = CONDITIONAL
F6_CORRECTED = CONDITIONAL (q_l/q_i directly observed, but droplet effective radii r_e must be parameterized)

FINAL_EXPERIMENT_RUN = FALSE
FINAL_MODEL_TRAINING = FALSE
FINAL_ODD_ACCESS = FALSE
OPERATIONAL_CHAMPION_CHANGED = FALSE
MASTER_HANDOFF_CHANGED = FALSE
ROUTE_REGISTRY_CHANGED = FALSE
```
