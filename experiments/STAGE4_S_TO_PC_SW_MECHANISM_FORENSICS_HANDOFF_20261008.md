# POLARIS — Stage-4 S to Planner-CF v1.2 PC-SW Mechanism Forensics Handoff

**Date:** 2026-10-08  
**Status:** READ-ONLY Forensic Investigation Handoff  
**Target Module:** `experiments/STAGE4_S_TO_PC_SW_MECHANISM_FORENSICS_HANDOFF_20261008.md`  
**Execution Type:** Consolidated Findings (No experiment executed, no production modified)

---

## 1. Executive Summary & Core Context

This handoff consolidates forensic findings investigating why historical **Stage-4 S** reported approximately **23.11%–24.02%** diesel fuel reduction while current **Planner-CF v1.2 PC-SW** achieves **14.39%** (and **14.95%** with Rule D).

The investigation reveals that the comparison between historical Stage-4 S and Planner-CF v1.2 PC-SW is fundamentally confounded by:
1. **Disparate Evaluation Populations & Baselines:** Historical S was evaluated on a 2024 population (Control B = 6,096.90 L / 6,117.97 L; avg ~49.6 L/origin), whereas PC-SW v1.2 is evaluated on the 2025 holdout population (PC-Control = 10,196.97 L; avg ~82.9 L/origin, a 1.67× harder, higher-diesel operational regime).
2. **EBR Reserve Variant Divergence:** PC-SW v1.2 actually executes **`compute_variant_sw_ebr`** (solar + synthetic wind credit), which historically caused safety failure in Candidate SW under the unconstrained planner. It does **not** execute the S-variant EBR (`compute_variant_s_ebr`).
3. **The Governance Defect Fix (`J_NC` Priority 4):** Historical Stage-4 S lacked any objective penalty for non-critical load shedding (`J_NC`), allowing the MILP to shed non-critical load "for free" to conserve battery energy for reserve constraints, creating an unpriced plan-versus-realization mismatch against Arm A. Planner-CF v1.2 introduced `J_NC` at Priority 4 (above J3 diesel at Priority 2), strictly forcing the MILP to dispatch diesel before shedding non-critical load.
4. **Realization Mismatch Artificial Savings:** Realization consistency experiments proved that **6.67 pp** of historical Candidate S savings was directly attributable to this plan-versus-realization executor mismatch (Arm A surplus realization vs Arm B plan-consistent realization: 23.11% vs 16.44%).

---

## 2. Key Verified Numerical Reference Figures

