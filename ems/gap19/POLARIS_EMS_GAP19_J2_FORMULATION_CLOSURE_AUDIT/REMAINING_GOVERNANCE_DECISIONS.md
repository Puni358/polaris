# Remaining Unresolved Governance Decisions Register

## Governance Boundary Principle

This audit strictly distinguishes between **GOVERNANCE DECISIONS** (policy choices that require human project owner authorization) and **ENGINEERING DEFINITIONS** (technical specifications, mathematical formulations, and code implementations that follow from authorized governance).

Under GAP19 governance rules:
- No AI assistant or engineering team may invent, choose, or authorize policy values.
- All unresolved governance choices must remain explicitly registered as `UNAUTHORIZED` until formal human authorization is granted.

---

## Unresolved Governance Decision Register

### Decision 1: Numerical EBR Target Calculation Rule
- **Decision ID**: `GOV-J2-01`
- **Scope**: Authorizing the exact numerical formula or scaling factor for the 6-hour protected critical load target $E_{\text{EBR,target}}[t]$.
- **Open Policy Options**:
  - *Option 1.1*: Direct 100% 6-hour critical demand sum: $E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{t+5} P_{\text{crit}}[k] \Delta t$.
  - *Option 1.2*: Multiplier-scaled critical demand: $E_{\text{EBR,target}}[t] = \mu_{\text{EBR}} \cdot \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{t+5} P_{\text{crit}}[k] \Delta t$ (where $\mu_{\text{EBR}} > 0$).
  - *Option 1.3*: Fixed minimum stored energy floor (e.g., static $X\text{ kWh}$ or static $Y\%\text{ SOC}$).
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

### Decision 2: Numerical Terminal Reserve Target Rule
- **Decision ID**: `GOV-J2-02`
- **Scope**: Authorizing the structural model (A, B, C, or D) and numerical policy value for Terminal Reserve $E_{\text{term,target}}$ at horizon boundary $t = 24\text{h}$.
- **Open Policy Options**:
  - *Option 2.1 (Model A)*: Initial state cyclic restoration: $E_{\text{term,target}} = E_{\text{bat}}[0]$.
  - *Option 2.2 (Model B)*: Fixed usable capacity fraction: $E_{\text{term,target}} = E_{\text{min}} + \alpha_{\text{term}} (E_{\text{max}} - E_{\text{min}})$.
  - *Option 2.3 (Model C)*: Forward 6-hour critical load of subsequent horizon ($t \in [24, 29]$).
  - *Option 2.4 (Model D)*: Dawn net-deficit coverage envelope.
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

### Decision 3: Horizon-Edge Lookahead Extension Strategy
- **Decision ID**: `GOV-J2-03`
- **Scope**: Authorizing the mathematical strategy for handling the 6-hour lookahead window at timesteps $t \in [19, 23]$ where window extends beyond 24h forecast bundle.
- **Open Policy Options**:
  - *Option 3.1*: Tail persistence extrapolation ($P_{\text{crit}}[k] = P_{\text{crit}}[23]$ for $k \ge 24$).
  - *Option 3.2*: Canonical 30-hour `ForecastBundle` extension.
  - *Option 3.3*: Terminal Reserve coupling envelope constraint.
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

### Decision 4: Lexicographic Stage Lock Tolerances ($\epsilon_1, \epsilon_2, \epsilon_3$)
- **Decision ID**: `GOV-J2-04`
- **Scope**: Authorizing the exact numerical tolerances for sequential MILP stage locks in Option A:
  - $\epsilon_1$: Stage 1 Critical Load Lock Tolerance (kWh)
  - $\epsilon_2$: Stage 2 Reserve Shortfall Lock Tolerance (kWh)
  - $\epsilon_3$: Stage 3 Fuel Consumption Lock Tolerance (Liters)
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

### Decision 5: Economic Valuation & Degradation Parameters
- **Decision ID**: `GOV-J2-05`
- **Scope**: Authorizing physical/financial coefficients for lower objective stages:
  - Battery degradation penalty per Wh ($\text{deg\_penalty}$)
  - Diesel fuel cost per Liter ($\text{fuel\_cost}$) and startup cost ($\text{startup\_cost}$)
  - Renewable curtailment penalty weight
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

### Decision 6: Critical Load Protected Fraction ($\gamma_{\text{crit}}$)
- **Decision ID**: `GOV-J2-06`
- **Scope**: Authorizing the protected fraction of total station demand designated as critical load ($P_{\text{crit}}[t] = \gamma_{\text{crit}} \cdot P_{\text{demand}}[t]$) when explicit tier breakdowns are absent.
- **Governance Status**: `UNAUTHORIZED / GOVERNANCE_DECISION_REQUIRED`

---

## Governance Summary Table

| Decision ID | Decision Title | Current Status | Prerequisite For |
| :--- | :--- | :--- | :--- |
| **GOV-J2-01** | Numerical EBR Target Rule | `UNAUTHORIZED` | Implementation Design / Execution |
| **GOV-J2-02** | Numerical Terminal Reserve Rule | `UNAUTHORIZED` | Implementation Design / Execution |
| **GOV-J2-03** | Horizon-Edge Extension Strategy | `UNAUTHORIZED` | Implementation Design |
| **GOV-J2-04** | Stage Lock Tolerances ($\epsilon_1, \epsilon_2, \epsilon_3$) | `UNAUTHORIZED` | Sequential Lexicographic Orchestration |
| **GOV-J2-05** | Degradation & Fuel Valuation | `UNAUTHORIZED` | Stage 3 / 4 Objective Calculations |
| **GOV-J2-06** | Critical Load Ratio ($\gamma_{\text{crit}}$) | `UNAUTHORIZED` | `ForecastBundle` Fallback Logic |
