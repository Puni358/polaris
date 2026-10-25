# MODEL DELTA AUDIT

## COMPONENT-BY-COMPONENT COMPARISON TABLE

| Model Feature | Current Production `milp.py` | Experiment Test Model | Delta Classification |
|---|---|---|---|
| Variable Count $N$ | 360 | 385 | ADDITIVE_DIFFERENCE (+25 Stage-2 slacks) |
| Binary Count | 96 | 120 | ADDITIVE_DIFFERENCE (+24 $w_{\text{stop}}$ binaries) |
| Continuous Count | 264 | 265 | ADDITIVE_DIFFERENCE (+25 slacks, -24 $p_{\text{served}}$) |
| Constraint Count $M$ | 264 | 265 | MODIFIED (Consolidated bus balance + 25 Stage-2) |
| Horizon $H$ | 24 hours | 24 hours | IDENTICAL |
| Timestep $\Delta t$ | 1.0 hour | 1.0 hour | IDENTICAL |
| Objectives | Single scalar sum | Lexicographic $J_1, J_2, J_3, J_4$ | MODIFIED (Governed target multi-objective) |
| EBR Formulation | None | $s_{\text{EBR}}(t)$ slacks & constraints | ADDITIVE_DIFFERENCE (Stage-2 extension) |
| Terminal Reserve | None | $s_{\text{term}}$ slack & constraint | ADDITIVE_DIFFERENCE (Stage-2 extension) |
| Flexible Load | Supported in schema | Fixed upper bound in experiment | MODIFIED |
