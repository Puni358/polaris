# Multi-Regime Priority Evidence

## Regime Comparison Matrix

The 409-model experiment evaluated Option A, Current Option B (Priorities 1,2,3,4), and Aligned Option B (Priorities 100,80,60,40) across three operational regimes:

### 1. `RENEWABLE_SURPLUS` Regime
- **Option A**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=0.0\text{ Wh}$
- **Current Option B (1,2,3,4)**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=0.0\text{ Wh}$
- **Aligned Option B (100,80,60,40)**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=0.0\text{ Wh}$
- **Observation**: Objectives do not conflict; all configurations achieve exact objective zero.

### 2. `DIESEL_REQUIRED` Regime
- **Option A**: $J_1=0.0, J_2=0.0, J_3=17.3652\text{ L}, J_4=0.0\text{ Wh}$
- **Current Option B (1,2,3,4)**: $J_1=24000.0, J_2=397200.0, J_3=0.0\text{ L}, J_4=0.0\text{ Wh}$ (FAILED)
- **Aligned Option B (100,80,60,40)**: $J_1=0.0, J_2=0.0, J_3=17.3652\text{ L}, J_4=0.0\text{ Wh}$ (EXACT MATCH)
- **Observation**: Reversing priority order restores 100% exact objective vector equivalence with Option A.

### 3. `HIGH_CURTAILMENT` Regime
- **Option A**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=2347120.0\text{ Wh}$
- **Current Option B (1,2,3,4)**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=2347120.0\text{ Wh}$
- **Aligned Option B (100,80,60,40)**: $J_1=0.0, J_2=0.0, J_3=0.0\text{ L}, J_4=2347120.0\text{ Wh}$
- **Observation**: Curtailment occurs only after load and battery charging are fully satisfied; priority order does not alter the objective vector.

## Scientific Conclusion

The empirical evidence across all three regimes confirms that aligning priority order ($P(J_1) > P(J_2) > P(J_3) > P(J_4)$) is necessary and sufficient to eliminate objective vector discrepancies between Option B and Option A.
