# POLARIS EMS — P_CRITICAL(t) & T_REQUIRED 6-HOUR BASELINE INTERACTION AUDIT

## 1. Executive Summary

This document audits the mathematical and physical interaction between **Protected Critical Load ($P_{\text{critical}}(t)$)** and the sealed **6-Hour $T_{\text{required}}$ Baseline** (`TREQ-001`).

---

## 2. Six-Hour Energy Integral Formulation

To evaluate resource endurance ($T_{\text{battery}}, T_{\text{diesel}}$) against the $6\text{-hour}$ baseline under zero-renewable stress ($P_{\text{solar}}=0, P_{\text{wind}}=0$), the system must compute total required critical energy:

$$E_{\text{critical\_required}}(6\text{h}) = \int_{0}^{6\text{h}} P_{\text{critical}}(t) \, dt \approx \sum_{t=1}^{6} P_{\text{critical}}(t) \times 1\text{h}$$

---

## 3. Illustrative Evaluation (Prototype vs Real Station)

### Prototype Scale Evaluation (For Illustrative Calibration Only)
Using prototype constant load $P_{\text{crit}} = 30\text{ kW}$ ($30,000\text{ W}$):
$$E_{\text{critical\_required}}(6\text{h}) = 30,000\text{ W} \times 6\text{h} = 180,000\text{ Wh} = 180\text{ kWh}$$

- **Prototype Battery Endurance Check**:
  - Prototype battery usable energy ($C_{\text{bat}}=200\text{kWh}, \text{SOC}\in[20\%, 80\%], \eta_{\text{dis}}=0.92$):
    $$E_{\text{bat\_usable}} = 200\text{ kWh} \times (0.80 - 0.20) \times 0.92 = 110.4\text{ kWh}$$
  - $E_{\text{bat\_usable}} (110.4\text{ kWh}) < E_{\text{critical\_required}} (180\text{ kWh})$.
  - Prototype battery alone provides only **$3.68\text{ hours}$** of $30\text{ kW}$ critical load support ($\le 6\text{h}$). Battery endurance test fails ($T_{\text{battery}} < 6\text{h}$).
- **Prototype Diesel Endurance Check**:
  - At $30\text{ kW}$, fuel rate $f_{\text{rate}} = 12.5\text{ L/h}$.
  - Required fuel for 6h: $F_{\text{required}} = 12.5\text{ L/h} \times 6\text{h} = 75.0\text{ Liters}$.
  - Diesel endurance test passes if remaining fuel $F_{\text{rem}} \ge 75.0\text{ Liters}$.

### Real Nuolja Station Evaluation
- Station-specific $P_{\text{critical}}(t)$ is `NOT_ESTABLISHED`.
- Real station battery usable capacity and fuel tank inventory are `NOT_ESTABLISHED`.
- Therefore, $E_{\text{critical\_required}}(6\text{h})$ **CANNOT** be evaluated for Nuolja station.

---

## 4. Status Classification

```yaml
P_CRITICAL_T_REQUIRED_6H_READINESS: NOT_READY
STATION_EVIDENCE_STATUS: DATA_BLOCKED
FIREWALL_RULE: The 6-hour baseline T_required = 6h remains sealed under TREQ-001. This audit confirms that calculating the 6h energy requirement requires empirical station P_critical(t) data.
```
