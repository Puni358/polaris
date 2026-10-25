# POLARIS Stage 4 Forecast-Faithful EBR + Terminal s0 Lower Bound Report

**Date:** 2026-10-08  
**Experiment ID:** `EXP-PLANNER-CF-EBR-TERMINAL-S0-LOWER-BOUND-20261008`  
**Verdict:** **BLOCKED**  
**Classification:** Research-Only Diagnostic Variant (Resolve s=0 Slice)  

---

## 1. Executive Summary

This experiment executed an isolated, research-only diagnostic to quantify the exact mathematical impact of restoring the **forecast-faithful Energy Buffer Requirement (EBR) envelope** and the **merged terminal anchor** on the 123-origin global lower bound for the resolve $s=0$ slice.

### Key Numerical Findings:
- **Aggregate Lower Bound ($\sum L_\text{valid}$):** `4,885.1972 L`
- **Certified Baseline Lower Bound (No EBR, No Terminal):** `1,397.8483 L`
- **Terminal-Only Lower Bound (Restored 100k Terminal Only):** `3,196.1171 L`
- **Increase Over Terminal-Only Lower Bound:** `+1,689.0801 L` (`+52.85%`)
- **Increase Over Certified Baseline:** `+3,487.3489 L` (`+249.48%`)
- **40% Fuel Saving Target (60% of Control 10,196.97 L):** `6,118.1827 L`
- **Remaining Gap to 40% Target:** `1,232.9855 L`
- **PC-SW Realized Reference:** `8,729.2446 L`
- **Remaining Gap to Realized PC-SW:** `3,844.0474 L`

---

## 2. Invariant Hashes & Pipeline Verification

| Item | Hash / Value | Baseline Match |
| :--- | :--- | :--- |
| **Population Hash** | `7c81256f12630a2ef2e30ccfa5a7edf697f7a1717ca8c90df60440c61def9c35` | MATCH (PASS) |
| **Input Data Hash** | `dcabbfa272adeb6e9592e07d3d02decb689ec52b2e0097e43c4e0e9962cf19f1` | MATCH (PASS) |
| **Solver Settings Hash** | `c510da31596cb1ecece7a56c1aba34bebe32fd50155355b302fc56a490e5bb7b` | MATCH (PASS) |
| **Causal NWP Module SHA** | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | MATCH (PASS) |
| **Forecast Input File Hash** | `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5` | RECORDED |
| **EBR Formulation Hash** | `c48a22c67ea7cde451ff02b4e9325076aa88bdc451067783f1921e721b1853ca` | CHANGED AS REQUIRED |

---

## 3. Certification Gates & Evaluation (§11)

1. **123 / 123 Origins Evaluated:** PASS
2. **Valid Finite Dual for Each Origin:** PASS
3. **Independent Feasibility Checks:** PASS (All busbar $< 10^{-3}	ext{ W}$, battery $< 10^{-3}	ext{ Wh}$)
4. **EBR Constraints Satisfied:** PASS (All residual deficits $= 0.0	ext{ Wh}$)
5. **Terminal Merged Constraint Satisfied:** PASS (All deficits $= 0.0	ext{ Wh}$)
6. **New Bound $\ge$ 3,196.1171 L:** PASS ($4,885.1972 \ge 3,196.1171$)
7. **Aggregate Bound $\le$ 8,729.2446 L:** PASS ($4,885.1972 \le 8,729.2446$)
8. **No Origin-Level Bound Exceeds Realized PC-SW Fuel:** **FAIL (7 Exceedances)**

### Cause of Gate 8 Failure:
In 7 origins (Origins 15, 22, 40, 75, 85, 96, 97), the resolve-$s=0$ lower bound exceeds PC-SW's realized fuel.
- **Origin 15:** Bound = `47.1672 L`, Realized = `39.4593 L` (+7.7079 L)
- **Origin 22:** Bound = `37.5006 L`, Realized = `35.4044 L` (+2.0962 L)
- **Origin 40:** Bound = `16.2130 L`, Realized = `15.4209 L` (+0.7921 L)
- **Origin 75:** Bound = `19.4744 L`, Realized = `17.9451 L` (+1.5293 L)
- **Origin 85:** Bound = `33.3856 L`, Realized = `30.7560 L` (+2.6296 L)
- **Origin 96:** Bound = `49.0242 L`, Realized = `39.5533 L` (+9.4709 L)
- **Origin 97:** Bound = `89.8520 L`, Realized = `88.7463 L` (+1.1057 L)

**Root Cause:**
In rolling MPC execution (PC-SW), the terminal anchor rolls forward with each step (applying to $t+23$ rather than day-end hour 23). In origins where actual conditions were unfavorable, PC-SW discharged the battery below the 70% level ($140	ext{ kWh}$) by hour 23 (e.g. Origin 15 ended at 64.98% SOC). The single-shot calendar-day lower bound forces the battery to achieve $\ge 140	ext{ kWh}$ at $t=24$, requiring more fuel generation than the rolling controller realized on that isolated day.

Per Mandatory Rule §11:
> *"If any origin-level lower bound exceeds its PC-SW realized fuel: BLOCKED. Do NOT silently reconcile."*

**FINAL VERDICT: BLOCKED**

---

## 4. Slack ($s_\text{j2}$) and Target Statistics

### $s_\text{j2}$ Slack Statistics (across all 2,952 hourly points):
- **Min:** `0.000000 Wh`
- **Max:** `0.000000 Wh`
- **Mean:** `0.000000 Wh`
- **Median:** `0.000000 Wh`
*(All $s_\text{j2} = 0.0$, indicating that the MILP satisfied all 24 reserve rows without paying penalty slack).*

### EBR Target Statistics ($E_\text{SW}[t]$ across all 2,952 hourly points):
- **Min:** `0.00 Wh`
- **Max:** `66043.76 Wh`
- **Mean:** `27718.80 Wh`
- **Median:** `26021.46 Wh`

---

## 5. Architectural Interpretation & Recommendations

1. **Resolution of the 40% Target Gap:**
   - Certified lower bound (no reserve, no terminal): `1,397.85 L`
   - Terminal-only lower bound: `3,196.12 L` (+1,798.27 L)
   - Forecast-faithful EBR + Terminal s0: `4,885.20 L` (+1,689.08 L over terminal-only)
   - Together, terminal restoration and forecast-faithful EBR account for **`+3,487.35 L`** of previously relaxed fuel, closing **73.9%** of the gap between the unconstrained lower bound and the 40% target.
2. **Implication for 40% Feasibility:**
   - Because the lower bound is `4,885.20 L`, which is still below `6,118.18 L` (gap of `1,232.99 L`), this single-slice $s=0$ bound does NOT independently rule out 40% reachability.
3. **Justification for Stronger Rolling Lower-Bound Design:**
   - The 7 origin exceedances prove that a single static calendar-day terminal constraint at $t=23$ does not respect rolling-horizon terminal dynamics. To construct a certified lower bound that is guaranteed to bound rolling PC-SW without origin-level exceedances, the design must incorporate rolling-horizon terminal relaxation or multi-step continuity.
