# POLARIS — Post-Stage-4 Efficiency Forensic Analysis and Next-Research Design

**Date (UTC):** 2026-10-06
**Status:** RESEARCH / DESIGN ONLY. No implementation, no campaign, no parameter sweep, no production or Stage 4 artifact modified.
**Scope:** explain where SW-L's diesel-saving efficiency loss relative to SW comes from, and choose the next experiment.

**Labels used throughout:** `[VERIFIED]` recomputed from frozen artifacts; `[INFERRED]` a reasoned reading of verified facts; `[HYPOTHESIS]` a proposed mechanism or parameter, not a candidate; `[UNKNOWN]` not established by available evidence.

---

## 1. Executive Conclusion

**CURRENT WINNER: S — 24.02% diesel reduction among safety-qualified candidates.**
**SAFETY-LEADING ALTERNATIVE: SW-L — 14.66% diesel reduction.**
**SW: 36.50% diesel reduction, SAFETY FAILURE (proportional −0.356194 pp).**
**40% TARGET: NOT ACHIEVED.**

> **Correction to the brief:** the brief gives S as 23.04%. The frozen Stage 4 freeze, the campaign summary, and a recomputation from the frozen totals all give **24.02%** (1 − 4,648.3272 / 6,117.9691 = 0.24024). This document uses 24.02%. The 23.04% figure appears to be a transcription error and should be corrected in the brief. `[VERIFIED]`

**Strongest forensic finding.** The entire efficiency loss (+1,336.3 L, equal to 21.84 pp of Control B) is a low-sun effect. Its largest single component is the **origin-hour-0 (00:00 UTC) diesel commitment**: at hour 0, SOC is 50% in every arm, yet SW-L commits diesel in 100% of origins, SW in 32%, and S in 76%. Hour 0 alone accounts for +1,019.6 L, about 76% of the gap. This is a planning-policy effect, not a state effect. `[VERIFIED]`

**Strongest remaining uncertainty.** Whether that hour-0 full-window reserve is *necessary* for the proportional safety gain, or whether part of it is conservatism. Closed-loop telemetry cannot separate these, because each arm's state diverges after hour 0. `[UNKNOWN]`

**Top next direction.** A parameter-free, open-loop **hour-0 attribution replay** (diagnostic, not a candidate): from an identical state, vary only the origin-start reserve target and measure the resulting critical unmet and diesel over the first window. It answers the biggest open question with the smallest experiment. Preregistrable as a diagnostic; no production change required. Section 9.

**Can a successor plausibly beat S?** Not yet established. SW-L already gives up 9.36 pp versus S. Any next candidate must recover most of that while keeping proportional reliability ≥ Control B. The diagnostic in Section 9 is the step that tells us whether that is possible without losing the safety gain.

---

## 2. Frozen Stage 4 Recap

Authority: `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` (SHA-256 `e73558cf…21cd7`), `.json` (`6b0bb6f7…b87`), `_MANIFEST.json` (`abb60913…489`). All three hashes were verified against the files on disk before this analysis. Stage 4 is closed; its artifacts are treated as immutable.

Control B re-executed on the 2025 holdout (123 origins, 2,952 hours, 0 failures). `[VERIFIED]`

| Arm | Fuel (L) | Saving vs B | Crit-first rel. | ΔR_CF (pp) | Prop. rel. | ΔR_P (pp) | Min SOC | Floor hours | Safety |
|---|---|---|---|---|---|---|---|---|---|
| Control B | 6,117.9691 | — | 93.669482% | — | 83.823383% | — | 54.99% | 0 | ref |
| S | 4,648.3272 | **24.02%** | 94.327168% | +0.657686 | 84.604885% | +0.781502 | 20.00% | 3 | PASS |
| SW | 3,885.0225 | 36.50% | 94.090514% | +0.421032 | 83.467189% | **−0.356194** | 20.00% | 21 | **FAIL** |
| S-L | 5,334.1331 | 12.81% | 94.455173% | +0.785691 | 85.150455% | +1.327072 | 20.00% | 11 | PASS |
| SW-L | 5,221.3152 | 14.66% | 94.484413% | +0.814931 | 85.264223% | +1.440840 | 20.00% | 16 | PASS |

