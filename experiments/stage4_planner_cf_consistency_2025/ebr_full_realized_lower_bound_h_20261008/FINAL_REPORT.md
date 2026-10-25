# POLARIS — FORMULATION H: LOWER-BOUND TIGHTENING REPORT
**Experiment ID:** `EXP-PLANNER-CF-EBR-FULL-REALIZED-H-LOWER-BOUND-20261008`  
**Execution Timestamp:** 2026-10-08 03:56:04 UTC  
**Final Classification:** `CERTIFIED BUT NO MATERIAL TIGHTENING`  
**40% Target Status:** `BELOW 6,118.1827 L → 40% still not ruled out`  

---

### 1. Executive Summary & Objective
Formulation H investigates whether restoring the physical $10\text{ kW}$ diesel minimum-output constraint ($d[t] \ge 10000 \cdot y[t]$) onto Formulation G materially tightens the certified lower bound toward the 40% fuel-saving target ($6,118.1827\text{ L}$).

**Key Finding:**  
Restoring the diesel minimum constraint is mathematically certified, monotonically non-decreasing ($H \ge G$ across all 123 origins), and strictly bounded above by actual PC-SW fuel ($H \le \text{PC-SW realized}$ across all 123 origins). However, it produces **only $+5.3097\text{ L}$ ($+0.22\%$) of aggregate tightening** across the entire 123-origin population:
* **Formulation G Lower Bound:** `2,403.3078 L`
* **Formulation H Lower Bound:** `2,408.6175 L`
* **Tightening ($H - G$):** `+5.3097 L` (`+0.22%`)
* **Classification:** **`CERTIFIED BUT NO MATERIAL TIGHTENING`**

Because $\text{LB}_H = 2,408.6175\text{ L} \le 6,118.1827\text{ L}$, the 40% fuel-saving target is **STILL NOT RULED OUT**.

---

### 2. Mandatory Validity Requirement Check
Before solving, the PC-SW realized trajectory was audited for the diesel minimum condition:
* Total hourly records audited: 2,952 ($123 \times 24$)
* Operating diesel hours ($d > 0$): 547
* **Minimum positive diesel power observed:** **`10,000.00 W`**
* **Violations ($0 < d < 10,000$):** **0**
* **Status:** **PASSED**. The actual PC-SW execution never operated below $10\text{ kW}$, confirming that Formulation H is an unassailable mathematical relaxation of the realized system.

---

### 3. Aggregate Comparison & Metrics

| Benchmark / Metric | Value (L) | Delta vs $\text{LB}_H$ | Notes |
| :--- | :--- | :--- | :--- |
| **Formulation H Lower Bound ($\text{LB}_H$)** | **`2,408.6175 L`** | — | **123/123 certified tight** |
| **Formulation G Lower Bound ($\text{LB}_G$)** | `2,403.3078 L` | **`+5.3097 L`** | **`+0.22%` tightening** |
| **Fully Relaxed Base Bound** | `1,397.8483 L` | `+1,010.7692 L` | `+72.31%` over fully relaxed base |
| **Terminal-Only Diagnostic Bound** | `3,196.1171 L` | `-787.4996 L` | Single-shot terminal diagnostic |
| **40% Target (60% Control 10,196.97 L)** | `6,118.1827 L` | **`-3,709.5652 L`** | **Remaining gap H → 40% target** |
| **PC-SW Realized Reference** | `8,729.2446 L` | **`-6,320.6271 L`** | Actual PC-SW fuel consumption |

---

### 4. Origin-Level Tightening Breakdown
* **Origins where $H > G$:** **7 / 123**
  * Origin 5: $7.0585\text{ L} \to 7.5000\text{ L}$ ($+0.4415\text{ L}$)
  * Origin 6: $6.4903\text{ L} \to 7.5000\text{ L}$ ($+1.0097\text{ L}$)
  * Origin 21: $6.7277\text{ L} \to 7.5000\text{ L}$ ($+0.7723\text{ L}$)
  * Origin 44: $7.0852\text{ L} \to 7.5000\text{ L}$ ($+0.4148\text{ L}$)
  * Origin 64: $6.7568\text{ L} \to 7.5000\text{ L}$ ($+0.7432\text{ L}$)
  * Origin 86: $7.3600\text{ L} \to 7.5000\text{ L}$ ($+0.1400\text{ L}$)
  * Origin 105: $5.7118\text{ L} \to 7.5000\text{ L}$ ($+1.7882\text{ L}$)
* **Origins where $H == G$:** **116 / 123**
* **Maximum origin-level tightening:** `+1.7882 L` (Origin 105)
* **Minimum positive tightening:** `+0.1400 L` (Origin 86)
* **Origins where $H < G$:** **0**
* **Origins where $H > \text{PC-SW Realized}$:** **0**

---

### 5. Why Does Diesel Minimum Tighten by Only 5.31 L?
In Formulation G, the diesel on-off fixed cost is $5.0\text{ L/h}$ whenever $y[t]=1$.
Because turning on the diesel already costs $5.0\text{ L}$ plus $0.00025 \times \text{power}$, the solver only turns on the generator when a substantial energy deficit exists. In 116 out of 123 origins, whenever the generator turned on in Formulation G, it was already dispatched at $\ge 10\text{ kW}$ to serve busbar demand or charge the battery efficiently.
Only in 7 origins did Formulation G dispatch the generator for a single hour at $< 10\text{ kW}$ (e.g., $2\text{--}8\text{ kW}$). Forcing those 7 origins to generate at least $10\text{ kW}$ moved their 1-hour generation fuel from $(5.0 + 0.00025 \times \text{power})$ to exactly $5.0 + 0.00025 \times 10,000 = 7.5000\text{ L}$, producing the observed $+5.31\text{ L}$ total difference.

---

### 6. Gate Compliance Summary
* **Gate 1 (Solver Optimal):** PASS (123/123 origins optimal)
* **Gate 2 (Feasibility Residuals):** PASS (Busbar max $1.25\text{ nW}$, Battery max $0.065\text{ nWh}$)
* **Gate 3 (EBR Constraints Satisfied):** PASS (Max EBR residual $0.029\text{ nWh}$)
* **Gate 4 (Diesel Min Satisfied):** PASS (All origins satisfy $d \ge 10000 \cdot y$)
* **Gate 5 (No Terminal Constraint):** PASS (0 terminal rows/slacks)
* **Gate 6 (H >= G Monotonicity):** PASS (0 violations)
* **Gate 7 (LB_H <= PC-SW Actual):** PASS (0 exceedances; max violation = $0.0\text{ L}$)
* **Gate 8 (123/123 Tight Certification):** PASS (123 certified tight)
