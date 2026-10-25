# POLARIS — Post-Corrected-Stage-4 Hour-0 Trace (ISSUE-5, Candidate S)

**Date (UTC):** 2026-10-06
**Scope:** the 12 Candidate-S origins whose hour-0 diesel was classified as "unexplained" in the corrected reproduction. Read-only diagnostic.
**Campaign run:** NO. **Results modified:** NO. **Production modified:** NO. **Solver configuration changed:** NO.
**Companion:** `experiments/POST_CORRECTED_STAGE4_HOUR0_TRACE.json` (per-origin records).

**Method.** Reconstructed the hour-0 optimisation inputs from the corrected run's own artefacts (state, forecast bundle, router, S-arm EBR, terminal config). Ran the unmodified `ResearchNumericalGAP19Optimizer.optimize` once per origin, and checked that its hour-0 diesel reproduces the recorded telemetry to 0.0 W for all 12. On the same HiGHS instance, one diagnostic re-solve pinned hour-0 diesel to zero, with all bounds, objectives, and lexicographic priorities unchanged. That re-solve is a counterfactual used only for classification and is not stored as a result.

**Labels:** `[VERIFIED]` reproduced in this trace. `[INFERRED]` a structural argument from verified facts. `[UNKNOWN]` not established.

---

## 1. Result

| Classification | Count | Origins |
|---|---|---|
| FORCED | 0 | — |
| **SELECTED** | **12** | all |
| TIED | 0 | — |
| UNKNOWN | 0 | — |

Every hour-0 diesel decision in the 12 origins is **lexicographically selected**: a diesel-off hour 0 is feasible, but its global solution is lexicographically worse than the recorded one. `[VERIFIED]`

**Two mechanisms:**
- **Index-0 soft reserve (9 origins: 13, 22, 44, 46, 85, 88, 92, 95, 96).** Diesel-off forces the hour-0 critical deficit onto the battery, which drops end-of-hour-0 energy below the reserve requirement. The reserve is soft at priority J2, above fuel, so diesel-off is lexicographically worse. `[VERIFIED]`
- **J3 fuel consolidation (3 origins: 12, 18, 62).** Diesel-off keeps J1 and J2 at zero but costs 0.08–0.11 L more fuel globally. The diesel-on solution is the fuel-optimal one. `[VERIFIED]` for the margin; the source of the margin (diesel energy and start placement) is partly `[INFERRED]`.

---

## 2. Reproduction and Verification

- **Route mode:** EMERGENCY at hour 0 (recorded telemetry, reproduced by the router on the reconstructed state). `[VERIFIED]`
- **Optimizer mode:** EMERGENCY. The MILP built **24 EMERGENCY rows** (`p_dis(t) − p_served(t) ≤ 0`, t = 0…23) in all 12 origins. `[VERIFIED]`
- **Reproduction:** recomputed hour-0 diesel equals the recorded value exactly (|Δ| = 0.0 W) in all 12 origins. `[VERIFIED]`
- **Solver status:** optimal in the recorded solve and in the counterfactual. Recorded MIP gap is 0 in 10 origins, 1.9×10⁻¹⁵ (origin 92), and 5.8×10⁻⁵ relative (origin 46). `[VERIFIED]`

---

## 3. Hour-0 Inputs (common to all 12)

| Input | Value |
|---|---|
| Initial energy / SOC | 100,000 Wh / 50% |
| Initial fuel | 100 L |
| Diesel initial state | off (startup charged on any hour-0 ON) |
| Critical demand | 11,600 W |
| Total demand (step 0) | 17,897.78 W |
| Wind forecast, hour 0 | 7,000 W (L₀ = 4,500 W) |
| Solar forecast, hour 0 | 0–547 W (per origin, §4) |
| Renewable credit (S) | solar only |
| Terminal target | 100,000 Wh at horizon index 23 |
| Battery | 20–95% of 200 kWh; charge and discharge ≤ 50 kW; η = 0.92 each |
| Diesel | 10–100 kW when ON; 5 L/h base; 0.25 L/kWh marginal; 2.0 L startup (MILP only) |

---

## 4. Per-Origin Results

Energies in kWh. Reserve requirement at the end of hour 0 = EBR₀ + 40 kWh.

