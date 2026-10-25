# Decision Options Matrix

## Candidate EBR Formulations
- **EBR-A:** Fixed Absolute Energy Reserve (e.g. $X\text{ Wh}$).
- **EBR-B:** Fixed SOC Percentage Reserve (e.g. $Y\%\text{ SOC}$).
- **EBR-C:** Dynamic Reserve derived from protected critical load over $T_{\text{REQUIRED}} = 6\text{h}$ ($E_{\text{EBR}}[t] = \sum_{k=t}^{t+6} P_{\text{crit}}[k] \Delta t$).
- **EBR-D:** Dynamic Reserve derived from ECD survivability assessment.
- **EBR-E:** Hybrid formulation (Hardware SOC floor + dynamic $T_{\text{REQUIRED}}$ reserve).

## Candidate Terminal Reserve Formulations
- **TR-A:** Fixed Terminal SOC Target (e.g. $Z\%\text{ SOC}$).
- **TR-B:** Fixed Terminal Energy Target ($E_{\text{terminal}} \ge E_{\text{initial}}$).
- **TR-C:** Dynamic Terminal Reserve derived from forecast horizon boundary condition.
- **TR-D:** Dynamic Terminal Reserve derived from future critical load survivability.
- **TR-E:** Zero separate terminal reserve (Eliminate $s_{\text{terminal}}$, rely on $s_{\text{EBR}}[23]$).

*Note: This matrix presents options neutrally for stakeholder decision. No option is pre-selected or ranked.*
