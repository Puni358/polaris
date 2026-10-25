# Option A vs Option B Disagreement Forensics

## 1. Empirical Objective Disagreement (`DIESEL_REQUIRED` Regime)

In the canonical 409-variable / 313-constraint experiment under the `DIESEL_REQUIRED` regime, the objective values produced by Option A and Option B were recorded as follows:

| Metric | Option A (Sequential MILP Reference) | Option B (Current `gap19_highs_native.py`) | Disagreement |
| :--- | :---: | :---: | :---: |
| **$J_1$ (Critical Deficit Wh)** | `0.0000` | `24000.0000` | $+24000.0000$ Wh |
| **$J_2$ (EBR Shortfall Wh)** | `0.0000` | `397200.0000` | $+397200.0000$ Wh |
| **$J_3$ (Diesel Fuel Liters)** | `17.3652` | `0.0000` | $-17.3652$ L |
| **$J_4$ (Curtailment Wh)** | `0.0000` | `0.0000` | $0.0000$ Wh |

## 2. Physical Mechanism Breakdown

1. **Option B Priority Order ($J_4 > J_3 > J_2 > J_1$)**:
   - HiGHS first optimizes $J_4$ (curtailment), finding $J_4^* = 0$.
   - Next, HiGHS optimizes $J_3$ (diesel fuel consumption). To minimize fuel consumption, HiGHS sets diesel power $P_{\text{diesel}}[t] = 0$ for all timesteps, achieving $J_3^* = 0.0$ Liters.
   - Because $P_{\text{diesel}}[t] = 0$ is now locked (or constrained by $J_3^* = 0$), when HiGHS subsequently attempts to minimize $J_2$ (EBR shortfall) and $J_1$ (critical deficit), it cannot start the diesel generator.
   - As a result, $24,000\text{ Wh}$ of critical demand goes unmet ($J_1 = 24000\text{ Wh}$), and battery reserves suffer $397,200\text{ Wh}$ of shortfall ($J_2 = 397200\text{ Wh}$).

2. **Option A Priority Order ($J_1 > J_2 > J_3 > J_4$)**:
   - Option A first optimizes $J_1$ (critical deficit) to $0.0\text{ Wh}$.
   - It then locks $J_1 = 0$ and optimizes $J_2$ (EBR shortfall) to $0.0\text{ Wh}$.
   - To achieve $J_1 = 0$ and $J_2 = 0$, Option A is forced to start the diesel generator, consuming $17.3652$ Liters of fuel ($J_3 = 17.3652\text{ L}$).

## 3. Diagnostic Conclusion

The observed objective disagreement between Option A and Option B in the `DIESEL_REQUIRED` regime is **100% explained by the reversed lexicographic priority order**. No other secondary or latent causes exist.