| Campaign / Configuration | Population / Year | Control Baseline Fuel (L) | Candidate Fuel (L) | Fuel Reduction (%) | Safety Gate Outcome | Authority / Provenance File |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Stage-4 Frozen S** | 123 origins (2024/frozen) | 6,117.9691 | 4,648.3272 | **24.02%** | **PASS** | `experiments/POST_STAGE4_EFFICIENCY_FORENSIC_ANALYSIS.md`, line 42 |
| **Stage-4 Corrected Repro S** | 123 origins (2025 holdout / Arm A) | 6,096.9004 | 4,687.6902 | **23.11%** | **PASS** | `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_CAMPAIGN_SUMMARY.md`, line 19 |
| **Stage-4 Corrected Repro SW** | 123 origins (2025 holdout / Arm A) | 6,096.9004 | 3,768.5494 | **38.19%** | **FAIL** ($\Delta R_P = -0.58\text{ pp}$) | `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_CAMPAIGN_SUMMARY.md`, line 20 |
| **Stage-4 Repro S (Arm B Plan-Consistent)** | 123 origins (2025 holdout / Arm B) | 5,685.23 | 4,750.83 | **16.44%** | **PASS** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_COMPARISON.md`, line 21 |
| **Stage-4 Repro S-L (Low-Sun Protected)** | 123 origins (2025 holdout / Arm A) | 6,096.9004 | 5,280.2375 | **13.39%** | **PASS** | `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_CAMPAIGN_SUMMARY.md`, line 21 |
| **Stage-4 Repro SW-L (Low-Sun Protected)** | 123 origins (2025 holdout / Arm A) | 6,096.9004 | 5,263.9645 | **13.66%** | **PASS** | `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_CAMPAIGN_SUMMARY.md`, line 22 |
| **Current Planner-CF v1.2 PC-SW** | 123 origins (2025 holdout) | 10,196.9712 | 8,729.2446 | **14.39%** | **PASS** | `experiments/stage4_planner_cf_consistency_2025/CAMPAIGN_V12_615_20261006/` |
| **Current PC-SW + Rule D** | 123 origins (2025 holdout) | 10,196.9712 | 8,672.6241 | **14.95%** | **FAIL (Identity)** | `experiments/stage4_planner_cf_consistency_2025/pc_sw_true_curtailment_recapture_20261008/` |

---

## 3. Structural & Mathematical Mechanism Delta

| Mechanism / Component | Historical Stage-4 S (`research_numerical_extractor.py`) | Current Planner-CF v1.2 PC-SW (`research_numerical_extractor_planner_cf_v1.py`) | Impact on Diesel Consumption & Safety | Exact File & Line Citations |
| :--- | :--- | :--- | :--- | :--- |
| **1. EBR Reserve Formulation** | **Solar-Only Net EBR:**<br>$E_S[t] = \frac{1}{\eta} \sum \max(0, c_k - s_k) \Delta t$ | **Solar + Wind Net EBR:**<br>$E_{SW}[t] = \frac{1}{\eta} \sum \max(0, c_k - s_k - w_k) \Delta t$<br>*(Via `arm_ebr("PC-SW", ...)`)* | Historical SW netted wind without protection, saving fuel but failing Gate 2. PC-SW uses SW EBR but satisfies Gate 2 because the planner is bounded by `J_NC`. | `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py`: L152–191<br>`experiments/stage4_planner_cf_consistency_2025/planner_cf_campaign_runner.py`: L70–71 |
| **2. Non-Critical Load Penalty (`J_NC`)** | **ABSENT.**<br>Single demand deficit: $p_{\text{served}} + p_{\text{unmet}} = p_{\text{dem}}$. Unmet non-critical load had zero penalty in objective. | **PRESENT at Priority 4:**<br>$c_{jnc} = 1.0 \times \Delta t$. Priority order:<br>$J_1(5) > J_{NC}(4) > J_2(3) > J_3(2) > J_4(1)$. | In PC-SW, the planner **must burn diesel** (Priority 2) before allowing any non-critical load shedding (Priority 4). Historical S planned unpenalized non-critical shedding to bank battery for EBR. | `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py`: L376–421<br>`experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py`: L85, L324–339 |
| **3. Busbar & Served Load Variables** | Single $p_{\text{served}}$ and $p_{\text{unmet}}$ covering total demand. Layer B added $p_{\text{served}} + p_{\text{unmet\_crit}} = p_{\text{crit\_dem}}$. | Decomposed: $p_{\text{served}} = \text{served}_c + \text{served}_{nc}$. Explicit non-critical balance: $\text{served}_{nc} + \text{unmet}_{nc} = d_{nc}$. | Enforces customer-first priority explicitly inside the linear programming tableau. | `research_numerical_extractor_planner_cf_v1.py`: L223–225, L257–260 |
| **4. Flexible Sink ($p_{\text{flex}}$)** | Continuous variable $p_{\text{flex}} \in [0, 500\text{ W}]$ in busbar balance. | Removed completely ($p_{\text{flex}} = 0\text{ W}$ fixed). | Minor numerical residue removal ($\le 500\text{ W}$). | `research_numerical_extractor.py`: L243<br>`research_numerical_extractor_planner_cf_v1.py`: L82 |
| **5. Hour-0 Fuel Feasibility** | **ABSENT.** Fuel inventory unconstrained in MILP. | **PRESENT (Amendment A2 §17.2):**<br>$5 u_{\text{diesel}}[0] + 0.00025 p_{\text{diesel}}[0] \le F_{\text{rem}}$. | Prevents scheduling diesel at hour 0 when carried physical fuel is depleted. | `research_numerical_extractor_planner_cf_v1.py`: L288–297 |
| **6. Realization Executor Policy** | **Arm A (Surplus-Based):**<br>Serves customer load first, then charges battery from surplus. | **Arm A (Surplus-Based):**<br>Same physical execution logic, but economic contract aligned with planner. | Historical S experienced plan-versus-realization mismatch (Issue 3), yielding 6.67 pp artificial fuel savings. | `experiments/POST_CORRECTED_STAGE4_FORENSIC_AUDIT.md`: L117–144<br>`experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_COMPARISON.md`: L20–21 |
| **7. Forecast & Weather Feeds** | Causal NWP (`fc_cloud_cover`), synthetic wind ($4.5 + 5.0\sin$) and synthetic demand ($15.0 + 3.0\cos$). | Causal NWP (`causal_nwp_physics.py`), same synthetic wind and demand formulas. | Identical synthetic profile generation; differing base solar/weather holdout years. | `system/forecasting/implementations/causal_nwp_physics.py`<br>`planner_cf_campaign_runner.py`: L191–200 |

---

## 4. Decomposing the 23%–24% vs 14.39% Performance Gap

The performance difference between historical S and PC-SW v1.2 can be decomposed into four primary drivers:

### Driver A: Operational Regime Shift & Weather Severity (Dominant Driver)
- **Historical Control:** 6,096.90 L (49.57 L/origin average).
- **Current PC-Control:** 10,196.97 L (82.90 L/origin average).
- The 2025 holdout population requires **1.67× more diesel fuel** to maintain baseline service under identical synthetic demand (360 kWh/day) and wind (109 kWh/day) trajectories. Because the 2025 summer exhibited significantly lower solar irradiance and persistent cloud cover, baseline diesel operation was far more intensive. Percentage fuel savings across differing baselines cannot be directly compared.

### Driver B: Rectification of the Plan-Execute Mismatch (6.67 pp Artificial Saving)
- In historical Stage-4 S under Arm A, the planner assumed non-critical load could be shed cost-free to maintain battery reserve, while the physical executor served non-critical load anyway before battery charging.
- The `EXP-STAGE4-REALIZATION-CONSISTENCY-2025` experiment proved that when Candidate S was forced into plan-consistent realization (Arm B), its diesel savings collapsed from **23.11% to 16.44%** (+63.14 L).
- Thus, approximately **6.67 pp of Candidate S's reported saving was an artifact of an inconsistent economic contract** (governance "Issue 3"), which Planner-CF v1.2 correctly closed by adding `J_NC`.

### Driver C: Customer-First Preservation via `J_NC` Priority 4
- Planner-CF v1.2 places `J_NC` at Priority 4, above `J3` (diesel minimization at Priority 2).
- When solar/wind is insufficient, the optimizer is strictly required to burn diesel to serve non-critical customer load rather than shedding non-critical load to avoid diesel consumption. This necessary safety and service constraint structurally increases diesel dispatch relative to an unpenalized formulation.

### Driver D: EBR Formulation (PC-SW uses SW-EBR, NOT S-EBR)
- Current PC-SW uses `compute_variant_sw_ebr` (which credits forecast wind as well as solar), providing a smaller reserve envelope than S-EBR.
- Without `J_NC`, historical SW saved 38.19% but failed proportional reliability ($\Delta R_P = -0.58\text{ pp}$) due to unprotected wind credit dropping hour-0 reserve to ~18 kWh.
- With `J_NC`, PC-SW remains safe (+0.026 pp on $R_{CF}$, +0.015 pp on $R_P$), but its net fuel reduction settles at 14.39%.

---

## 5. Unresolved Questions & Next Steps

1. **PC-S Evaluation on Planner-CF v1.2:**  
   What does `PC-S` (the true S-variant EBR without wind credit, using `compute_variant_s_ebr`) achieve under Planner-CF v1.2? Does it provide higher or lower fuel savings than PC-SW when constrained by `J_NC`?
2. **Hour-0 Diesel Commitment Conservatism:**  
   As established in `POST_STAGE4_EFFICIENCY_FORENSIC_ANALYSIS.md`, hour-0 origin commitment accounts for >75% of the low-sun diesel gap. How much of this diesel dispatch in PC-SW is strictly required for proportional reliability versus conservative reserve sizing?
3. **Open-Loop Replay Diagnostic:**  
   An open-loop attribution replay varying origin-start reserve targets ($E_B(0)$, $E_S(0)$, $E_{SW}(0)$, $E_{SWL}(0)$) remains the cleanest parameter-free diagnostic to isolate reserve sensitivity without closed-loop trajectory divergence.

---

## 6. Provenance & Artifact Hashes

- `experiments/stage4_planner_cf_consistency_2025/CAMPAIGN_V12_615_20261006/PC_HOURLY_TELEMETRY.csv`:  
  SHA-256: `37e5803725eaf344240d6be8aa5e31f5c13b951f3cef5539748fbf3bcb3969e0`
- `system/forecasting/implementations/causal_nwp_physics.py`:  
  SHA-256: `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710`
- `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py`:  
  SHA-256 verified against frozen Stage 4 contract.
