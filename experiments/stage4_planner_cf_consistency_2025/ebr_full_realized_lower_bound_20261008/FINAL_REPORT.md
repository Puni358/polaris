# POLARIS — FORMULATION G: FULL REALIZED-EBR LOWER BOUND REPORT
**Experiment ID:** `EXP-PLANNER-CF-EBR-FULL-REALIZED-LOWER-BOUND-20261008`  
**Execution Timestamp:** 2026-10-08 03:40:06 UTC  
**Governance Verdict:** `CERTIFIED LOWER BOUND`  

---

### 1. Executive Summary
Formulation G executes the approved mathematical relaxation restoring the 24-hour exogenous realized Energy Buffer Requirement (EBR) while **completely removing all terminal SOC constraints**.

Because the actual PC-SW online receding-horizon trajectory $x_{\text{real}}$ is mathematically feasible in Formulation G, the fundamental lower-bound relationship holds:
$$\text{LB}_G \le \text{objective}_G(x_{\text{real}}) = \text{PC-SW realized fuel}$$

Every single one of the 123 origins satisfies this relation with zero violations. Across all 123 origins, 123/123 achieved tight certification, and all independent feasibility, residual, and reconstruction gates passed.

---

### 2. Key Metrics & Benchmark Comparison
* **Formulation G Lower Bound ($\text{LB}_G$):** **`2403.3078 L`**
* **Base Certified Lower Bound:** `1,397.8483 L`
* **Terminal-Only Diagnostic Bound:** `3,196.1171 L`
* **Previous EBR+Terminal s0 Diagnostic:** `4,885.1972 L` (BLOCKED, diagnostic-only)
* **40% Target (60% Control 10,196.97 L):** `6,118.1827 L`
* **PC-SW Realized Reference:** `8,729.2446 L`
* **Control Reference:** `10,196.9712 L`

#### Deltas and Gaps
* **Increase over Base Certified Lower Bound:** `+1005.4595 L` (`+71.93%`)
* **Difference vs Terminal-Only Diagnostic:** `-792.8093 L`
* **Remaining Gap to 40% Target:** `3714.8749 L`
* **Remaining Gap to PC-SW Realized Fuel:** `6325.9368 L`

---

### 3. Lower-Bound Gates Evaluation
1. **Solver Optimal Solution:** PASS (123/123 optimal)
2. **Feasibility Residuals:** PASS (Max busbar residual: `2.13e-08 W`, Max battery residual: `4.63e-09 Wh`)
3. **EBR Constraints Satisfied:** PASS (Max EBR residual: `4.37e-11 Wh`)
4. **Base-Model Constraints Intact:** PASS (All original relaxations preserved)
5. **No Terminal Constraint Exists:** PASS (Verified zero terminal rows across all 123 models)
6. **No Future Realization in EBR RHS:** PASS (Verified causal NWP physics, deterministic wind/demand formulas)
7. **Lower-Bound Fuel $\le$ PC-SW Realized Fuel:** PASS (0 exceedances out of 123 origins; max violation = 0.0 L)
8. **Tight Certification Count:** PASS (123 / 123 origins certified tight)

---

### 4. Independent EBR Reconstruction Check
Reconstruction of all $123 \times 24 = 2,952$ hourly EBR targets from frozen causal NWP physics and deterministic formulas:
* **Total values checked:** 2,952
* **Maximum absolute difference:** `7.275958e-12 Wh`
* **Telemetry verification:** All `j2_shortfall_wh == 0.0` verified across all 2,952 records.

---

### 5. Slack Statistics ($s_{\text{ebr}}$)
* **Total $s_{\text{ebr}}$ across all origins:** `0.0000 Wh`
* **Origins with $s_{\text{ebr}} > 0$:** `0`
* **Min / Max / Mean / Median:** `0.0 Wh / 0.0 Wh / 0.0 Wh / 0.0 Wh`

---

### 6. Mathematical Interpretation
Because $\text{LB}_G = 2,403.3078\text{ L} \le 6,118.1827\text{ L}$, the 40% fuel-saving target is **NOT mathematically ruled out** by Formulation G alone. This lower bound does not prove achievability, but confirms that restoring the full realized EBR profile yields a certified lower bound of `2,403.3078 L` that rigorously respects the realized trajectory upper bound across the entire population.
