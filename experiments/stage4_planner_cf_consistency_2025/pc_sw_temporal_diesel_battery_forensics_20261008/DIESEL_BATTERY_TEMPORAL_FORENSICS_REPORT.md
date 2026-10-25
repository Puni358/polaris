# POLARIS — PC-SW v1.2 Temporal Diesel/Battery Allocation Forensics

**Date:** 2026-10-08
**Status:** READ-ONLY forensic research. No production code, PC-SW semantics, EBR, objective weights, priorities, or battery parameters modified. No policy campaign executed in this pass. No parameter tuned.
**Hash verification:** `verify_protected_hashes(REPO)` — **0 mismatches** (VERIFIED), re-checked before this analysis.

**Closed branches, not reopened:** EBR formulation/multipliers — CLOSED. Rule-D true-curtailment recapture — CLOSED. T1 temporal tie-break — CLOSED (`C`, safety failure), its **persisted campaign artifact is read and cited**, not re-run, because it directly answers several questions in this report.

---

## Scope and method

This report is built from three sources, each labeled by provenance: (1) population-level aggregation of the certified `PC_HOURLY_TELEMETRY.csv` (2,952 resolves, VERIFIED, no re-solve); (2) the already-persisted **T1 123-origin campaign artifact** (`t1_temporal_tie_break_campaign_20261008/CAMPAIGN_REPORT.md`), which is the single most informative source in this report because it is an *actual, governed, full-population test* of exactly the "is diesel timing degenerate" question this task asks — reused, not duplicated; (3) the fully-traced origin-2 single resolve (reused from two prior tasks). No new 24-step MILP reconstruction across all 526 diesel+charging hours was performed in this pass — population-level proxies and the T1 campaign's own resolve-level audit stand in for it.

---

## 1. The actual planner objective (VERIFIED, traced from executable source, re-confirmed)

`research_numerical_extractor_planner_cf_v1.py:84-85`: `PRIORITY = {"J1":5, "J_NC":4, "J2":3, "J3":2, "J4":1}` — **J1 > J_NC > J2 > J3 > J4, confirmed from source, not configuration.**

`J3` (lines 335-337), exact:
```
c_j3[diesel[t]]  = MARGINAL_FUEL_L_PER_WH · dt     # 0.00025 L/Wh
c_j3[u_diesel[t]] = BASE_FUEL_L_PER_H · dt           # 5.0 L/h, charged whenever u_diesel[t]=1, independent of power level
c_j3[v_start[t]] = STARTUP_FUEL_L                     # 2.0 L, charged only when diesel transitions off→on
```
Diesel min/max (`R9`/`R10`): `p_diesel[t] ≥ 10,000·u_diesel[t]`, `p_diesel[t] ≤ 100,000·u_diesel[t]` (governed `diesel.yaml`). Fuel-inventory row (Amendment A2) constrains only hour 0 of each resolve: `5·u_diesel[0] + 0.00025·p_diesel[0] ≤ F_rem`. All confirmed directly in source, not inferred.

---

## 2–3. The 526 diesel+charging hours — reused population evidence (VERIFIED)

Reconfirmed from the immediately preceding task: **526/547 (96.2%)** diesel-on hours co-occur with charging, accounting for **8,557.77 L (98.04%)** of total fuel. All 526 show EBR margin **7,280–148,027 Wh** (never tight). **539/547 (98.5%)** diesel-on hours have zero unmet load of any kind, i.e. `J1=J_NC=0`, and `J2=0` in 100% of all 2,952 resolves population-wide. **Full 24-step internal reconstruction for every one of the 526 was not re-performed in this pass** — the central counterfactual question ("why does the optimizer want energy in the battery NOW") is answered below using the J3 geometry (§6) and the T1 campaign's resolve-level audit (§5/§11), which together give a population-scale, not single-resolve, answer.

---

## 4. Tracing stored energy forward (DIAGNOSTIC, origin 2; reused — not re-derived for all 526)

Reused from the origin-2 single-resolve trace (two tasks prior): diesel at hours 0–1 charges the battery to 165,958.2 Wh; this energy is drawn down via discharge-only operation through hours 2–7, landing **exactly** at the Layer-C floor at hour 7 (headroom 0.0 Wh) — i.e., in this one fully-traced case, the stored energy is **fully consumed by discharge before the next binding point**, not left idle or SOC-ceiling-capped. This was the planned (not merely realized) trajectory. Generalizing this exact pattern to all 526 hours was **not performed** — marked UNKNOWN at that scale.

---

## 5. Temporal substitution — now answered empirically, not just theoretically (VERIFIED — decisive finding)

