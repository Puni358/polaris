# Audit & Correction Report: Diesel-Reduction Control Design

**Audit Target:** `DIESEL_REDUCTION_CONTROL_DESIGN.md`, `DIESEL_REDUCTION_CONTROL_DESIGN.json`  
**Auditor Reference:** Independent AI assistant Audit (`DIESEL_REDUCTION_CONTROL_DESIGN_INDEPENDENT_AUDIT.md`)  
**Correction Date:** 2026-10-05  
**Corrected Verdict:** `RESEARCH_DESIGN_COMPLETE — AWAITING SAFETY-GATE PREREGISTRATION`  
**Governance Status:** Design Correction Only. Zero production code modified; zero controller experiments run.  

---

## 1. Executive Summary of Corrections

Following the independent forensic audit by AI assistant and subsequent technical reviews, the diesel-reduction control design study has been brought to full mathematical and epistemic rigor. All unsupported numerical projections, artificial safety guarantees, mathematical formulation flaws, and unverified constants have been eliminated or re-classified according to strict scientific governance.

### Summary of Major Corrections
1. **Elimination of Unsupported Performance Claims:** Removed all headline percentage claims ("~35–45%", "~50–65%", "~15–25%", "~40–55%", "10–14%") and the claim of "strictly guaranteeing 100% critical reliability."
2. **Correction of EBR Horizon Mechanics:** Formally documented that the 6-hour EBR window shrinks at the horizon edge ($t \ge 19$), reaching 1 hour ($12,609\text{ Wh}$) at $t=23$, where the terminal target dominates.
3. **De-listing of Candidate 1 (Solar Headroom):** Formally marked Candidate 1 as `BLOCKED / NOT READY` due to structural mathematical infeasibility (cap can become negative and fall below $E_{\min}$, causing MILP infeasibility on 53/173 fixture origins and worsening diesel under $J_2 \succ J_3$).
4. **Re-specification of Candidate 2 (Net-Deficit EBR):**
   - **Variant S Input Stream:** Explicitly consumes `bundle.solar_generation.point` directly in Watts. The controller does NOT compute $51 \cdot I$ or apply a 60 kW cap a second time. The $51\text{ W}/(\text{W/m}^2)$ mapping is clarified as an upstream campaign adapter prototype, not an authorized physical constant.
   - **Critical-Demand Vector Semantics:** Corrected from an assumed scalar constant to the dynamic 24-step vector $\text{critical\_demand}[k] = \min(11600.0, \text{demand.point}[k])$.
   - **No Extra Reserve Floor:** No artificial additive or $\max()$ reserve floor is added to the EBR formula. The governed physical battery floor $E_{\min} = 40\text{ kWh}$ remains enforced in GAP19 busbar constraints.
   - **Variant S Properties:** Completely immune to wind forecast errors in reserve sizing (wind remains active in busbar balance); reverts to governed unconditional EBR when forecast solar is zero across the entire window.
   - **Variant SW Synthetic Wind Warning:** Explicitly documented that the campaign wind series is synthetic ($4500 + 5000\sin(2\pi t/24 + \phi)$); Variant SW results constitute synthetic-wind research evidence and cannot be generalized to real wind forecasting. Substantially replicates prior critical-aware experiment.
5. **Separation of Terminal Target Removal:** Terminal target pruning was removed from the primary candidate to prevent multi-variable confounding, as prior evidence showed it increased unmet load by $+6.3\%$.
6. **Candidate 3 (Elastic Slack) Correction:** Removed the erroneous $\lambda = 0.00035\text{ L/Wh}$ derivation. Labelled Candidate 3 strictly as a future parametric sweep requiring code modifications.
7. **Candidate 4 (JIT Diesel) Correction:** Corrected the attribution of the 68.4% fuel reduction (which belongs to total EBR removal, not step-0 commitment alone), resolved the 2h vs 3h inconsistency, and flagged the non-linearity for $t \ge 1$.
8. **Evaluation Dataset & Protocol Overhaul:**
   - Abandoned the 6 diagnostic origins as a primary test set to avoid circularity/contamination.
   - Preregistered the full 123-origin campaign framework, labelled as a *pre-specified paired historical evaluation set; not a pristine holdout*.
   - Mandated exact research critical-load metrics:
     $$\text{critical\_realized\_demand}[t] = \min(11600.0, \, \text{realized\_demand}[t])$$
     $$\text{critical\_unmet}[t] = \max(0, \, \text{critical\_realized\_demand}[t] - \text{critical\_served}[t])$$
     $$\text{critical\_reliability} = 1.0 - \frac{\sum_t \text{critical\_unmet}[t]}{\sum_t \text{critical\_realized\_demand}[t]}$$
   - Explicitly prohibited the campaign legacy `reliability_pct`.
   - Mandated 95% BCa bootstrap confidence intervals and paired two-sided Wilcoxon signed-rank tests across all 123 origins.
9. **Preregistration Requirement for Safety Gate:** Critical reliability acceptance threshold *REQUIRES PREREGISTRATION/GOVERNANCE BEFORE EXECUTION*. No safety guarantees are asserted.

---

## 2. Audit Item Disposition Matrix

