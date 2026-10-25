# OPTION D SCENARIO COVERAGE REVIEW
## AUDIT OF SEALED OPTION D POLICY BEHAVIOR MAPPING (OD-01 TO OD-11)

### 1. FORENSIC AUDIT OF OPTION D GOVERNANCE REQUIREMENTS
Sealed human governance decision `DEC-004` selected **OPTION D — PROTECTED CRITICAL LOAD FALLBACK**. Option D encompasses 11 mandatory operational behaviors (OD-01 through OD-11).

This preflight audit verified that the 5 proposed deterministic scenarios provide complete test coverage for all 11 Option D policy behaviors.

### 2. OPTION D BEHAVIORAL MAPPING MATRIX

| Code | Sealed Option D Governance Rule | Exercising Scenario(s) | Verification Condition |
|---|---|---|---|
| **OD-01** | Renewable directly supports protected critical load | SC-01 (Normal) | $P_{\text{PV}} + P_{\text{wind}}$ allocated to $P_{\text{critical}}$ first |
| **OD-02** | Renewable insufficient $\rightarrow$ diesel supports remaining critical demand | SC-02 (Battery-Limited) | $u_{\text{gen}}=1$ when renewables $< P_{\text{critical}}$ |
| **OD-03** | Diesel minimum output ($10\text{ kW}$) creates excess generation | SC-01 / SC-02 | $P_{\text{gen,min}} > P_{\text{critical\_rem}}$ creates excess |
| **OD-04** | Excess diesel generation charges battery | SC-02 (Hour 0–4) | $P_{\text{batt,charge}} = P_{\text{gen}} - P_{\text{critical\_rem}}$ |
| **OD-05** | Battery reaches max SOC limit $\rightarrow$ remaining excess curtailed | SC-01 (Hour 12) | $P_{\text{curtail}} > 0$ when SOC = $95\%$ |
| **OD-06** | Renewable + diesel unavailable $\rightarrow$ battery supports critical load | SC-03 (Diesel-Limited) | Battery discharges to $P_{\text{critical}}$ when genset off |
| **OD-07** | Battery discharge prohibited for noncritical load | SC-01 / SC-03 | $P_{\text{flexible\_served}} = 0$ when battery discharging |
| **OD-08** | Available power insufficient for all critical minimums | SC-04 (Both-Limited) | $P_{\text{avail}} < P_{\text{critical\_min\_total}}$ ($30\text{ kW}$) |
| **OD-09** | Protected critical systems receive proportional allocation | SC-04 (Both-Limited) | Allocations match $15:10:5$ ($50\%:33.3\%:16.7\%$) |
| **OD-10** | Operator escalation condition triggered | SC-04 / SC-05 | Alarm flag `OPERATOR_ESCALATION_REQUIRED` emitted |
| **OD-11** | Recovery from degraded operation to normal operation | SC-01 (Hour 18–24) | Revert from Emergency to Normal mode upon resource recovery |

### 3. MINIMALITY EVALUATION
All 11 sealed Option D behaviors are fully exercised across the 5 deterministic scenarios without requiring additional test runs.

### 4. CONCLUSION & RECOMMENDATION
`OPTION_D_COVERAGE_STATUS = MINIMUM_COVERAGE_VERIFIED`.
The proposed synthetic fixture design guarantees 100% test coverage of sealed Option D policy governance.
