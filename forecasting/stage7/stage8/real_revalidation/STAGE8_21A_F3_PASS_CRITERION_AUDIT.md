# POLARIS STAGE 8.21A — F3 PASS-CRITERION & DENOMINATOR AUDIT REPORT

## 1. Executive Summary & F3 Decision

- **Route Identifier:** STAGE 8.21A (3D Solar Slant-Path Hydrometeor Geometry)
- **F3 Resolution Verdict:** **`F3_FINAL = CONDITIONAL`**
- **Coverage Criterion:** **NO PRE-LOCKED COVERAGE THRESHOLD**
- **Selected Baseline Window:** **$47 \times 47$ Grid Window** ($57.5\text{ km}$ cardinal radius, $81.32\text{ km}$ corner radius, $115.0\text{ km}$ physical span)
- **Actual Coverage on Relevant Rays (Elev $\ge 5^\circ$):** **$99.30\%$** ($3,262 / 3,285$ rays covered, $23$ uncovered)
- **Actual Coverage on All Daytime Rays (Elev $> 0^\circ$):** **$86.99\%$** ($3,625 / 4,167$ rays covered, $542$ uncovered)
- **Governance Firewall Verification:**
  - `EXPERIMENT_RUN` = **FALSE**
  - `MODEL_TRAINING` = **FALSE**
  - `ODD_ACCESS` = **FALSE**
  - `ODD_PREDICTIONS` = **FALSE**
  - `ODD_METRICS` = **FALSE**
  - `HYPERPARAMETER_TUNING` = **FALSE**
  - `CHAMPION_CHANGED` = **FALSE**
  - `MASTER_HANDOFF_CHANGED` = **FALSE**
  - `ROUTE_REGISTRY_CHANGED` = **FALSE**

### One-Paragraph Decision Summary
Because no pre-locked coverage threshold exists in POLARIS prior to this audit and a $47 \times 47$ extraction window achieves $99.30\%$ coverage of relevant rays (leaving $23$ rays / $0.70\%$ outside the window), `F3_FINAL` is classified as **CONDITIONAL**. It will become `PASS` once the experiment design phase explicitly locks either a $47 \times 47$ window with a $99.0\%$ coverage experiment scope or an extended $79 \times 79$ window ($10.07\text{ GB}$ total payload) for absolute $100.0\%$ spatial containment.

---

## 2. Issue 2 — Exact Denominator Accounting Identity

Reconciliation formula across all 8,328 benchmark forecast tuples ($347 \text{ origins} \times 24 \text{ horizons}$):

$$\mathbf{8,328 \text{ Total Tuples}} = \mathbf{4,161 \text{ Nighttime Tuples}} + \mathbf{4,167 \text{ Daytime Tuples}} \left(\mathbf{882 \text{ Low-Sun Edge Tuples}} + \mathbf{3,285 \text{ Relevant Solar Ray Tuples}}\right)$$

| Tuple Category | Solar Elevation ($\text{elev}$) | Count ($N$) | Fraction of Total ($8,328$) | Explanation / Handling |
|---|---|---|---|---|
| **Nighttime Tuples** | $\text{elev} \le 0^\circ$ | **$4,161$** | $49.96\%$ | Nighttime hours where pyranometer $SW_{\text{IN}} = 0\text{ W/m}^2$. Excluded from solar ray tracing. |
| **Low-Sun Edge Tuples** | $0^\circ < \text{elev} < 5^\circ$ | **$882$** | $10.59\%$ | Near-horizon sunrise/sunset hours where solar zenith $\ge 85^\circ$ creates extreme long slant paths. |
| **Relevant Solar Ray Tuples** | $\text{elev} \ge 5^\circ$ | **$3,285$** | $39.45\%$ | Physically relevant daytime shortwave radiation hours where ray-tracing feature is evaluated. |
| **All Daytime Tuples** | $\text{elev} > 0^\circ$ | **$4,167$** | $50.04\%$ | Sum of low-sun edge tuples ($882$) and relevant solar ray tuples ($3,285$). |

---

## 3. Issue 1B & 5 — Honest Evaluation of All Candidate Extraction Windows

Containment testing using exact square geometry ($|\Delta x| \le R_{\text{card}}$ AND $|\Delta y| \le R_{\text{card}}$):

