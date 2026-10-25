# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## PROTOTYPE FIXTURE SPECIFICATION (RE-AUDITED SPECIFICATION)

**Audit Date**: 2026-09-23  
**Status**: SPECIFICATION ONLY — NO RUNTIME FIXTURE IMPLEMENTED  
**Classification**: `SYNTHETIC_ENGINEERING_TEST_DATA`  
**Station Meaning**: `NONE`  

---

### 1. PROTOTYPE FIXTURE SPECIFICATION CONTRACT

This specification defines the 72-hour synthetic prototype fixture package (`ECD_SYNTHETIC_TEST_FIXTURE`) for controlled ECD logic testing.

1. **Governance Closed Inputs**:
   - $T_{\text{required}} = 72.0\text{ hours}$ (`SYNTHETIC_ENGINEERING_TEST_VALUE`)
   - Zero renewable stress scenario ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$)
2. **Governed Physical Models**:
   - Battery: $C_{\text{bat}} = 200\text{ kWh}, \text{SOC}_{\text{min}} = 20\%, \eta_{\text{dis}} = 0.92$. Equation: $T_{\text{battery}} = \frac{200,000 \times ((\text{SOC}-20)/100) \times 0.92}{P_{\text{crit}}}$.
   - Diesel: $f_{\text{rate}} = 5.0 + 0.00025 \times P_{\text{crit}}\text{ L/h}$. Equation: $T_{\text{diesel}} = \frac{F_{\text{initial}}}{f_{\text{rate}}}$.
3. **Pending Governance Selection**:
   - Synthetic battery state selection rule: `GOVERNANCE_REQUIRED`.
   - Synthetic fuel state selection rule: `GOVERNANCE_REQUIRED`.
