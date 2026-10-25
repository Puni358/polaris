# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## TEST CASE REACHABILITY & MATRIX SPECIFICATION

**Audit Date**: 2026-09-23  
**Status**: FEASIBILITY AUDIT COMPLETE — RE-AUDITED TEST CASE MATRIX  
**Governance Horizon**: $T_{\text{required}} = 72.0\text{h}$ (Preserved Unchanged)  
**Synthetic Logic Validation Horizon**: $T_{\text{test}} = 2.0\text{h}$ (Feasible Test Space)  

---

### 1. REASON FOR TWO MATRIX SPECIFICATIONS

1. **Under $T_{\text{required}} = 72.0\text{h}$ (Governed Emergency Survivability Horizon)**:
   - Maximum battery endurance at $95\%\text{ SOC}$ ($P_{\text{crit}} = 30\text{ kW}$) is $T_{\text{battery,max}} = 4.60\text{ hours}$.
   - Battery time margin $M_{\text{battery}} = T_{\text{battery}} - 72.0\text{h}$ is ALWAYS negative ($M_{\text{battery}} \le -67.40\text{h}$).
   - Therefore, State A (NORMAL: $M_{\text{battery}} \ge 0$) and State C (DIESEL-LIMITED: $M_{\text{battery}} > 0 > M_{\text{diesel}}$) are **UNREACHABLE** under $T_{\text{required}} = 72\text{h}$.

2. **Under $T_{\text{test}} = 2.0\text{h}$ (Synthetic Logic Validation Horizon)**:
   - For $T_{\text{test}} \in (0, 4.60\text{h})$, battery margin $M_{\text{battery}} = T_{\text{battery}} - T_{\text{test}}$ CAN be positive ($M_{\text{battery}} > 0$).
   - ALL FIVE ECD LOGICAL DECISION STATES ARE 100% REACHABLE.

---

### 2. FEASIBLE 5-STATE TEST MATRIX ($T_{\text{test}} = 2.0\text{h}, P_{\text{crit}} = 30\text{ kW}$)

All numerical inputs are generated using predeclared test bands ($\text{SOC}_{\text{high}} = 80\%, \text{SOC}_{\text{low}} = 30\%, F_{\text{high}} = 50.0\text{L}, F_{\text{low}} = 12.5\text{L}$):

| Case ID | Logical State | Predeclared Initial State | $T_{\text{battery}}$ | $T_{\text{diesel}}$ | $M_{\text{battery}}$ ($T_{\text{test}}=2\text{h}$) | $M_{\text{diesel}}$ ($T_{\text{test}}=2\text{h}$) | Calculated Mode | Preserved Resource | Limiting Resource | Reachability Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CASE-1** | **NORMAL** | $\text{SOC}=80\%, F=50.0\text{L}$ | $3.68\text{h}$ | $4.00\text{h}$ | $+1.68\text{h}$ | $+2.00\text{h}$ | `NORMAL` | `N/A` | `N/A` | **REACHABLE** |
| **CASE-2** | **BATTERY-LIMITED** | $\text{SOC}=30\%, F=50.0\text{L}$ | $0.61\text{h}$ | $4.00\text{h}$ | $-1.39\text{h}$ | $+2.00\text{h}$ | `EMERGENCY` | `Diesel` | `Battery` | **REACHABLE** |
| **CASE-3** | **DIESEL-LIMITED** | $\text{SOC}=80\%, F=12.5\text{L}$ | $3.68\text{h}$ | $1.00\text{h}$ | $+1.68\text{h}$ | $-1.00\text{h}$ | `EMERGENCY` | `Battery` | `Diesel` | **REACHABLE** |
| **CASE-4** | **BOTH-FAIL** | $\text{SOC}=30\%, F=12.5\text{L}$ | $0.61\text{h}$ | $1.00\text{h}$ | $-1.39\text{h}$ | $-1.00\text{h}$ | `EMERGENCY` | `Diesel` | `Battery` | **REACHABLE** |
| **CASE-5** | **EQUAL-MARGIN** | $\text{SOC}=80\%, F=46.0\text{L}$ | $3.68\text{h}$ | $3.68\text{h}$ | $+1.68\text{h}$ | $+1.68\text{h}$ | `NORMAL` | `TIE / BOTH` | `TIE / BOTH` | **REACHABLE** (Tie-break `GOVERNANCE_REQUIRED`) |

*Note: For Case 5 Equal Margin, $F_{\text{initial}} = 12.5 \times 3.68 = 46.0\text{ Liters}$ is analytically derived from the predeclared SOC value.*
