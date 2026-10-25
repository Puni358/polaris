# Current Option-B Model Trace & Audit

## 1. Overview of Existing `GAP19HighsNativeOptimizer`

The active Option-B solver implementation is located at:
`system/optimization/implementations/gap19_highs_native.py`.

It formulates a Mixed-Integer Linear Program (MILP) over a 24-hour horizon ($H=24$) and invokes the HiGHS C++ MILP engine via the `highspy` Python API (`highspy.Highs()`).

---

## 2. Current Variable Vector Layout ($N = 409$)

The existing decision variable vector $x$ has total length $N = 409$ (96 Binary, 313 Continuous):

| Variable Range | Indexing | Description | Type | Count | Retain Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0 .. 359` | $t \times 15 + k$ ($k \in [0, 14]$) | Base decision variables per timestep (15 per step for 24 steps) | 96 Bin, 264 Cont | 360 | **RETAIN** |
| `360 .. 383` | $360 + t$ | Unmet Protected Critical Load Power ($P_{\text{unmet\_crit}}[t]$) | Continuous | 24 | **RETAIN** |
| `384 .. 407` | $384 + t$ | Reserve Shortfall ($s_{\text{EBR}}[t]$) | Continuous | 24 | **RETAIN (RE-LABEL AS $s_{J2}[t]$)** |
| `408` | `408` | Terminal Reserve Shortfall ($s_{\text{terminal}}$) | Continuous | 1 | **REMOVE (UNIFIED INTO $s_{J2}[23]$)** |

### Base Timestep Variables ($k = 0 \dots 14$ for $t \in [0, 23]$):
- `base + 0`: $P_{\text{sol\_used}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 1`: $P_{\text{wind\_used}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 2`: $P_{\text{curt\_sol}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 3`: $P_{\text{curt\_wind}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 4`: $P_{\text{chg}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 5`: $P_{\text{dis}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 6`: $E[t+1]$ (Continuous, stored energy at end of timestep $t$) $\implies$ **RETAIN**
- `base + 7`: $P_{\text{diesel}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 8`: $P_{\text{served}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 9`: $P_{\text{unmet}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 10`: $P_{\text{flex}}[t]$ (Continuous) $\implies$ **RETAIN**
- `base + 11`: $u_{\text{chg}}[t]$ (Binary, charge commitment) $\implies$ **RETAIN**
- `base + 12`: $u_{\text{dis}}[t]$ (Binary, discharge commitment) $\implies$ **RETAIN**
- `base + 13`: $u_{\text{diesel}}[t]$ (Binary, generator running state) $\implies$ **RETAIN**
- `base + 14`: $v_{\text{start}}[t]$ (Binary, generator startup event) $\implies$ **RETAIN**

---

## 3. Current Constraint Breakdown ($M = 313$)

The current model builds $M = 313$ linear constraints in NORMAL mode:

1. **Base Timestep Constraints (Indices 0 .. 263)**: 11 constraints per timestep $\times$ 24 timesteps = 264 constraints:
   - Constraints 1..24: Solar Decomposition ($P_{\text{sol\_used}} + P_{\text{curt\_sol}} = P_{\text{solar\_gen}}$) $\implies$ **RETAIN**
   - Constraints 25..48: Wind Decomposition ($P_{\text{wind\_used}} + P_{\text{curt\_wind}} = P_{\text{wind\_gen}}$) $\implies$ **RETAIN**
   - Constraints 49..72: Bus-Bar Power Balance ($P_{\text{sol\_used}} + P_{\text{wind\_used}} + P_{\text{dis}} + P_{\text{diesel}} - P_{\text{served}} - P_{\text{chg}} - P_{\text{flex}} = 0$) $\implies$ **RETAIN**
   - Constraints 73..96: Total Demand Deficit Balance ($P_{\text{served}} + P_{\text{unmet}} = P_{\text{demand}}$) $\implies$ **RETAIN**
   - Constraints 97..120: Charge Power Limit vs Binary ($P_{\text{chg}} - P_{\text{chg,max}} u_{\text{chg}} \le 0$) $\implies$ **RETAIN**
   - Constraints 121..144: Discharge Power Limit vs Binary ($P_{\text{dis}} - P_{\text{dis,max}} u_{\text{dis}} \le 0$) $\implies$ **RETAIN**
   - Constraints 145..168: Exclusivity ($u_{\text{chg}} + u_{\text{dis}} \le 1$) $\implies$ **RETAIN**
   - Constraints 169..192: Battery Energy State Transition ($E[t+1] - E[t] - \eta_{\text{chg}} P_{\text{chg}} \Delta t + \frac{P_{\text{dis}}}{\eta_{\text{dis}}} \Delta t = 0$) $\implies$ **RETAIN**
   - Constraints 193..216: Diesel Min Output ($P_{\text{diesel}} - P_{\text{diesel,min}} u_{\text{diesel}} \ge 0$) $\implies$ **RETAIN**
   - Constraints 217..240: Diesel Max Output ($P_{\text{diesel}} - P_{\text{diesel,max}} u_{\text{diesel}} \le 0$) $\implies$ **RETAIN**
   - Constraints 241..264: Diesel Startup Tracking ($v_{\text{start}}[t] - u_{\text{diesel}}[t] + u_{\text{diesel}}[t-1] \ge 0$) $\implies$ **RETAIN**

2. **Layer B Constraints (Indices 264 .. 287)**: 24 Critical Demand Balance Constraints:
   - $P_{\text{served}}[t] + P_{\text{unmet\_crit}}[t] = P_{\text{crit\_dem}}[t]$ $\implies$ **RETAIN**

3. **Layer C Constraints (Indices 288 .. 311)**: 24 EBR Shortfall Constraints:
   - $E[t+1] + s_{\text{EBR}}[t] \ge E_{\text{EBR,target}}$ $\implies$ **MODIFY (UPDATE RHS TO POINTWISE ENVELOPE $E_{\text{stage2,target}}[t]$)**

4. **Layer C Constraint 313 (Index 312)**: 1 Terminal Reserve Shortfall Constraint:
   - $E[24] + s_{\text{terminal}} \ge E_{\text{term,target}}$ $\implies$ **REMOVE (UNIFIED INTO $E_{\text{stage2,target}}[23]$)**

---

## 4. Current Objectives & Priority Setup in `highspy`

The current code defines four linear objectives using `highspy.HighsLinearObjective()`:

```python
# obj1: J1 (Critical Deficit Wh) - Priority 4 (Highest)
obj1.priority = 4; obj1.coefficients = c1.tolist() # c1[idx_unmet_crit + t] = 1.0 * dt

# obj2: J2 (Reserve Shortfall Wh) - Priority 3
obj2.priority = 3; obj2.coefficients = c2.tolist() # c2[idx_s_ebr + t] = 1.0, c2[idx_s_term] = 1.0

# obj3: J3 (Diesel Fuel Liters) - Priority 2
obj3.priority = 2; obj3.coefficients = c3.tolist() # Fuel consumption coefficients

# obj4: J4 (Renewable Curtailment Wh) - Priority 1 (Lowest)
obj4.priority = 1; obj4.coefficients = c4.tolist() # Curtailment coefficients
```

HiGHS option: `blend_multi_objectives = False` (enforces strict lexicographic optimization).

---

## 5. Retention Summary

- **Retained Base Variables**: All 360 base variables (indices 0..359).
- **Retained Layer B Variables**: All 24 $P_{\text{unmet\_crit}}[t]$ variables (indices 360..383).
- **Retained & Re-labeled Layer C Variables**: 24 $s_{\text{EBR}}[t]$ variables re-labeled as $s_{J2}[t]$ (indices 384..407).
- **Eliminated Variable**: $s_{\text{terminal}}$ (index 408) is eliminated via pointwise maximum envelope unification.
- **Retained Constraints**: 288 constraints (264 base + 24 critical demand balance).
- **Modified Constraints**: 24 Stage 2 reserve constraints (288..311) updated to pointwise envelope target $E_{\text{stage2,target}}[t]$.
- **Eliminated Constraint**: Separate terminal constraint 312 eliminated.
