# Research-Exception Decision Record
## Simulated Terminal Reserve Assumptions for the Stage 8.1-vs-Baseline Closed-Loop MILP Research Simulation

**Role of signer**: `SIMULATED_STATION_MANAGER` (a role-played research stand-in, NOT a real
organizational authority; see Governance Disclaimer below).
**Scope**: This record authorizes NOTHING in the real governance system. It exists solely to
make ONE specific, already-code-reviewed research script (`run_research_simulation.py` in
this directory) executable, by fixing provisional numeric inputs for `terminal_target_wh`
that the real governance package (`POLARIS_EMS_GAP19_STAGE81_EXPERIMENT_HUMAN_GOVERNANCE_DECISION_PACKAGE/`)
explicitly could not resolve.

---

## GOVERNANCE DISCLAIMER (read first)

- This record does **not** change `FINAL_GOVERNANCE_DECISION_STATUS.md`,
  `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md`, or any other governance document. Those
  documents remain exactly as they were: `TERMINAL_PHYSICAL_UNIT`, `TERMINAL_NUMERICAL_TARGET`,
  and `NUMERICAL_POLICY_VALUES_AUTHORIZED = NO` are still true of the real system.
- Nothing here is a battery specification. SD-07 (vendor minimum SOC) and SD-08 (degradation
  curves) remain `NOT_ESTABLISHED`; this record does not claim otherwise and uses none of
  them beyond the existing `CURRENT_IMPLEMENTATION_FACT` already frozen in `battery.yaml`.
- `EXPERIMENT_EXECUTION` / `SIMULATION_EXECUTION` / `MILP_EXECUTION` in the real policy
  documents remain `NOT_AUTHORIZED` for production use. The run this record enables is a
  **sandboxed, read-only-on-production-code research script**, reusing real optimizer/router/
  simulator code but with a config input it manufactures itself, outside of `worker.py` and
  outside of any production execution path.
- Every value below is labeled `SIMULATED_RESEARCH_ASSUMPTION` unless marked
  `CURRENT_IMPLEMENTATION_FACT` (frozen, already in the codebase) or
  `GOVERNANCE_AUTHORIZED` (a real, already-decided governance value). No value is presented
  as a real operational or stakeholder-authorized figure.
- Production code and config (`system/`, `worker.py`, `gap19_highs_native.py`, `*.yaml`) are
  **unchanged**. The terminal target is computed in the research script itself and supplied
  through GAP19's existing `config["terminal_target_wh"]` input slot — the same mechanism the
  codebase's own unit tests already use (`system/tests/test_gap19_j2_option_b.py`) — not by
  modifying GAP19.

---

## ASSUMPTION REGISTER

