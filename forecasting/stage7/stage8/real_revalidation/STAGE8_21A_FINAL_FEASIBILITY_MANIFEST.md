# POLARIS STAGE 8.21A FINAL F3/F6 PHYSICS RESOLUTION MANIFEST

## 1. Executive Summary & Audit Resolution

This manifest completes the final physics resolution audit for Stage 8.21A (3D Solar Slant-Path Hydrometeor Geometry):

- **F3 Spatial Geometry:** **`PASS`** (PASS FOR EXPERIMENT DESIGN — Real MEPS cloud height distribution established; $41 \times 41$ grid window covers $>99.5\%$ of daytime solar rays; $47 \times 47$ grid window covers $100\%$ up to $\theta_z = 85^\circ$).
- **F4 Vertical Coordinate:** **`PASS`** (Hydrostatic pressure-to-height coordinate reconstruction $z(p)$ verified and demonstrated on real MEPS columns).
- **F6 Optical Proxy:** **`PASS`** (PASS FOR EXPERIMENT DESIGN — Parameterized direct-beam extinction feature proxy derived with explicit microphysical assumptions $r_{e,\text{liq}}=10\,\mu\text{m}, r_{e,\text{ice}}=30\,\mu\text{m}$; explicitly bounded as direct-beam proxy, NOT full SW_IN).
- **Computational Feasibility:** **`PASS`** (2.91 GB payload for $41 \times 41$ window across 347 origins is operationally tractable).
- **Final Classification:** **`A. FEASIBILITY VERIFIED — EXPERIMENT DESIGN MAY BEGIN`**

---

## 2. Manifest of Created & Updated Artifacts

| Artifact Filename | Description / Purpose | Target Directory |
|---|---|---|
| `STAGE8_21A_FINAL_F3_F6_RESOLUTION_AUDIT.md` | Main final physics resolution report | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FINAL_F3_F6_RESOLUTION_AUDIT.json` | Machine-readable resolution summary JSON | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FINAL_CLOUD_HEIGHT_GEOMETRY.csv` | Machine-readable cloud-top height & displacement table | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FINAL_OPTICAL_PROXY_SENSITIVITY.csv` | Machine-readable optical proxy microphysics sensitivity table | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FINAL_FEASIBILITY_MANIFEST.md` | Final audit manifest markdown | `real_revalidation/` & Artifact Dir |
| `STAGE8_21A_FINAL_FEASIBILITY_MANIFEST.json` | Final audit manifest JSON | `real_revalidation/` & Artifact Dir |
| `run_stage8_21a_final_f3_f6_audit.py` | Final audit resolution script | `real_revalidation/` |

---

## 3. Final Governance Verification Block

```
==============================================================
STAGE 8.21A FINAL F3/F6 RESOLUTION
==============================================================

F3_SPATIAL_GEOMETRY = PASS
F4_VERTICAL_COORDINATE = PASS
F6_OPTICAL_PROXY = PASS

COMPUTATIONAL_FEASIBILITY = PASS

FINAL_DECISION = A

EXPERIMENT_RUN = FALSE
MODEL_TRAINING = FALSE
ODD_ACCESS = FALSE
ODD_PREDICTIONS = FALSE
ODD_METRICS = FALSE
CHAMPION_CHANGED = FALSE
MASTER_HANDOFF_CHANGED = FALSE
ROUTE_REGISTRY_CHANGED = FALSE
```