| Origin | EBR₀ | Requirement | Solar₀ (kW) | Recorded diesel (kW) | Recorded E₀ | Recorded charge (kW) | Recorded unmet non-crit (kW) | Recorded J2 / J3 (L) | Diesel-off: J2 (kWh) | Diesel-off: ΔJ3 (L) | Classification | Mechanism |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | 51.47 | 91.47 | 0.000 | 46.45 | 138.5 | 41.85 | 6.3 | 0 / 55.242 | 0.000 | +0.081 | SELECTED | J3 consolidation |
| 13 | 57.47 | 97.47 | 0.000 | 34.75 | 127.7 | 30.15 | 6.3 | 0 / 38.079 | 2.468 | −2.139 | SELECTED | Index-0 reserve |
| 18 | 54.25 | 94.25 | 0.000 | 10.00 | 105.0 | 5.40 | 6.3 | 0 / 20.931 | 0.000 | +0.096 | SELECTED | J3 consolidation |
| 22 | 56.48 | 96.48 | 0.000 | 10.00 | 104.5 | 4.90 | 6.3 | 0 / 19.000 | 1.477 | −9.500 | SELECTED | Index-0 reserve |
| 44 | 56.13 | 96.13 | 0.547 | 45.28 | 137.9 | 41.23 | 6.3 | 0 / 68.773 | 0.534 | +0.184 | SELECTED | Index-0 reserve |
| 46 | 57.84 | 97.84 | 0.142 | 10.00 | 104.6 | 5.04 | 6.3 | 0 / 9.500 | 2.682 | −9.500 | SELECTED | Index-0 reserve |
| 62 | 53.01 | 93.01 | 0.319 | 51.09 | 143.1 | 46.81 | 6.3 | 0 / 77.774 | 0.000 | +0.112 | SELECTED | J3 consolidation |
| 85 | 59.01 | 99.01 | 0.000 | 10.00 | 103.6 | 3.94 | 6.3 | 0 / 19.000 | 4.005 | −9.500 | SELECTED | Index-0 reserve |
| 88 | 58.47 | 98.47 | 0.000 | 10.00 | 104.5 | 4.90 | 6.3 | 0 / 23.814 | 3.472 | −9.500 | SELECTED | Index-0 reserve |
| 92 | 57.03 | 97.03 | 0.000 | 10.00 | 104.5 | 4.90 | 6.3 | 0 / 19.000 | 2.025 | −9.500 | SELECTED | Index-0 reserve |
| 95 | 58.15 | 98.15 | 0.000 | 50.85 | 142.6 | 46.25 | 6.3 | 0 / 42.113 | 3.147 | −0.290 | SELECTED | Index-0 reserve |
| 96 | 59.03 | 99.03 | 0.000 | 10.00 | 104.5 | 4.90 | 6.3 | 0 / 19.178 | 4.026 | 0.000 | SELECTED | Index-0 reserve |

Notes on the table:
- "Recorded unmet non-crit" is the plan's non-critical shedding, which is unpriced in the MILP (see the prior audit, §5.13). `[VERIFIED]`
- Recorded E₀ exceeds the requirement by 4–46 kWh in every origin. The excess is not required by the index-0 term. `[VERIFIED]`
- In origins 13, 22, 85, 88, 92, 95, 96 the diesel-off J3 is lower than the recorded J3, but diesel-off has positive J2, so lexicographic order still prefers diesel-on. `[VERIFIED]`

### Per-origin active constraints at hour 0 (recorded)

Binding at hour 0 in every origin: R3 bus balance, R4 demand balance, R8 battery transition, R6 discharge-binary, R7 exclusivity, R11 startup (v₀ = 1 is binding), and LB critical balance. LC reserve at index 0 is **not** binding in the recorded solution (E₀ exceeds the requirement). `[VERIFIED]`

Diesel-off (counterfactual): LC reserve at index 0 binds with a positive slack in the 9 index-0 origins, and nowhere else. `[VERIFIED]`

---

## 5. The Index-0 Mechanism (Verified Quantitatively)

With hour-0 diesel off, the 11.6 kW critical load is served by wind (7.0 kW), solar (s₀), and battery discharge. The battery must supply `(11.6 − 7.0 − s₀)/0.92` kWh, so the largest reachable end-of-hour-0 energy is

`E₀,max(diesel-off) = 100 − (4.6 − s₀)/0.92` kWh (= 95 kWh when s₀ = 0).

The reserve requirement at the end of hour 0 is `EBR₀ + 40`. The shortfall with diesel-off is therefore `max(0, EBR₀ + 40 − E₀,max)`.

Predicted shortfalls match the counterfactual slack to the Wh in all 12 origins: 2.468, 1.477, 0.534, 2.682, 4.005, 3.472, 2.025, 3.147, 4.026 kWh for the nine index-0 origins, and 0 for 12, 18, 62. `[VERIFIED]`

**Correction to earlier reports.** The earlier reconciliation tested the index-0 requirement against the 100 kWh start alone (`EBR₀ + 40 > 100`). That omitted the hour-0 critical discharge, so it under-counted forcing. With the discharge included, the threshold is about 95 kWh. Re-counted across all 123 origins:

