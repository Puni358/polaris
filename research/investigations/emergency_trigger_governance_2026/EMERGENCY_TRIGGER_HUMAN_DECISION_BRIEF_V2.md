# POLARIS — HUMAN GOVERNANCE DECISION BRIEF (V2)

## Executive Briefing & Decision Preparation

This decision brief frames the five unresolved governance decisions required prior to implementing POLARIS Emergency Mode trigger semantics.

All options are presented in strictly neutral technical language. No option is characterized as "recommended", "optimal", "best", or "correct". The choices belong exclusively to the human project owner.

---

### DECISION GAP 1: Generator Credibility Model Selection
- **Question**: What mathematical model shall POLARIS use to quantify "credible" dispatchable generator energy ($E_{\text{gen\_credible}}$) over the 6-hour critical survivability horizon?
- **Why It Matters**: Influences the calculated Critical Load Survivability Margin ($M_{\text{surv}}$). Determines whether generator potential capacity is bounded by critical load demand or day-tank fuel volume.
- **Option A**: *Unbounded Nameplate Potential Energy*. $E_{\text{gen}} = 6.0 \times \sum P_{\text{gen\_max\_available}}$. Assumes maximum rated generator output for 6 hours.
- **Option B**: *Credible Operating Capacity*. $E_{\text{gen}} = 6.0 \times \sum (A_k \cdot \delta_{\text{derate}} \cdot P_{\text{rated}})$. Accounts for asset fault lockouts and polar derating.
- **Option C**: *Fuel-Constrained Energy*. $E_{\text{gen}} = \min(6.0 \times \sum A_k P_{\text{max}}, \, V_{\text{fuel}} \cdot \rho \cdot \eta_{\text{gen}})$. Bounds generator energy by measured day-tank fuel volume.
- **Option D**: *Critical-Load Bounded Energy*. $E_{\text{gen\_bus}} = \min(6.0 \times \sum A_k P_{\text{max}}, \, \max(0, E_{\text{critical\_req}} - E_{\text{batt\_deliverable}}))$. Caps generator credit at net critical load demand.
- **Consequences**:
  - *Option A/B*: High credit for generators; reduces early Emergency triggers, but relies on unmeasured fuel availability.
  - *Option C*: High safety against fuel exhaustion; requires reliable fuel telemetry.
  - *Option D*: Exact dimensional match to critical bus balance; ignores excess unserved generator potential.
- **Required Inputs**: Generator availability telemetry, derating tables, fuel volume measurements.
- **Current POLARIS Status**: Unresolved (Previously assumed Model A in draft spec).

---

### DECISION GAP 2: Renewable Forecast Credibility Policy
- **Question**: Shall renewable generation forecasts (solar/wind) be credited toward 6-hour critical load survivability guarantees, and if so, under what confidence mechanism?
- **Why It Matters**: Determines whether a hybrid station can avoid Emergency Mode during daylight solar or high wind conditions when diesel generators are offline.
- **Option A**: *Fixed Percentage Derating*. Derate raw forecasts by fixed factor ($\gamma_{\text{solar}} = 0.50, \gamma_{\text{wind}} = 0.50$).
- **Option B**: *Probabilistic Quantile Bound*. Use the 10th percentile (P10) lower confidence bound from weather forecasts.
- **Option C**: *Zero Renewable Credit for Emergency Guarantee*. Set $E_{\text{ren\_credible}} = 0.0\text{ kWh}$ during emergency survivability checks. Critical safety relies strictly on battery + diesel.
- **Option D**: *Resource-Specific Derating*. Derate solar by 20% ($\gamma_{\text{solar}} = 0.80$) and wind by 70% ($\gamma_{\text{wind}} = 0.30$) based on polar turbulence.
- **Consequences**:
  - *Option A/B/D*: Prevents unnecessary Emergency load shedding during clear weather; introduces dependency on weather forecast accuracy.
  - *Option C*: Maximum fail-safe protection; triggers Emergency Mode during solar periods if diesel is offline and battery is low.
- **Required Inputs**: Solar/wind 6-hour forecast data, historical forecast error variance.
- **Current POLARIS Status**: Unresolved (Draft spec used Option A placeholder).

---

