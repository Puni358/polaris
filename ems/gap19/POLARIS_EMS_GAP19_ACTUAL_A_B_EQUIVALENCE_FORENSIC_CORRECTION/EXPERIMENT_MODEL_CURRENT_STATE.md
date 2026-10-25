# EXPERIMENT MODEL CURRENT STATE AUDIT

## SOURCE FILE: `scratch/polaris_gap19_highspy_validation/run_experiment.py`

Inspection of the script used to generate the equivalence test model in `POLARIS_EMS_GAP19_ACTUAL_A_B_EQUIVALENCE_TEST/` demonstrates:

- **Total Variables**: $N = 385$
  - Base variables: $24 \times 15 = 360$
  - Additional Stage-2 EBR slacks: $24$ ($s_{\text{EBR}}(t)$ for $t=0..23$)
  - Additional Stage-2 Terminal energy slack: $1$ ($s_{\text{term}}$)
- **Binary Variables**: 120 (5 per step $\times 24$: $u_{\text{diesel}}, v_{\text{start}}, w_{\text{stop}}, u_{\text{ch}}, u_{\text{dis}}$)
- **Continuous Variables**: 265 ($385 - 120 = 265$)
- **Constraints**: $M = 265$
  - Power Balance (24 equalities)
  - Diesel Min Output (24 inequalities)
  - Diesel Max Output (24 inequalities)
  - Diesel Status Transitions (24 equalities)
  - Battery Charge Power Bound (24 inequalities)
  - Battery Discharge Power Bound (24 inequalities)
  - Battery Charge/Discharge Exclusivity (24 inequalities)
  - Energy Storage Dynamics (24 equalities)
  - Solar Generation Balance (24 equalities)
  - Wind Generation Balance (24 equalities)
  - Emergency Battery Reserve Slack Relations (24 inequalities)
  - Terminal Battery Energy Relation (1 inequality)
- **Objective Structure**: Full GAP19 governed 4-stage lexicographic vector $[J_1, J_2, J_3, J_4]$.
- **Canonical Model Hash**: `9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c`
