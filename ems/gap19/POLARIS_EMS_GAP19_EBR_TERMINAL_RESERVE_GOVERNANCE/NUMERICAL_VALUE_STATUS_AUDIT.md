# Numerical Value Governance Status Audit

| Numerical Value | Context / Location | Provenance Status | Governance Status |
| :--- | :--- | :--- | :--- |
| **56,000 Wh** | Test script `config["ebr_target_wh"]` | `NEW TEST-HARNESS VALUE` | `NOT ESTABLISHED` |
| **160,000 Wh** | Test script `config["terminal_target_wh"]` | `NEW TEST-HARNESS VALUE` | `NOT ESTABLISHED` |
| **20% SOC** | `battery.yaml` / `gap19_highs_native.py` | `IMPLEMENTATION FACT` (Technical Min) | `NOT ESTABLISHED` (as policy floor) |
| **95% SOC** | `battery.yaml` / `gap19_highs_native.py` | `IMPLEMENTATION FACT` (Technical Max) | `NOT ESTABLISHED` |
| **50 kW** | `battery.yaml` | `IMPLEMENTATION FACT` (Max Power) | `NOT ESTABLISHED` |
| **200 kWh** | `battery.yaml` | `IMPLEMENTATION FACT` (Nameplate) | `NOT ESTABLISHED` |
| **72 Hours** | ECD Prototype | `SYNTHETIC TEST VALUE` | `NOT ESTABLISHED` (Superseded by 6h) |
| **6 Hours** | $T_{\text{REQUIRED}}$ Policy | `GOVERNANCE-AUTHORIZED` | **`ESTABLISHED`** |
| **30 kW** | Test script demand profile | `SYNTHETIC TEST VALUE` | `NOT ESTABLISHED` |
| **12.5 L / 50 L** | Fuel test values | `SYNTHETIC TEST VALUE` | `NOT ESTABLISHED` |

```text
NUMERICAL_POLICY_VALUES_AUTHORIZED = NO
```
