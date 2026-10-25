# PRODUCTION VS GAP19 DELTA AUDIT

## FORMULATION DELTA BETWEEN CURRENT `milp.py` AND GOVERNED GAP19 TARGET

- **Current Production MILP**:
  - $N = 360$ variables ($96$ binary, $264$ continuous)
  - $M = 264$ base constraints
  - Objective: Single scalar weighted sum ($)
- **Governed GAP19 Target MILP**:
  - $N = 385$ variables ($120$ binary, $265$ continuous)
  - $M = 265$ constraints
  - Objective: 4-stage lexicographic priority vector $[J_1, J_2, J_3, J_4]$

To elevate `milp.py` to the Governed GAP19 Target, $+25$ variables and $+25$ Stage-2 constraints must be formally added via an authorized model extension phase.
