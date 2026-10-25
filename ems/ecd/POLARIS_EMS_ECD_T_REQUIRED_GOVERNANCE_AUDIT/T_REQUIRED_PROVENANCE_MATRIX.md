# POLARIS EMS — T_REQUIRED MASTER PROVENANCE MATRIX

## 1. Executive Summary

This provenance matrix classifies every parameter associated with $T_{\text{required}}$ and ECD survivability assessment into its precise governance, engineering, or synthetic test status.

---

## 2. Master Provenance Classification Register

| Parameter | Governance / Engineering Category | Current Value / State in Repository | Authoritative Source Reference | Production Readiness Status |
| :--- | :--- | :--- | :--- | :--- |
| **$T_{\text{required}}$ Semantics** | Governance Policy Decision | `GOVERNANCE_DECISION_REQUIRED` | [`T_REQUIRED_SEMANTIC_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_T_REQUIRED_GOVERNANCE_AUDIT/T_REQUIRED_SEMANTIC_AUDIT.md) | `BLOCKED` (Requires human choice) |
| **$T_{\text{required}}$ Numerical Value** | Governance / Engineering Parameter | `72.0 h` (`SYNTHETIC_TEST_VALUE_ONLY`) | [`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json) | `NOT_AUTHORIZED` |
| **$T_{\text{test}}$ Numerical Value** | Synthetic Validation Parameter | `2.0 h` (`SYNTHETIC_LOGIC_VALIDATION_ONLY`) | [`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json) | `TEST_SPACE_ONLY` |
| **$T_{\text{required}}$ Override Authority** | Security / Governance Decision | `GOVERNANCE_DECISION_REQUIRED` | [`POLARIS_EMS_ECD_IMPLEMENTATION_CONTRACT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_IMPLEMENTATION_CONTRACT_AUDIT/POLARIS_EMS_ECD_IMPLEMENTATION_CONTRACT.md) | `UNRESOLVED` |
| **$T_{\text{required}}$ Override TTL** | Software Config Parameter | `OPEN` (BLK-006) | [`POLARIS_EMS_ECD_TREQUIRED_FRESHNESS_RESOLUTION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_BLOCKER_RESOLUTION_AUDIT/POLARIS_EMS_ECD_TREQUIRED_FRESHNESS_RESOLUTION.md) | `PARAMETERIZED` |
| **Critical Load Trajectory $P_{\text{crit}}(t)$** | Station Engineering Input | `30,000 W` (`SYNTHETIC_PROTOTYPE_PARAMETER`) | [`POLARIS_EMS_ECD_PROTOTYPE_FIXTURE_SPECIFICATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_PROTOTYPE_FIXTURE_SPECIFICATION.md) | `ENGINEERING_REQUIRED` |
| **Renewable Survivability Assumption** | Governance / Engineering Assumption | `Zero-Renewable Stress` ($P_{\text{sol}}=0, P_{\text{wnd}}=0$) | [`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json) | `DECISION_REQUIRED_FOR_PRODUCTION` |
| **Usable Battery Energy $C_{\text{usable}}$** | Component Engineering Spec | `160 kWh` ($200\text{kWh}, \text{SOC}\in[20\%, 100\%]$) | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `PROTOTYPE_ESTABLISHED` |
| **Battery Reserve Floor $\text{SOC}_{\text{min}}$** | Component Engineering Spec | `20%` ($0.20$) | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `PROTOTYPE_ESTABLISHED` |
| **Generator Fuel Curve $f_{\text{rate}}(P)$** | Component Engineering Spec | `5 + 0.00025 * P` L/h | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml) | `PROTOTYPE_ESTABLISHED` |
| **Remaining Fuel Inventory $F_{\text{rem}}$** | Ingress Telemetry Signal | `StationState.fuel_remaining_liters` | [`POLARIS_EMS_ECD_INPUT_CONTRACT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_IMPLEMENTATION_CONTRACT_AUDIT/POLARIS_EMS_ECD_INPUT_CONTRACT.json) | `INTERFACE_ESTABLISHED` |
| **Fuel Resupply Interval** | Site Logistics Input | `NOT_ESTABLISHED` | [`T_REQUIRED_INPUT_GAP_REGISTER.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_T_REQUIRED_GOVERNANCE_AUDIT/T_REQUIRED_INPUT_GAP_REGISTER.md) | `MISSING` |
| **Fuel Reserve Floor $F_{\text{reserve,min}}$** | Governance / Engineering Parameter | `OPEN` (HD-06) | [`POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/OPEN_ITEMS_AFTER_DEC004.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/OPEN_ITEMS_AFTER_DEC004.md) | `UNRESOLVED` |
| **Option D Watchdog $T_{\text{max,degraded}}$** | Governance Policy Parameter | `OPEN` (D5 threshold) | [`POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/DEC004_GOVERNANCE_RESOLUTION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/DEC004_GOVERNANCE_RESOLUTION.md) | `UNRESOLVED` |
| **Telemetry Max-Age TTL** | Software Config Parameter | `OPEN` (BLK-007) | [`POLARIS_EMS_ECD_TREQUIRED_FRESHNESS_RESOLUTION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_BLOCKER_RESOLUTION_AUDIT/POLARIS_EMS_ECD_TREQUIRED_FRESHNESS_RESOLUTION.md) | `PARAMETERIZED` |

---

## 3. Provenance Audit Summary

No synthetic test values have been promoted to production status. The provenance boundaries between prototype research artifacts and binding deployment policy are 100% intact.
