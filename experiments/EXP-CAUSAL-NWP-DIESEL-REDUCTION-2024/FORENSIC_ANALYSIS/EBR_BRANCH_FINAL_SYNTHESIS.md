# EBR Branch: Final Synthesis

**Status:** design synthesis only. No experiments run, no production code changed, no new EBR experiment started. Completed frozen experiments and diagnostics are treated as authoritative.
**Reviewed:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` results; `FORENSIC_REPORT.md`; `HOURLY_TRACE_REPORT.md`; `TERMINAL_ABLATION_REPORT.md`; `EBR_ABLATION_REPORT.md`; `EBR_ABLATION_123_REPORT.md`; `EBR_LOAD_CLASS_DIAGNOSTIC.md`; `CRITICAL_AWARE_EBR_DESIGN.md`; `CRITICAL_AWARE_EBR_EXPERIMENT.md`; `CRITICAL_AWARE_EBR_FAILURE_REVIEW.md`; `WIND_ERROR_ANALYSIS.md`; `SOLAR_ONLY_EBR_EXPERIMENT.md`.

---

## 1. What Is Proven

These rest on frozen results or on reproduced, exact computations.

**Frozen campaign (authoritative):**
- Arm B (causal MEPS NWP + physics) burns **+1,125.7 L (+20.5%)** more diesel than Arm A over 123 origins. Arm B is worse in 87 of 123 origins.
- Accounting, the battery floor, and optimizer status are clean in all arms (0 floor violations, 0 optimizer failures, 0 busbar residual).
- Min SOC for Arm A is exactly 57.83% in every origin. This matches the governed 6-hour EBR reserve: `(40,000 + 6 × 11,600 / 0.92) / 200,000 = 57.83%`.

**Mechanism-level, reproduced exactly (the six traced origins reproduce the frozen fuel to four decimals; 123/123 for the EBR-OFF baseline):**
- The early diesel commitment is at **step 0 of each origin**, in the same physical state for both arms. It comes from the 24-hour solar forecast.
- **EBR removal eliminates step-0 diesel in all 123 origins** (123/123 EBR-OFF origins have zero step-0 diesel). Fuel falls 68.4%, and diesel-on hours fall 73%.
- **Removing only the terminal target does not remove early diesel charging.** Step-0 diesel is unchanged in three of six origins and differs in the other three, so the terminal target is not the source of the early commitment.
- **The reserve is the constraint that forces the commitment.** It is tight at step 0 in every arm and origin, and its removal eliminates the commitment.
- **Critical-load split (research definition min(11.6 kW, realized demand), accounting only):** of the +1,328 kWh extra unmet under EBR-OFF, about 93% is non-critical. Critical reliability moves only −0.28 pp.
- **Curtailment mechanism (realization rule):** same-hour discharge accounts for about 93–96% of curtailment. The executor curtails surplus when the plan discharges in the same hour, rather than reducing the discharge.
- **Critical-aware EBR (six origins, pre-registered):** fuel −33.9%, critical reliability −0.46 pp. **FAIL.**
- **Solar-only critical-aware EBR (six origins, pre-registered):** fuel −35.0%, critical reliability −0.29 pp. **FAIL.**
- **Critical-reliability failures are concentrated in 11 hours**, all at night or low sun. The per-hour identity `critical unmet = 11,600 − realized renewable` holds exactly at origin 66 steps 3–4, where the reserve was zero and no diesel was committed.
- **Wind error in this benchmark is a deterministic one-sided profile.** Realized wind is always at or below forecast (−5,000 W to 0 W), and the error depends only on the step index within the origin. It is identical in all six origins and repeats every 12 steps. It is not a sample of weather.

---

## 2. What Is Only Inferred

- **Why causal NWP increases diesel, as a single mechanism.** The evidence supports a chain: solar-poor forecast → reserve unconditional on forecast → diesel charges the reserve → realization curtails surplus. Each link is measured, but the full chain was not isolated by a single counterfactual that holds every other term fixed.
- **That forecast accuracy is worse for Arm B than for Arm A.** Forecast accuracy against realized solar was measured only as a sign and magnitude pattern (104 of 123 origins under-forecast), not as a validated accuracy comparison across all origins.
- **That the origin-66 timing error explains that origin's penalty.** The hourly timing pattern is observed; its causal weight is not isolated.
- **That the solar-only reserve is the right direction.** Its fuel and critical-reliability effects are measured on six origins. Whether it generalises across the campaign is unknown.
- **That the critical/non-critical split is 93%.** This depends on the research-layer definition. The planner's own forecast-based convention was never resolved, and the earlier sensitivity was blocked, so the split is not established under the planner's convention.
- **Wind-error magnitudes as representative of anything physical.** These are not measured. The benchmark wind is synthetic.

---

## 3. Why Causal NWP Currently Increases Diesel

1. Arm B's solar forecast is **solar-poor on many days and shifted in timing on others**. In the 123-origin forecast-only pass, Arm B under-forecasts 24-hour solar on 104 of 123 origins, and on cloud-saturated days it forecasts near zero.
2. The **EBR reserve is unconditional**. It requires the battery to hold about 57.8% SOC against the 6-hour critical load, whatever the forecast says renewables will deliver. Arm A's surplus forecast fills the reserve with solar. Arm B's does not, so GAP19 charges the reserve from diesel.
3. The reserve is **ranked above fuel** in the lexicographic objective (J2 above J3), so the planner buys diesel to meet it before minimising fuel.
4. The **realization rule** then curtails the surplus whenever the plan discharges in the same hour as the sun arrives. Diesel committed for the reserve, plus planned discharge, becomes curtailed energy.

So the increase is not caused by the forecast alone, nor by the terminal target, nor by the battery. It is the forecast shape meeting an unconditional reserve, with the realization rule converting the surplus into waste.

---

## 4. Why EBR Removal and Critical-Aware EBR Are Not Acceptable Replacements

**EBR removal (EBR-OFF):**
- Fuel falls 68.4%, but **total unmet rises 16.9%**, and the frozen reliability gate fails in 101 of 123 origins.
- The planned critical load is still protected, but **realized critical reliability falls** (93.7% vs 95.1% over six origins), and the reserve-free SOC reaches the 20% floor in many origins.
- It removes the protection that the frozen design encodes (a 6-hour survivability reserve) rather than making that reserve smarter.

**Critical-aware EBR (wind-including):**
- Fuel −33.9% and curtailment −13%, but **critical reliability falls 0.46 pp**, failing the pre-registered rule.
- The failure is concentrated in 11 night and low-sun hours where forecast wind over-predicts realized wind (0.7–5.0 kW). With the reserve released and no diesel committed, the shortfall goes straight to critical unmet.
- Depending on forecast wind is the wrong design: wind is the term that fails.

**Solar-only critical-aware EBR:**
- Fuel −35.0%, curtailment −17%, but **critical reliability still falls 0.29 pp** and fails the same rule.
- It removes the wind dependence but keeps the same structural weakness: the reserve is sized to a forecast, with no safeguard for forecast error at night. Its improvement over the wind variant is small.
- The critical convention is unresolved, so even this result cannot yet be taken as settled.

Neither variant is a replacement. Both trade critical protection for fuel, and the frozen reserve's protection is what they give up.

---

## 5. Genuinely Open Research Questions

1. **Planner critical convention.** Under the planner's own forecast-based convention, what is the critical-reliability and non-critical split for Arms A, B, and the EBR variants? This is unresolved, and the EBR pass/fail decisions depend on it.
2. **Real forecast-error distributions.** What are the solar and wind forecast error distributions against real observations, at this site, across the full campaign? The current wind benchmark is synthetic, so none of the magnitudes can be taken as physical.
3. **Whether Arm B's forecast is less accurate than Arm A's.** The sign and pattern are measured, but a validated accuracy comparison against realized solar across all origins is not.
4. **Whether a reserve can be made forecast-conditioned without losing protection.** This is open. The evidence shows that unconditional reserves cost fuel, and that naive forecast-conditioned reserves lose critical reliability. Whether a middle ground exists, and what would guarantee protection under forecast error, is not established.
5. **Whether the realization rule should reduce planned discharge instead of curtailing surplus.** The curtailment mechanism is measured. Whether the physically correct realization would reduce waste is not tested.

---

## 6. Recommended Next Research Branch

**Branch: forecast-error-aware critical-load protection, evaluated on real observations rather than the synthetic benchmark.**

Concretely, this is a research-only evaluation question: given observed solar and wind series at the site, measure how often and by how much the current 24-hour forecast fails to cover critical load, and what the realized critical unmet would be under the frozen reserve and under alternatives that protect the same critical energy without depending on a point forecast.

The branch does **not** tune the EBR formula. It first establishes the forecast-error distribution that any protection scheme must survive, using data that is not synthetic. Only after that would a candidate be formulated, and it would be judged against the same frozen reliability gate.

Scope for the first step: the existing site data for solar, and whether real wind is available at the site. Output is a measured error distribution, with no candidate controller and no margin chosen.

---

## 7. Production Status

- GAP19 (`gap19_highs_native.py`) hash: `fd1afe10…`, matching the preregistered value.
- Causal NWP forecaster (`causal_nwp_physics.py`) hash: `14e72d8a…`, matching the preregistered value.
- No production file was modified by this branch. All research harnesses live in `FORENSIC_ANALYSIS/` and import the frozen code unchanged.

---

FINAL DIAGNOSIS: Arm B's extra diesel comes from an unconditional 6-hour EBR reserve that is ranked above fuel, combined with a solar-poor forecast that cannot fill it. The realization rule then curtails the surplus whenever discharge and sun coincide. The terminal target is not the source. Removing the reserve fixes the fuel but costs unmet load, and making it forecast-conditioned on the synthetic wind benchmark fails critical reliability.

CURRENT PRODUCTION STATUS: Production is unchanged by this branch. GAP19 and the causal NWP forecaster match their preregistered hashes. The EBR reserve in production is the governed formula, and the campaign's Arm B result (+20.5% diesel vs Arm A) stands as authoritative.

EBR BRANCH STATUS: Closed for tuning. Removing the reserve (EBR-OFF) and the two critical-aware variants (wind-including and solar-only) were all tested under pre-registered rules. None is an acceptable replacement: each trades critical protection for fuel, and both critical-aware variants fail their criterion.

PRIMARY OPEN RESEARCH QUESTION: What is the real distribution of solar and wind forecast error at the site, and can critical load be protected under that error without an unconditional reserve?

NEXT RESEARCH BRANCH: Forecast-error-aware critical-load protection, evaluated on real observed solar and wind data (measurement first, no candidate controller and no margin chosen).

WHY THIS BRANCH: Every EBR variant tested so far was judged against a synthetic wind benchmark whose error is deterministic and one-sided, so none of the results can say how the reserve behaves under real forecast error. Measuring the real error distribution is the prerequisite for any defensible protection rule. Further EBR tuning would only fit the synthetic benchmark, which the evidence cannot validate.
