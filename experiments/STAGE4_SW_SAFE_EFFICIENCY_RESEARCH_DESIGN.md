# STAGE 4 — Safe-Efficiency Research Design (DESIGN ONLY)

**Status:** DESIGN COMPLETE — not implemented, not executed, not tuned.
**Scope:** research-only, synthetic benchmark, Mount Nuolja (`ANS_NMS`).
**Governing contracts (frozen, unchanged):** `EXP_CANDIDATE_S_SW_PREREGISTRATION.md/.json`, `EXP_CANDIDATE_S_SW_PREREGISTRATION_ADDENDUM_NUMERICAL_BOUNDARY.md/.json`.
**Classification carried forward unchanged:** S passes the preregistered gates on the synthetic benchmark (+0.364 pp critical-first, +0.105 pp proportional, zero SOC violations, 27.25% diesel saving). SW fails the preregistered proportional gate (−1.091 pp) and is not advanced. No validation claim for physical operation is made.

---

## 1. Executive research question

Can the extra diesel reduction unlocked by SW's renewable (wind) credit be retained while restoring the stored-energy protection that prevents the night-time reliability loss, without weakening any preregistered gate?

Equivalently: is SW's failure caused by giving renewables too much credit in general, or by removing stored-energy protection at specific times and states? The experiment is designed to separate these two.

---

## 2. Stage 3 evidence summary

**OBSERVED (archived telemetry, 123 origins, 8,856 arm-hours):**

- Mean executed-hour reserve: SW 18.3 kWh, S 54.0 kWh.
- Diesel energy: SW 1,490 kWh less than S. Diesel-on hours: 264 vs 331. Startups: 168 vs 232.
- About 87% of the diesel reduction occurs in hours where diesel and battery charging overlap (proxy).
- Total unmet: SW 8,420 kWh vs S 7,819 kWh (+601 kWh). About 428 kWh of the increase falls in 00–05 UTC.
- 208 hours where S runs diesel and SW does not. SW's reserve averages 30 kWh there vs 71 kWh for S. Unmet in those hours is +1,081 kWh for SW.
- Proportional critical service: 246 hours where SW is below S, 113 of them in 00–05 UTC.
- Wind forecast minus realized wind is positive in 83% of SW hours but is smaller at the diesel-gap hours (1,782 W vs 2,500 W average). Correlation of wind error with the proportional deficit ≈ 0.02.
- SOC floor reached: S 4 hours (4 origins), SW 19 hours (10 origins). Only 2 of 246 deficit hours are at the floor.
- Router EMERGENCY share at deficit hours: S 87%, SW 79%. Baseline share is 57–60%. Not discriminating.

**INFERRED:**

- The wind credit lowers the planned reserve, which removes night diesel commitment, which leaves night shortfall without diesel backup.

**NOT ESTABLISHED:**

- A counterfactual run that removes the wind term (or the reserve effect) while holding everything else fixed. Stage 3 used paired arms differing in more than one term at a time in the telemetry sense, so causality is not identified.

---

## 3. Hypotheses

- **H0 (null):** Reserve protection does not explain the night loss. The loss is equally present in S-L (see §5) and SW-L.
- **H1 (over-credit):** The loss arises from the renewable credit itself across the day. The wind credit is too large regardless of time of day. Predicts: SW-L still fails; the wind term degrades reliability even when stored-energy protection is restored at low sun.
- **H2 (protection removal at low sun):** The loss arises from removing stored-energy protection at low-sun / night hours, where renewable credit is unreliable and diesel is the only backup. Predicts: SW-L passes the proportional gate; S-L and SW-L both pass.

H1 and H2 are not mutually exclusive. Both can hold partly; §15 gives the interpretation rules.

---

## 4. Candidate mechanisms (conceptual comparison — no winner selected)

