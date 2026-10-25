# Fuel First-Action Propagation Audit

## First-Action Commitment Constraint

```text
State_k (SOC_k, Fuel_k)
   │
   ▼
DispatchPlan_k (24h schedule)
   │
   ▼
Committed First Action Only (k=0):
   P_diesel,0 = dispatch_plan.diesel_power[0]
   diesel_running_0 = (P_diesel,0 > 0)
   │
   ▼
DigitalTwinSimulator.step():
   Fuel_consumed,0 = (F_base * diesel_running_0 + F_marg * P_diesel,0) * 1.0h
   Fuel_{k+1} = max(0.0, Fuel_k - Fuel_consumed,0)
   │
   ▼
State_{k+1} (SOC_{k+1}, Fuel_{k+1})
```

## Truth Firewall Verification:
- Tail planned actions ($k=1\dots23$) in `DispatchPlan` do **NOT** physically consume fuel in `DigitalTwinSimulator`.
- Fuel state advances strictly through executed first action $k=0$.

---

## Verdict
`FUEL_FIRST_ACTION_ONLY = ESTABLISHED`.
