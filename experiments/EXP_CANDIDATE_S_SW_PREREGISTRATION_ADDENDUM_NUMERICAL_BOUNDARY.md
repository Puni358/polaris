# Preregistration Addendum: Numerical-Boundary Residue Protocol

**Experiment Identifier:** `EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024`  
**Addendum Identifier:** `ADDENDUM-NUMERICAL-BOUNDARY-RESIDUE-01`  
**Governance Authority:** Independent AI assistant Review Audit (Approved Addendum)  
**Date:** October 5, 2026  
**Governing Preregistration Reference:**
- `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md` (`1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5`)
- `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json` (`3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4`)

---

## 1. Rationale & Problem Description

During the execution of the 123-origin closed-loop campaign, an execution interruption occurred at origin ~105 under Candidate S with the following exception:
```text
ValueError: DispatchPlan violates charge/discharge exclusivity at index 11: charge=46041.9, discharge=0.01.
```

### Root Cause Analysis:
1. **Mathematical Optimization Context:**  
   In the POLARIS MILP model solved by HiGHS in `GAP19HighsNativeOptimizer`, battery continuous flows $P_{\mathrm{chg}}[t]$ and $P_{\mathrm{dis}}[t]$ are bounded against binary commitment variables $u_{\mathrm{chg}}[t], u_{\mathrm{dis}}[t] \in \{0, 1\}$ using Big-M constraints with $M = 50,000.0\text{ W}$:
   $$P_{\mathrm{chg}}[t] \le M \cdot u_{\mathrm{chg}}[t], \quad P_{\mathrm{dis}}[t] \le M \cdot u_{\mathrm{dis}}[t], \quad u_{\mathrm{chg}}[t] + u_{\mathrm{dis}}[t] \le 1$$
2. **Solver Tolerances:**  
   GAP19 uses HiGHS defaults without overrides:
   - MIP feasibility tolerance: $\epsilon_{\mathrm{integrality}} = 1.0 \times 10^{-6}$
   - Primal feasibility tolerance: $\epsilon_{\mathrm{primal}} = 1.0 \times 10^{-7}$
3. **Residue Bound Derivation:**  
   Under these solver tolerances, an inactive binary variable ($u_{\mathrm{dis}} = 0$) can be assigned a non-zero continuous relaxation value up to $\epsilon_{\mathrm{integrality}}$, and primal bounds can relax by up to $\epsilon_{\mathrm{primal}}$. Consequently, the continuous variable can exhibit a non-physical solver boundary residue:
   $$\tau = M \cdot (\epsilon_{\mathrm{integrality}} + \epsilon_{\mathrm{primal}}) = 50,000 \cdot (10^{-6} + 10^{-7}) = 0.055\text{ W}$$
4. **Validation Threshold:**  
   The observed failure exhibited a raw residue of $\sim 0.009\text{ W}$ (rounded to $0.01\text{ W}$), and prior diagnostic traces exhibited $\sim 0.039\text{ W}$. Both are strictly below the theoretical residue bound $\tau = 0.055\text{ W}$. However, `DispatchPlan` strictly tests `if chg > 1e-3 and dis > 1e-3:`, throwing a false-positive violation on pure floating-point solver residue.

---

## 2. Governed Numerical Extraction Protocol

To resolve this issue without altering solver physics, model formulations, or production code, the following research-layer extraction protocol is formally approved:

1. **Extraction Timing:**  
   The protocol operates strictly on raw, unrounded continuous solution values extracted directly from the solver solution vector prior to `DispatchPlan` construction.
2. **Residue Correction Rule:**  
   For each operating hour $t \in \{0 \dots 23\}$:
   $$\text{If } P_{\mathrm{chg}}[t] > 0 \text{ and } P_{\mathrm{dis}}[t] > 0:$$
   - If $\min(P_{\mathrm{chg}}[t], P_{\mathrm{dis}}[t]) \le \tau = 0.055\text{ W}$:
     Zero the smaller flow (the non-physical residue).
   - If $\min(P_{\mathrm{chg}}[t], P_{\mathrm{dis}}[t]) > \tau = 0.055\text{ W}$:
     Raise a genuine simultaneous charge/discharge violation and abort execution.
   $$\text{Otherwise: no change.}$$
3. **Strict Constraints:**
   - Unrounded values must be tested directly against $\tau$.
   - No rounding before the residue test.
   - No binary normalization: $u_{\mathrm{chg}}$ and $u_{\mathrm{dis}}$ remain unrounded raw solver values.
   - No alteration to the MILP formulation, constraint matrix, or objectives.
   - No modification to HiGHS solver tolerances or options.
   - Zero tolerance for genuine simultaneous flow ($> 0.055\text{ W}$).

---

## 3. Governance Invariants & Campaign Execution Rules

1. **Universal Applicability:**  
   The rule applies identically and without exception to all three arms: Control Frozen B, Candidate S, and Candidate SW. No candidate-specific branch or conditional logic is permitted.
2. **Re-Execution from Scratch:**  
   All 123 origins must be re-executed from scratch across all three arms. The incomplete run from the initial attempt (including the first 100 completed origins) is formally designated as non-campaign diagnostic material and discarded.
3. **Baseline Comparison Reference:**  
   The frozen Control B baseline telemetry and reports remain permanently immutable. In the re-executed campaign, the newly re-run Control B arm (executed under the identical research-layer extraction) serves as the synchronized comparison reference, verifying that Control B is completely unaltered by the protocol.
4. **Comprehensive Diagnostic Logging:**  
   Every reoptimization cycle must capture:
   - Raw $P_{\mathrm{chg}}$, $P_{\mathrm{dis}}$, $u_{\mathrm{chg}}$, $u_{\mathrm{dis}}$, $P_{\mathrm{diesel}}$, $u_{\mathrm{diesel}}$, $v_{\mathrm{start}}$
   - Corrected $P_{\mathrm{chg}}$, $P_{\mathrm{dis}}$
   - Binary flag indicating whether the residue correction fired
   - Magnitude of zeroed residue
   - Solver status and MIP gap
5. **Campaign Completeness Rule:**  
   If an origin fails, a failure record is logged and the run continues, but any campaign containing even a single failed origin is classified as INCOMPLETE and barred from safety-gate or fuel-gate qualification.
6. **Code Immutability:**  
   The following files remain 100% untouched with verified SHA-256 cryptographic hashes:
   - `system/optimization/implementations/gap19_highs_native.py`
   - `system/schemas/dispatch_plan.py`
   - `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py`
   - `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md`
   - `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json`
