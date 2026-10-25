# Toy Test Forensics

## Setup Analyzed
- **Decision Variable**: $x \in [0, 10]$
- **Objective A**: $\min x$ (`priority = 4`)
- **Objective B**: $\min -x$ (`priority = 1`)
- **Mode**: `blend_multi_objectives = False`
- **Result**: $x = -0.0$ (Objective A dominated)

## Forensic Finding
The toy LP test conclusively demonstrates that under `highspy` 1.15.1, priority 4 takes precedence over priority 1.
