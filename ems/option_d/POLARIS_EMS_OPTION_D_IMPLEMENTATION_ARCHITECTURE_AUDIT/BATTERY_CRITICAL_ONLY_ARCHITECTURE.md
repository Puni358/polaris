# BATTERY CRITICAL ONLY ARCHITECTURE

## 1. CONSTRAINT ARCHITECTURE FOR BATTERY DISCHARGE RESTRICTION

Governance DEC-004 requires:
> "Battery discharge is permitted ONLY for protected critical service. Battery must not support noncritical loads during Option D."

---

## 2. MATHEMATICAL CONSTRAINTS

During emergency modes (`OPTION_D_EMERGENCY` or `UNKNOWN_INVALID_SAFE_STATE`), the Policy Layer sets the upper bound for battery discharge power to the hourly critical demand:

$$0 \le P_{\text{dis}}[t] \le P_{\text{critical}}[t] \quad \forall t \in \{0 \dots H-1\}$$

In addition, the busbar balance constraint for noncritical flexible load ($P_{\text{flex}}$) strictly excludes battery discharge:

$$P_{\text{served,flex}}[t] \le P_{\text{ren,flex}}[t] + P_{\text{dies,flex}}[t]$$
$$(P_{\text{dis}}[t] \text{ is strictly omitted from flexible load balance})$$

---

## 3. INTEGRATION WITH MILP VARIABLE LAYOUT

In `LocalMILPEnergyOptimizer`, the upper bound array `ub` for variable `p_dis` (index $base + 5$) is set dynamically by the `ModeConstraintSet`:

```python
# In NORMAL mode:
ub[base + 5] = max_p_dis  # 50,000 W

# In OPTION_D_EMERGENCY mode:
ub[base + 5] = min(max_p_dis, p_critical[t])  # Bounded by P_critical(t)
```

This enforces the sealed Option D restriction at the physical bound level of the mathematical optimization problem, preventing any battery power from being dispatched to noncritical loads.
