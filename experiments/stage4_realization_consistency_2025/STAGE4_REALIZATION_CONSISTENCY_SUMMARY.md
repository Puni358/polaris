# POLARIS Stage 4: Realization Consistency Experiment Comparison Report

**Experiment ID:** EXP-STAGE4-REALIZATION-CONSISTENCY-2025  
**Governing Preregistration:** `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md`  
**Classification:** **SAFETY-CHANGING**  
**Classification Reason:** Candidate safety gate status changed between A and B: A={'Candidate_S': True, 'Candidate_SW': False, 'Candidate_SL': True, 'Candidate_SWL': True}, B={'Candidate_S': True, 'Candidate_SW': True, 'Candidate_SL': True, 'Candidate_SWL': True}  
**Winner Under Arm A:** Candidate_S (23.11% saving)  
**Winner Under Arm B:** Candidate_SW (23.77% saving)  
**Candidate S Remains Winner:** NO  
**Production Promotion Authorized:** **NO** (Research findings only; operational policy not established)

---

## 1. Summary Metrics Comparison (Arm A vs Arm B)

| Arm | Realization | Fuel (L) | Saving (%) | R_CF (%) | R_P (%) | Min SOC (%) | SOC Violations | Unmet (kWh) | Curtail (kWh) | On Hours | Starts | EFC | Mean $\delta_c$ (W) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Control_Frozen_B | A (Current) | 6096.90 | 0.00% | 93.7538% | 83.8500% | 54.99% | 0 | 7797.27 | 10015.26 | 442 | 308 | 66.45 | 1079.58 |
| Control_Frozen_B | B (Plan-Consistent) | 5685.23 | 0.00% | 93.9752% | 78.6555% | 57.83% | 0 | 10354.71 | 11384.87 | 389 | 303 | 67.09 | 933.04 |
| Candidate_S | A (Current) | 4687.69 | 23.11% | 94.3945% | 84.6726% | 20.00% | 0 | 7428.47 | 8269.99 | 327 | 237 | 69.12 | 717.14 |
| Candidate_S | B (Plan-Consistent) | 4750.83 | 16.44% | 94.5705% | 80.4092% | 20.00% | 0 | 9469.69 | 10097.28 | 332 | 237 | 66.65 | 1002.55 |
| Candidate_SW | A (Current) | 3768.55 | 38.19% | 94.0361% | 83.2685% | 20.00% | 0 | 8140.83 | 8009.08 | 248 | 159 | 67.04 | 485.62 |
| Candidate_SW | B (Plan-Consistent) | 4333.90 | 23.77% | 94.2706% | 79.9774% | 20.00% | 0 | 9673.63 | 10044.98 | 279 | 186 | 65.49 | 1008.73 |
| Candidate_SL | A (Current) | 5280.24 | 13.39% | 94.3932% | 85.0064% | 20.00% | 0 | 7250.23 | 8655.90 | 379 | 281 | 69.29 | 806.26 |
| Candidate_SL | B (Plan-Consistent) | 5229.27 | 8.02% | 94.6114% | 80.4890% | 20.00% | 0 | 9444.77 | 10433.86 | 371 | 277 | 68.53 | 955.28 |
| Candidate_SWL | A (Current) | 5263.96 | 13.66% | 94.4946% | 85.2411% | 20.00% | 0 | 7133.65 | 8682.50 | 375 | 270 | 69.46 | 824.82 |
| Candidate_SWL | B (Plan-Consistent) | 5318.57 | 6.45% | 94.6586% | 80.5652% | 20.00% | 0 | 9402.98 | 10438.74 | 381 | 279 | 68.72 | 970.34 |

---

## 2. Safety Gates Status (Arm A vs Arm B)

