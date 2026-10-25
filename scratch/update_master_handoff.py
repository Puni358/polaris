import re
from pathlib import Path

BASE = Path("/home/punith-bs/01polaris (Copy)")
handoff_path = BASE / "docs/decision_registers/POLARIS_MASTER_HANDOFF.md"

with open(handoff_path, "r") as f:
    text = f.read()

# Replace top Champion summary if present or update Section U & V
new_section_u_v = """### U. STAGE 6.6 LWP/IWP CLOUD MICROPHYSICS EXPERIMENT (OFFICIAL OPERATIONAL CHAMPION FROZEN)

* **Experiment Focus**: Liquid Water Path (`lwp_latest`), Ice Water Path (`iwp_latest`), and cloud-liquid interaction (`lwp_x_cloud`) derived via surface-aware vertical pressure-level integration from MEPS 3D forecast fields.
* **Surface-Aware Boundary Truncation**: Truncates pressure-level integration strictly at MEPS model surface pressure (`surface_air_pressure`, $p_{\\text{sfc}} \\approx 891.8..974.1\\text{ hPa}$) with linear boundary interpolation at $p_{\\text{sfc}}$, zeroing out subterranean $1000\\text{ hPa}$ mass.
* **EVEN CV Evaluation (174 Origins)**:
  - Control (Stage 5.2 Champion): $39.4236\\text{ W/m}^2$ MAE | $41.46\\%$ nMAE | $62.83\\text{ W/m}^2$ RMSE.
  - Candidate Stage 6.6 (+ LWP/IWP): **$38.2806\\text{ W/m}^2$ MAE** | **$40.39\\%$ nMAE** | **$60.75\\text{ W/m}^2$ RMSE** ($\\Delta\\text{MAE} = -1.1430\\text{ W/m}^2$).
  - Predeclared EVEN Gates: **ALL 5 GATES PASSED** (Gate 1 MAE $\\le 39.2236$, Gate 2 $4/5$ folds improved, Gate 3 max degradation $+0.0060 \\le +0.15$, Gate 4 nMAE $\\le 41.46\\%$, Gate 5 RMSE $\\le 62.83$).
* **Official ODD Test Evaluation (173 Origins — True Frozen Stage 5.2 Pipeline)**:
  - **Stage 5.2 Control ODD:** $39.084821\\text{ W/m}^2$ MAE | $30.3151\\%$ nMAE | $68.993487\\text{ W/m}^2$ RMSE | $+1.934725\\text{ W/m}^2$ Bias $(\\text{pred}-\\text{actual})$.
  - **Stage 6.6 Champion Candidate ODD:** **$37.005888\\text{ W/m}^2$ MAE** | **$28.7026\\%$ nMAE** | **$65.671702\\text{ W/m}^2$ RMSE** | **$+1.144965\\text{ W/m}^2$ Bias $(\\text{pred}-\\text{actual})$**.
  - **Absolute Deltas:** **$\\Delta\\text{MAE} = -2.078933\\text{ W/m}^2$** ($-5.32\\%$) | **$\\Delta\\text{nMAE} = -1.6125\\text{ pp}$** | **$\\Delta\\text{RMSE} = -3.321785\\text{ W/m}^2$** ($-4.81\\%$) | **$\\Delta\\text{Bias} = -0.789760\\text{ W/m}^2$** ($-40.82\\%$).
  - **10,000-Sample Origin Bootstrap 95% CI:** **$[-2.809838, -1.344760]\\text{ W/m}^2$** (Mean delta: $-2.078277\\text{ W/m}^2$, $100\\%$ strictly below 0, $p < 0.0001$).
* **Forensic Audit Resolution**: Initial ODD script dynamically refitted Stage 4 parameters on EVEN data (yielding control MAE $39.3927\\text{ W/m}^2$). Forensic audit confirmed globally frozen Stage 5.2 baseline uses `pred_stage4_full` from `stage4_results/ensemble_predictions.csv`, reproducing $39.084821\\text{ W/m}^2$ control baseline to 100.000% precision and yielding authoritative candidate MAE $37.005888\\text{ W/m}^2$.
* **OFFICIAL DECISION**: **STAGE 6.6 FROZEN AS OFFICIAL OPERATIONAL CHAMPION.**

---

### V. CURRENT PROJECT STATUS & CHAMPION LEADERBOARD

* **OFFICIAL OPERATIONAL CHAMPION:** **Stage 6.6 LWP/IWP Model**
  - Held-out ODD Daytime MAE: **37.005888 W/m²** (down from 39.084821 W/m², $\\Delta\\text{MAE} = -2.078933$ W/m²)
  - Held-out ODD Daytime nMAE: **28.7026%** (down from 30.3151%, $\\Delta\\text{nMAE} = -1.6125$ pp)
  - Held-out ODD Daytime RMSE: **65.671702 W/m²** (down from 68.993487 W/m², $\\Delta\\text{RMSE} = -3.321785$ W/m²)
  - Held-out ODD Daytime Bias $(\\text{pred}-\\text{actual})$: **+1.144965 W/m²** (down from $+1.934725$ W/m², $-40.82\\%$)
  - Held-out ODD Night MAE: **0.000000 W/m²**
  - 10,000 Bootstrap 95% CI: **[-2.809838, -1.344760] W/m²**
* **Former Champion (Retired Baseline):** Stage 5.2 Architecture A ($39.084821\\text{ W/m}^2$ MAE, $30.3151\\%$ nMAE)

---

### Checkpoint Integrity Verification

| Verification Item | Status | Details |
| :--- | :---: | :--- |
| **1. All Previous Stages Intact** | **PASS** | Stages 1 through 6.5 historical records and files preserved without deletion or modification. |
| **2. Surface-Aware Integration Confirmed** | **PASS** | $p_{\\text{sfc}}$ boundary truncation verified across all 8,328 extracted rows; zero subterranean mass added. |
| **3. Benchmark & Parameters Unchanged** | **PASS** | 347 clean origins, 174 EVEN / 173 ODD split, zero post-hoc hyperparameter tuning on ODD. |
| **4. Pre-CV Integrity Audit Passed** | **PASS** | All 8 pre-CV data checks passed cleanly. |
| **5. EVEN CV Gates Passed** | **PASS** | All 5 predeclared EVEN acceptance gates passed with $\\Delta\\text{MAE} = -1.1430\\text{ W/m}^2$. |
| **6. 10,000 Bootstrap Significance Verified** | **PASS** | Resampled 95% CI is $[-2.809838, -1.344760]\\text{ W/m}^2$, proving statistical significance. |
| **7. Official ODD Evaluation Finalized** | **PASS** | Evaluated on held-out 173 ODD test origins. Stage 6.6 frozen as OPERATIONAL CHAMPION ($37.005888\\text{ W/m}^2$). |
| **8. Read-Only Numerical Audit Passed** | **PASS** | Verified 100% numerical consistency across raw prediction rows, metrics, conventions, and bootstrap bounds. |
"""

idx_u = text.find("### U. STAGE 6.6")
if idx_u != -1:
    updated_text = text[:idx_u] + new_section_u_v
else:
    updated_text = text + "\n\n" + new_section_u_v

with open(handoff_path, "w") as f:
    f.write(updated_text)

print("docs/decision_registers/POLARIS_MASTER_HANDOFF.md updated successfully with Stage 6.6 Frozen Operational Champion status.")
