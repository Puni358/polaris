# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## CANONICAL SYNTHETIC FIXTURE SPECIFICATION

**Audit Date**: 2026-09-23  
**Status**: SPECIFICATION COMPLETE — FIXTURE GENERATED  
**Fixture ID**: `ECD_CANONICAL_SYNTHETIC_FIXTURE_V1`  

---

### 1. FIXTURE SPECIFICATION CONTRACT

1. **Governance Closed Inputs**:
   - $T_{\text{required}} = 72.0\text{ hours}$ (`SYNTHETIC_ENGINEERING_TEST_VALUE_PRESERVED_UNCHANGED`)
   - $T_{\text{test}} = 2.0\text{ hours}$ (`SYNTHETIC_ECD_LOGIC_VALIDATION_ONLY`)
   - $P_{\text{crit}} = 30,000\text{ W}$ ($30\text{ kW}$, `SYNTHETIC_ENGINEERING_TEST_PARAMETER`)
   - Zero renewable stress scenario ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$)
2. **Governed Component Models**:
   - Battery: $C_{\text{bat}} = 200\text{ kWh}, \text{SOC}_{\text{min}} = 20\%, \eta_{\text{dis}} = 0.92$.
   - Diesel: $f_{\text{rate}} = 5.0 + 0.00025 \times P_{\text{crit}} = 12.5\text{ L/h}$ at $30\text{ kW}$. Physical startup fuel = $0.0\text{ L}$.
3. **Authorized Test Bands**:
   - $\text{HIGH\_SOC} = 80.0\%$
   - $\text{LOW\_SOC} = 30.0\%$
   - $\text{HIGH\_FUEL} = 50.0\text{ L}$
   - $\text{LOW\_FUEL} = 12.5\text{ L}$
   - Equal-Margin Fuel ($80\%\text{ SOC}$) = $46.0\text{ Liters}$ (Analytically derived)
4. **Tie Semantics**:
   - Output: `TIE / BOTH`
   - Resource Preference: `NONE`

---

### 2. DETERMINISM & SERIALIZATION

- **Zero Randomness**: No pseudo-random generators (`random.seed`), stochastic distributions, or external data fetching were used.
- **Canonical Serialization**: All JSON artifacts are generated with key sorting enabled (`sort_keys=True`) and 2-space indentation. Byte-for-byte reproducible across Unix environments.
