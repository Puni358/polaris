# POLARIS EMS — DEC-004-D1: EXACT PROTECTED CRITICAL-LOAD DEFINITION

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION**
> This document prepares decision **DEC-004-D1** for human governance review. It presents evidence, technical boundaries, policy options, and synthetic numerical examples. It does **NOT** select or approve a policy.

---

## 1. Exact Governance Question

**DEC-004-D1**: *What scope, categorization, and engineering representation constitute the authorized "protected critical load" ($P_{\text{critical}}$) during Option D execution?*

---

## 2. Authoritative Evidence & Technical Boundaries

### 2.1 Established Evidence
- **Conceptual Categories**: The human governance process has identified three conceptual life-safety categories:
  1. **Essential Heating**: Thermal environmental control required for human survivability in polar environments.
  2. **Essential Water Treatment & Filtration**: Life-support water purification processing.
  3. **Emergency Communications**: Radio, satellite, and telemetry infrastructure.
- **Circuit Separation**: The existing total station demand vector (`demand.point`) does **NOT** distinguish critical from noncritical circuits.

### 2.2 Unestablished Items (Requires Definition)
- **Station Circuit Mapping**: No mapping exists connecting physical station breaker panels or load channels to the conceptual categories.
- **Heating Scope**: Unresolved whether "heating" encompasses full station space heating or strictly minimum habitability shelters.
- **Water Scope**: Unresolved whether "water treatment" includes full greywater recycling or strictly emergency potable filtration.
- **Time Variance & Surge**: Unresolved whether $P_{\text{critical}}$ is static or time-varying, and how motor startup/surge currents are handled.

---

## 3. Policy Candidate Options for Human Review

- **Option D1-A (Static Circuit Inventory)**: Define a fixed, dedicated set of physical critical circuits in station configuration (`station_config.yaml`). Option D energizes only these circuits.
- **Option D1-B (Static Power Allocation Cap)**: Define a fixed maximum power cap $P_{\text{critical,max}}$ (e.g. $7\text{ kW}$). Option D limits total station load to this budget.
- **Option D1-C (Dynamic Schedule/Thermal Profile)**: Define a time-varying or temperature-dependent critical load function $P_{\text{critical}}(t, T_{\text{amb}})$.

---

## 4. Synthetic Illustrative Numerical Example

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Scenario Setup:
- **Total Station Demand**: $30\text{ kW}$
- **Noncritical Demand**: $23\text{ kW}$ (Shed / Disconnected)
- **Synthetic Critical Load**: $7\text{ kW}$ total, broken down conceptually as:
  - Essential Heating: $4\text{ kW}$
  - Water Treatment: $2\text{ kW}$
  - Emergency Communications: $1\text{ kW}$

```text
Total Station Load (30 kW)
 ├── Noncritical Load (23 kW) ──► SHED / DISCONNECTED
 └── Protected Critical Load (7 kW)
      ├── Essential Heating (4 kW) ──► SERVED
      ├── Water Treatment (2 kW) ───► SERVED
      └── Emergency Comms (1 kW) ───► SERVED
```

---

## 5. Cross-Decision Interactions & Dependencies

- **Interaction with D2 (Battery)**: Critical load magnitude determines battery discharge duration if battery discharge is authorized.
- **Interaction with D4 (Shortfall)**: If available generation is $< P_{\text{critical}}$, D4 determines whether critical categories are shed proportionally or by priority.
- **Interaction with D6 (Excess Diesel)**: $P_{\text{critical}}$ defines the threshold above which diesel minimum generation becomes excess power.

---

## 6. Required Engineering Definitions

1. Physical electrical panel and circuit breaker mapping for critical loads.
2. Minimum thermal heating power required to prevent structural freezing.
3. Inrush / surge current tolerance for water pumps and heating elements.

---

## 7. Human Decision Form (DEC-004-D1)

```text
DECISION ID: DEC-004-D1
QUESTION: How shall the protected critical load be defined for Option D?

SELECTED POLICY OPTION: [ D1-A / D1-B / D1-C / OTHER ]

HUMAN DECISION STATUS: UNRESOLVED (Awaiting Human Selection)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D1_DECISION_PREPARATION_COMPLETE`