Factorial (frozen): C1 = SW − S = −1.1377 pp [−1.5910, −0.7184]; C2 = SW-L − SW = +1.7970 pp; C3 = S-L − S = +0.5456 pp; **C4 = +1.2515 pp [+0.8683, +1.6546]**. `[VERIFIED]`

**Observation not flagged in the freeze:** every candidate arm (S, SW, S-L, SW-L) reaches exactly 20.00% SOC, which is the floor. The "zero below 20%" gate passes, but the floor is binding in all four. Control B never touches it (min 54.99%). `[VERIFIED]` This is a safety-margin fact, not a violation.

---

## 3. SW vs SW-L Efficiency-Loss Decomposition

### 3.1 Fuel model (fitted from telemetry)

Least-squares fit over all 14,760 arm-hours: **fuel ≈ 5.0 L × runtime-hours + 0.25 L × diesel-kWh**, RMSE 0.033 L. The per-start coefficient fitted to ~0, so the 2.0 L start cost in the design text does **not appear in the recorded fuel column** `[VERIFIED]`. Whether the optimizer's objective charges starts is `[UNKNOWN]` from these artifacts.

### 3.2 Gap components

Total gap: SW-L − SW = **+1,336.29 L** (21.84 pp of Control B). `[VERIFIED]`

| Component | SW | SW-L | Δ | Fuel effect |
|---|---|---|---|---|
| Diesel runtime (h) | 256 | 372 | +116 | +580.0 L (43%) |
| Diesel energy (kWh) | 10,420.1 | 13,445.3 | +3,025.2 | +756.3 L (57%) |
| Diesel starts | 161 | 267 | +106 | not in fuel column |

### 3.3 By low-sun state (L_k = 1[e < 15°], frozen convention)

| Subset | Hours | Δfuel (L) | Δdiesel-on h | Δunmet (kWh) |
|---|---|---|---|---|
| Low-sun (L=1) | 1,345 | **+1,939.8** | +156 | −903.4 |
| Non-low-sun (L=0) | 1,607 | **−603.5** | −40 | −13.5 |

`[VERIFIED]`. Protection costs fuel in low-sun hours and **saves** fuel in daylight. The daylight saving is path-driven (the arms diverge in state), not an identity violation: at L=0 the per-hour equation makes SW-L and SW identical for the same window, and the window-level reserve at L=0 differs only because the 6-hour forward window can contain low-sun hours (Section 5.2).

### 3.4 By elevation band

| Band | Δfuel (L) | Δdiesel-on h |
|---|---|---|
| e < 0 (night) | +964.7 | +74 |
| 0 ≤ e < 15 | +975.1 | +82 |
| 15 ≤ e < 30 | −337.2 | −21 |
| e ≥ 30 | −266.3 | −19 |

`[VERIFIED]`. The +1,940 L of low-sun cost is split evenly between "below horizon" and "0–15°", i.e., the protection acts on the entire low-sun regime, not only deep night.

### 3.5 By hour of day (UTC)

| Hour (UTC) | Δfuel (L) | Diesel-on SW → SW-L | Reserve SW → SW-L (kWh) | Note |
|---|---|---|---|---|
| **00** | **+1,019.6** | 39 → 123 | 17.7 → 71.5 (mean) | origin-start commitment |
| 01 | +281.5 | 24 → 41 | — | |
| 02 | +40.8 | 0 → 4 | — | |
| 06–13 (day) | −652.4 (sum) | — | low at both | daylight saving |
| 19–20 | +439.5 | 44 → 74 | | evening commitment |

`[VERIFIED]`. Hours 00–01 UTC carry +1,301 L (97% of the gap). Hour 0 is the origin start; it is the same hour in every origin.

---

## 4. Hour and Origin Findings

### 4.1 Hour 0 (origin start) — the dominant contributor `[VERIFIED]`

