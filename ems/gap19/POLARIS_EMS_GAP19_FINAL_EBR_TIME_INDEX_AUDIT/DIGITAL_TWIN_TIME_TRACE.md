# Digital Twin Time Trace (`DIGITAL_TWIN_TIME_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/simulation/simulator.py`  
**VERDICT**: `CONFIRMED`

---

## 1. Digital Twin Step Execution Semantics

- Input State $S_n$: Observation timestamp $t_n = t_{\text{now}}$.
- Executed Action $a_{n,0}$: $P_{\text{chg}}[0], P_{\text{dis}}[0], P_{\text{diesel}}[0]$ applied over $[t_n, t_n + 1\text{h}]$.
- Output State $S_{n+1}$: Timestamp $t_{n+1} = \text{actuals\_next\_step}["\text{timestamp}"] = t_{\text{now}} + 1\text{h}$.

```text
DIGITAL_TWIN_TIMESTEP_ADVANCEMENT = EXACT_PLUS_1H
```
