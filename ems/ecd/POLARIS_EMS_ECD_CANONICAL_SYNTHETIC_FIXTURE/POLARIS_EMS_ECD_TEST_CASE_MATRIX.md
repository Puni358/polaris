# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## CANONICAL SYNTHETIC FIXTURE TEST-CASE MATRIX

**Audit Date**: 2026-09-23  
**Status**: GENERATED & INDEPENDENTLY VERIFIED  
**Fixture ID**: `ECD_CANONICAL_SYNTHETIC_FIXTURE_V1`  
**Governed Policy Horizon**: $T_{\text{required}} = 72.0\text{h}$ (Preserved Unchanged)  
**Synthetic Logic Horizon**: $T_{\text{test}} = 2.0\text{h}$ (`SYNTHETIC_ECD_LOGIC_VALIDATION_ONLY`)  

---

### 1. MASTER 5-CASE TEST MATRIX

All cases use constant $P_{\text{crit}} = 30,000\text{ W}$ ($30\text{ kW}$) and $T_{\text{test}} = 2.0\text{ hours}$:

| Case ID | Case Name | Predeclared SOC | Predeclared Fuel | $T_{\text{battery}}$ | $T_{\text{diesel}}$ | $M_{\text{battery}}$ ($T_{\text{test}}=2\text{h}$) | $M_{\text{diesel}}$ ($T_{\text{test}}=2\text{h}$) | Expected Mode | Preserved Resource | Limiting Resource | Case Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CASE 1** | **NORMAL** | $80.0\%$ | $50.0\text{ L}$ | $3.68\text{h}$ | $4.00\text{h}$ | $+1.68\text{h}$ | $+2.00\text{h}$ | `NORMAL` | `N/A` | `N/A` | **PASS** |
| **CASE 2** | **BATTERY-LIMITED** | $30.0\%$ | $50.0\text{ L}$ | $0.61\text{h}$ | $4.00\text{h}$ | $-1.39\text{h}$ | $+2.00\text{h}$ | `EMERGENCY` | `DIESEL` | `BATTERY` | **PASS** |
| **CASE 3** | **DIESEL-LIMITED** | $80.0\%$ | $12.5\text{ L}$ | $3.68\text{h}$ | $1.00\text{h}$ | $+1.68\text{h}$ | $-1.00\text{h}$ | `EMERGENCY` | `BATTERY` | `DIESEL` | **PASS** |
| **CASE 4** | **BOTH-FAIL** | $30.0\%$ | $12.5\text{ L}$ | $0.61\text{h}$ | $1.00\text{h}$ | $-1.39\text{h}$ | $-1.00\text{h}$ | `EMERGENCY` | `DIESEL` | `BATTERY` | **PASS** |
| **CASE 5** | **EQUAL-MARGIN / TIE** | $80.0\%$ | $46.0\text{ L}$* | $3.68\text{h}$ | $3.68\text{h}$ | $+1.68\text{h}$ | $+1.68\text{h}$ | `NORMAL` | `TIE / BOTH` | `TIE / BOTH` | **PASS** |

*\*Note for Case 5: $F_{\text{equal}} = 3.68\text{h} \times 12.5\text{ L/h} = 46.0\text{ Liters}$ is analytically derived from the predeclared SOC=80% value to achieve exact equal time margins ($M_{\text{battery}} == M_{\text{diesel}} = +1.68\text{h}$, tolerance error $\epsilon = 0.0000\text{h}$).*

---

### 2. INDEPENDENT SELF-AUDIT VERIFICATION

Every case in the canonical fixture was independently recalculated from stored inputs:
1. `CASE_1_NORMAL`: $M_{\text{battery}} = +1.68\text{h} \ge 0$, $M_{\text{diesel}} = +2.00\text{h} \ge 0 \implies$ Mode = `NORMAL`. `PASS`.
2. `CASE_2_BATTERY_LIMITED`: $M_{\text{battery}} = -1.39\text{h} < 0$, $M_{\text{diesel}} = +2.00\text{h} > 0 \implies$ Mode = `EMERGENCY`, Preserved = `DIESEL`, Limiting = `BATTERY`. `PASS`.
3. `CASE_3_DIESEL_LIMITED`: $M_{\text{battery}} = +1.68\text{h} > 0$, $M_{\text{diesel}} = -1.00\text{h} < 0 \implies$ Mode = `EMERGENCY`, Preserved = `BATTERY`, Limiting = `DIESEL`. `PASS`.
4. `CASE_4_BOTH_FAIL`: $M_{\text{battery}} = -1.39\text{h} < 0$, $M_{\text{diesel}} = -1.00\text{h} < 0 \implies$ Mode = `EMERGENCY`, Preserved = `DIESEL` ($-1.00\text{h} > -1.39\text{h}$), Limiting = `BATTERY`. `PASS`.
5. `CASE_5_EQUAL_MARGIN`: $|M_{\text{battery}} - M_{\text{diesel}}| = |1.68 - 1.68| = 0.0000\text{h} \implies$ Preserved = `TIE / BOTH`, Limiting = `TIE / BOTH`. `PASS`.