The immediately preceding governance audit (two tasks prior) formally proved that, **within a single isolated resolve**, shifting charge timing between two already-diesel-committed hours of the same run is a genuine solve-level tie (does not change `J1/J_NC/J2/J3`, provided `u_diesel`/`v_start` are explicitly pinned). **This has now been tested at full 123-origin, 2,952-resolve, closed-loop scale — the T1 campaign** — and the result settles the question precisely:

- **Solve-level invariance: 100% VERIFIED.** Across all 2,941 resolves where the tie-break was applied, `J1, J_NC, J2, J3, u_diesel*, v_start*` were **bit-identical** to the baseline solve in every case (0 invariance failures) — exactly as the theoretical proof predicted.
- **Realized closed-loop outcome: fuel increased by +241.6077 L (+2.77%), and Gate S2 (proportional reliability) FAILED** (`R_P = 97.7948% < 97.7963%` control reference).

**This is the single most important finding of this report: diesel timing is genuinely degenerate at the solve level (answer to §5's question: "B — one of multiple J3-equivalent solutions", confirmed, not merely conjectured), but that solve-level degeneracy does NOT survive translation into the realized closed-loop trajectory.** The documented mechanism (`CAMPAIGN_REPORT.md` §5, reused verbatim): (a) in 330/2,941 resolves the reallocation actually *increased* hour-0 charging rather than decreasing it, because the tie-break objective sums over an *entire run*, not a single hour, creating cross-run trade-offs the single-resolve proof didn't model; (b) where charging was genuinely postponed, hour-0 battery reserve was left lower, and when realized solar/wind in the next rolling cycles diverged from forecast, the **depleted battery state forced additional diesel later** (+9 starts, +1,626 kWh diesel energy) — a direct, now-empirically-confirmed instance of the plan-vs-realization gap under rolling MPC that the theoretical proof could not rule out; (c) postponing charging toward the morning solar ramp caused **+1,207.52 kWh of additional curtailment** when solar then arrived against an already-full battery.

---

## 6. J3 objective geometry — break-even analysis (DERIVED, new in this pass)

For a fixed total energy requirement `E` delivered within diesel's governed bounds, concentrating it into **fewer, higher-power hours** is strictly cheaper in base fuel than spreading it over **more, lower-power hours continuously**, because base fuel (`5 L/h`) is charged **per hour-on**, not per unit energy, while marginal fuel (`0.00025 L/Wh`) is energy-linear and therefore concentration-invariant. Example: delivering `E` in 1 hour costs `5+2+0.00025E` (one start); delivering the same `E` continuously over 2 hours costs `10+2+0.00025E` — **5 L more**, for identical marginal fuel and critical/non-critical service. **This structural bias toward concentrated, bursty operation is an inherent, unavoidable property of the governed `J3` formula itself — not a bug, not something this report proposes changing.**

**Quantified from actual trajectories (VERIFIED):** mean diesel power when on is **43,834 W**; the maximum ever observed across all 547 hours is **67,826 W** — never approaching the 100,000 W diesel ceiling, and closely tracking the **effective ceiling set by load (~12–18 kW) plus the 50 kW battery charge-rate cap (a governed, unmodifiable battery parameter)**. **The planner is already operating close to the concentration ceiling the battery's own charge-rate limit allows** — there is a theoretical upper bound on how much further base-fuel savings concentration alone could unlock (e.g., `2,735.0 L` actual base fuel vs. a `1,763.0 L` floor *if* diesel ran at the ~68 kW realistic ceiling in every one of a reduced hour-count — itself almost certainly infeasible hour-by-hour given real demand variability), but this bound is **not a reachable target**, only an order-of-magnitude sense of how tightly bound the concentration effect already is by the (excluded-from-modification) battery charge-rate cap.

---

## 7. Startup/base-fuel fragmentation — is it causal or a consequence? (DERIVED, decomposed)

335 runs; **170 (50.7%) are single-hour, 127 (37.9%) are two-hour**, mean 1.63 h. This decomposes into two genuinely distinct, non-overlapping sub-mechanisms:

1. **Why each individual run is short/concentrated:** directly caused by `J3`'s own base-fuel structure (§6) — this is a **genuine, demonstrated causal mechanism**, not merely a consequence of something else.
2. **Why there are multiple separate runs per day rather than one continuous run:** caused by the (closed, not reopened) reserve/EBR timing structure — each run replenishes the battery ahead of a *different* future binding point (established at origin 2: separate bursts ahead of hours 7, 19, 23). This is a consequence of the already-closed EBR mechanism, re-cited here only to avoid double-attributing it as something new.

**Would these short runs disappear if diesel charging were not needed?** Not fully testable without reopening EBR (excluded) — but the T1 result (§5) already shows that even changing *only the timing within* existing runs (not their number or the underlying reserve requirement) is enough to destabilize the realized outcome, so a stronger intervention on run structure itself would carry at least as much risk.

---

## 8. Battery energy arbitrage (DERIVED, origin-2 bound only; not generalized)

For origin 2's fully-traced hours 0–1 charging event: `0.92 × 71,693.7 Wh` charged → `65,958.2 Wh` stored → discharged at `η_dis=0.92` through hours 2–7 → `~60,681.5 Wh` delivered to load, landing exactly at the hour-7 floor with **zero residual** (fully consumed, not left idle). Round-trip loss for this one traced episode: `~11,012.2 Wh` (≈15.4% of the charged energy, matching the governed `1−0.92×0.92` constant). **This was not computed for the other 525 diesel+charging hours — UNKNOWN at population scale**, consistent with the same limitation flagged in the two preceding tasks.

---

## 9. Forecast vs. realization for the 526 events (reused, DIAGNOSTIC — not re-derived)

Reused from the EBR population forensics (two tasks prior): wind forecast error is **exactly zero** for every origin (deterministic formula); solar forecast error is mildly *optimistic* on average (realized < forecast by ~10,771 Wh over 6h, population mean) — **not** systematically pessimistic as an earlier (unverified) claim had assumed. No population-scale forecast-error decomposition specific to the 526 diesel+charging subset (as opposed to all origins) was newly computed in this pass.

---

## 10. Rolling-horizon effect (VERIFIED — now has a concrete, empirically observed instance)

The T1 campaign (§5) **is** the requested demonstration: diesel charging that was open-loop optimal (invariant `J1-J3`) for a single resolve's own 24-hour plan became **harmful** once the next rolling resolve reacted to the resulting lower battery reserve and diverging realized solar/wind — i.e., **the rolling-horizon architecture, combined with the plan-vs-realization gap, is exactly the mechanism by which a locally-costless temporal change cascades into a globally costly one.** This is not a new architecture flaw being proposed for change — it is the explanation for why temporal interventions at this layer are structurally risky, reinforcing (not merely restating) the D classification from two tasks prior.

---

## 11. Solver degeneracy / tie analysis (VERIFIED — fully answered, not merely forensic)

**Diesel timing is genuinely NOT uniquely determined at the solve level** — `B` from the Section-5 taxonomy, now with full-population empirical confirmation via the T1 campaign's 100%-invariance audit (2,941/2,941 resolves bit-identical on `J1,J_NC,J2,J3,u_diesel,v_start`). **But exploiting that degeneracy changes the realized closed-loop trajectory even when it cannot change the planned objective values** — the degeneracy is real at the planning layer and simultaneously inert-to-exploit at the realized layer, because realization depends on the *specific* charge/discharge schedule, not just the fuel total it implies. No new tie-break is proposed here, consistent with T1 already being closed.

---

## 12. Mutually exclusive causal partition (hierarchical, overlaps flagged — reused + extended)

| Category | Hours (of 547) | Fuel (L) | Basis |
|---|---|---|---|
| 1. Immediate physical load requirement | ≤21 (upper bound; exact count UNKNOWN) | ≤171.48 | VERIFIED (count), DERIVED (necessity) |
| 2. Future battery-energy requirement (temporal positioning, §4/§6) | overlaps with 3 below | overlaps | DERIVED |
| 3. EBR/reserve requirement | 526 (co-occurrence) | 724.5549 (aggregate DIAGNOSTIC) | VERIFIED/DIAGNOSTIC — CLOSED branch, cited not reopened |
| 4. Terminal requirement | not separable from 3 | UNKNOWN | per §9 of the EBR task |
| 5. Base/startup economics (concentration bias, §6/§7) | explains *shape*, not a separate liter bucket — base+startup = 2,735.00+670.00=3,405.00 L structurally, overlapping with 1/3 | 3,405.00 (structural, not causal-exclusive) | VERIFIED (structural), DERIVED (causal role) |
| 6. Fuel-inventory constraint | not isolated as proximate driver in the one traced case | UNKNOWN | DIAGNOSTIC (origin 2 only) |
| 7. Lexicographic objective effect (J2>J3 forcing banking ahead of binding points) | 526 | overlaps with 3 | VERIFIED/DERIVED |
| 8. Solver degeneracy (within-run timing only) | 2,941 resolves show degenerate *timing*, but **zero net fuel liters** by definition (tie) | 0 | **VERIFIED, now empirically confirmed via T1** |
| 9. Mixed/indeterminate | remainder | remainder | UNKNOWN |

**An exact mutually-exclusive liter partition remains impossible**, as stated in the prior task — categories 2/3/4/7 are the same underlying mechanism viewed from different angles, and category 5 (base/startup) is a structural, not causal-exclusive, axis that explains the *timing shape* of categories 2/3/7 rather than standing apart from them.

---

## 13. Largest remaining NEW mechanism (after EBR/Rule-D/T1/cloud/terrain exclusions)

**None was found that meets the five required criteria simultaneously.** The base-fuel concentration bias (§6) is a real, causally-demonstrated, quantifiable mechanism — but it is **already near its practical ceiling** (diesel power when on tracks the ~68 kW load+charge-cap ceiling, not the 100 kW diesel max), meaning the achievable improvement from "more concentration" is small and bounded by a battery parameter explicitly excluded from modification. The within-run temporal degeneracy (§5/§11) is real and large in principle (T1's reallocation moved 17.93% of the tie-objective) but has now been **empirically shown to be unsafe to exploit** at full population scale (S2 failure, +241.6 L worse).

---

## 14. Potential lever

**None is proposed.** Both candidate mechanisms examined in this pass were either already near their physical ceiling (§6/§13) or already empirically tested and failed safety (§5, T1). No new, untested, non-arbitrary candidate emerged from this analysis.

**Classification: D — mechanism real, no safe online lever exists.**

---

## 16. Required final answers

1. **Why does PC-SW charge the battery with diesel when EBR is not currently binding?** Because the Layer-C reserve row is enforced at *every* hour of the 24-hour horizon, not only the hours where it happens to be tight at realization time — diesel at an early, slack-margin hour funds the battery for a *later* hour in the *same* horizon that will be binding (demonstrated exactly at origin 2: hours 0–1 fund hour 7's floor). "Not currently binding" and "not needed at all" are different statements; margin being large at the charging hour is expected and consistent with forward provisioning, not evidence of waste (§4/§5).
2. **Physically necessary, economically induced, or an artifact of the hierarchy?** All three, inseparably: the *need* for some reserve is EBR-structural (closed branch); the *timing/shape* of each burst (short, concentrated) is economically induced by J3's base-fuel geometry (§6, DERIVED, new in this pass); and the *specific* within-run allocation is a genuine artifact/degeneracy of the hierarchy (§5/§11, VERIFIED empirically via T1).
3. **Fuel associated with the mechanism?** 8,557.77 L (98.04%) co-occurs with charging; 724.5549 L is the aggregate EBR-attributable figure (nested within the 8,557.77 L, not additive); 3,405.00 L is base+startup fuel (structural axis, also overlapping).
4. **How much from base-fuel/startup fragmentation specifically?** Not separable as a standalone liter figure from the reserve-timing mechanism it serves (§7) — it explains *shape*, not an independent quantity.
5. **How much genuinely required for future critical service?** Negligible in the strict J1 sense (only 1/547 hours show any critical-unmet risk even under full realized conditions); the broader J2-preserving figure is the same 724.5549 L aggregate already cited, known to be a population *mixture* (77 beneficial / 44 harmful origins, established two tasks prior).
6. **How much merely temporal positioning?** This is exactly what T1 attempted to capture (§5) — found real at the solve level but net **harmful** (+241.6 L) when actually exploited at full closed-loop scale, so no safe, isolable "merely positioning" liters can be claimed as recoverable.
7. **Uniquely determined or degenerate?** **Degenerate at the solve level (VERIFIED via T1's 100% invariance audit)**, but the degeneracy does not survive the realized closed loop.
8. **Does the rolling-horizon architecture create the behavior?** It is the **mechanism by which a solve-level-costless temporal change becomes realized-costly** (§10), empirically confirmed via T1 — not something newly discovered here, but now concretely evidenced rather than hypothesized.
9. **Largest remaining causal mechanism after exclusions?** None identified that is simultaneously material, untested, and safe (§13).
10. **Non-arbitrary online lever?** **No.**
11. N/A.
12. **Next most valuable forensic question:** whether a *trajectory-shape* (multi-hour-ahead, not static or single-hour) decision-time signal could separate the 77/44 origin populations found in the EBR discriminator task — flagged as untested in that task and still untested here; this remains the only unexplored avenue in the current line of investigation.

"NO POLICY EXPERIMENT WAS EXECUTED."
