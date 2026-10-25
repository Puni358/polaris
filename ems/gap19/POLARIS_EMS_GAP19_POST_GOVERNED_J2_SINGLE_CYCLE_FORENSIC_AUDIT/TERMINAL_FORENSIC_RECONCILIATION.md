# Terminal Forensic Reconciliation Report

## 1. Input Provenance & Policy Firewall

- `terminal_target_wh = 100,000 Wh` was supplied strictly as a `SYNTHETIC_ENGINEERING_TEST_VALUE`.
- It did **NOT** come from production source defaults.
- It did **NOT** overwrite EBR.
- It did **NOT** enter intermediate timesteps $t < 23$.

---

## 2. Boundary Condition Verification

- Intermediate timesteps $t \in [0, 22]$: Terminal target contribution is **$0.0\text{ Wh}$**.
- Horizon boundary $t = 23$: Terminal target contribution is **$100,000.00\text{ Wh}$**.
- Pointwise target at $t = 23$: $\max(21,739.13, 100,000.00) = 100,000.00\text{ Wh}$.

---

## 3. Dispatch Result Verification

- Battery energy level required at $t = 23$:
  \[
  E_{\text{next}}[23] \ge 100,000 + 40,000 = 140,000\text{ Wh} \quad (70.0\% \text{ SOC})
  \]
- Actual battery energy level in DispatchPlan at $t = 23$: `battery_soc[23] = 70.0%` ($140,000.00\text{ Wh}$).
- Terminal target was fully satisfied with zero shortfall.

---

## 4. Verdict

```
TERMINAL_APPLIED_AT_T23_ONLY = YES
TEST_VALUE_PROVENANCE_ISOLATED = YES
FINAL_SOC_70_PCT_CONFIRMED = YES
TERMINAL_FORENSIC_STATUS = PASS
```