- Initial SOC is 50.00% in all arms at hour 0 (`soc_before`), so the **state is identical**.
- Diesel-on share at hour 0: **Control 100%, S-L 100%, SW-L 100%, S 76%, SW 32%**.
- Reserve at hour 0 (mean kWh): Control 75.7, S-L 73.1, SW-L 71.5, S 64.2, **SW 17.7**.
- Hour 0 accounts for +1,019.6 L (SW-L − SW) and +309.4 L (SW-L − S).

Interpretation `[INFERRED]`: SW's unprotected wind credit drops the origin-start reserve to ~18 kWh, so SW often does not commit diesel at 00 UTC. SW-L restores the full governed reserve at hour 0 (because the 6-hour window from 00 UTC contains low-sun hours), so it commits diesel every time. The safety gain of SW-L appears to come largely from this origin-start commitment, and the cost is also largely here.

### 4.2 Origin distribution — diffuse, not outlier-driven `[VERIFIED]`

- 99 of 123 origins have ΔFuel > 0; 24 have < 0.
- Per-origin ΔFuel quantiles (L): p10 −3.4, p25 +2.7, p50 +10.4, p75 +17.9, p90 +28.7.
- Top 15 origins: 36% of total; top origin +44.7 L.
- Origins 1–50 carry 35% of the gap; origins 51–123 carry 65%.

So the loss is a systematic per-origin effect, not a handful of bad days. This argues against "a few extreme nights" as the explanation and against any fix that targets only outliers.

### 4.3 Routing — no router-mode explanation `[VERIFIED]`

SW-L − SW by route and low-sun state: EMERGENCY/L=1 +1,613 L; NORMAL/L=1 +327 L; EMERGENCY/L=0 −472 L; NORMAL/L=0 −131 L. The cost sits in both router modes, in the low-sun hours, so router mode is not the discriminating mechanism.

### 4.4 Battery banking `[VERIFIED for counts; INFERRED for interpretation]`

- Battery charge: SW 16,647.5 kWh → SW-L 17,723.3 kWh (+1,075.8).
- Battery discharge: SW 10,420.9 → SW-L 10,002.8 (−418.1).
- Diesel-to-battery proxy (min of diesel and charge power per hour): SW 7,835.6 → SW-L 9,241.5 kWh (+1,405.9); diesel-to-load: 2,584.5 → 4,203.7 (+1,619.2).

The extra diesel is split roughly evenly between load and battery banking. Banking means diesel generated at night is stored and used later, so part of the cost is round-trip loss, not extra load served. The round-trip loss is `[UNKNOWN]` from these artifacts.

### 4.5 SOC floor — binding in both protected and unprotected SW

Floor hours: S 3, S-L 11, SW 21, SW-L 16. SW's floor hours are low-sun (14 of 21); SW-L's are all daylight (16 of 16). `[VERIFIED]` SW-L's daytime floor touches are a new feature of protection, not of wind credit, and they are not a safety violation (SOC never < 20.00%).

### 4.6 Terminal reserve — no differential effect at hour 23 `[VERIFIED, with an open item]`

Hour-23 reserve is 75.65 kWh for Control, S-L, and SW-L, and 48–76 kWh for S and 17–42 kWh for SW. This differs from the written terminal rule (§5.2 of the preregistration would give max(window, 100 kWh) = 100 kWh at hour 23). The recorded column does not show the 100 kWh floor. Recorded hour-23 values match a full 6-hour sum, not the truncated window the design describes. This is an **open item** `[UNKNOWN]` (Section 10). It affects only the final hour and does not explain the SW-L − SW gap, which is concentrated at hour 0.

---

## 5. Mechanism Evidence

### 5.1 Reserve magnitude by low-sun state (mean kWh) `[VERIFIED]`

| Arm | L = 1 | L = 0 |
|---|---|---|
| Control | 75.7 | 75.7 |
| S | 61.4 | 44.4 |
| S-L | 66.9 | 45.1 |
| SW | 24.3 | 12.1 |
| SW-L | 59.2 | 24.1 |

