# POLARIS EMS — GATE-06 OPTION D MODIFICATION AUDIT

> [!IMPORTANT]
> **Narrow Provenance & Regression Audit of Option-D Source Modification**
> Audits the single source modification made to `system/optimization/implementations/option_d.py` during Gate-06 validation.
> Confirms that the change is a **governance-neutral engineering correction** preventing simultaneous battery charge/discharge exclusivity violations.

---

## 1. Summary Classification

- **`OPTION_D_MODIFICATION`**: `if p_diesel > 0 and p_dis == 0`
- **`SOURCE_MODIFICATIONS`**: `1`
- **`OTHER_SOURCE_MODIFICATIONS`**: `0`
- **`POLICY_CHANGE`**: `NO` (Governance-neutral bug fix)
- **`OPTION_D_REGRESSION`**: `PASS` (36 / 36 tests pass)

---

## 2. Hash Provenance Register

| Artifact Path | SHA256 Checksum Hash | Governance Status |
| :--- | :--- | :--- |
| **Previous `option_d.py`** | `eb15854400561c1dd29382c087f352633bc4816c5a51f0cb4112511acee72159` | Recovered from `POLARIS_EMS_GAP19_IMPLEMENTATION_CHECKPOINT/PROTECTED_HASH_REGISTER.json` |
| **Current `option_d.py`** | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` | Verified post-modification hash |

---

## 3. Exact Code Modification Diff

```diff
--- system/optimization/implementations/option_d.py (eb15854400561c1dd29382c087f352633bc4816c5a51f0cb4112511acee72159)
+++ system/optimization/implementations/option_d.py (78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12)
@@ -155,3 +155,3 @@
             # 5. Excess Diesel Generation Battery Charging
-            # Excess diesel power can charge battery ONLY when diesel is running for load
-            if p_diesel > 0:
+            # Excess diesel power can charge battery ONLY when diesel is running for load AND battery is not discharging
+            if p_diesel > 0 and p_dis == 0:
                 excess_diesel_w = max(0.0, p_diesel - p_rem_demand)
```

---

## 4. Technical Failure Mode Explanation

### Root Cause Analysis
1. In `OptionDFallbackSolver.solve`, when `assessment.preserved_resource == ResourceSelection.DIESEL`, Section 4 attempts to discharge available battery power first:
   $$\text{p\_dis} = \min(\text{max\_dis\_avail\_w}, \text{p\_rem\_demand})$$
2. When the battery is near minimum SOC (e.g. 20.0%), usable discharge capacity $\text{max\_dis\_avail\_w}$ is small (e.g. 3,199.99 W), leaving remaining unmet demand $\text{p\_rem\_demand\_after\_bat} > 0$.
3. Section 4 then runs the diesel generator to cover remaining demand:
   $$\text{p\_diesel} = \min(\text{max\_diesel\_w}, \max(\text{min\_diesel\_w}, \text{p\_rem\_demand\_after\_bat}))$$
4. In the original implementation, Section 5 evaluated:
   $$\text{if } \text{p\_diesel} > 0: \quad \text{excess\_diesel\_w} = \max(0.0, \text{p\_diesel} - \text{p\_rem\_demand}); \quad \text{p\_chg} = \min(\text{max\_chg\_avail\_w}, \text{excess\_diesel\_w})$$
5. When diesel power exceeded total remaining demand, Section 5 computed $\text{p\_chg} > 0$ while Section 4 had already assigned $\text{p\_dis} > 0$ for the same timestep.
6. This resulted in simultaneous positive charging ($\text{p\_chg} > 0$) and discharging ($\text{p\_dis} > 0$) in the same 1-hour interval, violating the charge/discharge exclusivity schema constraint enforced by `DispatchPlan`:
   `DispatchPlan violates charge/discharge exclusivity at index 17: charge=5229.61, discharge=155.74.`

### Scope & Neutrality of Modification
- The addition of `and p_dis == 0` restricts excess diesel battery charging to timesteps where the battery is NOT discharging.
- When $\text{p\_dis} == 0$, behavior is 100% identical to the original logic.
- When $\text{p\_dis} > 0$, charging is suppressed ($\text{p\_chg} = 0$), preventing exclusivity schema violations.
- **Policy Neutrality**: The modification does not change emergency dispatch priorities, E3 preservation rules, or critical load allocation semantics. It is a **governance-neutral engineering bug fix**.

---

## 5. Regression Test Results

The following test suites were executed to verify regression safety:
1. `tests/test_ecd_option_d_integration.py` (18 tests) $\rightarrow$ **PASS**
2. `tests/test_gap19_ecd_option_d.py` (12 tests) $\rightarrow$ **PASS**
3. `tests/test_gate06_rolling_twin_fixture.py` (6 tests) $\rightarrow$ **PASS**

**Total Option-D & Gate-06 Tests**: 36 passed out of 36.  
**Option-D Regression Status**: **PASS**.
