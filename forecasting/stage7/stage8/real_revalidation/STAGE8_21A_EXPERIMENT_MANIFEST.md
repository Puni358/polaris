# POLARIS STAGE 8.21A EXPERIMENT MANIFEST

## 1. Executive Summary & Design Status

This manifest completes the experiment design freeze for Stage 8.21A (3D Solar Slant-Path Hydrometeor Geometry):

- **Spatial Window:** $47 \times 47$ MEPS Grid Points ($57.5\text{ km}$ cardinal radius, $81.32\text{ km}$ corner radius, $115.0\text{ km}$ physical span)
- **Solar Elevation Domain:** Solar elevation $\ge 5.0^\circ$ ($\theta_z \le 85.0^\circ$)
- **Predeclared Coverage Criterion:** $\ge 99.0\%$ coverage requirement
- **Empirically Verified Coverage:** **$99.30\%$** ($3,262 / 3,285$ relevant solar-ray tuples)
- **Relevant Solar Ray Denominator:** $N = 3,285$ tuples
- **F3 Status:** `READY FOR EXPERIMENT DESIGN`
- **F4 Status:** `PASS`
- **F6 Status:** `PASS FOR EXPERIMENT DESIGN`
- **Design Status:** **FROZEN — READY FOR IMPLEMENTATION & EVEN-ONLY VALIDATION**

---

## 2. Manifest of Created Experiment Design Artifacts

| Artifact Filename | Purpose / Description | Target Directory |
|---|---|---|
| `STAGE8_21A_EXPERIMENT_SPECIFICATION.md` | Authoritative experiment specification & locked scope | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_EXPERIMENT_SPECIFICATION.json` | Machine-readable experiment specification JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEATURE_DEFINITION.md` | Detailed 4-feature compact set mathematical formulas | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FEATURE_DEFINITION.json` | Machine-readable feature definitions JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_DATA_COVERAGE_PLAN.md` | OPeNDAP extraction plan & outside-window fallback | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_DATA_COVERAGE_PLAN.json` | Machine-readable data coverage plan JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_PRE_RUN_GOVERNANCE_CHECKLIST.md` | 11-point pre-run governance verification checklist | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_PRE_RUN_GOVERNANCE_CHECKLIST.json` | Machine-readable governance checklist JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_EXPERIMENT_MANIFEST.md` | Master experiment design manifest markdown | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_EXPERIMENT_MANIFEST.json` | Master experiment design manifest JSON | `real_revalidation/` & Artifact Dir |
| `run_stage8_21a_pre_run_validation.py` | Pre-run governance & parameter validation script | `real_revalidation/` |
| `build_stage8_21a_experiment_design.py` | Experiment design build script | `real_revalidation/` |

---

## 3. Pre-Run Final Output Verification Block

```
STAGE8.21A EXPERIMENT DESIGN STATUS

SPATIAL_WINDOW = 47x47
SOLAR_ELEVATION_DOMAIN = >=5 degrees
PREDECLARED_COVERAGE_THRESHOLD = >=99.0%
EMPIRICAL_COVERAGE = 99.30%
RELEVANT_RAY_TUPLES = 3285

F3_STATUS = READY FOR EXPERIMENT DESIGN
F4_STATUS = PASS
F6_STATUS = PASS FOR EXPERIMENT DESIGN

EXPERIMENT_RUN = FALSE
MODEL_TRAINING = FALSE
ODD_ACCESS = FALSE
ODD_PREDICTIONS = FALSE
ODD_METRICS = FALSE
CHAMPION_CHANGED = FALSE
MASTER_HANDOFF_CHANGED = FALSE
ROUTE_REGISTRY_CHANGED = FALSE
```
