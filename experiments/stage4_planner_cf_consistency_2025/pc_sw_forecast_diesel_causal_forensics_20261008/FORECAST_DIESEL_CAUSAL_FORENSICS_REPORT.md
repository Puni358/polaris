# POLARIS — PC-SW Forecast→Diesel Causal Forensics & Candidate-F Value/Leakage Closure

**Date:** 2026-10-08
**Status:** READ-ONLY forensic research. No production code, PC-SW, model artifacts, or governed campaign outputs modified. No AGY execution. No model promotion.
**Hash verification:** `verify_protected_hashes(REPO)` — 0 mismatches (VERIFIED). `causal_nwp_physics.py` SHA-256 re-computed: `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` — **matches the governed value quoted in the task exactly (VERIFIED).**

---

## Critical anti-hallucination finding — stated first, because it reframes the whole task

**`F-Causal21` and `F-Causal35` do not exist anywhere in this repository.** An exhaustive case-insensitive search (`causal21`, `causal35`, `causal_21`, `causal_35`, and variants) across every `.md`, `.json`, and `.py` file in the repository returns **zero matches**. There is no persisted model, report, feature list, or metric under these names. Per the governing anti-hallucination instruction, this is marked **UNKNOWN/NOT FOUND**, and the "F → F-Causal degradation" premise in §3/§14.3 of the task **cannot be forensically reconstructed from repository evidence** — it is not analyzed as a real event, only addressed as a hypothesis that the available evidence does not support (see §3 below).

Separately, and more importantly: **the specific claim that "removing the LWP/IWP/LWP×cloud family eliminated much of F's advantage" because that family was leaked is directly contradicted by two independent, already-persisted forensic audits** (§2), both of which found LWP/IWP to be legitimately **causal** (NWP-forecast-derived), not leaked. This is addressed fully below, not glossed over.

---

## 1. Candidate F — reconstructed history (VERIFIED, from persisted artifacts)

**Exact identity, confirmed from `stage7/stage8/stage8_1_station_tuning_research/CANDIDATE_F_REPORT.md`:** Candidate F = the frozen Stage 8.1 champion's existing **37-feature** `HistGradientBoostingRegressor` (`max_depth=4, min_samples_leaf=30, l2_regularization=10.0, loss="absolute_error", random_state=42`) **plus one new additive feature**: `elevation_x_cloud_frac = solar_elevation × cloud_frac` — **38 features total**. This matches the task's description ("37 Stage8.1 features + elevation×cloud interaction") exactly.

**Training/validation/blind population (VERIFIED, hash-gated):** trained on **2024 EVEN** origins only; **2024 ODD** reported as validation; **2025** (whole year, no further split) used as the genuinely blind test set — the frozen Stage 8.1 methodology's own convention, not invented for Candidate F.

**Artifact hashes (re-confirmed in `CANDIDATE_F_PRE_TRAINING_AUDIT.md`, independently re-hashed in that audit, not merely trusted):**

| Artifact | SHA-256 |
|---|---|
| `phase2_candidateF_additive_feature.py` | `08fdcbe41a636ac0a65a427ceb494405812de8dc33296046bd9247927c52c0aa` |
| `candidateF_elevation_x_cloud.joblib` | `e8b89b2790286ea342b97594961d260bb5fa585cb8b89d7c3c536f30cc0a1c84` |
| Frozen Stage 8.1 model | `64ea4abada78a257f9ad053f1d869dddb983160490e06d1528954fd2205009ce` |

**Results (VERIFIED):** Blind-2025 MAE 35.9745 → 35.4948 W/m² (−0.4797), bootstrap CI excludes zero under both the original and a corrected (per-draw row-duplication) resampling method. EMS replay on 245 NORMAL origins: diesel +0.3555%, unmet −80,793.5 Wh (−4.6452%) — all independently re-derived from raw JSON in the pre-training audit, not merely re-stated.

