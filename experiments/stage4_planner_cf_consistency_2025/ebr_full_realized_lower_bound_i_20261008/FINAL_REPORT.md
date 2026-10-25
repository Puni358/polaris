# POLARIS — FORMULATION I: FUEL-INVENTORY LOWER-BOUND TIGHTENING REPORT
**Experiment ID:** `EXP-PLANNER-CF-EBR-FULL-REALIZED-I-LOWER-BOUND-20261008`  
**Execution Timestamp:** 2026-10-08 05:14:06 UTC  
**Final Classification:** `CERTIFIED BUT NO MATERIAL TIGHTENING`  
**40% Target Status:** `40% STILL NOT RULED OUT`  

---

### 1. Executive Summary & Core Mathematical Finding
Formulation I investigates the effect of restoring the exact rolling fuel-inventory state:
$$F[0] = 100.0\text{ L}, \quad F[t+1] = F[t] - 5.0\cdot y[t] - 0.00025\cdot d[t] \ge 0 \quad (t = 0..23)$$
onto Formulation H across all 123 holdout origins.

**Rigorous Mathematical Result:**
$$\text{LB}_I \equiv \text{LB}_H = 2,408.6175\text{ L} \quad (\text{Tightening } I - H = +0.0000\text{ L})$$

**Physical Explanation:**
Formulation I minimizes total fuel subject to an upper bound of $100.0\text{ L}$ on cumulative fuel consumption ($F[t] \ge 0$). In Formulation H, the unconstrained optimal diesel dispatch consumed at most **`69.7941 L`** on any single origin (Origin 97). Because the lower-bound minimum fuel never approaches the $100.0\text{ L}$ ceiling on any origin, the fuel-inventory constraint is **strictly non-binding** everywhere in the relaxed minimization space.

Consequently, while Formulation I is 100% certified, feasible, and admissible:
* It produces **zero tightening** over Formulation H ($+0.0000\text{ L}$ / $+0.00\%$).
* All 123 origins yield identical solutions ($I \equiv H$).
* **Classification:** **`CERTIFIED BUT NO MATERIAL TIGHTENING`**.
* Because $\text{LB}_I = 2,408.6175\text{ L} \le 6,118.1827\text{ L}$, the 40% fuel-saving target is **STILL NOT RULED OUT**.

---

### 2. Pre-Execution Validation & Telemetry Findings
All pre-execution validation checks were independently verified against [`PC_HOURLY_TELEMETRY.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/experiments/stage4_planner_cf_consistency_2025/CAMPAIGN_V12_615_20261006/PC_HOURLY_TELEMETRY.csv):
1. **Grid Completeness:** 2,952 rows (123 origins $\times$ 24 hours), 0 missing, 0 NaNs.
2. **Initial Fuel:** $100.0\text{ L}$ at step 0 for all origins.
3. **Cumulative Fuel Cap:** Maximum realized fuel across all 123 origins is **`100.0000 L`** (cumulative fuel never exceeds 100.0 L).
4. **Origins Reaching Exactly 100.0 L:** Exactly **9 origins** reach $100.0000\text{ L}$ (Origins 16, 33, 39, 49, 60, 62, 99, 111, 112).
5. **Origins Exceeding Thresholds:**
   * In persisted telemetry, exactly **14 origins exceed 99.0 L** (the 9 origins at 100.0 L plus Origins 48 [99.99 L], 9 [99.84 L], 109 [99.78 L], 107 [99.69 L], 2 [99.23 L]).
   * Exactly **48 origins exceed 88.0 L**.
6. **Diesel Minimum Output:** Minimum positive diesel power = **`10,000.00 W`** (0 violations).
7. **Base Formulation:** Formulation H verified exact base with 0 terminal rows and 0 startup cost.

---

### 3. Aggregate Comparison & Metrics

| Benchmark / Metric | Value (L) | Delta vs $\text{LB}_I$ | Notes |
| :--- | :--- | :--- | :--- |
| **Formulation I Lower Bound ($\text{LB}_I$)** | **`2,408.6175 L`** | — | **123/123 certified tight** |
| **Formulation H Lower Bound ($\text{LB}_H$)** | `2,408.6175 L` | **`+0.0000 L`** | **`+0.00%` tightening ($I - H$)** |
| **Formulation G Lower Bound ($\text{LB}_G$)** | `2,403.3078 L` | `+5.3097 L` | $+0.22\%$ over Formulation G |
| **Fully Relaxed Base Bound** | `1,397.8483 L` | `+1,010.7692 L` | $+72.31\%$ over fully relaxed base |
| **Terminal-Only Diagnostic Bound** | `3,196.1171 L` | `-787.4996 L` | Single-shot terminal diagnostic |
| **40% Target (60% Control 10,196.97 L)** | `6,118.1827 L` | **`-3,709.5652 L`** | **Remaining gap I → 40% target** |
| **PC-SW Realized Fuel Reference** | `8,729.2446 L` | **`-6,320.6271 L`** | Actual PC-SW realized fuel |

---

### 4. Origin-Level Tightening Breakdown
* **Origins where $I > H$:** **0 / 123**
* **Origins where $I == H$:** **123 / 123**
* **Origins where $I < H$:** **0 / 123**
* **Origins exceeding PC-SW Actual:** **0 / 123**
* **Maximum Origin-Level Fuel in $\text{LB}_I$:** **`69.7941 L`** (Origin 97; well below 100 L)
* **Origins reaching 100 L in $\text{LB}_I$:** **0 / 123**
* **Total Tightening:** **`0.0000 L`**

---

### 5. Mandatory Certification Gates (G1–G10)

| Gate | Description | Status | Verification Details |
| :---: | :--- | :---: | :--- |
| **G1** | 123/123 origins solve optimally | **PASS** | 123/123 returned `HighsModelStatus.kOptimal` |
| **G2** | $I \le \text{PC-SW actual fuel}$ | **PASS** | 0 exceedances across all 123 origins |
| **G3** | $I \ge H$ monotonicity | **PASS** | 0 violations; 123 origins strictly equal to H |
| **G4** | Realized trajectory satisfies fuel state | **PASS** | Telemetry cumulative fuel never exceeds 100 L |
| **G5** | Objective recomputation matches formula | **PASS** | Max objective difference $\le 10^{-6}\text{ L}$ |
| **G6** | Busbar/battery/EBR residuals pass tolerances | **PASS** | Busbar max $1.25\text{ nW}$, Battery max $0.065\text{ nWh}$ |
| **G7** | Fuel-state balance residual passes | **PASS** | Fuel balance error $\le 10^{-11}\text{ L}$ |
| **G8** | Zero terminal constraints exist | **PASS** | 0 terminal rows / targets / slacks |
| **G9** | No startup cost/fuel introduced | **PASS** | Startup fuel = $0\text{ L}$ throughout |
| **G10**| No forecast assumptions introduced | **PASS** | Exogenous EBR RHS preserved identically |