| Arm | Forced (refined) | Forced and ON | ON but not forced |
|---|---|---|---|
| Candidate S | 91 | 91 | 3 (origins 12, 18, 62) |
| Candidate SW | 0 | 0 | 39 (not traced here) |
| Candidate SW-L | 123 | 123 | 0 |
| Candidate S-L | 123 | 123 | 0 |
| Control | 123 | 123 | 0 |

`[VERIFIED]`. The earlier counts (S forced 82; S unexplained 12) were based on the looser threshold. With the refined threshold, S's unexplained set shrinks from 12 to 3.

---

## 6. Why These Are Not FORCED or TIED

- **Not FORCED.** The frozen model makes the reserve a *soft* constraint with slack `s_j2`, penalised at priority J2. Diesel-off is feasible for all 12 origins. So no hard infeasibility exists, and FORCED is excluded under the brief's definition. `[VERIFIED]`
- **Not TIED.** Every diesel-off solution differs from the recorded one by a nonzero amount at its first differing lexicographic priority: J2 by 0.5–4.0 kWh (nine origins), or J3 by 0.08–0.11 L (three origins). The J3 margins are about 10² × the MIP tolerance. `[VERIFIED]`
- **SELECTED** is the correct label. `[VERIFIED]`

---

## 7. Mechanism Classification (Real Model Consequence vs Artefact)

| Candidate explanation | Verdict | Evidence |
|---|---|---|
| Real model consequence (soft reserve at J2, hour-0 critical service from battery) | **YES, for the 9 index-0 origins** | Predicted shortfall equals the counterfactual slack to the Wh (§5) |
| Real model consequence (J3 fuel consolidation) | **YES, for the 3 J3 origins**, with a small margin | Diesel-off J2 = 0 but J3 is 0.08–0.11 L higher; recorded MIP gap 0 |
| Numerical or tie-breaking artefact | **NO** | J2 margins of thousands of Wh; J3 margins ≫ tolerance; recorded and counterfactual solves both optimal; no tie (§6) |
| Harness inconsistency | **NO** | Recorded diesel reproduced to 0.0 W; the recorded solution is lexicographically no worse than any diesel-off alternative tested, in all 12 origins; the EMERGENCY rows are built (24 each) |
| Unresolved | **Partly** | The 3 J3 origins' fuel margin is not decomposed into kWh and start placement; the reason the optimum over-charges by 4–46 kWh beyond the index-0 need is not identified beyond fuel consolidation. `[UNKNOWN]` |

---

## 8. Is S's Result Affected?

- **No error was found.** The hour-0 decisions are what the frozen model prescribes. `[VERIFIED]`
- **Interpretation is affected.** Under the soft reserve, the hour-0 battery-charge cost is what the reserve rule demands. Whether the reserve should be hard, or should net the hour-0 critical deficit differently, is a **policy** question. It is not a bug. It must be settled by a separate preregistration if changed.
- The S-vs-SW-L ranking does not depend on these 12 origins. The earlier audit bounded the accounting effects on ranking at ≤ 0.12 pp. `[VERIFIED]` (earlier audit)

---

## 9. Required Evidence and Experiments

- **New experiment required for ISSUE-5: no.** The mechanism is now established for the 12 origins. `[VERIFIED]`
- **Still open:**
  - Issue 3 (planned vs realised charge) requires a separately preregistered experiment, as the earlier audit states. This trace does not change that.
  - SW's 39 unexplained origins were not traced here. They are outside the brief's scope and do not affect S.
  - Duals and reduced costs are not available from HiGHS for this MIP. Extracting them would require an LP re-solve with integers fixed. That was not performed, and the classification does not need it.

---

## 10. Hashes

| Artefact | SHA-256 |
|---|---|
| `experiments/POST_CORRECTED_STAGE4_HOUR0_TRACE.json` | `deba157e29e44716b2a4b7e6cafb86bf41e2c06fcc212a459855592af77bdd70` |
| `experiments/POST_CORRECTED_STAGE4_HOUR0_TRACE.md` | recorded in the final response |

---

## 11. Final Answers

- **ISSUE-5 STATUS:** RESOLVED to **SELECTED**. 12 of 12 origins are a real model consequence. Nine follow from the soft index-0 reserve plus the hour-0 critical deficit served from the battery; three follow from J3 fuel consolidation with a small margin. No FORCED, TIED, numerical artefact, or harness inconsistency was found. Earlier index-0 counts were under-stated and are corrected here.
- **Is S's result affected:** no error. The result stands as the frozen research output. Its interpretation depends on the soft-reserve policy, which is a governance question.
- **New experiment required:** no, for ISSUE-5. A separate preregistration is needed only if the reserve policy is changed. Issue 3 still needs its own experiment.
- **NO CAMPAIGN RUN.**
