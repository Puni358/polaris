# Option D E3 Resource Preservation Semantics Audit

## Verification of E3 Resource Semantics (`system/control/ecd.py`)

1. **Larger Survivability Margin ($m_{\text{battery}} > m_{\text{diesel}}$)**:
   - `preserved_resource = BATTERY`
   - `limiting_resource = DIESEL`
   - **Option D Action**: Minimize battery discharge; rely on diesel generator.

2. **Smaller Survivability Margin ($m_{\text{battery}} < m_{\text{diesel}}$)**:
   - `preserved_resource = DIESEL`
   - `limiting_resource = BATTERY`
   - **Option D Action**: Discharge usable battery energy to save diesel fuel.

3. **Equal Margins ($|m_{\text{battery}} - m_{\text{diesel}}| \le 10^{-6}\text{h}$)**:
   - `preserved_resource = BOTH` (Tie)
   - `limiting_resource = BOTH` (Tie)
   - **Option D Action**: No resource preference.

---

## Verdict
E3 resource preservation semantics are 100% verified and strictly preserved.
