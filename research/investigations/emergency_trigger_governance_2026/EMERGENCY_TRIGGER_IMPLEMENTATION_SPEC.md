# POLARIS — EMERGENCY TRIGGER IMPLEMENTATION SPECIFICATION

## 1. System Overview & Scope

This implementation specification defines the software mathematical models, data structures, and algorithms for the **POLARIS Emergency Controller Dispatcher (ECD)** Emergency Detection System.

**IMPORTANT GOVERNANCE DIRECTIVE**: This document defines the formal software specification ONLY. **No production source code (including `ecd.py`, `gap19_highs_native.py`, or `router.py`) shall be modified during this phase.**

---

## 2. Mathematical Survivability Assessment Algorithm

The core innovation of POLARIS Emergency Governance is replacing static SOC thresholds (e.g. naive `SOC < 37.83%` rules) with a **Dynamic Critical Load Survivability Assessment**.

### 2.1 Usable Stored Battery Energy ($E_{\text{batt, usable}}$)
Let $SOC(t) \in [0.0, 1.0]$ be the validated state-of-charge at time $t$. Usable battery energy above the physical minimum SOC floor ($SOC_{\text{physical\_min}} = 0.20$) delivered to the critical bus accounting for discharge efficiency ($\eta_{\text{dis}} = 0.92$) is:

$$E_{\text{batt, usable}}(t) = \max\left(0.0, \, \left( SOC(t) - SOC_{\text{physical\_min}} \right) \times C_{\text{nom}} \times \eta_{\text{dis}} \right)$$

For the synthetic benchmark parameters ($C_{\text{nom}} = 200.0\text{ kWh}$, $SOC_{\text{physical\_min}} = 0.20$, $\eta_{\text{dis}} = 0.92$):
- At $SOC(t) = 37.83\%$ ($75.65\text{ kWh}$ total stored energy):
  $$E_{\text{batt, usable}} = (0.37826 - 0.2000) \times 200.0 \times 0.92 = 0.17826 \times 184.0 = 32.80\text{ kWh delivered}$$
- At $SOC(t) = 95.00\%$ ($190.00\text{ kWh}$ total stored energy):
  $$E_{\text{batt, usable}} = (0.9500 - 0.2000) \times 200.0 \times 0.92 = 138.00\text{ kWh delivered}$$

### 2.2 Credible Dispatchable Generation Energy ($E_{\text{gen, credible}}$)
Let $K$ be the set of available dispatchable generators (e.g., diesel generator sets). For each generator $k \in K$, let $P_{\text{gen\_k, max}}(t)$ be its maximum rated power and $A_k(t) \in \{0, 1\}$ be its operational availability status (accounting for faults, maintenance lockouts, or fuel exhaustion). The total credible dispatchable energy over the 6-hour autonomy horizon $H = 6.0\text{ hours}$ is:

$$E_{\text{gen, credible}}(t, H) = \sum_{k \in K} \int_{0}^{H} A_k(t+\tau) \cdot P_{\text{gen\_k, max\_credible}}(t+\tau) \, d\tau$$

Assuming constant generator capability over horizon $H$:
$$E_{\text{gen, credible}}(t, H) = H \cdot \sum_{k \in K} \left( A_k(t) \cdot P_{\text{gen\_k, max}}(t) \right)$$

### 2.3 Credible Renewable Generation Energy ($E_{\text{ren, credible}}$)
To remain conservative under polar conditions, renewable generation forecasts ($\hat{P}_{\text{solar}}(\tau), \hat{P}_{\text{wind}}(\tau)$) are derated by governed confidence factors ($\gamma_{\text{solar}} = 0.50$, $\gamma_{\text{wind}} = 0.50$):

$$E_{\text{ren, credible}}(t, H) = \int_{0}^{H} \left( \gamma_{\text{solar}} \hat{P}_{\text{solar}}(t+\tau) + \gamma_{\text{wind}} \hat{P}_{\text{wind}}(t+\tau) \right) d\tau$$

