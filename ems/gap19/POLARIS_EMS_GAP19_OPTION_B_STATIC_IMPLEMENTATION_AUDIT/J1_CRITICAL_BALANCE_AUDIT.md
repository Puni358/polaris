# J1 Critical Balance Audit

The critical load balance equation is implemented on lines 230-238:
$$P_{\text{served}}[t] + P_{\text{unmet,critical}}[t] = P_{\text{critical\_demand}}[t]$$

Semantics:
- Protected critical demand ($P_{\text{critical\_demand}}[t]$) is distinct from total station demand ($P_{\text{demand}}[t]$).
- If critical demand is unspecified in config, default fallback to total demand is established safely without altering baseline schemas.

`J1_CRITICAL_BALANCE = PASS`
