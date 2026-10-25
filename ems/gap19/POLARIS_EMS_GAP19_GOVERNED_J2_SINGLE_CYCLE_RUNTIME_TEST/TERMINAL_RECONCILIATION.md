# Terminal Reserve Reconciliation Report

## 1. Boundary Application Verification

- **Explicit Synthetic Terminal Target Input**: $E_{\text{term,target}} = 100,000\text{ Wh}$ (clearly labelled `SYNTHETIC_ENGINEERING_TEST_VALUE`).
- **Boundary Application Rule**: Terminal reserve is applied **exclusively** at the final decision timestep $t = 23$ ($\delta_{t, 23} \cdot E_{\text{term,target}}$).

---

## 2. Timestep Boundary Trace

| Timestep $t$ | EBR Target $E_{\text{EBR}}[t]$ | Terminal Target $E_{\text{term}}[t]$ | Unified Envelope Target $E_{\text{stage2,target}}[t]$ |
| :---: | :---: | :---: | :---: |
| $t = 0 \dots 18$ | $130,434.78\text{ Wh}$ | $0.0\text{ Wh}$ | **$130,434.78\text{ Wh}$** |
| $t = 19$ | $108,695.65\text{ Wh}$ | $0.0\text{ Wh}$ | **$108,695.65\text{ Wh}$** |
| $t = 20$ | $86,956.52\text{ Wh}$ | $0.0\text{ Wh}$ | **$86,956.52\text{ Wh}$** |
| $t = 21$ | $65,217.39\text{ Wh}$ | $0.0\text{ Wh}$ | **$65,217.39\text{ Wh}$** |
| $t = 22$ | $43,478.26\text{ Wh}$ | $0.0\text{ Wh}$ | **$43,478.26\text{ Wh}$** |
| $t = 23$ | $21,739.13\text{ Wh}$ | **$100,000.00\text{ Wh}$** | **$\max(21,739.13, 100,000.00) = 100,000.00\text{ Wh}$** |

---

## 3. Physical State Verification at $t=23$

- Required minimum battery energy at $t=23$:
  \[
  E_{\text{batt}}[23] \ge E_{\text{stage2,target}}[23] + E_{\text{min,wh}} = 100,000\text{ Wh} + 40,000\text{ Wh} = 140,000\text{ Wh} \quad (70.0\% \text{ SOC})
  \]
- **Actual Battery State in Dispatch Plan at $t=23$**:
  `battery_soc[23] = 70.0%` ($140,000.00\text{ Wh}$).
- Shortfall slack $s_{J2}[23] = 0.0\text{ Wh}$.

---

## 4. Verdict

```
TERMINAL_APPLIED_AT_T23_ONLY = YES
INTERMEDIATE_STEPS_UNTOUCHED = YES
FINAL_SOC_MATCHES_TARGET = EXACT (70.0% SOC / 140,000 Wh)
TERMINAL_RECONCILIATION_STATUS = PASS
```