| Window Size | Grid Points | Cardinal Radius | Corner Radius | Relevant Covered ($N=3,285$) | Relevant Coverage | Relevant Uncovered | All Daytime Covered ($N=4,167$) | All Daytime Coverage | Payload Size ($347$ Origins) |
|---|---|---|---|---|---|---|---|---|---|
| **$25 \times 25$** | $625$ | $30.0\text{ km}$ | $42.43\text{ km}$ | $3,092$ | **$94.12\%$** | $193$ | $3,237$ | **$77.68\%$** | $1.01\text{ GB}$ |
| **$31 \times 31$** | $961$ | $37.5\text{ km}$ | $53.03\text{ km}$ | $3,179$ | **$96.77\%$** | $106$ | $3,392$ | **$81.40\%$** | $1.55\text{ GB}$ |
| **$35 \times 35$** | $1,225$ | $42.5\text{ km}$ | $60.10\text{ km}$ | $3,219$ | **$97.99\%$** | $66$ | $3,473$ | **$83.35\%$** | $1.98\text{ GB}$ |
| **$41 \times 41$** | $1,681$ | $50.0\text{ km}$ | $70.71\text{ km}$ | $3,250$ | **$98.93\%$** | $35$ | $3,549$ | **$85.17\%$** | $2.71\text{ GB}$ |
| **$47 \times 47$** | **$2,209$** | **$57.5\text{ km}$** | **$81.32\text{ km}$** | **$3,262$** | **$99.30\%$** | **$23$** | **$3,625$** | **$86.99\%$** | **$3.56\text{ GB}$** |
| **$51 \times 51$** | $2,601$ | $62.5\text{ km}$ | $88.39\text{ km}$ | $3,272$ | **$99.60\%$** | $13$ | $3,668$ | **$88.02\%$** | $4.20\text{ GB}$ |
| **$57 \times 57$** | $3,249$ | $70.0\text{ km}$ | $98.99\text{ km}$ | $3,277$ | **$99.76\%$** | $8$ | $3,724$ | **$89.37\%$** | $5.24\text{ GB}$ |
| **$63 \times 63$** | $3,969$ | $77.5\text{ km}$ | $109.60\text{ km}$ | $3,282$ | **$99.91\%$** | $3$ | $3,759$ | **$90.21\%$** | $6.40\text{ GB}$ |
| **$79 \times 79$** | $6,241$ | $97.5\text{ km}$ | $137.89\text{ km}$ | **$3,285$** | **$100.00\%$** | **$0$** | **$3,840$** | **$92.15\%$** | **$10.07\text{ GB}$** |

---

## 4. Issue 3 & 4 — Qualification of Low-Sun Rays & Regime Definition

- **Relevant Solar Ray Definition:** Solar elevation $\ge 5^\circ$ (solar zenith $\le 85^\circ$).
- **Low-Sun Edge Qualification:** Very low solar elevation ($0^\circ < \text{elev} < 5^\circ$, zenith $\ge 85^\circ$) creates a geometrically demanding long-slant-path regime and is treated explicitly as a low-sun edge case.
- **Instrument Claim Removal:** Unsupported pyranometer cosine error claims have been completely removed and replaced with explicit geometric long-slant-path regime qualifications.

---

## 5. Issue 6 — Computational Feasibility Recalculation

- **Baseline $47 \times 47$ Window ($2,209$ points):** $\mathbf{3.56\text{ GB}}$ total payload across 347 origins.
- **Extended $79 \times 79$ Window ($6,241$ points):** $\mathbf{10.07\text{ GB}}$ total payload across 347 origins.
- Both window options remain operationally tractable via server-side OPeNDAP slicing.

---

## 6. Final Decision Block Print

```
F3_COVERAGE_CRITERION = NO PRE-LOCKED THRESHOLD — CONDITIONAL ON EXPERIMENT SCOPE LOCK
TOTAL_FORECAST_TUPLES = 8328
DAYTIME_TUPLES = 4167
RELEVANT_RAY_TUPLES = 3285

SELECTED_WINDOW = 47x47
ACTUAL_COVERAGE = 99.30% (Relevant elev >= 5°) / 86.99% (All Daytime elev > 0°)
UNCOVERED_RAYS = 23

F3_FINAL = CONDITIONAL
```
