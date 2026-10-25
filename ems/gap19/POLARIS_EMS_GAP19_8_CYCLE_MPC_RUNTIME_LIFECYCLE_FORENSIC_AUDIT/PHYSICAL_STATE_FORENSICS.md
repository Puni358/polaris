# Physical State Update Forensics

## 1. Physical State Variables Propagation Audit

1. **Battery SOC / Energy**:
   - Initial SOC: $80.0\%$ ($160,000.0\text{ Wh}$).
   - Cycle 1 action: $P_{\text{chg}} = 29,064.27\text{ W}$ for $1.0\text{ h} \implies \text{Energy Added} = 0.92 \times 29,064.27 = 26,739.1284\text{ Wh}$.
   - SOC after Cycle 1: $(186,739.1284 / 200,000) \times 100 = 93.3696\%$.
   - Cycles 2..8 actions: $P_{\text{chg}} = 0\text{ W}, P_{\text{dis}} = 0\text{ W}$. SOC held at $93.3696\%$ ($186,739.13\text{ Wh}$).
2. **Diesel Generator Running State**:
   - Cycle 1: $P_{\text{diesel}} = 44,064.27\text{ W} > 0 \implies \text{diesel\_running} = \text{True}$.
   - Cycles 2..8: $P_{\text{diesel}} = 15,000.00\text{ W} > 0 \implies \text{diesel\_running} = \text{True}$.
3. **Fuel Inventory State**:
   - Fuel consumption is computed and recorded per cycle in `DispatchPlan` (`j3_objective`). Fuel inventory was not passed as a hard constraint in this synthetic setup (`FUEL_STATE_CONTINUITY = NOT_APPLICABLE`).

---

## 2. Verdict

```
PHYSICAL_STATE_PROPAGATION_EXACT = YES
PHYSICAL_STATE_FORENSICS_STATUS = PASS
```
