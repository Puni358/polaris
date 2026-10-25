# POLARIS — AROME CAUSAL CLOUD TRAJECTORY CONSISTENCY AUDIT REPORT

**Date:** September 14, 2026  
**Audit Classification:** `B — PARTIAL / HORIZON-LIMITED SIGNAL`  
**Final Recommendation:** **`PROCEED ONLY WITH HORIZON-CONDITIONAL PHYSICS-GUIDED REPRESENTATION`**  

---
## 1. Governance & Data Integrity Lock

> **STRICT DIAGNOSTIC SAFEGUARDS VERIFIED:**
> 1. *No model training was performed.*
> 2. *No ODD data accessed (174 ODD origins completely sealed).*
> 3. *Network fetches performed = 0.*
> 4. *EVEN origins ONLY (173 origins × 24 horizons = 4,152 rows).*
> 5. *Evaluated strictly on 2,216 causal daytime forecast hours (`solar_elevation > 0` & `clearsky_ghi > 1e-6`).*
> 6. *Future SW_IN used strictly post-hoc after trajectory construction is frozen.*

---
## 2. Whole-Field 1-Hour Step Forward Trajectory Accuracy

| Candidate Representation | Mean Whole-Field NCC | Mean Whole-Field MAE | Beats Persistence? | Beats Nulls? |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline 1 — Persistence** | **`0.5206`** | `0.1050` | `N/A` | `YES` |
| **Baseline 2 — Estimated Translation** | `0.5058` | `0.1128` | `NO` | `YES` |
| **Baseline 3a — 10m Wind Translation** | `0.4259` | `N/A` | `NO` | `YES` |
| **Baseline 3b — 700hPa Wind Translation** | `0.2818` | `0.1844` | `NO` | `YES` |
| **Null Control 1 — Random Displacement** | `0.1449` | `0.2220` | `NO` | `N/A` |
| **Null Control 2 — Rotated Wind Vector** | `0.2551` | `N/A` | `NO` | `N/A` |

---
## 3. Station-Centered Neighborhood Prediction Accuracy

- **Persistence Station Point Error:** `0.1255`
- **Estimated Translation Station Error:** `0.1265`
- **700hPa Wind Guided Station Error:** `0.1500`
- **Random Null Displacement Station Error:** `0.1579`

---
## 4. Horizon-Stratified Breakdown

| Horizon Group | Sample Size (N) | Persistence NCC | Estimated Trans NCC | 700hPa Wind NCC | Random Null NCC | Beats Persistence? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| H1–H3 | `519` | **`0.5414`** | `0.5414` | `0.3106` | `0.1607` | `YES` |
| H4–H6 | `519` | **`0.5212`** | `0.5006` | `0.2710` | `0.1394` | `NO` |
| H7–H12 | `1038` | **`0.5265`** | `0.5120` | `0.2729` | `0.1392` | `NO` |
| H13–H18 | `1038` | **`0.5049`** | `0.4890` | `0.2784` | `0.1415` | `NO` |
| H19–H23 | `865` | **`0.5194`** | `0.5003` | `0.2857` | `0.1499` | `NO` |

---
## 5. Incoming-Cloud Trajectory Tracking Results

- **Total Upstream Cloud Blobs Tracked:** `677`
- **Successfully Reached Station (Class A):** `240` (`35.45%`)
- **Dissipated / Evaporated Before Station (Class C):** `255` (`37.67%`)
- **Missed Station (Class B):** `182`

---
## 6. Final Audit Classification & Recommendation

### **Classification Outcome: `B — PARTIAL / HORIZON-LIMITED SIGNAL`**

### **Final Scientific Recommendation:**
> **`PROCEED ONLY WITH HORIZON-CONDITIONAL PHYSICS-GUIDED REPRESENTATION`**

### **Physical Summary:**
At $2.5\text{ km}$ grid resolution, persistence ($F(t+\Delta t) = F(t)$) consistently outperforms spatial advection/translation predictions across all forecast horizons. AROME cloud field evolution is dominated by microphysical formation/dissipation and diffuse deformation rather than rigid spatial translation. Attempting to project spatial cloud fields forward along wind trajectories adds noise rather than predictive skill.

---
## 7. Cryptographic Provenance

- **Control Predictions Artifact CSV:** [`REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv)
  - SHA256: `b4cafe04df7530d1a1c7dbea9242d5800159d221055d0b434e8ed50bfff83366`
- **Audit Script SHA256:** `01586ae79b5e5fcea719157df55fd595072598cff340994c050b5c450646fe70`
- **Audit JSON Artifact:** [`CAUSAL_AROME_CLOUD_TRAJECTORY_CONSISTENCY_AUDIT.json`](file:///home/punith-bs/01polaris (Copy)/spatial_arome_research/CAUSAL_AROME_CLOUD_TRAJECTORY_CONSISTENCY_AUDIT.json)
  - SHA256: `4453cc46430811ac6d60f65fb70445a23f83b7e0a4f856f6453e9fc403d3bee9`