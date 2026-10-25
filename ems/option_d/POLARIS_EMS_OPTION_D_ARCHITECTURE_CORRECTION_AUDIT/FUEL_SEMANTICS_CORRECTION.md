# FUEL SEMANTICS CORRECTION

## 1. PHYSICAL TANK STATE vs RESUPPLY FUEL BUDGET

The audit clarified the distinct definitions of diesel fuel concepts to prevent conflation between real-time telemetry and seasonal supply policy:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ fuel_remaining_liters : Physical Diesel Fuel Volume Remaining in Tank (L)  │
├─────────────────────────────────────────────────────────────────────────────┤
│ fuel_resupply_budget  : Seasonal / Periodic Logistics Resupply Allocation (L)│
├─────────────────────────────────────────────────────────────────────────────┤
│ fuel_critical_buffer  : Emergency Fuel Reserve Floor for Critical Operations │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. COMPATIBILITY & SCOPE
1. **ECD Survivability Input**: ECD `evaluate()` requires **`fuel_remaining_liters`** (physical fuel volume currently in the diesel storage tank) to compute fuel endurance $t_{\text{diesel}} = \frac{V_{\text{fuel}}}{F(P_{\text{critical}})}$.
2. **Fuel Budget Policy Firewall**: Seasonal resupply budgets or economic fuel allocation policies are separately governed and MUST NOT be conflated with real-time physical tank inventory tracking.