| Field | Value | Label | Rationale / Evidence |
|---|---|---|---|
| Physical unit | Watt-hours (Wh) | `SIMULATED_RESEARCH_ASSUMPTION` | DEC-TR-03 is unresolved, but `StationState.terminal_target_wh_override` and GAP19's own `terminal_target_wh` input are already typed as Wh throughout the codebase (`system/schemas/station_state.py`, `gap19_highs_native.py`). Choosing a different unit would require new code; Wh is the only unit the existing, unmodified code can accept. |
| Technical minimum SOC (floor basis) | 20% of 200,000 Wh = 40,000 Wh | `CURRENT_IMPLEMENTATION_FACT` | `battery.yaml` (frozen, SHA-verified per `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` §6.4). Not an assumption — this is the existing hardware-protection floor already in production config. |
| Terminal reserve floor = technical minimum SOC | 40,000 Wh | `SIMULATED_RESEARCH_ASSUMPTION` | Governance (D11/D12) treats EBR/terminal floor as structurally *distinct* from the technical minimum, but authorizes no separate number. In the absence of an authorized separate floor, this record equates the two for simulation purposes only (closest to candidate **TR-E** in `DECISION_OPTIONS_MATRIX.md`, which relies on the technical-minimum/EBR layer rather than a separate terminal number). |
| Look-ahead window for the dynamic component | 6 hours | `GOVERNANCE_AUTHORIZED` | $T_{\text{REQUIRED}} = 6\text{h}$ is the one numerical value in this entire governance space marked `ESTABLISHED` (`NUMERICAL_VALUE_STATUS_AUDIT.md:12`). Reused here exactly as authorized, not re-derived or altered. |
| Dynamic target formula | `max(0, Σ_{k=19..24} (crit_demand[k] − renewable_avail[k]) · 1h)` over the forecast's own last 6 horizon hours (hours 19–24 of the 24h `ForecastBundle`), using THAT cycle's own forecasted `demand`, `solar_generation`, and `wind_generation` | `SIMULATED_RESEARCH_ASSUMPTION` | Operationalizes the already-decided human policy ("dynamic, based on future demand + renewable availability") using candidate **TR-D** (dynamic terminal reserve from future critical-load survivability) as the closest matching option in `DECISION_OPTIONS_MATRIX.md`. Since the `ForecastBundle` horizon is exactly 24h with no data beyond it, this record uses the forecast's own trailing 6h (hours 19–24) as the only available proxy for "risk at the horizon boundary" — it does NOT fabricate any data point beyond what the forecast engine already produced for that cycle, and uses no hindsight/future-actual value (consistent with the policy decision "use only information available at optimization time"). |
| Uncertainty/risk margin | +10% applied multiplicatively to the computed energy deficit | `SIMULATED_RESEARCH_ASSUMPTION` (value sourced from a pre-existing, explicitly unauthorized advisory figure) | The human policy decision requires *some* uncertainty component but leaves the model open (`TECHNICAL_VALIDATION_REQUIRED`). Rather than inventing a new number, this record reuses **NC-07** ("Demand forecast upward margin %, +10%") from the existing `POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md` pending-requirements register — itself explicitly marked `NOT_STAKEHOLDER_AUTHORIZED` there, and remains so here. It is borrowed only as a transparent, already-written-down placeholder, not newly fabricated. |
| Recalculation frequency | Every cycle, from that cycle's own fresh forecast | `SIMULATED_RESEARCH_ASSUMPTION` | NS-10 (re-optimization interval) is `NEXT_EMS_OBJECTIVE_SPECIFICATION`; recomputing every cycle is the simplest assumption consistent with standard rolling-MPC practice and requires no additional state. |
| Enforcement mechanism | Secondary lexicographic $J_2$ objective (not a hard constraint) | `GOVERNANCE_AUTHORIZED` (policy structure, decided in the prior turn of this package) | Already recorded as `DECIDED` in `POLARIS_EMS_GAP19_STAGE81_EXPERIMENT_HUMAN_GOVERNANCE_DECISION_PACKAGE/HUMAN_GOVERNANCE_DECISION_PACKAGE.md` §2a. Implemented via GAP19's existing, unmodified `config["terminal_target_wh"]` → $J_2$ pathway (`gap19_highs_native.py:151,299-305,334`). |
| Emergency Mode interaction | None — this value is never read by the EMERGENCY/OptionD path | `GOVERNANCE_AUTHORIZED` (policy structure, decided previously) | Confirmed by code trace: `system/optimization/implementations/option_d.py` contains no reference to `terminal_target_wh`. |
| Identical treatment across arms | The SAME formula, SAME floor, SAME look-ahead window, and SAME margin are applied to both the baseline-engine run and the Stage 8.1-engine run; only each arm's own forecasted `demand`/`solar_generation`/`wind_generation` inputs differ (because the forecast engine differs) | `SIMULATED_RESEARCH_ASSUMPTION` (methodological control) | Required by the task: "run the controlled MILP comparison using identical assumptions for both forecasts." This isolates the forecast engine as the only varying factor. |

**Nothing above claims to be a real battery specification, a real station parameter, or a
real governance authorization.** Every number that is not a `CURRENT_IMPLEMENTATION_FACT` or
`GOVERNANCE_AUTHORIZED` value is clearly a `SIMULATED_RESEARCH_ASSUMPTION`, chosen for
internal consistency and traceability to existing (if unauthorized) register entries, never
invented from nothing.

---

## RESPONSIBLE-SELECTION CHECK

Per the instruction to STOP if any assumption cannot be responsibly selected even for
simulation: every field above is either (a) a literal hard-coded fact already frozen in the
codebase, (b) a governance value already marked `ESTABLISHED`/`GOVERNANCE_AUTHORIZED`, or (c)
a transparent placeholder already written down somewhere in the governance register (NC-07) or
options matrix (TR-D/TR-E) and merely re-labeled honestly for this sandbox. No field required
inventing a number with no textual precedent anywhere in the repository. **No STOP condition
was triggered.**

---

## FREEZE

This assumption set is frozen for the single research run executed in this package
(`run_research_simulation.py`, see `RESEARCH_SIMULATION_RESULTS.md` for output). Any
different run must produce its own decision record; this one is not a template for
production use.

**Signed (role-played)**: `SIMULATED_STATION_MANAGER`
**Date**: 2026-10-03
**Authorization scope**: Research sandbox execution of the one script named above. No
real-world, production, or governance authorization is granted or implied.
