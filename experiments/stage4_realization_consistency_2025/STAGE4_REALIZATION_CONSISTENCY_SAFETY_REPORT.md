# POLARIS Stage 4: Realization Consistency Safety Report

**Experiment ID:** `EXP-STAGE4-REALIZATION-CONSISTENCY-2025`  
**Governing Contract:** `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md`  
**Date:** 2026-10-06  
**Safety Classification Verdict:** **SAFETY-CHANGING**

---

## 1. Safety Gates Specification

For each realization $r \in \{A, B\}$ and candidate $c \in \{S, SW, S-L, SW-L\}$, evaluated against Control B under the **same** realization:
- **Gate 1 (Critical-First Reliability):** $\Delta R_{\text{CF}} = R_{\text{CF}}(c, r) - R_{\text{CF}}(\text{Control}, r) \ge 0.00\text{ pp}$.
- **Gate 2 (Proportional Critical Reliability):** $\Delta R_P = R_P(c, r) - R_P(\text{Control}, r) \ge 0.00\text{ pp}$.
- **Gate 3 (SOC Floor Protection):** Zero hours with realized SOC $< 20.00\%$ (min SOC $\ge 20.00\%$).

---

## 2. Realization A Safety Evaluation (Current Realization Semantics)

*Control B (A) Reference:* Fuel = 6,096.90 L | $R_{\text{CF}} = 93.7538\%$ | $R_P = 83.8500\%$ | Min SOC = 54.99% | Violations = 0

| Candidate | $\Delta R_{\text{CF}}$ (pp) | Gate 1 | $\Delta R_P$ (pp) | Gate 2 | Min SOC (%) | Gate 3 | Safety Verdict |
|---|---|---|---|---|---|---|---|
| **Candidate S** | $+0.6406$ | **PASS** | $+0.8227$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |
| **Candidate SW** | $+0.2823$ | **PASS** | **$-0.5815$** | **FAIL** | 20.00% | **PASS** | **DISQUALIFIED** |
| **Candidate S-L** | $+0.6393$ | **PASS** | $+1.1565$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |
| **Candidate SW-L** | $+0.7408$ | **PASS** | $+1.3911$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |

*Under Realization A, Candidate SW suffers a $-0.5815\text{ pp}$ drop in proportional reliability relative to Control B, failing Gate 2 and disqualifying it from competition.*

---

## 3. Realization B Safety Evaluation (Plan-Consistent Diagnostic Realization Semantics)

*Control B (B) Reference:* Fuel = 5,685.23 L | $R_{\text{CF}} = 93.9752\%$ | $R_P = 78.6555\%$ | Min SOC = 57.83% | Violations = 0

| Candidate | $\Delta R_{\text{CF}}$ (pp) | Gate 1 | $\Delta R_P$ (pp) | Gate 2 | Min SOC (%) | Gate 3 | Safety Verdict |
|---|---|---|---|---|---|---|---|
| **Candidate S** | $+0.5953$ | **PASS** | $+1.7537$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |
| **Candidate SW** | $+0.2954$ | **PASS** | **$+1.3220$** | **PASS** | 20.00% | **PASS** | **QUALIFIED** |
| **Candidate S-L** | $+0.6362$ | **PASS** | $+1.8335$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |
| **Candidate SW-L** | $+0.6834$ | **PASS** | $+1.9098$ | **PASS** | 20.00% | **PASS** | **QUALIFIED** |

*Under Realization B, because planned charging is prioritized before uncoordinated non-critical load service, Control B serves less non-critical load ($R_P$ drops to $78.66\%$). Candidate SW maintains $R_P = 79.98\%$, exceeding Control B by $+1.3220\text{ pp}$ and passing Gate 2.*

---

## 4. Root Cause of the Safety Flip

1. **In Arm A:** The realization executor serves all available energy to total demand first (`served = min(demand, supply)`). Non-critical demand absorbs the power that the MILP planned to store in the battery. Control B runs diesel more aggressively to cover energy later, achieving higher proportional load service ($83.85\%$). Candidate SW sheds non-critical load in its plan, but the realization executor cannot sustain both non-critical load and battery charging, causing Candidate SW to drop below Control B in proportional service ($-0.58\text{ pp}$).
2. **In Arm B:** The realization executor reserves planned charging from available supply before non-critical load. Control B's uncoordinated non-critical service falls by $-5.19\text{ pp}$ (from $83.85\%$ to $78.66\%$). Candidate SW's planned charging is realized, protecting battery energy and enabling it to outperform Control B ($+1.32\text{ pp}$).
3. **Conclusion:** Candidate SW's safety disqualification in Stage 4 is an artifact of the planned-vs-realized charge mismatch in the research executor, not an intrinsic physical infeasibility of the solar+wind EBR policy.
