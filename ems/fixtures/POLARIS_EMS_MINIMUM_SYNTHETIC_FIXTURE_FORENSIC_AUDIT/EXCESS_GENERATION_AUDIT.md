# EXCESS GENERATION AUDIT
## DIESEL MINIMUM OUTPUT EXCESS & CURTAILMENT AUDIT

### 1. EXCESS GENERATION INPUT VERIFICATION
In Scenario SC-02, generator minimum rating $P_{\text{gen,min}} = 10.0\text{ kW}$. If critical load remaining $P_{\text{crit}} < 10.0\text{ kW}$, unavoidable excess generation is created.

The fixture provides storage headroom ($20\% \to 95\%$) to accept excess charging, and zero headroom when SOC reaches $95\%$ to test curtailment.

### 2. CONCLUSION
`EXCESS_GENERATION_INPUT_STATUS = PASS`.