| Candidate | Realization | Gate 1 (R_CF $\ge$ Ctrl) | Gate 2 (R_P $\ge$ Ctrl) | Gate 3 (SOC $\ge$ 20%) | Safety Verdict |
|---|---|---|---|---|---|
| Candidate_S | A | PASS (+0.6406 pp) | PASS (+0.8227 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_S | B | PASS (+0.5953 pp) | PASS (+1.7537 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_SW | A | PASS (+0.2823 pp) | FAIL (-0.5815 pp) | PASS (min 20.00%) | **FAIL** |
| Candidate_SW | B | PASS (+0.2954 pp) | PASS (+1.3220 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_SL | A | PASS (+0.6393 pp) | PASS (+1.1565 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_SL | B | PASS (+0.6362 pp) | PASS (+1.8335 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_SWL | A | PASS (+0.7408 pp) | PASS (+1.3911 pp) | PASS (min 20.00%) | **PASS** |
| Candidate_SWL | B | PASS (+0.6834 pp) | PASS (+1.9098 pp) | PASS (min 20.00%) | **PASS** |

---

## 3. Statistical Diesel Saving Gates (Arm A vs Arm B)

| Candidate | Realization | Diesel Saving (L) | Saving (%) | Mean Paired Saving (L) | BCa 95% CI (L) | Wilcoxon Raw $p$ | Holm Adjusted $p$ | Diesel Gate |
|---|---|---|---|---|---|---|---|---|
| Candidate_S | A | 1409.21 | 23.11% | 11.46 | [8.50, 14.32] | 2.4547e-10 | 7.3641e-10 | **PASS** |
| Candidate_S | B | 934.40 | 16.44% | 7.60 | [5.40, 9.75] | 1.9777e-09 | 5.9331e-09 | **PASS** |
| Candidate_SW | A | 2328.35 | 38.19% | 18.93 | [15.87, 21.84] | 5.0807e-17 | 2.0323e-16 | **FAIL** |
| Candidate_SW | B | 1351.33 | 23.77% | 10.99 | [8.55, 13.46] | 4.1056e-12 | 1.6422e-11 | **PASS** |
| Candidate_SL | A | 816.66 | 13.39% | 6.64 | [4.31, 8.84] | 7.1960e-07 | 1.4392e-06 | **PASS** |
| Candidate_SL | B | 455.96 | 8.02% | 3.71 | [1.78, 5.52] | 8.4891e-05 | 1.6978e-04 | **PASS** |
| Candidate_SWL | A | 832.94 | 13.66% | 6.77 | [4.38, 9.12] | 8.1659e-07 | 1.4392e-06 | **PASS** |
| Candidate_SWL | B | 366.66 | 6.45% | 2.98 | [1.03, 4.90] | 3.5829e-03 | 3.5829e-03 | **PASS** |

---

## 4. Paired A vs B Differences ($B_o - A_o$) per Arm

| Arm | Fuel Diff (L) | BCa 95% CI (L) | Holm $p$ | $\Delta R_{CF}$ (pp) | BCa 95% CI (pp) | $\Delta R_P$ (pp) | BCa 95% CI (pp) | $\Delta$ Min SOC (pp) | Mean $\delta_c$ Diff (W) |
|---|---|---|---|---|---|---|---|---|---|
| Control_Frozen_B | -411.67 | [-5.16, -1.43] | 1.5251e-03 | +0.2213 | [+0.0812, +0.3564] | -5.1945 | [-5.5715, -4.8282] | +0.60 | -3517.09 |
| Candidate_S | +63.14 | [-1.22, +2.21] | 1.0000e+00 | +0.1760 | [+0.0239, +0.3169] | -4.2635 | [-4.5993, -3.9626] | +0.60 | +6849.96 |
| Candidate_SW | +565.35 | [+2.66, +6.72] | 1.2194e-04 | +0.2345 | [+0.1148, +0.3881] | -3.2910 | [-3.6561, -2.9355] | -0.24 | +12554.53 |
| Candidate_SL | -50.97 | [-2.18, +1.34] | 1.0000e+00 | +0.2182 | [+0.0583, +0.3807] | -4.5175 | [-4.8666, -4.2033] | +0.17 | +3576.55 |
| Candidate_SWL | +54.60 | [-0.94, +1.85] | 1.0000e+00 | +0.1639 | [+0.0068, +0.2851] | -4.6759 | [-5.0189, -4.3689] | +0.29 | +3492.49 |

---

## 5. Audit Gates Summary (G1 - G11)

| Gate | Description | Status | Diagnostics |
|---|---|---|---|
| **G1** | Determinism (Arm A == Corrected Repro Telemetry) | **PASS** | Max diff: diesel 0.000000 W, chg 0.000000 W |
| **G2** | Population Accounting (123 origins, 29,520 rows) | **PASS** | Total rows: 29520 |
| **G3** | Optimizer Status (All OPTIMAL) | **PASS** | Non-optimal: 0 |
| **G4** | Route Mode Propagation | **PASS** | Mismatches: 0 |
| **G5** | EMERGENCY Rows Built (24 on EM, 0 on NORM) | **PASS** | Violations: 0 |
| **G6** | Busbar Energy Balance (|error| $\le$ 1e-3 W) | **PASS** | Max error: 0.000000 W |
| **G7** | SOC Floor Bounds & Continuity | **PASS** | Min SOC: 20.00%, Violations: 0 |
| **G8** | Fuel Accounting & Starvation Check | **PASS** | Max diff: 0.000050 L |
| **G9** | Planned vs Realized Reconciliation ($P_c, C, \delta_c$) | **PASS** | Missing: 0 |
| **G11** | Hour-0 Optimizer Identity (A == B) | **PASS** | Max diff: diesel 0.000000 W |
| **G10** | Cryptographic Hash Guards Before & After | **PASS** | Verified: 18 files |