### DECISION GAP 3: Emergency Exit Battery & Generator Requirements
- **Question**: What minimum resource state is required before POLARIS may automatically exit Emergency Mode and return to `NORMAL`?
- **Why It Matters**: Controls mode hysteresis. Prevents rapid chatter between Emergency and Normal modes.
- **Option A**: *Strict Restoration (SOC $\ge 37.83\%$ AND Generator Available)*. Requires stored battery energy to reach $75.65\text{ kWh}$ ($37.83\%\text{ SOC}$) AND at least one primary diesel generator online before exiting Emergency.
- **Option B**: *Survivability Secure Only ($M_{\text{surv}} \ge +10.0\text{ kWh}$)*. Allows exiting Emergency as soon as net survivability margin is positive, regardless of whether $SOC$ has reached $37.83\%$.
- **Option C**: *Battery-Only Exit Permitted*. Allows exiting Emergency if battery $SOC \ge 57.83\%$ ($115.65\text{ kWh}$) even if all diesel generators are offline.
- **Consequences**:
  - *Option A*: Highly conservative; holds Option C load curtailment until battery reserve target is restored.
  - *Option B*: Restores flexible loads sooner; may result in returning to `RESERVE_DEFICIT` mode if $SOC < 37.83\%$.
  - *Option C*: Permits exit during diesel maintenance if battery energy is sufficient for 6h standalone autonomy.
- **Required Inputs**: Battery SOC telemetry, generator status, $M_{\text{surv}}$ margin.
- **Current POLARIS Status**: Unresolved (Draft spec included Option A parameters).

---

### DECISION GAP 4: Missing Forecast Fallback Governance
- **Question**: How shall POLARIS evaluate 6-hour critical load survivability if weather telemetry or forecasts become missing, stale, or corrupt?
- **Why It Matters**: Ensures deterministic state machine behavior during communication outages.
- **Option A**: *Zero-Renewable Fallback*. If forecasts are missing, automatically set $E_{\text{ren\_credible}} = 0.0\text{ kWh}$ and evaluate $M_{\text{surv}}$ using battery + diesel.
- **Option B**: *Persistence Fallback*. Hold last valid measured renewable power output constant for 2 hours, then decay to zero.
- **Option C**: *Transition to UNKNOWN_INVALID*. Treat missing forecasts as sensor failure and suspend automatic optimization (`UNKNOWN_INVALID` state).
- **Consequences**:
  - *Option A*: Fail-safe execution without entering `UNKNOWN_INVALID` sensor lock.
  - *Option B*: Maintains economic dispatch during brief 15-minute comm drops.
  - *Option C*: Halts automatic operation; requires operator intervention.
- **Required Inputs**: Forecast timestamp freshness check ($\Delta t \le 30\text{ s}$).
- **Current POLARIS Status**: Unresolved.

---

### DECISION GAP 5: Emergency Exit Target State & Transition Path
- **Question**: Shall Emergency Mode exit directly into `NORMAL` mode only, or permit exiting into `RESERVE_DEFICIT` mode when critical survivability is secure ($M_{\text{surv}} \ge 0$) but battery energy remains below target ($SOC < 37.83\%$)?
- **Why It Matters**: Defines state transition topology and flexible load restoration timing.
- **Option A**: *Direct to NORMAL Only*. System remains in `EMERGENCY` with Option C load shedding active until battery reaches $37.83\%\text{ SOC}$.
- **Option B**: *Permit Exit to RESERVE_DEFICIT*. System exits `EMERGENCY` as soon as $M_{\text{surv}} \ge 0$, restoring flexible loads and transitioning into `RESERVE_DEFICIT` mode to restore battery reserve.
- **Consequences**:
  - *Option A*: Prolongs load curtailment until battery reserve target is 100% replenished.
  - *Option B*: Immediately un-curtails flexible loads once generation secures 6-hour critical load.
- **Required Inputs**: State transition logic rules.
- **Current POLARIS Status**: Unresolved.

---

## Decision Summary Matrix

| Decision ID | Short Topic | Key Choices | Core Tradeoff |
| :---: | :--- | :--- | :--- |
| **GAP 1** | Generator Credibility Model | Option A (Nameplate), B (Operating), C (Fuel), D (Demand Cap) | Capacity potential vs fuel/demand bounds |
| **GAP 2** | Renewable Forecast Policy | Option A (50% Derate), B (P10 Bound), C (Zero Credit), D (Dynamic) | Preventing unneeded shedding vs fail-safe safety |
| **GAP 3** | Emergency Exit Requirements | Option A (SOC $\ge 37.83\%$ + Gen), B ($M_{\text{surv}} \ge +10$), C (Battery Only) | Conservative load hold vs prompt load restoration |
| **GAP 4** | Missing Forecast Fallback | Option A (Zero Renewable), B (Persistence), C (`UNKNOWN_INVALID`) | Fail-safe continuity vs comm fault lockout |
| **GAP 5** | Exit Target State Path | Option A (Direct to `NORMAL`), Option B (Exit to `RESERVE_DEFICIT`) | Reserve restoration first vs immediate load un-curtailment |