At low sun, **SW-L and S hold almost the same reserve (59.2 vs 61.4 kWh)**, yet SW-L runs 60 more diesel-on hours in those hours. So reserve magnitude at low sun alone does not explain the S vs SW-L difference (Section 6.2).

### 5.2 The forward-window reach of the low-sun flag `[VERIFIED for S/S-L; INFERRED for SW/SW-L]`

The reserve at hour t sums over k = t…t+5. A low-sun hour anywhere in that window removes renewable credit for its k, so protection leaks into daylight hours just before a low-sun period. For S and S-L, the recorded reserve matches the frozen equation exactly at hours 0–17 (max error 0 Wh), so the window mechanism is verified for solar credit.

The SW arms do not reconcile exactly with a reconstruction from the recorded forecast columns (max error 34.2 kWh) `[UNKNOWN]`; see Section 10. The directional mechanism (protection raising reserve in the window) still holds, because it is observable directly in the recorded SW-L and SW reserves.

### 5.3 Wind credit, closed-loop and state-dependent `[INFERRED]`

Wind credit in SW lowers the origin-start reserve to ~18 kWh (hour 0). Without protection, SW then declines diesel at 00 UTC in 68% of origins. This is the direct mechanism behind SW's safety failure in proportional reliability: SW has fewer diesel-on night hours (C1 = −1.14 pp).

---

## 6. Answers to the Forensic Questions

### 6.1 Question B — causal attribution of the 21.84 pp loss

| Candidate cause (brief list) | Verdict | Evidence |
|---|---|---|
| 1. Excessive low-sun protection duration | **Partly** `[INFERRED]` | Protection covers the whole low-sun regime (+1,940 L); the forward window extends it into daylight. But daylight with protection *saves* 604 L, so duration alone does not explain the cost. |
| 2. Excessive reserve magnitude | **Not the main driver** `[VERIFIED]` | At low sun, SW-L reserve (59 kWh) ≈ S (61 kWh), yet diesel differs. |
| 3. Conservative renewable credit | **Yes, at hour 0** `[INFERRED]` | SW's wind credit keeps hour-0 reserve at 18 kWh. Protection removes that credit at low sun, restoring the full commitment. |
| 4. Terminal reserve interaction | **No evidence** `[VERIFIED]` | No differential effect at hour 23; open item on the terminal rule (Section 10). |
| 5. Diesel commitment timing | **Yes, dominant** `[VERIFIED]` | Hours 00–01 UTC: 97% of the gap. Hour 0 alone: 76%. |
| 6. Battery banking behaviour | **Contributor** `[INFERRED]` | ~1.4 MWh more diesel energy goes to banking; round-trip loss `[UNKNOWN]`. |
| 7. Wind-credit interaction | **Yes** `[VERIFIED]` | C4 = +1.25 pp; the interaction is significant (Stage 4 freeze). |
| 8. Other GAP19 structural mechanism | **Not established** `[UNKNOWN]` | Not investigated beyond the telemetry; no solver internals were examined. |
| 9. Combination | **Most likely** `[INFERRED]` | Hour-0 commitment (5, 3) plus banking (6), with the forward window (1) as the trigger. |

**Answer:** the loss is primarily a **diesel commitment-timing effect at the origin start** (mechanisms 5 and 3), amplified by banking (6) and triggered by the forward-window reach of the low-sun flag (1). Reserve magnitude is not the main cause (2).

### 6.2 Question E — why S keeps 24.02% and SW-L keeps 14.66%

SW-L − S = +573.0 L (S uses less diesel than SW-L). `[VERIFIED]`

| Component | SW-L − S |
|---|---|
| Low-sun hours (L=1) | +778.4 L (diesel-on 263 → 324 h) |
| Daylight (L=0) | −205.4 L |
| Hour 0 | +309.4 L (S 76% → SW-L 100%) |
| Evening 19–21 UTC | +420 L |
| Runtime | +44 h |
| Diesel energy | +1,428 kWh |

