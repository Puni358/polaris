# POLARIS Stage 4: Realization Consistency Execution Audit Report

**Experiment ID:** `EXP-STAGE4-REALIZATION-CONSISTENCY-2025`  
**Governing Contract:** `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md`  
**Date:** 2026-10-06  
**Overall Audit Result:** **ALL 10 AUDIT GATES PASSED (G1 – G11)**

---

## 1. Audit Gates Detailed Verification

### G1 — Determinism vs Corrected Reproduction Telemetry
- **Specification:** Arm A must reproduce the corrected reproduction telemetry in `STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv` for all 14,760 rows (`diesel_power`, `battery_charge`, `battery_discharge`, `soc_after`, `unmet_load`, tolerance $\le 10^{-5}$ W / $10^{-4}$ %).
- **Observed:**
  - `max_diff_diesel_w`: $0.000000\text{ W}$
  - `max_diff_battery_charge_w`: $0.000000\text{ W}$
  - `max_diff_battery_discharge_w`: $0.000000\text{ W}$
  - `max_diff_soc_after_pct`: $0.000000\%$
  - `max_diff_unmet_load_w`: $0.000000\text{ W}$
- **Status:** **PASS**

### G2 — Population Accounting
- **Specification:** Exactly 123 unique origins per realization; exactly 2,952 hourly rows per arm-realization; total 14,760 per realization and 29,520 across both realizations. Zero duplicate origins.
- **Observed:**
  - `unique_origins_a`: 123
  - `unique_origins_b`: 123
  - `total_rows`: 29,520
  - `expected_rows`: 29,520
- **Status:** **PASS**

### G3 — Optimizer Status
- **Specification:** Every step `HighsModelStatus.kOptimal` (no infeasible, no time-limit).
- **Observed:**
  - `HighsModelStatus.kOptimal`: 29,520 / 29,520 steps (100.0%)
  - Non-optimal count: 0
- **Status:** **PASS**

### G4 — Route Mode Propagation
- **Specification:** `optimizer_received_mode == route` on every row.
- **Observed:**
  - Mismatches: 0 / 29,520
- **Status:** **PASS**

### G5 — EMERGENCY Rows Built
- **Specification:** On every EMERGENCY step, the MILP must build exactly 24 EMERGENCY rows (verified via `highspy.Highs.addRow` spy). Under NORMAL mode, exactly 0 rows.
- **Observed:**
  - Violations: 0 / 29,520
- **Status:** **PASS**

### G6 — Busbar Energy Balance
- **Specification:** $|S_{\text{avail}} - (\text{served} + C + F + \text{curt})| \le 10^{-3}\text{ W}$ on every step in both arms.
- **Observed:**
  - Maximum balance error across all 29,520 hours: $0.000000\text{ W}$
- **Status:** **PASS**

### G7 — SOC Accounting and Continuity
- **Specification:** Realized SOC bounded in $[19.999\%, 95.001\%]$, zero hours $< 20.00\%$.
- **Observed:**
  - Minimum realized SOC: $20.00\%$
  - Maximum realized SOC: $95.00\%$
  - Floor violations count: 0
- **Status:** **PASS**

### G8 — Fuel Accounting
- **Specification:** Accounted fuel equals $5 \cdot \text{on\_hours} + 0.25 \cdot \text{kWh}$ on every row except recorded starvation rows, which are listed and counted.
- **Observed:**
  - Starvation rows count: 1 (Origin 39, Candidate SW, Realization A, Hour 22: fuel remaining was 3.6293 L, below 5 L/h base consumption, consumed remaining fuel to 0.0 L).
  - Maximum fuel discrepancy across all 29,519 non-starvation rows: $0.000000\text{ L}$.
- **Status:** **PASS**

### G9 — Planned vs Realized Charge Reconciliation
- **Specification:** Complete recording of $P_c$, $C$, $\delta_c$, plan served, realized served, plan unmet, realized unmet on every row.
- **Observed:**
  - Missing or NaN fields: 0
- **Status:** **PASS**

### G11 — Hour-0 Optimizer Identity
- **Specification:** For every origin and candidate, the hour-0 optimizer inputs (state, forecasts, route, EBR vector, terminal target) and outputs ($p_{\text{diesel}}, p_{\text{chg}}, p_{\text{dis}}, p_{\text{served}}, p_{\text{unmet}}, p_{\text{flex}}, v_{\text{start}}$, J1–J4) must be identical between arms A and B.
- **Observed:**
  - Maximum difference across all inputs, dispatch variables, and objectives: $0.000000\text{ W}$
- **Status:** **PASS**

### G10 — Cryptographic Hash Guards
- **Specification:** All 18 reference and implementation hashes verified before and after execution.
- **Observed:**
  - All 18 files verified intact before run and after run. Zero modifications to production code, frozen Stage 4, or corrected reproduction.
- **Status:** **PASS**