If forecasts are unavailable or unverified, $E_{\text{ren, credible}}(t, H) = 0.0\text{ kWh}$.

### 2.4 Required Critical Energy Demand ($E_{\text{critical, req}}$)
The total critical load energy required at the bus over horizon $H = 6.0\text{ hours}$ for $P_{\text{critical}} = 11.6\text{ kW}$ is:

$$E_{\text{critical, req}}(H) = P_{\text{critical}} \times H = 11.6\text{ kW} \times 6.0\text{ h} = 69.60\text{ kWh delivered}$$

### 2.5 Critical Load Survivability Margin ($M_{\text{surv}}$)
The Critical Load Survivability Margin at time $t$ is:

$$M_{\text{surv}}(t) = E_{\text{batt, usable}}(t) + E_{\text{gen, credible}}(t, H) + E_{\text{ren, credible}}(t, H) - E_{\text{critical, req}}(H)$$

**IMMINENT SURVIVABILITY FAILURE GUARD**:
$$\text{Trigger\_Imminent\_Emergency}(t) = \begin{cases} 
\text{TRUE} & \text{if } M_{\text{surv}}(t) < 0.0\text{ kWh} \\
\text{FALSE} & \text{if } M_{\text{surv}}(t) \ge 0.0\text{ kWh}
\end{cases}$$

---

## 3. Emergency Trigger Detection Logic

The ECD Emergency Detection algorithm evaluates three distinct trigger paths:

```
+-----------------------------------------------------------------------------------+
|                        POLARIS EMERGENCY DETECTION LOGIC                          |
+-----------------------------------------------------------------------------------+
                                          |
                        +-----------------+-----------------+
                        | Telemetry Validated Check (V_telemetry) |
                        +-----------------+-----------------+
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
               [ V_telemetry == INVALID ]        [ V_telemetry == VALID ]
                         |                                 |
                         v                                 v
                 STATE = UNKNOWN_INVALID           Evaluate Emergency Conditions:
               (LOCK SAFE-HARBOR DISPATCH)        1. P_crit_srv < P_crit_req (Hard Failure)
               (HALT AUTO OPTIMIZATION)           2. M_surv(t) < 0 (Imminent Deficit)
               (LOAD SHEDDING PROHIBITED)                  |
                                                  +--------+--------+
                                                  |                 |
                                                  v                 v
                                             [ Either True ]   [ Both False ]
                                                  |                 |
                                                  v                 v
                                           STATE = EMERGENCY   Check Reserve Target:
                                           (ENFORCE OPTION C)  SOC < 37.83% ?
                                                                    |
                                                            +-------+-------+
                                                            |               |
                                                            v               v
                                                        [ Yes ]           [ No ]
                                                           |                |
                                                           v                v
                                                  STATE = DEFICIT    STATE = NORMAL
```

### 3.1 Trigger Path 1: Validated Critical-Load Service Failure
- **Mathematical Condition**: $P_{\text{critical, served}}(t) < P_{\text{critical, required}}(t) - \epsilon_{\text{power}}$ (where $\epsilon_{\text{power}} = 0.1\text{ kW}$).
- **Requirement**: Must be verified by $\text{V}_{\text{telemetry}} = \text{VALID}$.
- **Action**: Immediate transition to `EMERGENCY`. **Zero intentional delay / no persistence waiting.**

### 3.2 Trigger Path 2: Imminent Survivability Failure
- **Mathematical Condition**: $M_{\text{surv}}(t) < 0.0\text{ kWh}$.
- **Requirement**: Calculated on every control interval (15 minutes).
- **Action**: Immediate transition to `EMERGENCY`. Enforces Option C load shedding *before* actual blackout occurs.

