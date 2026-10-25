# POLARIS EMS — EMERGENCY CONDITION DETECTOR FULL SPECIFICATION & GOVERNANCE CORRECTION

## 1. EXECUTIVE SUMMARY & GOVERNANCE STATUS

This document defines the authoritative engineering specification for the **POLARIS Emergency Condition Detector (ECD)**, updated with the **CLOSED Governance Decisions** for primary survivability margin selection and failure behavior bounds.

### Executive Classification Block:
```
ECD_SPECIFICATION_STATUS =
    BLOCKED_BY_SPECIFICATION_GAPS

PRIMARY_SURVIVABILITY_MARGIN =
    TIME_MARGIN

TIME_MARGIN_STATUS =
    GOVERNANCE_CLOSED

ENERGY_MARGIN_STATUS =
    DIAGNOSTIC_ONLY

SURVIVABILITY_RATIO_STATUS =
    DIAGNOSTIC_ONLY

E3_RESOURCE_SELECTION =
    LARGER_TIME_MARGIN_IS_PRESERVED_RESOURCE

LIMITING_RESOURCE =
    SMALLER_TIME_MARGIN

T_REQUIRED_MISSING_BEHAVIOR =
    FAIL_CLOSED

OTHER_INPUT_MISSING_BEHAVIOR =
    NOT_UNIFORMLY_GOVERNED

CRITICAL_LOAD_MODEL =
    ADDITIVE_SCHEMA_REQUIRED

72H_PROTOTYPE_TESTABILITY =
    BLOCKED

SCHEMA_STATUS =
    ADDITIVE_EXTENSION_REQUIRED

IMPLEMENTATION_AUTHORIZATION =
    NOT_GRANTED

EXECUTION_AUTHORIZATION =
    NOT_GRANTED
```

---

## 2. REQUIRED GOVERNANCE DECISION RECORD

```
DECISION:
    Survivability margin is governed primarily by time margin.

PRIMARY:
    M_r = T_r - T_required

DIAGNOSTICS:
    Energy margin
    Survivability ratio

RATIONALE:
    Time margin directly represents how much additional survivability
    duration remains beyond the required survival window and provides
    a common temporal basis for comparing battery and diesel
    survivability.

E3:
    Preserve the resource with the larger time margin while
    maintaining critical service.
```

### 2.1 Authoritative Survivability Margin Definitions:
- **PRIMARY SURVIVABILITY MARGIN**: **`TIME_MARGIN`** ($M_r = T_r - T_{\text{required}}$ in hours).
- **DIAGNOSTIC METRIC B**: **Energy Margin** ($E_{\text{margin,r}} = E_{\text{available,r}} - E_{\text{required,r}}(T_{\text{required}})$) — `DIAGNOSTIC_ONLY`.
- **DIAGNOSTIC METRIC C**: **Survivability Ratio** ($R_r = \frac{T_r}{T_{\text{required}}}$) — `DIAGNOSTIC_ONLY`.

### 2.2 E3 Resource Preservation Semantics:
- **Authoritative Emergency Policy**: *"In emergency mode, dynamically preserve whichever resource has the larger survivability margin, while maintaining critical service."*
- **PRESERVED RESOURCE**: Resource with the larger time margin ($M_r$). Represents greater remaining survivability time beyond $T_{\text{required}}$.
- **LIMITING RESOURCE**: Resource with the smaller time margin ($M_r$).
- **Tie Handling**: If $M_{\text{battery}} = M_{\text{diesel}}$, state is classified as `TIE / BOTH`. Any tie-breaking preference remains **`GOVERNANCE_REQUIRED`** (do not invent a tie-breaker).
- **Dynamic Preservation**: E3 preference is determined dynamically from computed time margins, NOT hardcoded to always discharge battery or always consume diesel first.

### 2.3 Failure Behavior Bounds (Critical Correction):
- **Governed Fail-Closed**: Detector executes **`FAIL_CLOSED`** strictly when $T_{\text{required}}$ is missing, invalid, stale, or unauthorized.
- **Other Inputs**: Missing trajectory, missing battery state, missing fuel remaining, missing generator parameters, unit mismatch, timestamp mismatch are classified as **`GOVERNANCE_REQUIRED`** / **`NOT_UNIFORMLY_GOVERNED`**. They must NOT be automatically declared `FAIL_CLOSED` or `EMERGENCY` without explicit repository evidence or closed governance.

---

## 3. MODE DISTINCTION: PROTOTYPE VS REAL STATION

1. **`PROTOTYPE_TEST_MODE`**:
   - $T_{\text{required}} = 72\text{ HOURS}$ (**`SYNTHETIC_ENGINEERING_TEST_VALUE`** used solely to validate multi-day survivability logic).
   - Real-Station Operational Meaning: **NONE** (does not represent station requirement, logistics schedule, or autonomy mandate).
2. **`REAL_STATION_OPERATIONAL_MODE`**:
   - $T_{\text{required}} = \text{NOT\_ESTABLISHED}$.
   - Fail-Closed Behavior: If no valid, authorized $T_{\text{required}}$ is resolved, ECD emits **`FAIL_CLOSED`**.

---

## 4. AUTHORITATIVE FORMULATIONS

### 4.1 Time Margin Formulation (Primary Metric):
For resource $r \in \{\text{battery}, \text{diesel}\}$:
$$M_r = T_r - T_{\text{required}} \quad (\text{hours})$$
- $M_{\text{battery}} = T_{\text{battery}} - T_{\text{required}}$
- $M_{\text{diesel}} = T_{\text{diesel}} - T_{\text{required}}$

