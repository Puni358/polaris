# POLARIS — Stage 8.17A Documentation Correction Audit

**Timestamp:** 2026-09-13T15:14:28Z  
**Authoritative Machine Artifact:** [`STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv)  
**Verification Status:** `STAGE8_17A_REPORT_CORRECTION = COMPLETED`

---

## 1. Executive Summary

An independent audit compared the machine-generated feature-forensics table ([`STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/real_revalidation/STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv)) against the narrative postmortem text. 

While the **Stage 8.17A real-data failure result remains 100% verified** (Daytime MAE degraded from $36.211027\text{ W/m}^2$ to $36.426418\text{ W/m}^2$, $+0.215\text{ W/m}^2$), four narrative correlation figures in the old prose postmortem misstated the machine-generated values. In addition, the architectural description of AROME-Arctic vs MEPS required correction.

Per project governance rules: **The machine-generated CSV table is authoritative.** All prose narrative has been corrected to align strictly with the machine-generated figures.

---

## 2. Narrative vs Machine Discrepancy Log

| Metric / Description | Old Narrative Prose Value | Authoritative Machine CSV Value | Source Artifact | Action / Correction Taken | Impact on Scientific Verdict |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **`wind_disagreement_700` vs `ctx_std_6h` (Spearman $r$)** | $+0.4218$ | **$-0.1905$** | `STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv` | Corrected: 700 hPa wind disagreement has a slight negative correlation ($-0.1905$) with 6h context GHI std. | **NONE** (Failure confirmed) |
| **`wind_disagreement_700` vs `u700` (Spearman $r$)** | $-0.3812$ | **$+0.5694$** | `STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv` | Corrected: 700 hPa wind disagreement has a strong positive correlation ($+0.5694$) with baseline $U_{700}$. | **NONE** (Failure confirmed) |
| **`LWP_disagreement` vs `lwp_latest` (Spearman $r$)** | $+0.6812$ | **$+0.8939$** | `STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv` | Corrected: Reflects extremely high positive correlation ($+0.8939$) with baseline MEPS LWP. | **NONE** (Confirms heavy redundancy) |
| **`LWP_disagreement` vs `cloud_frac` (Spearman $r$)** | $+0.5419$ | **$+0.6053$** | `STAGE8_17A_REAL_AROME_FEATURE_FORENSICS.csv` | Corrected: Reflects strong positive correlation ($+0.6053$) with baseline MEPS cloud fraction. | **NONE** (Confirms heavy redundancy) |
| **Model Resolution Hierarchy** | "AROME-Arctic is higher-resolution than MEPS" | **Both are 2.5 km HARMONIE-AROME systems** | MET Norway Catalogue Metadata | Corrected: Disagreement arises from domain configuration, boundary conditions, data assimilation, ensemble setup, and init—not resolution superiority. | **NONE** |

---

## 3. Revised Scientific Mechanics

1. **Scalar Disagreement Failure Verified:**  
   Raw point-level scalar magnitude disagreement (`wind_disagreement_700` and `LWP_disagreement`) provides **no directional sign information** ($r_{\text{Spearman}} = +0.0482$ and $+0.0763$ with signed residuals).
2. **Redundancy Structure Corrected:**  
   `LWP_disagreement` is heavily redundant with baseline MEPS LWP ($r = +0.8939$) and MEPS cloud fraction ($r = +0.6053$). `wind_disagreement_700` scales directly with baseline 700 hPa wind speed ($r = +0.5694$).
3. **Governance Conclusion:**  
   Stage 8.17A real-data degradation is verified. The old mechanistic redundancy narrative was partially misstated and has been corrected against authoritative machine-generated tables. **No model route is reopened by this correction.**
