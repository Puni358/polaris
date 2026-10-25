# TIME HORIZON TERMINOLOGY CORRECTION
## RE-CLASSIFIED TIME HORIZON & TIMESTEP TERMINOLOGY

### 1. SPECIFICATION RECONCILIATION
All imprecise claims regarding "mathematically proven minimum duration" or "optimal timestep" are formally removed.

The time horizon and timestep parameters are re-classified into four strictly uncoupled concepts:

### 2. FORMAL UNCOUPLED CLASSIFICATION MATRIX

| Horizon Concept | Symbol | Reconciled Value | Precise Terminology Classification | Governance Role |
|---|---|---|---|---|
| **MPC Lookahead Horizon** | `MPC_HORIZON` | $24\text{ Hours}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Lookahead window for multi-period optimization solver |
| **Demonstration Duration** | `DEMONSTRATION_DURATION` | $24\text{ Hours}$ | `SELECTED_DEMONSTRATION_WINDOW` | Standard window selected for diurnal solar MPC cycles |
| **Simulation Timestep** | `TIMESTEP` | $1.0\text{ Hour}$ | `ARCHITECTURALLY_SUFFICIENT_FOR_MACRO_ENERGY_BALANCE_AND_CONSISTENT_WITH_CURRENT_MPC` | Macro energy balance optimization step |
| **ECD Baseline Horizon** | `T_required` | $6.0\text{ Hours}$ | `SEALED_HUMAN_GOVERNANCE_DECISION` (`TREQ-001`) | Emergency Condition Detector survivability policy limit |

### 3. MANDATORY TERMINOLOGY RULES
1. **24-Hour Demonstration Window**: Must be cited as `SELECTED_DEMONSTRATION_WINDOW`. It is NOT mathematically proven to be the absolute minimal possible test duration, but is selected as the standard window for diurnal solar cycle demonstration.
2. **1.0-Hour Timestep**: Must be cited as `ARCHITECTURALLY_SUFFICIENT_FOR_MACRO_ENERGY_BALANCE_AND_CONSISTENT_WITH_CURRENT_MPC`. It is NOT claimed to be "optimal" for sub-second electrical transients.
3. **6-Hour $T_{\text{required}}$ Baseline**: Uncoupled from the 24-hour simulation window. $T_{\text{required\_baseline}} = 6\text{h}$ is a sealed emergency survivability policy parameter.

`TIME_HORIZON_STATUS = RECONCILED_AND_CLEARED`.