Key comparisons `[VERIFIED]`:
- **Reserve at low sun is nearly identical** (S 61.4 vs SW-L 59.2 kWh), yet SW-L runs more diesel at night.
- **Reserve in daylight differs**: S 44.4 vs SW-L 24.1 kWh (06–13 UTC: S 33–43, SW-L 8–22 kWh). SW-L holds less daytime reserve and saves daylight diesel.
- **Dusk SOC does not explain the difference.** Mean SOC is within 1.3 pp at 18 UTC (S 79.1%, SW-L 77.7%) and SW-L is *higher* than S at 20–21 UTC (76.7 vs 76.3, 77.8 vs 74.5). A state-at-dusk explanation is therefore not supported `[VERIFIED]`. The cause of S's lower night diesel at equal reserve is `[UNKNOWN]`.

So S keeps more of the saving because it reaches a similar low-sun reserve **with less night diesel-on time** (263 vs 324 h at low sun). This is the key open question for a successor. S's safety does not depend on protection at all, so the mechanism that lets S run less night diesel at equal reserve is the thing to isolate.

### 6.3 Question D — is SW-L's extra diesel necessary?

- SW-L buys **+615 kWh** of proportional critical service over SW (critical-prop unmet 5,661 → 5,046 kWh), and **+135 kWh** critical-first.
- That costs **+1,336 L**, i.e. **≈2.17 L per kWh** of proportional critical recovered. The marginal diesel energy cost is 0.25 L/kWh, so the marginal diesel energy for 615 kWh would be ~154 L. Most of the cost is therefore not energy served to load.
- S, by comparison, passes the proportional gate with protection off, at 24.02% saving.

Verdict `[INFERRED]`: a substantial fraction of SW-L's diesel is **not** directly serving critical load. It is origin-start commitment and banking. Whether it is *necessary* for the proportional gate is `[UNKNOWN]`, because the telemetry is closed-loop and cannot be replayed from the same state under a different commitment. This is the question the top recommendation answers (Section 9).

---

## 7. Proven vs Inferred vs Unknown

**[VERIFIED]**
- Stage 4 freeze hashes and all headline numbers (Section 2). S saving is 24.02%, not 23.04%.
- Fuel ≈ 5 L/h runtime + 0.25 L/kWh (RMSE 0.033 L); starts not in recorded fuel.
- Gap = +1,336.3 L: runtime +580 L, energy +756 L.
- Low-sun (L=1) +1,939.8 L; daylight −603.5 L.
- Hour 0 +1,019.6 L; diesel-on at hour 0 = 100% (SW-L), 76% (S), 32% (SW), with identical 50% initial SOC.
- Hours 00–01 UTC carry 97% of the gap. Origins are diffuse (99 positive, 24 negative).
- Reserve at low sun: S 61.4, SW-L 59.2 kWh (≈ equal). Reserve at hour 0: SW 17.7, SW-L 71.5 kWh.
- Router mode is not discriminating (cost in both modes).
- All four candidate arms reach the 20% SOC floor exactly. Control never does.
- Reserve formula reproduces exactly for Control, S, S-L at hours 0–17.

**[INFERRED]**
- The origin-start commitment (hour 0) is the dominant mechanism, amplified by battery banking and triggered by the forward-window reach of the low-sun flag.
- The SW safety failure is caused by unprotected wind credit lowering the origin-start reserve to ~18 kWh.
- S keeps more saving because it runs fewer night diesel-on hours at an equal low-sun reserve. The cause is not dusk SOC (which does not explain it) and is not yet identified.
- Part of SW-L's extra diesel is conservatism at the origin start rather than critical-load need.

**[HYPOTHESIS]** (not candidates; no parameter is proposed for tuning)
- H-A: the origin-start full-window reserve (hour 0) is more than is needed for the proportional gate. Testable only by a same-state replay (Section 9).
- H-B: protection applied as a window-level rule, not a per-hour replacement, would remove the forward-window reach. Mechanism only.
- H-C: a governed minimum reserve at low sun (design mechanism F) may recover part of the gap. Requires a new numerical value; high tuning risk.