**Feature timestamp availability (VERIFIED, source-traced):** `solar_elevation` — pure astronomy/geometry, known arbitrarily far in advance (`build_corrected_feature_matrix.py:122`). `cloud_frac` — derived from `fc_cloud_cover`, an NWP **forecast** field (the `fc_` prefix denotes forecast-origin data throughout this feature contract), not an observation. Their product introduces no new information channel beyond what each already-cleared input carries.

---

## 2. Per-feature causal/leakage classification (VERIFIED — the decisive evidence against the task's leakage premise)

| Feature/family | Source | Required obs. time | Forecast issuance time | Available at decision time? | Leakage? | Classification |
|---|---|---|---|---|---|---|
| `solar_elevation` | Astronomy/clearsky file | N/A (deterministic) | N/A — known in advance | YES | No | **F (causal)** |
| `cloud_frac` (= `fc_cloud_cover/100`) | MEPS 18Z NWP run, `D-1` | Forecast lead `+6h` to `+29h` | `D-1 18:00 UTC`, strictly before `t0` | YES | No | **F (causal)** |
| `elevation_x_cloud_frac` | Product of the two above | — | — | YES | No | **F (causal)** — inherits both inputs' clearance |
| **`lwp_latest`, `iwp_latest`** | MEPS `D-1 18Z` run, per-horizon liquid/ice water path computed independently for each `h∈[1,24]` from the MEPS profile (`stage6_6/run_stage6_6.py:211-262`) | Forecast lead `+6h` to `+29h`, same run as `cloud_frac` | `D-1 18:00 UTC` | YES | **No — independently audited twice (STAGE8_11A forensic audit: "Causality Status: Strictly causal", and the Candidate-F historical replay's own gate check #10: "Target Leakage Check: PASS")** | **F (causal), NOT leaked** |
| `lwp_x_cloud` | `lwp_latest × cloud_frac` | — | — | YES | No | **F (causal)** — product of two already-cleared causal forecast fields |
| `actual_SW_IN` | Observed ground truth | Realized | N/A | **NO** | N/A — **confirmed absent from the feature matrix entirely** (`CANDIDATE_F_PRE_TRAINING_AUDIT.md §2`: "does not appear anywhere in the feature-construction code path") | **Correctly excluded, not a feature** |
| Stage4/ensemble predictions, 700hPa wind, terrain, `ctx_*` context features | Part of the frozen 37-feature contract; `ctx_*` context window ends strictly at `t0-1h` (historical replay audit §3) | Prior to `t0` | Prior to `t0` | YES | No (per the historical-replay temporal-causality audit, "No future data enters any origin context or feature calculation") | **F (causal)** |

**No feature in Candidate F's 38-feature contract was found to be a leakage case (B/C/D in the task's taxonomy) by any persisted audit.** Every item is causal (**category F** in the task's own letter scheme) or correctly excluded (`actual_SW_IN`).

---

## 3. The F → "F-Causal" degradation — cannot be reconstructed; the premise is contradicted

Because no `F-Causal21`/`F-Causal35` artifact exists (see top), the specific mechanistic question ("why did F-Causal21 become worse, why did F-Causal35 also become worse") **cannot be answered — UNKNOWN, not estimated.** What the repository *does* show, directly contradicting the premise that removing LWP/IWP "eliminated much of F's advantage" due to leakage: (a) LWP/IWP are independently confirmed causal by two separate forensic audits, not leaked; (b) a **separate, already-closed research question** (`STAGE8_11A_FINAL_FORENSIC_AUDIT.md`) establishes that LWP/IWP are **already fully present** in the frozen Stage 8.1 37-feature contract that both the control and Candidate F are built on — meaning there is no "F-Causal" variant with LWP/IWP *removed* that would even be a meaningful ablation of Candidate F specifically, since Candidate F's only addition over the frozen control is the single `elevation_x_cloud_frac` term, not the LWP/IWP family. **The premise appears to conflate two distinct research threads** (Candidate F's single-feature addition, and the separate Stage 8.11 LWP/IWP novelty question, which was closed as `NOT_NOVEL` — redundant, not leaked) **that are not the same investigation.**