| AI assistant Audit Finding | Initial Design Status | Correction Action Taken | Corrected Classification |
|---|---|---|---|
| **EBR Window Shrinkage** | Claimed constant 75.65 kWh at all timesteps | Corrected to show 6h window for $t \le 18$ shrinking to 1h ($12.61\text{ kWh}$) at $t=23$ | `VERIFIED` |
| **Terminal Target at $t=23$** | Claimed $\max(75.65\text{ kWh}, 100\text{ kWh})$ | Corrected to $\max(12.61\text{ kWh}, 100\text{ kWh}) = 100\text{ kWh}$ in Arm B-100 | `VERIFIED` |
| **Candidate 1 Infeasibility** | Cap lacked lower clamp; negative on sunny days | Candidate 1 marked `BLOCKED / NOT READY` and dropped from immediate shortlist | `VERIFIED / CORRECTED` |
| **Candidate 1 J2 Interaction** | Claimed reserve floor stays intact | Acknowledged that cap below reserve forces $s_{J2} > 0$ and triggers diesel | `VERIFIED / CORRECTED` |
| **Candidate 2 Night-Wind Clamp** | Claimed $\text{elev} \le 0$ protects night wind drops | Identified that at 68.36°N in June/July sun never sets ($\text{elev} > 0^\circ$). Clamp was inactive on test origins | `VERIFIED / CORRECTED` |
| **Candidate 2 Wind Margin (5 kW)** | Used as physical constant | Recognized as synthetic artifact of benchmark ($4500 + 5000\sin$). Removed | `VERIFIED / CORRECTED` |
| **Candidate 2 Emergency Floor** | 25,217 Wh justified by "2h start delay" | Identified that GAP19 has no start delay. Removed floor; rely on physical $E_{\min}$ | `VERIFIED / CORRECTED` |
| **Candidate 2 Safety Guarantee** | "Guaranteed 100% critical reliability" | Reclassified as hypothesis. Unconditional protection cannot be guaranteed with point forecasts | `VERIFIED / CORRECTED` |
| **Candidate 2 Input Definition** | Stated $51 \cdot I$ calculation in controller | Corrected: consumes `bundle.solar_generation.point` in Watts. No double conversion/cap | `VERIFIED / CORRECTED` |
| **Candidate 2 Demand Vector** | Assumed scalar 11.6 kW | Corrected: $\text{critical\_demand}[k] = \min(11600.0, \text{demand.point}[k])$ dynamic vector | `VERIFIED / CORRECTED` |
| **Synthetic Wind Limitation** | Treated wind forecast as realistic | Explicitly documented synthetic wind equation and lack of real-wind generalizability | `VERIFIED / CORRECTED` |
| **Candidate 3 $\lambda$ Derivation** | $\lambda = \text{marg} / \text{risk} \approx 0.00035$ | Mathematical error ($0.00025 / x < 0.00025$ for $x > 1$). Derivation removed; treated as sweep parameter | `VERIFIED / CORRECTED` |
| **Candidate 3 Zero-Code Claim** | Claimed HiGHS configuration only | Flagged that merging $J_2$ and $J_3$ requires objective code modifications | `VERIFIED / CORRECTED` |
| **Candidate 4 Attribution** | 68.4% fuel attributed to step-0 commitment | Corrected: 68.4% is total 123-origin EBR-OFF fuel reduction | `VERIFIED / CORRECTED` |
| **Candidate 4 Horizon Conflict** | Formula used $k=t..t+1$ (2h); text said 3h | Corrected to explicit 2-hour lookahead formula | `VERIFIED / CORRECTED` |
| **Candidate 4 Linearity** | Written as non-linear indicator for $t \ge 1$ | Flagged as non-linear without big-M formulation. Marked not ready | `VERIFIED / CORRECTED` |
| **Terminal Target Pruning** | Claimed +10–14% fuel saving without cost | Restored forensic fact: $-14.6\%$ fuel came with $+6.3\%$ (+20.2 kWh) unmet load. Kept separate | `VERIFIED / CORRECTED` |
| **Diagnostic Origin Overfitting** | 6 traced origins proposed as test set | Rejected due to diagnostic contamination and small sample size. Full 123 origins mandated | `VERIFIED / CORRECTED` |
| **Evaluation Dataset Labeling** | Unspecified | Labeled as pre-specified paired historical evaluation set, not a pristine holdout | `VERIFIED / CORRECTED` |
| **Reliability Metric Definition** | Used legacy campaign reliability_pct | Replaced with exact research critical-load metrics; legacy metric prohibited | `VERIFIED / CORRECTED` |
| **Arbitrary Scoring (9.4, 8.6...)** | Subjective 0–10 scores | Removed. Replaced with qualitative multi-criteria matrix | `VERIFIED / CORRECTED` |

---

## 3. Governance and Final Status

- **Production Files Modified:** 0
- **Experiments Executed:** 0
- **GAP19 Status:** UNCHANGED
- **Stage 8.1 Status:** UNCHANGED
- **Final Verdict:** `RESEARCH_DESIGN_COMPLETE — AWAITING SAFETY-GATE PREREGISTRATION`
- **Required Next Actions Before Any Controller Execution:**
  1. Preregister the precise numerical critical reliability acceptance threshold ($\epsilon_{\mathrm{tol}}$) and governance decision rule.
  2. Obtain explicit user/governance authorization for implementation of Candidate 2 (Variant S and Variant SW) within the research test harness.
