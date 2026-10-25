# POLARIS Stage 4: Safety Gates Evaluation Report (2025 Holdout)

**Experiment:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`  
**Governing Document:** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md`  
**Population:** 123 origins (2025-05-01 through 2025-08-31), 2,952 hours per arm, 14,760 total arm-hours  
**Safety Contract Hierarchy:** Safety strictly precedes efficiency. A candidate failing ANY safety gate is rejected regardless of fuel.

---

## 1. Safety Gates Contract Definition

All candidates are evaluated against **Control Frozen B** re-executed on the identical 2025 origins under identical execution machinery:
1. **Gate 1 (Critical-First Reliability):**
   $$\Delta R_{CF} = R_{CF}(\text{candidate}) - R_{CF}(\text{Control B}) \ge 0.00\text{ pp}$$
2. **Gate 2 (Proportional Critical Reliability):**
   $$\Delta R_{P} = R_{P}(\text{candidate}) - R_{P}(\text{Control B}) \ge 0.00\text{ pp}$$
3. **Gate 3 (Realized SOC Floor):**
   Zero realized battery SOC below 20.00% across all 2,952 hours of all 123 origins.

---

## 2. Safety Gate Audit Results

| Arm | Role | Critical-First Rel (%) | ΔR_CF (pp) | Gate 1 | Proportional Rel (%) | ΔR_P (pp) | Gate 2 | Min SOC (%) | SOC <20% | Gate 3 | All Safety Gates |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Control_Frozen_B** | Reference Baseline | 93.669482% | — | — | 83.823383% | — | — | 54.99% | 0 | PASS | **BASELINE** |
| **Candidate_S** | Reference (protection OFF) | 94.327168% | +0.657686 | PASS | 84.604885% | +0.781502 | PASS | 20.00% | 0 | PASS | **PASS** |
| **Candidate_SW** | Reference (protection OFF) | 94.090514% | +0.421032 | PASS | 83.467189% | **-0.356194** | **FAIL** | 20.00% | 0 | PASS | **FAIL** |
| **Candidate_SL** | Efficiency Reference (S-L) | 94.455173% | +0.785691 | PASS | 85.150455% | +1.327072 | PASS | 20.00% | 0 | PASS | **PASS** |
| **Candidate_SWL** | Final Candidate (SW-L) | 94.484413% | +0.814931 | PASS | 85.264223% | +1.440840 | PASS | 20.00% | 0 | PASS | **PASS** |

---

## 3. Detailed Safety Findings

1. **Candidate SW (Unprotected) Fails Safety:**
   - As observed in the 2024 discovery campaign, unprotected Candidate SW suffers a reliability degradation on proportional accounting: $\Delta R_P = -0.356194\text{ pp}$ relative to Control B.
   - This independently confirms that unrestrained renewable credit at low sun creates a persistent critical reliability hazard.

2. **Candidate SW-L (Protected) Fully Restores Safety:**
   - With low-sun stored-energy protection active ($e_k < 15.0^\circ$), Candidate SW-L achieves:
     - $\Delta R_{CF} = \mathbf{+0.814931\text{ pp}}$ over Control B.
     - $\Delta R_P = \mathbf{+1.440840\text{ pp}}$ over Control B.
   - Zero realized SOC values fall below 20.00% (minimum realized SOC across all 2,952 hours is exactly 20.00%).
   - Candidate SW-L **PASSES ALL THREE SAFETY GATES**.

3. **Candidate S-L (Protected) Safety:**
   - Candidate S-L also passes all three safety gates ($\Delta R_{CF} = +0.785691\text{ pp}$, $\Delta R_P = +1.327072\text{ pp}$, min SOC 20.00%).

Both protected candidates (S-L and SW-L) are fully eligible for evaluation under the diesel gate.
