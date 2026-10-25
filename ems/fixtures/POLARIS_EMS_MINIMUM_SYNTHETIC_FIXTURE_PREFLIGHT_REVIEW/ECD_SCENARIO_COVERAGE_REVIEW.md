# ECD SCENARIO COVERAGE REVIEW
## AUDIT OF EMERGENCY CONDITION DETECTOR STATE COVERAGE

### 1. FORENSIC AUDIT OF ECD COVERAGE
The Emergency Condition Detector (ECD) evaluates whether available station energy resources can sustain protected critical load ($P_{\text{critical}} = 30\text{ kW}$) for the sealed baseline horizon $T_{\text{required\_baseline}} = 6\text{h}$.

The ECD outputs five operational states:
1. `ECD-NORMAL`: $T_{\text{surv}} \ge T_{\text{required\_baseline}} (6\text{h})$ using renewables + storage alone.
2. `ECD-BATTERY-LIMITED`: Battery depleted below critical floor during $6\text{h}$ window; diesel required.
3. `ECD-DIESEL-LIMITED`: Diesel fuel depleted below $6\text{h}$ reserve requirement; battery required.
4. `ECD-BOTH-LIMITED`: Both battery SOC and diesel fuel insufficient to guarantee $6\text{h}$ critical service.
5. `ECD-UNKNOWN_INVALID`: Missing or corrupt telemetry / forecast data inputs; triggers safe-state fallback.

### 2. SCENARIO-TO-ECD MAPPING
The proposed 5-scenario test suite maps to these ECD states as follows:

| Scenario ID | Scenario Name | Primary Initial State / Conditions | Expected ECD Classification | ECD Behavior Tested |
|---|---|---|---|---|
| **SC-01** | Normal Operation | SOC = 80%, $V_{\text{fuel}} = 500\text{ L}$, Full Renewables | `ECD-NORMAL` | Normal policy, baseline MPC dispatch |
| **SC-02** | Battery-Limited Emergency | SOC = 20% (min floor), Zero Renewables, $V_{\text{fuel}} = 500\text{ L}$ | `ECD-BATTERY-LIMITED` | Emergency mode trigger, Option D diesel support |
| **SC-03** | Diesel-Limited Emergency | SOC = 80%, Zero Renewables, $V_{\text{fuel}} = 20\text{ L}$ ($< 75\text{ L}$ needed) | `ECD-DIESEL-LIMITED` | Emergency mode trigger, battery critical discharge |
| **SC-04** | Both-Resources Limited | SOC = 20%, Zero Renewables, $V_{\text{fuel}} = 10\text{ L}$ | `ECD-BOTH-LIMITED` | Severe deficit, proportional allocation, escalation |
| **SC-05** | UNKNOWN_INVALID Fallback | Telemetry $P_{\text{critical}}$ set to `NaN` / missing | `ECD-UNKNOWN_INVALID` | Fallback policy layer, safe state execution |

### 3. MINIMALITY EVALUATION
- **Can any scenario be omitted?**
  - No. Omitting any scenario would leave at least one primary ECD state unverified in software execution.
- **Can multiple ECD states be tested in a single 24-hour run?**
  - Yes. In a sequential dynamic scenario, the system could transition from Normal to Battery-Limited to Both-Limited over 24 hours. However, defining 5 distinct deterministic initial-condition scenarios provides clear, isolated unit-integration test cases.

### 4. CONCLUSION & RECOMMENDATION
`ECD_COVERAGE_STATUS = MINIMUM_COVERAGE_VERIFIED`.
The 5 deterministic scenarios fully cover all 5 required ECD operational states using the sealed baseline $T_{\text{required\_baseline}} = 6\text{h}$.