---

## 4. Is Candidate F "wasted"? (DIAGNOSTIC + DERIVED, from VERIFIED underlying evidence)

Given §2/§3 establish **no leakage was actually found**, the four-way "what remains useful" framing needs restating: Candidate F is not a leakage-invalidated model requiring salvage — it is a **small, clean, already-causal, already-validated improvement** (blind MAE −0.48 W/m², EMS replay unmet −4.65%) that was never shown to rely on unavailable information in the first place. Against the task's four candidate values:

1. **Performance reference/upper-bound:** Not applicable in the usual "leakage shows the ceiling" sense, since no leakage was found — but it is still a valid reference for "how much a single well-chosen causal interaction term can improve the frozen model."
2. **Feature attribution:** **Supported.** The `elevation×cloud` interaction captures real, previously-uncaptured signal (GBDT splits don't automatically discover multiplicative interactions between existing features) — this is a genuine, exploitable, already-causal finding, not merely diagnostic.
3. **Leakage diagnosis:** **Not supported as stated** — there is no leakage to diagnose in Candidate F itself; this value category does not apply here.
4. **Causal feature recovery:** **Not applicable** — nothing needs recovering, because nothing causal-but-unavailable was ever shown to drive F's result.

---

## 5. Causal equivalents search (per §5 of the task) — not required for Candidate F, addressed for completeness

Since §2 found no leaked feature family in Candidate F, the "search for a causal equivalent" exercise has no leaked signal to replace. The one family the task flags by name (LWP/IWP) is **already** the causal, forecast-derived quantity requested (per-horizon MEPS liquid/ice water path, not realized observation) — it does not need a causal substitute; it already is one, and is already in both the control and Candidate F.

---

## 6–9. PC-SW forecast → diesel linkage (VERIFIED/DIAGNOSTIC, reused from the two immediately preceding tasks — not re-derived at new scale, per the explicit instruction not to conflate F with PC-SW)

**PC-SW uses `causal_nwp_physics.py`, a completely different forecaster from Stage 8.1/Candidate F's GBDT pipeline. F's ~28% nMAE figure is Stage-8.1-specific and is explicitly NOT used here as a PC-SW number** (per task §10).

Reused, population-scale, already-established findings for PC-SW specifically (EBR population forensics task, two tasks prior):
- **Wind forecast error is exactly 0.0 Wh for every one of the 123 origins** (deterministic baseline-engine formula) — VERIFIED.
- **Solar forecast error is mildly *optimistic* on average** (realized < forecast by ~10,771 Wh over a 6h window, population mean) — the **opposite** sign from an early unverified pessimism hypothesis — VERIFIED.
- **No statistically significant difference in forecast error between the "EBR-off-beneficial" (77-origin) and "EBR-off-harmful" (44-origin) populations** (Mann-Whitney p=0.78–0.92) — VERIFIED, directly answering §6/§7's central question: **forecast error does not systematically explain which origins experience unnecessary-looking early diesel banking.**
- **Classification against the task's A–F taxonomy (§7):** given wind error ≡ 0 and solar error's population-wide near-null correlation with outcome (established two tasks prior), the dominant population pattern is closest to **D (forecast approximately correct, optimizer still banks diesel)** — not B or C — consistent with the EBR mechanism (closed branch) being structurally, not forecast-error, driven. **DERIVED**, not individually classified per the 526 diesel+charging episodes (that per-episode classification was not performed, at this or the prior pass — marked UNKNOWN at that granularity).

**Rolling-horizon amplification (§8/§9):** this exact question was already answered empirically, not hypothetically, by the T1 campaign (reused from the immediately preceding task): a temporal reallocation that was provably invariant at the solve level (`J1,J_NC,J2,J3` bit-identical) still produced **+241.6 L** of realized fuel increase and an S2 safety failure once the rolling MPC reacted to the resulting lower battery reserve against diverging realized solar/wind in subsequent resolves. **This is direct, already-persisted evidence that the rolling-horizon architecture amplifies small plan-level differences into larger realized-trajectory differences** — the mechanism requested in §8/§9, already demonstrated, not re-run here.

---

## 10. F vs. PC-SW — explicitly not conflated

Confirmed and preserved throughout this report: Candidate F's blind MAE/EMS figures belong to the Stage 8.1 GBDT pipeline evaluated on its own 2024/2025 holdout; PC-SW's forecast error figures (wind=0, solar mildly optimistic) belong to `causal_nwp_physics.py` evaluated on the 2025 PC-SW campaign population. **Neither number is substituted for the other anywhere in this report.**

---

## 11. Legitimate forecast lever search

**None found.** For PC-SW: no decision-time forecast feature was shown (this or the prior task) to separate the populations where early banking turns out beneficial vs. harmful — the forecast error itself doesn't explain the split (§6-9). For Candidate F: it is already causal and already a small validated improvement at the Stage 8.1 layer — but that is a **different system** from PC-SW's forecaster, and no repository evidence shows a path to port Candidate F's specific `elevation×cloud` interaction into `causal_nwp_physics.py`'s different architecture; doing so would be a new, untested research question, not something this forensic pass can respecify without inventing a design.

---

## 12. Required F conclusion

**B — Partially.** Candidate F is valuable, but not for the reason the task's framing assumed: it is **not** a leakage-invalidated reference requiring causal-signal recovery (§2/§3 found no leakage to recover from) — it is a **small, already-causal, already-validated, low-risk improvement to the frozen Stage 8.1 model** (feature attribution value, §4.2, fully supported) that has **not been shown to be deployable to PC-SW** specifically, because PC-SW runs on an entirely different, unrelated forecaster (§10). Its performance figures must not be read onto PC-SW (§10, preserved). **No part of this analysis supports calling F "wasted" in the sense the leakage-degradation premise implied — that premise does not match repository evidence.**

---

## 14. Final questions

1. **What made Candidate F appear better?** A single additive `elevation×cloud` interaction term capturing real, previously-unmodeled nonlinear signal — VERIFIED, not a leakage artifact.
2. **Which F features are causal vs. leaked?** All 38 are causal (§2); none were found to be leaked.
3. **Why did F-Causal21/35 become worse?** **UNKNOWN — these artifacts do not exist in the repository; cannot be forensically reconstructed.**
4. **What scientifically useful information remains in F?** Feature attribution (the `elevation×cloud` interaction genuinely helps) — VERIFIED; not leakage diagnosis, since none was found.
5. **Causal equivalent for the useful F signal?** Not needed — the signal (elevation, cloud forecast) is already fully causal as used.
6. **Does PC-SW forecast error materially cause early diesel banking?** **No, not systematically** — wind error is zero, solar error shows no significant difference between the beneficial/harmful origin populations (reused, VERIFIED finding from the EBR population task).
7. **Fuel associated with forecast-induced diesel positioning?** Not separable from the already-attributed EBR-structural mechanism (§6-9); no new fuel figure computed in this pass beyond what was already reported (724.5549 L aggregate, reused).
8. **Diesel banking even when forecast is approximately correct?** The dominant population pattern (§6-9) — consistent with D in the task's taxonomy, not B/C.
9. **Does rolling-horizon amplify forecast errors into diesel-trajectory changes?** **Yes — already empirically demonstrated by the T1 campaign** (reused, not re-run).
10. **Non-arbitrary causal forecasting lever worth testing?** **No**, for PC-SW specifically (§11).
11. N/A.
12. **Next best research direction:** the Candidate F `elevation×cloud` interaction is a legitimate, independently-validated Stage 8.1 improvement that remains unexplored as a *design pattern* (not a direct transplant) for `causal_nwp_physics.py` — whether an analogous interaction term exists and would help PC-SW's own forecaster is a genuinely open, untested question, distinct from anything resolved in this report.

"NO POLICY EXPERIMENT WAS EXECUTED."
