# Emergency → Normal Return Interface Contract

## Governance Audit Status
- **`EMERGENCY_RETURN_POLICY = NOT_ESTABLISHED`**
- Classification: **`GOVERNANCE_REQUIRED`** / **`ENGINEERING_REQUIRED`**

## Interface Boundary Specification
1. In the synthetic demonstration track, ECD evaluates microgrid survivability margins ($m_{\text{battery}}, m_{\text{diesel}}$) independently at each timestep $k$.
2. If survivability margins recover ($m_{\text{battery}} \ge 0$ and $m_{\text{diesel}} \ge 0$), ECD evaluates `operating_mode = NORMAL`.
3. The EMS Router interface specification allows per-step return in synthetic simulation, but identifies that physical deployment requires an explicit governed hysteresis/cooldown policy to prevent mode chattering.

---

## Verdict
`EMERGENCY_RETURN_INTERFACE = SPECIFIED`. Synthetic per-step evaluation is specified; physical station cooldown remains `GOVERNANCE_REQUIRED`.