### 3.3 Trigger Path 3: Resource Loss Adequacy Assessment
- **Condition**: Loss of solar, wind, diesel, or battery asset.
- **Evaluation**: Update asset availability $A_k(t)$ or battery availability, recompute $M_{\text{surv}}(t)$.
- **Action**:
  - If $M_{\text{surv}}(t) \ge 0.0$: Remain in `NORMAL` or `RESERVE_DEFICIT`. Resource loss alone does **NOT** trigger Emergency.
  - If $M_{\text{surv}}(t) < 0.0$: Transition to `EMERGENCY`.

---

## 4. Governed Emergency Exit Criteria

Automatic return to `NORMAL` mode from `EMERGENCY` requires satisfying ALL of the following four conditions simultaneously over a governed persistence window $P = 4$ consecutive intervals (1.0 hour):

1. **Critical Load 100% Served**: $P_{\text{critical, served}}(t) \ge P_{\text{critical, required}}(t)$ for all $t \in [t_0 - 1\text{h}, t_0]$.
2. **Positive Survivability Margin**: $M_{\text{surv}}(t) \ge M_{\text{exit\_margin}}$ (where $M_{\text{exit\_margin}} = +10.0\text{ kWh}$ buffer).
3. **Reserve Target Restored or Replenishing**: Stored battery energy $E_{\text{batt}}(t) \ge 75.652\text{ kWh}$ ($SOC(t) \ge 37.83\%$).
4. **Dispatchable Generation Available**: At least one primary diesel generator $k \in K$ has $A_k(t) = 1$ and available capacity.

Upon satisfying all exit criteria, ECD emits an operator alert, logs the exit event with cryptographic hashes, and initiates governed ramp restoration of flexible loads ($P_{\text{flex}}$).

---

## 5. Software Data Structure & API Specification (For Future `ecd.py` Implementation)

```python
# PROPOSED SOFTWARE DATA STRUCTURES (SPECIFICATION ONLY - DO NOT IMPLEMENT YET)
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

class ECDOperatingState(Enum):
    NORMAL = "NORMAL"
    RESERVE_DEFICIT = "RESERVE_DEFICIT"
    EMERGENCY = "EMERGENCY"
    UNKNOWN_INVALID = "UNKNOWN_INVALID"

@dataclass(frozen=True)
class TelemetrySnapshot:
    timestamp_epoch: float
    soc_percent: float           # e.g. 37.83
    battery_kw: float            # positive = discharge, negative = charge
    p_critical_req_kw: float     # e.g. 11.6
    p_critical_srv_kw: float     # actual measured served critical load
    p_diesel_max_avail_kw: float # sum of available diesel capacity
    p_ren_forecast_6h_kwh: float # 6-hour derated forecast energy
    battery_healthy: bool
    telemetry_valid: bool

@dataclass(frozen=True)
class SurvivabilityAssessment:
    e_batt_usable_kwh: float
    e_gen_credible_kwh: float
    e_ren_credible_kwh: float
    e_critical_req_kwh: float
    m_surv_kwh: float
    imminent_failure: bool

class EmergencyTriggerGovernor:
    """
    Governed ECD State Evaluator.
    SPECIFICATION ONLY. DO NOT INSTANTIATE OR IMPORT IN PRODUCTION CODE YET.
    """
    NOMINAL_CAPACITY_KWH: float = 200.0
    PHYSICAL_MIN_SOC: float = 0.20
    DISCHARGE_EFFICIENCY: float = 0.92
    RESERVE_TARGET_SOC: float = 0.37826 # 75.65 kWh
    CRITICAL_AUTONOMY_HOURS: float = 6.0

    def evaluate_survivability(self, snapshot: TelemetrySnapshot) -> SurvivabilityAssessment:
        # Implements E_batt_usable + E_gen_credible + E_ren_credible - E_crit_req
        ...

    def evaluate_state_transition(
        self, 
        current_state: ECDOperatingState, 
        snapshot: TelemetrySnapshot
    ) -> ECDOperatingState:
        # Implements formal delta transition function
        ...
```
