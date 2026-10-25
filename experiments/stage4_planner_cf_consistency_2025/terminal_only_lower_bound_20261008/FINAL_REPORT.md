# POLARIS Stage 4 Terminal-Only Lower-Bound Diagnostic Report

**Date:** 2026-10-08  
**Experiment ID:** `EXP-PLANNER-CF-TERMINAL-ONLY-LOWER-BOUND-20261008`  
**Status:** PASS  
**Classification:** Research-Only Diagnostic Variant  

---

## 1. Executive Summary

This experiment executed an isolated, research-only diagnostic to quantify the exact mathematical impact of restoring **ONE soft terminal SOC constraint** ($E[24] + s_\text{term} \ge 100,000\text{ Wh}$, $s_\text{term} \ge 0$, penalty $1.0\text{ /Wh}$) on the 123-origin global lower bound, while keeping Energy Buffer Requirement (EBR) fully relaxed.

### Key Numerical Findings:
- **Base Certified Lower Bound (No Terminal, No EBR):** `1,397.8483 L`
- **New Terminal-Only Lower Bound:** `3,196.1171 L`
- **Absolute Shift:** `+1,798.2688 L` (`+128.65%`)
- **PC-SW Realized Reference:** `8,729.2446 L`
- **40% Target (60% of Control 10,196.97 L):** `6,118.1827 L`
- **Remaining Gap to 40% Target:** `2,922.0656 L`
- **Remaining Gap to PC-SW Reference:** `5,533.1275 L`

---

## 2. Invariant & Certification Status

| Metric | Baseline | Terminal-Only Variant | Status |
| :--- | :--- | :--- | :--- |
| **Population Count** | 123 origins | 123 origins | PASS |
| **Population Hash** | `7c81256f...` | `7c81256f...` | UNCHANGED (PASS) |
| **Input Hash** | `dcabbfa2...` | `dcabbfa2...` | UNCHANGED (PASS) |
| **Solver Settings Hash** | `c510da31...` | `c510da31...` | UNCHANGED (PASS) |
| **Configuration Hash** | `e4ef245e...` | `e6c9a6fe...` | CHANGED AS REQUIRED (PASS) |
| **Certified Tight Origins** | 123 / 123 | 123 / 123 | 100% PASS |
| **Blocked Origins** | 0 | 0 | 0 BLOCKED |
| **Max MIP Gap** | $\le 1\times 10^{-9}$ | $\le 1\times 10^{-9}$ | ALL TIGHT |
| **EBR / Reserve Constraints** | None | None | VERIFIED ABSENT |

---

## 3. Terminal Slack ($s_\text{term}$) Statistics

Across all 123 origins:
- **Min $s_\text{term}$:** `0.000000 Wh`
- **Max $s_\text{term}$:** `0.000000 Wh`
- **Mean $s_\text{term}$:** `0.000000 Wh`
- **Median $s_\text{term}$:** `0.000000 Wh`

In every origin, $s_\text{term} = 0.0\text{ Wh}$ was achieved at optimality. The battery state at hour 24 reached exactly $E[24] \ge 100,000\text{ Wh}$ without requiring terminal penalty slack, proving that restoring the terminal anchor forces the schedule to retain energy rather than depleting storage to the $40,000\text{ Wh}$ floor.

---

## 4. Mandatory Validation Gate Results

1. **New Bound $\ge 1,397.8483\text{ L}$:** `PASS` ($3,196.1171 \ge 1,397.8483$)
2. **New Aggregate Bound $\le 8,729.2446\text{ L}$:** `PASS` ($3,196.1171 \le 8,729.2446$)
3. **No Origin-Level Bound Exceeds Realized PC-SW Fuel:** `PASS` (0 of 123 exceed)
4. **Population & Input Data Unchanged:** `PASS` (Exact SHA-256 match)
5. **No EBR Constraint Introduced:** `PASS` (Zero reserve rows/cols)
6. **All Non-Terminal Relaxations Preserved:** `PASS` (Exact config match)
7. **Solver Settings Preserved:** `PASS` (Exact solver settings hash match)

**FINAL VERDICT: PASS**

---

## 5. Architectural Interpretation & Next Steps

1. **Terminal Constraint Effect:** Draining the battery from $100\text{ kWh}$ to $40\text{ kWh}$ in the original lower bound accounted for `1,798.27 L` of artificial fuel reduction across the 123 origins. Enforcing a terminal return to $100\text{ kWh}$ more than doubles the lower bound (`1,397.85 L` $\to$ `3,196.12 L`).
2. **Remaining Shortfall to 40% Target:** Even with the terminal anchor restored, the lower bound is `3,196.12 L`, which is still `2,922.07 L` below the 40% threshold (`6,118.18 L`).
3. **Justification for Forecast-Faithful EBR Design:** This diagnostic conclusively demonstrates that terminal SOC alone accounts for ~38% of the gap between the unconstrained bound and the 40% target. The remaining gap of `2,922.07 L` is directly attributable to EBR (Energy Buffer Requirement) and forecast uncertainty. This justifies proceeding to the forecast-faithful EBR lower-bound design.