**[UNKNOWN]**
- Whether the hour-0 reserve is *necessary* for the proportional gate (closed-loop telemetry cannot identify this).
- The wind-term vector that the SW plan actually used: the recorded forecast columns do not reproduce the SW reserve (max error 34.2 kWh), though the code path reads `bundle.wind_generation.point` (not realized wind).
- The terminal rule at hour 23 (recorded 75.65 kWh vs written max(window, 100 kWh)).
- Whether the optimizer charges a start cost (the 2.0 L design value does not appear in recorded fuel).
- Battery round-trip losses for the banked diesel energy.
- Any GAP19 solver-internal mechanism.

---

## 8. Ranked Hypotheses and Next Research Directions

Three directions at most. Ranked by how much they resolve the largest remaining uncertainty for the least cost.

### Rank 1 (recommended): Origin-start attribution replay (diagnostic)

- **Mechanism addressed:** the hour-0 full-window commitment (Section 4.1), the largest single contributor.
- **Expected efficiency benefit:** unknown until measured. The hour-0 component alone is 1,020 L, so the upper bound on recoverable diesel is large. **HYPOTHESIS ONLY**, not a candidate.
- **Safety risk:** none, because this is a diagnostic. The risk would appear only if a successor candidate is built on its result.
- **Evidence supporting it:** hour 0 is 76% of the gap and carries identical initial SOC (Section 4.1).
- **What must be measured:** for each of the 123 origins, from the identical hour-0 state, the critical unmet and diesel over the first 6 hours and the first 24 hours, under reserve targets {E_SW(0), E_SWL(0), E_S(0), E_B(0)}, each replayed open-loop against the same realized trajectory. No re-optimization after hour 0.
- **Discriminating experiment:** if E_SWL(0) and E_S(0) give the same critical unmet over hours 0–5, the protection at hour 0 is not necessary for safety, and the saving is recoverable. If E_SWL(0) gives materially lower critical unmet than E_S(0), the commitment is necessary, and the loss is the price of safety.
- **Preregistrable cleanly?** Yes, as a diagnostic with no gate and no parameter selection. The four reserve targets are existing, frozen quantities, not new values.
- **Production changes?** None. Implementable in the existing research adapter layer (`stage4_low_sun_adapter.py`-style, research-only).
- **Expected difficulty:** moderate. One open-loop replay per origin per target, with the existing optimizer and extractor.

### Rank 2: Window-level protection rule (mechanism H-B)

- **Mechanism addressed:** the forward-window reach of the low-sun flag into daylight (Section 5.2).
- **Expected efficiency benefit:** small. Daylight protection already saves 604 L in SW-L, so the reach costs little fuel. **HYPOTHESIS ONLY.**
- **Safety risk:** moderate. It could reopen the night loss if the window no longer protects the first low-sun hour.
- **Evidence:** daylight reserve is 24 kWh (SW-L) vs 12 kWh (SW) (Section 5.1).
- **Measurement needed:** reserve at L=0 hours that precede low-sun hours, versus hours that do not.
- **Discriminating experiment:** a Rank-1 result must come first. Without it, this direction cannot be ranked against H-A.
- **Preregistrable?** Yes, but only after Rank 1 identifies whether reserve reach matters.
- **Production changes?** None.
- **Expected difficulty:** moderate.

### Rank 3: Governed minimum-reserve hybrid (design mechanism F)

- **Mechanism addressed:** the commitment at low sun as a governed floor rather than a per-hour replacement.
- **Expected efficiency benefit:** unknown; depends entirely on the floor value. **HYPOTHESIS ONLY.**
- **Safety risk:** high if the floor is set too low, because it can reintroduce SW's night loss.
- **Evidence:** the design (§4) lists F as available once G is informative. G is now informative (C4 = +1.25 pp).
- **Measurement needed:** Rank 1 must show what minimum reserve is needed at the origin start.
- **Why third:** it introduces a new numerical value. Choosing that value from the holdout would be exactly the tuning the governance forbids. The value would have to be derived from Rank 1 on discovery data, not from 2025 outcomes.
- **Preregistrable?** Only after Rank 1 fixes the value from a non-holdout source.
- **Production changes?** None.
- **Expected difficulty:** high.

