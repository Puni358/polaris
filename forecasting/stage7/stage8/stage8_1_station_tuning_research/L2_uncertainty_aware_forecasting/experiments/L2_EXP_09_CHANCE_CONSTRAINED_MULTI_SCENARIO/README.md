# POLARIS L2-EXP-09: Multi-Scenario Stochastic GAP19 Optimization Research

## Overview
This directory contains the implementation, pre-registered policy, and execution harness for **L2-EXP-09**, testing whether explicit uncertainty-aware multi-scenario stochastic MILP optimization can improve the robustness/efficiency tradeoff over static conservative quantile planning (L2-EXP-07) and hand-designed adaptive risk budgeting (L2-EXP-08).

## Primary Research Comparison (5 Arms)
1. **Arm A**: Point-control GAP19 using Candidate F point forecast.
2. **Arm B**: Static $q_{10}$ conservative GAP19 from L2-EXP-07.
3. **Arm C**: Pre-registered Adaptive Risk-Budget GAP19 from L2-EXP-08.
4. **Arm D**: Two-Stage Stochastic Multi-Scenario GAP19 Optimizer (NEW).
5. **Arm E**: Perfect-Foresight Diagnostic Benchmark.

## Directory Structure
- `PRE_REGISTERED_POLICY.md`: Full mathematical derivation, non-anticipativity proofs, and pre-registration lock.
- `pre_registered_policy.json`: Machine-readable specification and cryptographic hashes.
- `run_l2_exp_09.py`: Self-contained execution script evaluating all 173 odd origins (123 NORMAL, 50 EMERGENCY) across 2024 held-out evaluation data.

## Governance
- Strictly RESEARCH-ONLY.
- No production code modified.
- Zero parameters tuned or swept against 2024 outcomes.
- `PRE_REGISTRATION_LOCKED = TRUE`.
- NO PRODUCTION PROMOTION AUTHORIZED.
