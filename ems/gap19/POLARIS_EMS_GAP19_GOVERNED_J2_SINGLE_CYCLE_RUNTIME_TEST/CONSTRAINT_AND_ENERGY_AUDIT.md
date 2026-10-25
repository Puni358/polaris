# Physical Constraint & Energy Accounting Audit Report

## 1. Physical Constraint Validation

| Physical Domain | Governed / Configured Bound | Minimum Observed | Maximum Observed | Audit Result |
| :--- | :--- | :---: | :---: | :---: |
| **Battery Energy / SOC** | $20.0\% \le \text{SOC} \le 95.0\%$ | **$52.61\%$** ($105,220\text{ Wh}$) | **$93.37\%$** ($186,740\text{ Wh}$) | **PASS (IN BOUNDS)** |
| **Battery Charge Power** | $0 \le P_{\text{chg}} \le 50,000\text{ W}$ | **$0.00\text{ W}$** | **$37,807.18\text{ W}$** | **PASS (IN BOUNDS)** |
| **Battery Discharge Power** | $0 \le P_{\text{dis}} \le 50,000\text{ W}$ | **$0.00\text{ W}$** | **$15,000.00\text{ W}$** | **PASS (IN BOUNDS)** |
| **Diesel Power Output** | $10,000\text{ W} \le P_{\text{dies}} \le 100,000\text{ W}$ | **$0.00\text{ W}$** (Off) | **$52,807.18\text{ W}$** | **PASS (IN BOUNDS)** |
| **Charge/Discharge Mutex** | $u_{\text{chg}}[t] + u_{\text{dis}}[t] \le 1$ | **$0$** | **$1$** | **PASS (NO SIMULTANEOUS)** |
| **Bus-Bar Balance Error** | $|(P_{\text{sol}}+P_{\text{wind}}+P_{\text{dis}}+P_{\text{dies}}) - (P_{\text{load}}+P_{\text{chg}})| = 0$ | **$0.00\text{ W}$** | **$0.00\text{ W}$** | **PASS (EXACT)** |
| **Numerical Sanity** | No NaN, Inf, or negative energy | All finite | All finite | **PASS (CLEAN)** |

---

## 2. Energy Accounting Reconciliation

Across all 24 timesteps:
1. `load_served[t]` = $20,000\text{ W}$ for all $t$.
2. `unmet_load[t]` = $0.0\text{ W}$ for all $t$.
3. `energy_balance_errors[t]` = `0.0` for all $t$.
4. Battery state transition:
   $E_{\text{batt}}[t] = E_{\text{batt}}[t-1] + \eta_{\text{ch}} P_{\text{chg}}[t] \Delta t - \frac{1}{\eta_{\text{dis}}} P_{\text{dis}}[t] \Delta t$.
   - Verified for all $t \in [0, 23]$ with $\eta_{\text{ch}} = 0.92, \eta_{\text{dis}} = 0.92$.

---

## 3. Verdict

```
PHYSICAL_CONSTRAINTS_VALIDATED = YES
ENERGY_ACCOUNTING_BALANCED = YES
NUMERICAL_SANITY_CONFIRMED = YES
CONSTRAINT_AND_ENERGY_AUDIT_STATUS = PASS
```