---

## 9. Top Recommended Next Experiment

**Origin-start attribution replay (Rank 1).**

**Question answered:** is the hour-0 full-window commitment necessary for proportional safety, or is part of it recoverable conservatism?

**Design (diagnostic, no parameter search):**
1. Use the frozen 2025 population (123 origins) and the frozen realized and forecast inputs.
2. For each origin, take the identical hour-0 state (SOC 50%).
3. Replay open-loop for 24 hours under each reserve target at hour 0 only, with no re-optimization after hour 0:
   - E_SW(0) (SW's origin-start reserve, ~18 kWh)
   - E_SWL(0) (SW-L's origin-start reserve, ~72 kWh)
   - E_S(0) (S's origin-start reserve, ~64 kWh)
   - E_B(0) (Control reserve, ~76 kWh)
4. Record critical-first and proportional unmet over hours 0–5 and 0–23, plus diesel.
5. Paired by origin; BCa 95% CI; seed 42; 10,000 resamples. This matches the frozen statistical convention.

**Decision rule (pre-declared, read as a diagnostic, not a gate):**
- If E_SWL(0) and E_S(0) produce statistically indistinguishable proportional unmet over hours 0–5, the origin-start commitment at SW-L level is not required for that window, and the recoverable diesel is the hour-0 component.
- If E_SWL(0) yields materially less proportional unmet than E_S(0) (CI excluding zero), the commitment is necessary, and the loss is the price of safety.

**Why this is the smallest defensible experiment:** it uses only existing, frozen reserve targets; it changes one decision (hour 0); it needs no new numerical value; and it answers the question that determines whether any successor candidate can plausibly beat S.

---

## 10. Explicit Reasons Other Directions Are Lower Priority

- **Angle threshold change (e.g., 12° instead of 15°):** forbidden as tuning. The forensic evidence does not show the 15° boundary is unnecessarily conservative. Low-sun cost is spread across both the below-horizon and 0–15° bands (Section 3.4), so the boundary is not the discriminating factor. `[VERIFIED]`
- **Wind coefficient or haircut:** forbidden as arbitrary tuning. The wind term's interaction is already captured by C4, and the wind vector used in the plan is itself unreconciled (Section 10), so a wind change would be made on an unknown input.
- **SOC threshold, diesel threshold, terminal target:** no evidence links these to the gap. The SOC floor is binding in all candidates (Section 2) but is not the discriminating factor, and the terminal reserve shows no differential effect (Section 4.6).
- **S-based direction:** S already passes all gates without protection. Any successor should build on S's structure rather than on SW-L's, because S is the current winner.

---

## 11. Proposed Preregistration Structure (for Rank 1)

1. Identity: experiment ID, design version, date, and reference to this document.
2. Hypothesis: H-A (origin-start commitment is not necessary for proportional safety) vs its negation.
3. Population: the frozen 2025 123-origin holdout, unchanged. No new population.
4. Arms: four open-loop replays at hour 0 with frozen reserve targets {E_SW(0), E_SWL(0), E_S(0), E_B(0)}. No new arm definitions.
5. Decision rule: as Section 9.
6. Outcomes: critical-first and proportional unmet (hours 0–5 and 0–23); diesel; SOC minimum.
7. Statistics: paired by origin, Wilcoxon (two-sided) and BCa 95% CI, 10,000 resamples, seed 42. Holm across the two primary comparisons.
8. Leakage controls: the 2025 holdout has already been used (Stage 4). **This is a second look at the same population, so this preregistration must state it as a diagnostic on the confirmatory population, not a confirmatory test, and must not be used to select a candidate.** If a candidate is later built from it, the candidate needs a new holdout (2026 prospective or a further split).
9. Production boundary: unchanged production files; research-only replay code; all frozen hashes guarded at startup, as in the Stage 4 preregistration.

**Important:** because the 2025 holdout has been used by Stage 4, a diagnostic replay on the same origins is a **second look**. This is acceptable only as mechanism attribution, not as confirmation. Any successor candidate must be tested on a fresh holdout.

---

## 12. Safety Gates (unchanged, for any successor candidate)

1. Critical-first reliability ≥ Control B (aggregate, 123 origins).
2. Proportional critical reliability ≥ Control B (aggregate, 123 origins).
3. Zero realized SOC below 20.00% in any hour.

Safety precedes efficiency. A candidate failing any gate is rejected regardless of fuel.

---

## 13. Efficiency Gates (unchanged, for any successor candidate)

- Diesel gate: Wilcoxon two-sided with Holm adjustment, and BCa 95% lower bound > 0 L/origin.
- Benchmark to beat: **S = 24.02% diesel reduction**. A candidate that cannot plausibly beat S while keeping safety should not be the next main candidate.
- 40% target: desirable, not a gate.

---

## 14. Required Telemetry (for any successor)

Everything in the current Stage 4 hourly telemetry, plus:
- Reserve-target vector per hour, with the per-k contributions (to separate the window-reach effect from the hour-0 effect).
- The wind vector actually used by each arm's plan (not only the forecast column), so the SW reserve can be reconciled.
- The terminal-hour reserve computation (to reconcile the 100 kWh rule).
- Optimizer objective components, including whether starts are charged.
- Battery round-trip accounting (charge losses and discharge losses separately).
- Origin-start (hour-0) state and decision, logged for every origin.

---

## 15. Leakage Controls

- Planning uses forecast quantities only (`bundle.*.point`), the timestamp-based ephemeris, and state. Code-level check: the plan's wind source is `bundle.wind_generation.point` (runner line 107, adapter line 420). Realized wind enters only the executor (runner line 229). `[VERIFIED by code reading]`. The numerical identity of the plan's wind vector is `[UNKNOWN]` (Section 10).
- The 2025 holdout has been used by Stage 4 and is therefore not a fresh holdout for any successor. The Rank-1 replay must be labelled a diagnostic on that population.
- No parameter is selected from 2025 outcomes. The 15° boundary, the 100 kWh terminal, the 0.055 W τ, η, and the SOC bounds are frozen.
- All arms use identical machinery.

---

## 16. Production-Boundary Requirements

- No production file modified. The S/SW preregistration, the numerical-boundary addendum, the Stage 4 freeze, and all Stage 4 artifacts are unchanged.
- Startup hash guards for GAP19, DispatchPlan, causal NWP, the S/SW adapter, the S/SW preregistration (MD and JSON), the numerical-boundary addendum (MD and JSON), and the Stage 4 freeze (MD, JSON, manifest).
- Any new code is research-only (replay layer on top of the existing adapter), and does not modify the optimizer, the forecast engine, or the extractor.

---

## 17. Open Items Requiring Resolution Before Any Implementation

1. **Wind-term reconciliation (SW, SW-L):** the recorded forecast-wind column does not reproduce the reserve (max 34.2 kWh). Confirm the exact wind vector used at each reoptimization from the runner logs. Until then, SW-arm reserve reconstructions are not exact, though the recorded reserves themselves are valid.
2. **Terminal rule (hour 23):** recorded hour-23 reserve (75.65 kWh for Control) does not show the 100 kWh floor in §5.2 of the preregistration. Confirm the implementation and the written rule agree, and record which is authoritative. This does not affect the Rank-1 result, which concerns hour 0.
3. **Start-cost in the objective:** determine whether the optimizer charges starts. The recorded fuel does not include the 2.0 L start value in the design.
4. **Brief correction:** S's diesel saving is **24.02%**, not 23.04%.

---

## 18. Status

**COMPLETE** (research and design only).

- CURRENT WINNER: **S — 24.02%** diesel reduction, safety-qualified.
- SAFETY-LEADING ALTERNATIVE: **SW-L — 14.66%**.
- SW: 36.50%, **SAFETY FAILURE**.
- 40% TARGET: **NOT ACHIEVED**.
- Stage 4: remains frozen and closed. No new candidate was implemented; no campaign was run; no parameter was tuned.
- New preregistration: **required** before the Rank-1 replay is run (Section 11).