| Mechanism | Description | Separates H1 from H2? | New parameters? | Stage 3 link |
|---|---|---|---|---|
| A. Time-aware reserve protection | Reserve depends on hour / time of day | Partly | Time boundaries | Night concentration |
| B. Night-period protection | Governed EBR at solar-elevation ≤ 0 | No (midnight sun makes it inactive in June–July) | None | Night concentration, but not robust to season |
| C. Future renewable availability | Credit scaled by future forecast availability | No | Yes (scaling) | Weakly |
| D. Battery-state / energy-autonomy | Credit gated by SOC or autonomy | Partly | Yes (threshold) | SOC not established as cause |
| E. Renewable-dependent period protection | Protection where renewable share is high | Partly | Yes | Not directly tested |
| F. Hybrid SW credit + explicit stored-energy minimum | Combines credit and a minimum | Yes, if the minimum is governed | Yes (minimum) | Directly targets the mechanism |
| G. **Low-sun stored-energy protection (selected for design)** | Renewable credit withheld at low sun; governed EBR restored there | **Yes, through the 2×2 factorial in §5** | **None beyond the existing 15° regime bin** | Directly targets the night loss |

**Selected for the experiment: G**, because it introduces no new numerical value (uses the project's existing solar-elevation regime boundary), separates the two hypotheses through a 2×2 factorial, and directly targets the observed night concentration. Mechanisms C–E add free parameters that would have to be tuned, which is excluded. Mechanism F is retained as a later candidate only if G is informative.

---

## 5. Proposed experiment arms

The minimal design is a **2×2 factorial on two factors**, plus Control B:

- **Factor W (renewable credit):** none vs solar+wind (S-type vs SW-type). Credit is applied only where the factor allows.
- **Factor P (low-sun protection):** off vs on. When on, renewable credit is withheld at low-sun hours, and the governed EBR term applies there.

| Arm | W (credit) | P (low-sun protection) | Purpose |
|---|---|---|---|
| **Control B** | — | — | Frozen reference (unchanged). |
| **S** | solar | off | Frozen reference (unchanged). |
| **SW** | solar + wind | off | Frozen reference (unchanged). |
| **S-L** | solar | on | Isolates the effect of low-sun protection when renewable credit is solar-only. |
| **SW-L** | solar + wind | on | **Final candidate mechanism.** Tests whether SW's saving can be kept with protection restored at low sun. |

Four candidate arms plus Control B. S and SW are frozen and are not re-run; their archived telemetry is the reference (see §9).

**Contrasts** (all paired by origin, same realized demand, wind and solar):

- **Protection effect, SW-type:** SW-L − SW (fuel, proportional reliability, unmet, curtailment).
- **Protection effect, S-type:** S-L − S.
- **Wind effect given protection:** SW-L − S-L. This is the key H1 test.
- **Interaction:** (SW-L − S-L) − (SW − S). If the interaction CI excludes zero, the wind effect depends on protection.

**Why this discriminates H1 from H2:**

- Under H2, SW-L should be safe and S-L should be at or near S. The protection effect should close most of SW's proportional gap.
- Under H1, SW-L should still fail, and the wind contrast SW-L − S-L should remain negative on proportional reliability even with protection on.

---

## 6. Exact equations

Notation: for origin `o`, hour `t` in {0..23}, horizon step `k` in {t..min(t+5, 23)}, `η = 0.92`, `Δt = 1 h`.

- `c_k` = critical demand = `min(11,600 W, D_forecast[k])` (unchanged).
- `s_k` = forecast solar power, W, from `bundle.solar_generation.point` (unchanged; already electrical power, no further conversion).
- `w_k` = forecast wind power, W, from `bundle.wind_generation.point` (unchanged).
- `e_k` = solar elevation at hour `k`, degrees, from the existing astronomical ephemeris (**to be verified as available to the forecast engine; see §8**).
- `L_k = 1[e_k < 15°]` — low-sun indicator. The 15° boundary is the project's existing regime bin (`Low_0_15` / `Mid_15_30`, trajectory audits). It is not chosen for this experiment.

**Control B (frozen):** `E_B[t] = (1/η) Σ_{k=t}^{min(t+5,23)} c_k Δt`, with terminal rule at t = 23.

**S (frozen):** `E_S[t] = (1/η) Σ_k max(0, c_k − s_k) Δt`.

**SW (frozen):** `E_SW[t] = (1/η) Σ_k max(0, c_k − s_k − w_k) Δt`.

**S-L (new):** `E_SL[t] = (1/η) Σ_k max(0, c_k − (1 − L_k)·s_k) Δt`.

**SW-L (new, final candidate):** `E_SWL[t] = (1/η) Σ_k max(0, c_k − (1 − L_k)·(s_k + w_k)) Δt`.

**Horizon edge (all arms, unchanged):** `E_stage2[23] = max(E_arm[23], E_term)`, with `E_term = 100,000 Wh` (as in GAP19 today). The terminal target is not modified by any arm.

**Properties (to be verified by unit tests before execution, not by tuning):**

1. If `L_k = 1` for every k in every window, `E_SWL = E_B` exactly (protection reverts to the governed EBR). Same for S-L.
2. If `L_k = 0` everywhere, `E_SWL = E_SW` and `E_SL = E_S`.
3. `E_SW ≤ E_SWL ≤ E_B` and `E_S ≤ E_SL ≤ E_B` pointwise.
4. No additive combination of EBR and a new term is used. The combination is a per-hour replacement of the renewable credit at low sun, which avoids double counting the critical energy.

**Why not `max(EBR, R)`:** the per-hour form keeps the governed EBR at low sun and the renewable credit in daylight. A `max` form would give the same result at low sun, but would not reduce the daytime reserve toward the SW level in the way the factorial requires. The design therefore uses the per-hour form, which is explicitly justified by the factorial.

---

## 7. State and reserve semantics

- Each arm is a closed-loop, hourly re-optimization. Only `plan[0]` is executed (unchanged).
- The reserve enters GAP19 only through `config["ebr_target_wh"]` (unchanged mechanism). `station_state.ebr_target_wh_override` remains `None`.
- The battery energy bounds, SOC bounds (20%–95%), diesel model (10 kW min, 100 kW max, 0.25 L/kWh marginal, 5 L/h base, 2.0 L start), charge/discharge limits (50 kW), objective, HiGHS tolerances, and the numerical-boundary rule (τ = 0.055 W) are all unchanged.
- Diesel charging, curtailment, and EMERGENCY/NORMAL routing are not directly modified. They are reported as interactions (§10).

---

## 8. Required inputs

1. Realized demand, wind, solar: identical to the frozen campaign (formulas in the preregistration §3; actual solar from `actual_SW_IN`).
2. Forecast solar and wind: identical to the frozen bundle (`causal_nwp_physics` engine, `baseline` wind heuristic).
3. Solar elevation `e_k` for every window hour, for every origin, computed by the same ephemeris used elsewhere in the project. **Must be verified** to be deterministic, causal (depends only on the timestamp), and archived per origin before execution.
4. Critical demand `c_k` as in the frozen adapter.
5. Terminal target 100,000 Wh; governed EBR formula for the L-indicator-true branch (existing `compute_governed_ebr`).

---

## 9. Frozen inputs

- GAP19 (`fd1afe10…e737`), DispatchPlan (`21c0b83e…fd7fb0b`), causal NWP (`14e72d8a…deb710`), S/SW adapter (`a3ba73ad…de4`), preregistration MD/JSON (`1f018b1a…e80be5`, `3607876a…342ba4`), addendum MD/JSON (`228474e1…1d0054`, `94c6f623…bfdd`), research extractor (`95b2f3b5…950e`), campaign runner (`fe6e8962…ae01`, may only be extended, never reinterpreted).
- Frozen campaign artifacts (telemetry, results, manifest, checkpoint). These are archived reference data, not modified.
- Control B, S, and SW: their archived results are the reference for the 2024 discovery set. They are not re-executed for the discovery set.
- Numerical-boundary rule τ = 0.055 W; HiGHS tolerances.

---

## 10. Safety gates (unchanged)

A candidate must satisfy **all three**, evaluated against **re-executed or archived Control B on the same origins** (as set by the addendum):

1. Critical-first reliability ≥ Control B: `ΔR_CF ≥ 0.00 pp`.
2. Proportional critical reliability ≥ Control B: `ΔR_P ≥ 0.00 pp`.
3. Zero realized SOC below 20.0% in any origin.

Safety precedes efficiency. A candidate failing any safety gate is rejected regardless of fuel.

Reliability is computed exactly as in the frozen campaign: critical-first `min(d_crit, served)` per hour; proportional `served × d_crit / d_real` per hour; `d_crit = min(11,600, d_real)`.

---

## 11. Diesel gate (evaluated only after safety passes)

- Paired per-origin fuel difference `Δ_o = Fuel_Control(o) − Fuel_candidate(o)`.
- Two-sided Wilcoxon signed-rank test: `p < 0.05`.
- BCa 95% bootstrap CI (seed 42, 10,000 resamples, origin-paired) for the mean paired saving: lower bound `> 0 L/origin`.

Both conditions are required. The 40% target is **not** a gate (§15).

---

## 12. Statistical analysis plan

- **Primary (gated):** the three safety gates and the diesel gate for each of S-L and SW-L against Control B. Two candidates × (2 safety + 1 diesel) = six primary tests. Correct for multiplicity with Holm across the six, at the same family-wise α = 0.05. Report uncorrected p-values alongside.
- **Secondary (descriptive, not gated):** the four contrasts in §5 (protection effect × 2, wind effect given protection, interaction). Paired bootstrap, BCa 95%, origin-paired. Report point estimates and CIs.
- **Reporting:** fuel (L), paired saving (L and %), median, diesel-on hours, startups, battery charge and discharge, curtailment, total unmet, critical unmet under both conventions, SOC minimum, EMERGENCY/NORMAL hour counts, residue corrections (τ rule), and per-origin tables for the worst ten origins under each contrast.
- **No post-hoc subgrouping** beyond the pre-declared night (`L_k = 1`) and router-mode strata.

---

## 13. Leakage controls

- Planning uses only forecast quantities (`bundle.*.point`), the timestamp-based ephemeris, and state. No realized solar or wind enters any plan.
- Realized wind, solar, and demand are used only in the executor and in the post-hoc accounting.
- The 15° boundary and the 100 kWh terminal are fixed before execution; no value is chosen from results.
- All arms use identical execution machinery (`RobustTelemetryRunner`, same extractor, same τ). Only the `ebr_target_wh` construction differs.
- Discovery vs holdout: the 123 2024 origins have been examined in Stage 3. They are **discovery data for this direction**. The confirmatory evaluation must use a holdout (§14).

---

## 14. Holdout and preregistration requirements

1. **The 2024 NORMAL-route origins are no longer a holdout** for this direction. They were examined in Stage 3 and motivated the design.
2. **Confirmatory holdout:** NORMAL-route origins from **2025**, using the same synthetic demand and wind formulas, the 2025 causal NWP forecast (`data/POLARIS_v0_1_future_weather_forecasts_2025.csv`, to be verified as the same forecast chain), and the 2025 actual solar. The 2025 origins have not been used for EMS or diesel work (only forecast-level metrics, per the freeze). This must be verified before the holdout is frozen.
3. The preregistration for this direction must be written, hashed, and frozen **before** the holdout is generated or run. It must include: the arm definitions in §5–6, the 15° boundary, the terminal rule, the gates in §10–11, the multiplicity rule in §12, and the holdout definition in §14.2.
4. The existing 2024 discovery results are not to be cited as confirmatory evidence.
5. No parameter in this design may be selected after seeing any new result. The only permitted parameter is the 15° bin, which is fixed by the existing project convention.

---

## 15. Interpretation matrix

| Result on confirmatory holdout | Interpretation | Action |
|---|---|---|
| SW-L passes both reliability gates and the diesel gate, with saving ≥ 40% | Target achieved safely (the contract's efficiency target) | Document; further confirmation in a second holdout before any claim beyond research |
| SW-L passes all gates, saving < 40% but > 0 with CI > 0 | Useful research result: protection costs part of SW's saving | Report the saving-vs-protection trade-off; do not claim the target |
| SW-L fails proportional; S-L passes; wind contrast (SW-L − S-L) negative | H1 partly supported: the wind credit degrades reliability even with protection on | Abandon wind credit in daylight; keep S-L as the efficiency reference |
| SW-L fails proportional; S-L also fails | H2 not supported; the protection term does not explain the failure | Abandon the low-sun protection direction; record the failure mechanism as unresolved |
| SW-L passes; S-L passes; interaction CI excludes zero | Wind effect depends on protection (H2) | Report; consider mechanism F only as a separate, pre-registered experiment |
| Any candidate fails the SOC floor | Safety failure | Reject regardless of fuel |

---

## 16. Failure criteria

A candidate fails if any of the following hold on the confirmatory holdout:

1. Critical-first reliability below Control B (`ΔR_CF < 0.00 pp`).
2. Proportional reliability below Control B (`ΔR_P < 0.00 pp`).
3. Any realized SOC below 20.0%.
4. Fuel saving CI includes zero or the Wilcoxon p ≥ 0.05, even if safety passes (the candidate is then not advanced, though it is still reported).
5. Any genuine simultaneous charge/discharge violation (failure to resolve under the τ rule), or any optimizer infeasibility.
6. Fewer than 123 complete origins, or any unreported arm-hour.

---

## 17. Conditions for advancing toward ≥ 40%

All of the following must hold:

- SW-L passes all three safety gates on the 2025 confirmatory holdout.
- The diesel gate passes.
- The protection effect (SW-L − SW) is reported with its CI, showing the cost of protection.
- The wind contrast (SW-L − S-L) on proportional reliability is non-negative, or its CI includes zero.
- A second confirmatory holdout (2026 prospective or a further preregistered split) reproduces the safety result.

Any further efficiency work toward 40% must then be a new preregistered design (for example mechanism F with a governed minimum), not a re-tuning of SW-L.

---

## 18. Conditions requiring abandonment of the direction

Abandon the wind-credit-plus-protection direction if any of the following occur:

- SW-L fails the proportional gate on the confirmatory holdout while S-L passes, and the wind contrast is significantly negative (H1 supported). Wind credit in daylight is not compatible with the safety contract.
- SW-L fails on the discovery set and the holdout in the same direction.
- The solar-elevation input cannot be made causal and deterministic from the forecast chain.
- The 2025 holdout cannot be shown to use the same forecast chain as the frozen campaign.
- Protection at low sun causes a systematic increase in curtailment large enough to offset the saving (report, and treat as a finding about the realization rule rather than a tuning opportunity).

---

## 19. What must be verified before any implementation

1. Solar elevation is available to the decision layer, causally, from timestamps alone.
2. The 2025 causal NWP and actual-solar files are the same chain as the frozen 2024 campaign.
3. The governed EBR branch used at low sun reproduces `compute_governed_ebr` exactly (unit test).
4. The per-hour replacement reproduces S and SW exactly when `L_k = 0` everywhere, and Control B when `L_k = 1` everywhere (unit tests).

---

## 20. Observed vs inferred vs causal diagnostic

- **OBSERVED:** the Stage 3 telemetry facts in §2.
- **INFERRED:** that the wind credit lowers night reserve and removes diesel commitment, which exposes night shortfall.
- **CAUSAL DIAGNOSTIC:** only the 2×2 factorial in §5 can identify the protection effect and the wind effect given protection. Stage 3 alone cannot. This design does not claim the causal chain until the confirmatory holdout is evaluated.

---

## 21. STATUS

**DESIGN COMPLETE.** Not implemented, not executed, not tuned. No production, S/SW, preregistration, or campaign artifact was modified.
