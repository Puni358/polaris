# Why Stage 8.1's More Accurate Solar Forecast Doesn't Translate Into Better System-Level Outcomes

**Scope**: Investigation/synthesis only, of already-computed, already-reviewed artifacts
(R1/R2 raw results, R1/R2 forensic/audit/design-review reports, GAP19 and Stage 8.1 source
code). **No new experiment was run. No code was modified.** Every claim below is tagged
**VERIFIED** (re-confirmed first-hand from a cited file/line in this investigation, or
directly re-derivable from already-stored raw data) or **INFERENCE/UNKNOWN** (stated
explicitly as such, with the reason it cannot currently be established). No speculative
redesign is proposed; §3/§4 describe the smallest *testable* next step, not an
implementation.

---

## 1. What exactly prevents better forecast information from producing better dispatch outcomes?

**VERIFIED finding: the reserve-envelope (J2) pathway, not GAP19's bus-bar dispatch logic
itself, is the dominant channel, and it is a research-formula artifact, not a GAP19 defect.**

Two independent, code-confirmed facts combine (`R2_OPTIMIZER_DESIGN_REVIEW.md:111-130`,
re-verified directly against `gap19_highs_native.py` in this session):

1. **GAP19's own governed reserve logic (EBR) never looks at the renewable forecast at
   all.** `gap19_highs_native.py:111-131` computes `ebr_target_wh_list` as a pure function of
   `critical_demand` and the fixed `eta_dis`; `solar_gen`/`wind_gen` do not appear anywhere in
   that formula. **VERIFIED** directly from the function body (read in full earlier this
   session).
2. **The one place a forecast enters the reserve envelope is `terminal_target_wh`**, supplied
   entirely by the *research script*, not by GAP19:
   ```
   terminal_target_wh = 40,000 + max(0, Σ_{k=19..24}(demand[k] − (solar_gen[k]+wind_gen[k]))·1h) × 1.10
   ```
   (`run_research_simulation.py:74-85`, `RESEARCH_EXCEPTION_DECISION_RECORD.md`, labeled
   `SIMULATED_RESEARCH_ASSUMPTION`). **VERIFIED** by direct read of the function this
   session.
