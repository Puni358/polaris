# POLARIS EMS — HD-03 C+A CONSISTENCY MATRIX

## 1. GOVERNANCE CONSISTENCY SUMMARY

This document evaluates the compatibility of the approved **HD-03 $T_{\text{required}}$ Source Architecture Model C+A** against all established POLARIS EMS governance decisions (HD-01A, HD-01B, HD-02, HD-04, HD-05, and Policy E3).

**Result**: **100% FULL CONSISTENCY — ZERO CONTRADICTIONS DETECTED.**

---

## 2. CROSS-GOVERNANCE COMPATIBILITY EVALUATION

| Governance Decision | Core Policy Rule | HD-03 C+A Compatibility Analysis | Consistency Status |
| :--- | :--- | :--- | :--- |
| **HD-01A** | EBR = `CRITICAL_LOAD_BASED_DYNAMIC` | Dynamic EBR formula remains active for normal battery resilience targets. $T_{\text{required}}$ C+A model supplies survival horizon to Emergency Detector only and does not alter EBR definition. | **CONSISTENT** |
| **HD-01B** | EBR Interval $N = 6\text{ HOURS}$ | $N = 6\text{h}$ is a fixed normal-operation buffer window. $T_{\text{required}}$ C+A model is completely decoupled from $N$, ensuring normal operation targets remain unchanged while operational survival windows are governed separately. | **CONSISTENT** |
| **HD-02** | Terminal Target $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ | Terminal target shortfall is counted exactly once at boundary horizon $H=24\text{h}$. $T_{\text{required}}$ C+A resolution does not interfere with terminal constraints or MPC horizon boundary conditions. | **CONSISTENT** |
| **HD-04** | Detector Stress Baseline ($P_{\text{solar}}=0, P_{\text{wind}}=0$) | Emergency Detector consumes resolved $T_{\text{required}}$ from C+A resolver to evaluate survival under zero-renewable generation. Normal MPC continues using standard causal forecasts. Zero friction between detector inputs and C+A source model. | **CONSISTENT** |
| **HD-05** | Battery Degradation & Fuel Tolerance | Normal MPC allows up to 5% extra fuel ($F_{\text{diesel}} \le 1.05 \cdot F_{\text{diesel}}^*$) to prevent unnecessary cycling. Emergency mode subordinates degradation to critical service. $T_{\text{required}}$ C+A determines *when* emergency mode triggers without altering objective priorities. | **CONSISTENT** |
| **Policy E3** | Emergency Resource Margin Preservation | Dynamically preserves resource (fuel vs. battery) with larger survivability margin during emergency mode. $T_{\text{required}}$ resolution provides the evaluation timeframe for survival without dictating dispatch trade-offs. | **CONSISTENT** |

---

## 3. SEMANTIC CONFLICT PREVENTION CHECKS

1. **No Horizon Confusion**:
   - $N = 6\text{h}$ (HD-01B): Normal operation battery buffer interval.
   - $H = 24\text{h}$ (HD-02): Rolling MPC optimization horizon.
   - $T_{\text{required}}$ (HD-03): Operational survival window consumed by Emergency Detector.
   - **Verification**: Model C+A preserves all three as distinct mathematical entities.

2. **No Fallback / Derivation Leaks**:
   - Model C+A prohibits Emergency Detector from deriving $T_{\text{required}}$ from fuel or battery capacities.
   - **Verification**: Prevents silent corruption of HD-04 survivability calculations.

3. **No Forecast Pollution**:
   - Model C+A supplies $T_{\text{required}}$ directly to Emergency Detector.
   - HD-04 stress scenario ($P_{\text{solar}}=0, P_{\text{wind}}=0$) is isolated within the Emergency Detector.
   - Normal MPC retains unpolluted causal forecasts from `ForecastBundle`.
   - **Verification**: Causal forecast contracts remain 100% intact.