Interpretation:
- $M_r > 0$: Resource survives beyond the required window.
- $M_r = 0$: Resource reaches exactly the required window.
- $M_r < 0$: Resource cannot independently cover the required window.

### 4.2 Diagnostic Formulations (Non-Governing):
- **Energy Margin**: $E_{\text{margin,batt}} = E_{\text{usable,AC}} - \sum_{k=1}^{T_{\text{req}}} D_{\text{critical}}(k) \Delta t$ ($\text{Wh}$). Follows repository physical accounting.
- **Survivability Ratio**: $R_{\text{batt}} = \frac{T_{\text{battery}}}{T_{\text{required}}}$, $R_{\text{diesel}} = \frac{T_{\text{diesel}}}{T_{\text{required}}}$.

---

## 5. BATTERY & DIESEL SURVIVABILITY MODELS

### 5.1 Battery Model (`battery.yaml` & `milp.py`):
- Nominal Capacity: $200\text{ kWh}$. Min SOC: $20\%$ ($40\text{ kWh}$). Max Discharge Power: $50\text{ kW}$.
- Discharge Efficiency: $\eta_{\text{dis}} = 0.92$.
- Usable AC Delivered Energy: $E_{\text{usable,AC}} = \max\left(0, \text{battery\_energy\_wh} - 40000\right) \cdot 0.92$.
- Battery Endurance $T_{\text{battery}}$: Duration over $D_{\text{critical}}(t)$ under zero-renewable emergency stress scenario ($P_{\text{solar}}=0, P_{\text{wind}}=0$).

### 5.2 Diesel Model (`diesel.yaml` & `milp.py`):
- Min Power: $10\text{ kW}$, Max Power: $100\text{ kW}$.
- Base Fuel Rate: $5.0\text{ L/h}$. Marginal Fuel Rate: $0.00025\text{ L/Wh}$.
- Fuel Rate Formula: $F_{\text{rate}}(P) = 5.0 \cdot u_{\text{gen}} + 0.00025 \cdot P_{\text{gen}}$ ($\text{L/h}$).
- Diesel Endurance $T_{\text{diesel}}$: Duration over $D_{\text{critical}}(t)$ under zero-renewable emergency stress scenario ($P_{\text{solar}}=0, P_{\text{wind}}=0$) until remaining fuel $V_{\text{fuel}}$ is depleted.
- *Data Gap*: Remaining fuel $V_{\text{fuel}}$ is missing from `StationState`.

### 5.3 Critical Load Terminology & Prototype Configuration:
- `loads.yaml` contains `30,000 W` as a **`SYNTHETIC / PROTOTYPE CONFIGURATION VALUE`**.
- It must **NOT** be described as an authoritative station critical-load requirement.
- Real station critical-load classification remains unestablished. The 5-tier demand structure remains an additive future schema requirement.

---

## 6. NORMAL / EMERGENCY CLASSIFICATION RULE

```
If T_required is missing, invalid, stale, or unauthorized:
    CLASSIFICATION = FAIL_CLOSED (No NORMAL or EMERGENCY classification issued)

Else if any other required detector input is missing or unresolved:
    CLASSIFICATION = GOVERNANCE_REQUIRED (Requires explicit policy choice)

Else if M_battery >= 0 AND M_diesel >= 0:
    CLASSIFICATION = NORMAL

Else:
    CLASSIFICATION = EMERGENCY
    Preserved Resource = Resource with larger M_r (greater remaining margin)
    Limiting Resource  = Resource with smaller M_r (smaller remaining margin)
```

---

## 7. SCHEMA STATUS & FUTURE EMERGENCY ASSESSMENT CANDIDATES

Schema status remains: **`ADDITIVE_SCHEMA_EXTENSION_REQUIRED`**. No code implementation authorized.

Future `EmergencyAssessment` specification payload candidates:
- `operating_mode`: `"NORMAL"`, `"EMERGENCY"`, `"FAIL_CLOSED"`, `"GOVERNANCE_REQUIRED"`
- `battery_survivability_hours`: $T_{\text{battery}}$
- `diesel_survivability_hours`: $T_{\text{diesel}}$
- `battery_time_margin_hours`: $M_{\text{battery}}$
- `diesel_time_margin_hours`: $M_{\text{diesel}}$
- `battery_energy_margin`: $E_{\text{margin,batt}}$ (diagnostic)
- `diesel_energy_margin`: $E_{\text{margin,diesel}}$ (diagnostic)
- `battery_survivability_ratio`: $R_{\text{batt}}$ (diagnostic)
- `diesel_survivability_ratio`: $R_{\text{diesel}}$ (diagnostic)
- `limiting_resource`: `"BATTERY"`, `"DIESEL"`, `"TIE / BOTH"`, or `"NONE"`
- `preserved_resource`: `"BATTERY"`, `"DIESEL"`, `"TIE / BOTH"`, or `"NONE"`
- `assessment_timestamp`: ISO-8601 timestamp string
- `provenance`: Traceability metadata

---

## 8. 72H PROTOTYPE TESTABILITY STATUS

$$\text{72H\_PROTOTYPE\_TESTABILITY} = \text{BLOCKED}$$

### Minimum Blocking Dependencies:
1. Missing 72h critical load forecast trajectory.
2. Missing `fuel_remaining_liters` field in `StationState`.
3. Additive schema extensions for 5-tier demand and EmergencyAssessment payload.
