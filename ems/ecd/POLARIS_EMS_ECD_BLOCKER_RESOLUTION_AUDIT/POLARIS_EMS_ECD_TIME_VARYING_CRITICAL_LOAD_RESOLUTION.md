# POLARIS EMS — TIME-VARYING CRITICAL-LOAD RESOLUTION AUDIT (BLK-010)

## 1. Executive Summary

This document establishes the resolution for **BLK-010** (Time-Varying Critical-Load Integration Algorithm). It provides the mathematical derivation and software input abstraction that enables full compatibility between the prototype constant-load fixture ($30,000\text{ W}$) and future production time-varying critical demand trajectories $P_{\text{crit}}(t)$.

---

## 2. Mathematical Formulation

### 2.1 Cumulative Critical Energy Trajectory
For a time-varying critical demand $P_{\text{crit}}(t) \ge 0$, the cumulative critical AC energy required over duration $t$ is:

$$E_{\text{crit}}(t) = \int_0^t P_{\text{crit}}(\tau) \, d\tau \quad \approx \quad \sum_{i=1}^{k(t)} P_{\text{crit}}(t_i) \cdot \Delta t$$

### 2.2 Battery Endurance $T_{\text{battery}}$
Available usable battery AC energy is:
$$E_{\text{bat,avail,AC}} = (E_{\text{stored}} - E_{\text{min}}) \cdot \eta_{\text{dis}}$$

The battery endurance $T_{\text{battery}}$ is the unique scalar time $T$ satisfying:
$$E_{\text{crit}}(T) = E_{\text{bat,avail,AC}}$$

*Proof of Reduction to Prototype Formula:*
When $P_{\text{crit}}(t) = P_{\text{crit}}$ (constant), $E_{\text{crit}}(T) = P_{\text{crit}} \cdot T$. Thus:
$$P_{\text{crit}} \cdot T_{\text{battery}} = E_{\text{bat,avail,AC}} \implies T_{\text{battery}} = \frac{(E_{\text{stored}} - E_{\text{min}}) \cdot \eta_{\text{dis}}}{P_{\text{crit}}}$$
This matches the audited canonical fixture equation with 100% precision.

### 2.3 Diesel Generator Endurance $T_{\text{diesel}}$
The generator fuel consumption rate under load $P_{\text{crit}}(t)$ is:
$$\dot{F}(t) = \alpha + \beta P_{\text{crit}}(t) \quad \text{for } P_{\text{min}} \le P_{\text{crit}}(t) \le P_{\text{max}}$$

The cumulative fuel consumed over duration $T$ is:
$$F(T) = \int_0^T \left( \alpha + \beta P_{\text{crit}}(\tau) \right) d\tau = \alpha T + \beta E_{\text{crit}}(T)$$

The diesel endurance $T_{\text{diesel}}$ is the unique scalar time $T$ satisfying:
$$F(T) = F_{\text{remaining}}$$

*Proof of Reduction to Prototype Formula:*
When $P_{\text{crit}}(t) = P_{\text{crit}}$ (constant), $F(T) = (\alpha + \beta P_{\text{crit}}) T$. Thus:
$$T_{\text{diesel}} = \frac{F_{\text{remaining}}}{\alpha + \beta P_{\text{crit}}}$$
This matches the audited canonical fixture equation with 100% precision.

---

## 3. Software Input Abstraction (`CriticalLoadTrajectory`)

To ensure zero architectural dead-ends, the ECD accepts critical demand via an abstract interface:

```python
class CriticalLoadTrajectory(Protocol):
    def get_cumulative_energy_kwh(self, duration_hours: float) -> float: ...
    def find_time_for_energy_kwh(self, target_kwh: float) -> float: ...
    def get_cumulative_fuel_liters(self, duration_hours: float, alpha: float, beta: float) -> float: ...
    def find_time_for_fuel_liters(self, target_liters: float, alpha: float, beta: float) -> float: ...
```

- **ConstantLoadTrajectory(30.0)** implements this interface analytically for the prototype.
- **TimeSeriesLoadTrajectory([P_1, P_2, ...])** implements this interface via piecewise-linear interpolation for production.

---

## 4. Gating & Decision Summary

- **Classification**: `ENGINEERING_DEFINITION_REQUIRED` (Resolved herein).
- **Blocks Unit Implementation**: **NO**
- **Blocks Integration**: **NO**
- **Blocks Production Deployment**: **NO**

Status: `ENGINEERING_DEFINITION_COMPLETE`