3. **`terminal_target_wh` numerically dominates the reserve envelope at the one timestep
   (t=23) where it enters, in every single R1/R2 cycle**: observed range 40,000–172,983 Wh
   (mean 147,009), versus the EBR formula's own theoretical maximum of `11,600 W × 1h / 0.92 =
   12,608.7 Wh` given the governed `critical_load.baseline_power_w` cap. **VERIFIED**,
   `R2_OPTIMIZER_DESIGN_REVIEW.md §1`, consistent with the GAP19 code's
   `e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)` (confirmed line
   151 this session).
4. **GAP19's priority order is strict (lexicographic), not weighted**:
   `blend_multi_objectives = False` (`gap19_highs_native.py:349`, re-confirmed this session),
   `J1(crit,4) > J2(reserve,3) > J3(diesel,2) > J4(curtailment,1)`. There is **no numeric cost
   trade-off anywhere between reserve shortfall and fuel** — the solver will spend any amount
   of diesel to reduce `s_J2` before J3 (fuel) is even considered. **VERIFIED** directly from
   code and from `h.setOptionValue("blend_multi_objectives", False)`.

**The mechanism, quantified (VERIFIED, `R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md §Step
3`)**: of the +5,265.28 L total diesel increase across the 245 NORMAL-route origins, **87.3%
(4,598.71 L) occurs specifically in the 125 origins where the reserve envelope binds for at
least one arm**; `corr(ΔJ2, Δdiesel) = 0.770` is the strongest correlation measured in the
entire analysis. The remaining 12.7% (666.58 L) is a separate, smaller, *direct* bus-bar
energy-balance effect (less forecasted solar → the ordinary demand-balance constraint,
`gap19_highs_native.py:227-231`, needs more diesel with zero reserve-envelope involvement).

**Why this blocks "better forecast → better outcome"**: a more accurate solar forecast
(Stage 8.1) more often reveals a real afternoon/evening deficit that the baseline's optimistic
constant curve hides. That deficit *raises* `terminal_target_wh` (via the research formula),
which *tightens* the reserve envelope, which the solver satisfies with diesel **before it is
even allowed to consider fuel cost**. So improved forecast accuracy is converted, via this one
specific formula, into a binary "spend more diesel to protect the now-visible reserve
requirement" decision — there is no intermediate mechanism (cost weighting, partial
relaxation, risk-adjusted margin) through which "better information" could instead produce,
say, "smarter but not necessarily more diesel-intensive" dispatch. The formulation has no
slot for that outcome.

**Secondary, smaller channel (VERIFIED)**: curtailment and diesel are **not** a cost
trade-off against each other either — `corr(ΔJ4, ΔJ3) = 0.014` (`R2_DIESEL_INCREASE_CAUSAL_
FORENSIC_REPORT.md §Step 2`), essentially zero. Less curtailment under Stage 8.1 is simply
"less forecasted surplus to curtail" (there's less phantom solar to discard), happening
independently of, not instead of, the diesel increase. **This directly falsifies any
"diesel cost vs. curtailment benefit" framing of the result.**

**Unmet load cannot show any forecast effect by construction (VERIFIED)**: unmet load is
driven purely by `demand − p_served`, and `demand` is bit-identical between arms in every
R1/R2 cycle (`Stage81CorrectedForecastEngine` only overrides the solar channel — verified
directly in `s81_corrected_solar.py:260-272` this session: `wind_generation` and `demand`
both fall back to `self.baseline_engine.predict(...)` unless explicitly supplied via
`runtime_context`, which R1/R2 never does). Result: `planned_unmet_load_wh` is **identical at
every one of the 347 origins** (`RESEARCH_SIMULATION_RESULTS_R1_FULL_WINDOW.md §5`,
`0` diff). **This metric is structurally blind to solar-forecast quality and cannot be used
as forecast-performance evidence** — consistent with this investigation's own instruction.

---

## 2. Which behavior is caused by the forecast vs. optimizer formulation vs. governance policy?

| Behavior | Caused by | Evidence (VERIFIED) |
|---|---|---|
| Solar-forecast accuracy itself (Stage 8.1 ~8× lower MAE, near-zero bias vs. baseline's +164.6 W/m² bias) | **Forecast** | `R2_AUDIT_AND_STOP_REPORT.md Q1`, computed against the frozen matrix's own ground-truth `actual_SW_IN` column |
| `terminal_target_wh` becoming sensitive to that forecast accuracy at all | **Research-script formula** (not GAP19, not governance) | `run_research_simulation.py:74-85`; labeled `SIMULATED_RESEARCH_ASSUMPTION` in `RESEARCH_EXCEPTION_DECISION_RECORD.md` — explicitly *not* an authorized/governed value |
| EBR's own insensitivity to renewables | **Optimizer formulation** (GAP19, governed, unmodified) | `gap19_highs_native.py:111-131`, verified this session |
| Zero cost trade-off between reserve (J2) and fuel (J3) | **Optimizer formulation** (GAP19, governed, unmodified) — `blend_multi_objectives=False`, strict priority | `gap19_highs_native.py:349`, `365-385`; `R2_OPTIMIZER_DESIGN_REVIEW.md §2` notes this *may be* an intentional reliability-over-fuel governance choice, but that intent is itself unconfirmed (see below) |
| 87.3%/12.7% split of the diesel delta by reserve-binding status | **Interaction** of the research formula (channel) with the governed GAP19 priority (mechanism) — neither alone produces this; both together do | `R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md §Step3`, `R2_OPTIMIZER_DESIGN_REVIEW.md §6` |
| Unmet load being forecast-blind | **Optimizer formulation** (critical-load balance structurally depends on `demand`, not `solar`) combined with the shared-demand-channel property of the Stage 8.1 engine (**forecast-pipeline design**, not GAP19) | `s81_corrected_solar.py:267-272`, `gap19_highs_native.py` constraint #4 (reviewed earlier this session) |
| Whether "no cost trade-off" (J2>J3 strict priority) reflects actual governance intent for reliability-over-fuel, vs. simply an unexamined modeling default | **UNKNOWN — governance policy, unresolved** | `R2_OPTIMIZER_DESIGN_REVIEW.md §3`: *DEC-TR-05 recorded "secondary lexicographic J2 objective, not a hard constraint" — but "not a hard constraint" and "strictly prioritized with no cost trade-off" are not the same thing, and this review does not resolve which the governed decision actually intended.* This is explicitly flagged UNRESOLVED in the source document, not answered here. |
| Whether a validated, non-forecast-sensitive terminal-reserve formula would change this outcome | **UNKNOWN — blocked on governance**, not an optimizer or forecast question | DEC-RES-03 (numeric value), DEC-TR-03 (unit) remain open per `R2_OPTIMIZER_DESIGN_REVIEW.md §4`; no authorized replacement formula exists |

**Governance-caused gap, confirmed separately**: the only available Q2-track improvement
(wind forecasting) is **blocked entirely by governance, not by any technical or forecast
limitation**: `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D4_WIND_SOURCE.md` records
`D4_WIND_SOURCE = EXISTING_TECHNICAL_SOURCE_NOT_AUTHORIZED`, and the companion deferred-wind
decision record states wind forecasting *"SHALL REMAIN A DEFERRED FUTURE RESEARCH AND
ENGINEERING CAPABILITY."* **VERIFIED**, `R2_AUDIT_AND_STOP_REPORT.md Q2` (re-cites the primary
governance documents by name and line).

---

## 3. What is the smallest research-only change that could test whether improved forecast information can translate into improved operational outcomes?

**Not implemented here — description only, per instruction.** Grounded entirely in the
mechanism already isolated above (§1), not a new hypothesis:

**Smallest change**: an **ablation of the terminal-reserve formula's solar-sensitivity**,
holding everything else (GAP19 itself, both forecast engines, the 347-origin window, initial
`StationState`, config YAMLs) exactly as R1/R2 already froze them. Concretely: re-run the
existing R1/R2 harness with `terminal_target_wh` computed from a **constant or
solar-forecast-independent** value (e.g., the existing `40,000` floor alone, or a governed
constant unrelated to either arm's solar forecast) instead of the current
`demand − renewables`-driven research formula — for **both** arms, so solar-forecast
*accuracy* can no longer be transmitted into the reserve envelope at all. Then compare the
Stage-8.1-vs-baseline diesel/curtailment delta under this ablated formula against the already-
measured delta under the current formula.

This is the smallest change because it requires **zero changes to GAP19, to either forecast
engine, or to the 347-origin evaluation protocol** — only the one already-isolated,
already-labeled-as-research-only external input (`terminal_target_wh`) is altered, exactly
the "research-only" boundary this whole investigation's prior reports (R1/R2/MILP-v2
checkpoint) have consistently respected.

**What this change would, and would not, show**:
- If the diesel/curtailment delta between baseline and Stage 8.1 **shrinks substantially**
  under the ablated (solar-insensitive) terminal-reserve formula, that would be strong
  evidence the reserve-envelope pathway (§1) is indeed the dominant transmission mechanism,
  not some other unidentified channel.
- If the delta **persists largely unchanged**, that would indicate the 12.7% direct bus-bar
  channel (§1, Step 3) — or some other mechanism not yet isolated — is more important than
  the 87.3%/12.7% split currently suggests, and the reserve-envelope explanation would need
  revision.
- It would **not**, by itself, establish whether more diesel (under either formula) is
  operationally "better" or "worse" — that judgment requires an authorized cost weighting
  that does not currently exist (same limitation already declared in every R1/R2 result
  document).

## 4. Exact experiment needed to prove/disprove this

**Design (description only, not run)**:

1. **Reuse, unmodified**: `H10RuntimeAdapter`, `EMSControlRouter`,
   `GAP19HighsNativeOptimizer`, `OptionDFallbackSolver`, `LocalBaselineForecastEngine`,
   `Stage81CorrectedForecastEngine`, all `system/config/*.yaml`, the same 347 origins, the
   same warmed-up `StationState` construction R1/R2 already use.
2. **The only change**: replace `compute_terminal_target_wh(bundle)` (currently
   `40,000 + max(0, Σ(demand−renewables)) × 1.10`, solar-sensitive) with a fixed constant
   (e.g. the `40,000` floor alone) — applied **identically to both arms**, so the ablation
   itself introduces no new asymmetry between baseline and Stage 8.1.
3. **Run both arms, all 347 origins**, exactly as R1/R2 did (694 total cycles).
4. **Compare, per the existing R1/R2 metric set** (already instrumented, no new code needed):
   diesel fuel (planned, NORMAL-route and total), curtailment, battery charge/discharge/EFC,
   SOC range, route agreement, solve status — **the same table shape as
   `RESEARCH_SIMULATION_RESULTS_R1_FULL_WINDOW.md §4–§8`**, so the new run is directly
   diffable against the existing frozen R1/R2 numbers.
5. **Primary comparison metric for proving/disproving the hypothesis**: the **percentage of
   the Stage-8.1-vs-baseline diesel delta attributable to reserve-envelope-binding cycles**
   (the same 87.3%/12.7% decomposition already computed for the current formula in
   `R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md §Step3`), recomputed under the ablated
   formula. A result near 0% (reserve envelope rarely or never binds under a solar-insensitive
   constant target) combined with a **much smaller total diesel delta** between arms would
   **prove** the reserve-envelope pathway was the dominant transmission mechanism. A result
   where the diesel delta between arms **persists at a similar magnitude** despite the
   envelope no longer being solar-sensitive would **disprove** it and point to the direct
   bus-bar channel (or an unidentified third mechanism) as dominant instead.
6. **Secondary, currently-impossible-without-new-instrumentation check** (flagged, not
   assumed): per-timestep `s_J2[t]` values (`DispatchPlan.reserve_shortfall`, already a field
   GAP19 returns — confirmed `gap19_highs_native.py:447` in the design review — but not
   currently retained by the R1/R2 result-collection script, which only stores the per-cycle
   sum) would need to be captured in this new run's own result-collection code (not a GAP19
   change) to additionally isolate "shortfall at t=23 specifically" from "shortfall at t<23,"
   resolving the one remaining precision caveat in the existing causal report.

**Governance status of this experiment**: research-only, following the exact same frozen-
control protocol (own manifest, own hashes, no production wiring) already established for
R1, R2, and the MILP-v2 checkpoint — **not proposed for authorization or execution here**;
this section documents the experiment design only, per the task's "no speculative redesign,
investigation only" instruction.

---

## Summary table: VERIFIED vs. UNKNOWN

| Claim | Status |
|---|---|
| GAP19's EBR formula is solar/wind-independent | **VERIFIED** (code, this session + prior review) |
| `terminal_target_wh` is the sole forecast-sensitive channel into J2 | **VERIFIED** (code, this session) |
| `terminal_target_wh` numerically dominates the t=23 envelope in every R1/R2 cycle | **VERIFIED** (R2_OPTIMIZER_DESIGN_REVIEW.md, numeric range vs. theoretical EBR max) |
| GAP19 uses strict (non-weighted) lexicographic priority, J2 before J3 | **VERIFIED** (code: `blend_multi_objectives=False`, priority ints) |
| 87.3% of the diesel delta occurs in reserve-binding cycles | **VERIFIED** (computed from stored R2 raw data, re-describable but not independently recomputed in this session — accepted as already-verified per its own report's stated method) |
| Curtailment/diesel deltas are uncorrelated (not a trade-off) | **VERIFIED** (`corr=0.014`, same source) |
| Unmet load is forecast-blind by construction | **VERIFIED** (code: `s81_corrected_solar.py` demand fallback, this session; data: 0 diff at all 347 origins) |
| No authorized wind-generation forecast exists | **VERIFIED** (governance documents cited by name/line in `R2_AUDIT_AND_STOP_REPORT.md Q2`) |
| Whether strict J2>J3 priority reflects deliberate governed reliability-over-fuel intent | **UNKNOWN** — explicitly unresolved in the source review, not answered here |
| Exact diesel liters attributable to t=23 research-formula term alone vs. t<23 EBR bindingness | **UNKNOWN** — requires per-timestep instrumentation not currently stored |
| Whether a different (also unauthorized) terminal-reserve formula would reduce the effect | **UNKNOWN** — would require the experiment in §4, not run here |
| Whether Stage 8.1's diesel-higher plans would be "more correct" in a true multi-step rollout | **UNKNOWN** — R1/R2 are single-step-per-origin by design; not addressed by any existing artifact |

## STOP

Investigation complete. No code, config, model, or forecast engine modified. No new
experiment run. Every VERIFIED claim above traces to a specific cited file/line re-checked
in this session or an already-computed, already-reviewed result; every UNKNOWN is stated as
such, with the reason it cannot currently be resolved.
