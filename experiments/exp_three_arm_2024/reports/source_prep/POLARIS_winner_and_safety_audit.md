# POLARIS: Current-Winner Diesel-Reduction Investigation and Safety Audit

_Read-only audit, 2026-10-11. Nothing was modified, trained, simulated or re-run on the device. Repo root: `~/01polaris (Copy)`. All paths below are relative to it. File timestamps are converted to UTC from on-disk modification times._

**What I read, and what I avoided.** Code, configs, manifests, governance records, the 2024 campaign artifacts, and the 240-origin non-blind replay artifacts (I checked their dates first; there are zero May–Aug 2025 rows). I read no per-origin or hourly file from the 123-origin 2025 campaign. I did read **aggregate** governance and result summaries for it (`PC_RESULT_SUMMARY.md` ×2, `RULE_D_GOVERNANCE_RECLASSIFICATION.md`, a few lines of `experiments/STAGE4_S_TO_PC_SW_MECHANISM_FORENSICS_HANDOFF_20261008.md`), because Phase 1 asks what the 14.95% refers to and those records are the only source. Disclosing it so you can judge.

---

## 1. Current winner

**There is no single "winning forecasting model". The 14.95% belongs to a controller arm, not a forecaster.**

| Layer | What the 14.95% pipeline actually uses | Evidence |
|---|---|---|
| Solar forecaster | `CausalNwpPhysicsForecastEngine`: `GHI = Ineichen clear-sky × (1 − MEPS cloud/100)`, night-zeroed, PV = min(51·GHI, 60 kW). Point only (lower = point = upper). No learned parameters. SHA-256 `14e72d8a…cdeb710` (matches the file on disk). | `system/forecasting/implementations/causal_nwp_physics.py:1-35`; hash pinned in `experiments/stage4_planner_cf_consistency_2025/run_rule_d_true_curtailment_recapture.py:64` and `pc_sw_true_curtailment_recapture_20261008/REPRODUCIBILITY_MANIFEST.json` |
| Wind / demand | Synthetic deterministic profiles: wind = max(0, 4500 + 5000·sin(hπ/6)), demand = max(10 kW, 15000 + 3000·cos(hπ/12)) | `planner_cf_campaign_runner.py:191-200` |
| Planner | `PlannerCFV1Optimizer` (Planner-CF v1.2, lexicographic MILP). Priority J1 critical > J_NC non-critical > J2 reserve > J3 fuel > J4 curtailment | `planner_cf_campaign_runner.py:40,98`; handoff table line 42 |
| Winning arm | **PC-SW**: the EBR reserve is credited with forecast solar + wind (`compute_variant_sw_ebr`) | `planner_cf_campaign_runner.py:63-77`; `CAMPAIGN_V12_615_20261006/PC_RESULT_SUMMARY.md` ("Winner: PC-SW") |
| +Rule D | Executor-level rule: if diesel is on while curtailing, cut diesel by the curtailed amount and re-realize | `run_rule_d_true_curtailment_recapture.py:1-20` |

- **Stage 8.1 corrected HGB is not the winner in this pipeline.** `system/forecasting/implementations/s81_corrected_solar.py` exists, but no diesel campaign instantiates it. Every `forecast_engine =` assignment in `experiments/` uses causal-NWP, local-baseline or perfect-foresight engines (`run_diesel_reduction_campaign.py:125-141`, `run_offline_optimizer_replay.py:410,421`). Its artifact sits under `stage7/stage8/stage8_1_corrected_2025/`. I couldn't verify whether that "2025" training touched the blind window; this needs checking before the model is ever used.
- **Candidate F** (`stage7/stage8/stage8_1_station_tuning_research/model_artifacts/candidateF_elevation_x_cloud.joblib`, SHA `e8b89b27…`) is a separate research model, also not wired in. See `candidate_F_future_data_findings.md` for its timing problems.
- **Forecast vs controller.** All of the documented saving comes from reserve-sizing arms and an executor rule with the forecaster held fixed. No artifact shows a better forecast producing a gated diesel saving.
- **Conflict to note.** Two `PC_RESULT_SUMMARY.md` files declare "Winner: PC-SW" with different numbers. The top-level one has control 10,382.31 L, PC-SW 13.66%, and three arms failing S1/S2. The `CAMPAIGN_V12_615_20261006/` one has control 10,196.97 L, PC-SW 14.39%, and all arms passing. The V12 one (newer, 10-06) is what the 14.95% builds on. The older file isn't marked superseded.

## 2. The 123-origin run(s)

**There are two different 123-origin populations, and they are not interchangeable.**

| | 2025 Planner-CF campaign (source of 14.39%/14.95%) | 2024 campaigns |
|---|---|---|
| Dates | **2025-05-01 → 2025-08-31, which is exactly the quarantined blind window** (hard-coded at `planner_cf_campaign_runner.py:180-188`; Rule D imports the same `origin_population`) | 2024-05-01 → 2024-08-31, 123 consecutive days, no gaps (verified from `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/per_origin_results.json`) |
| What it is | Closed-loop **evaluation** run (5 arms × 123 = 615 runs). No model training. | Closed-loop evaluation runs (`EXP-CAUSAL-NWP-…-2024`, `EXP-CANDIDATE-S-SW-…-2024`) |
| Independence | Rolling daily origins. Each origin is a fresh 24-h episode reset to 50% SoC and 100 L fuel, so episodes are independent in state. But adjacent days share weather regimes (autocorrelated), and the horizon tail of day d reads day d+1's forecast run (see §6.3). | Same structure |
| Safe to use? | **No.** Every arm, every reserve variant, Rule D and the reclassification were chosen after viewing results on it. It has been used for development, so it can no longer be a blind test. | Yes (not quarantined), but it is the same season one year earlier |
| Comparable with 14.95%? | It *is* the 14.95% population | Not directly: different year, different planner (GAP19, no J_NC), different control |

**Consequence:** the quarantined window's blind value is already spent by the Planner-CF campaign itself, independently of the two-file read incident. The two previous sessions only made it worse.

## 3. The 14.95% baseline: what it is

- **Calculation:** (PC-Control fuel − PC-SW+Rule-D fuel) / PC-Control fuel = (10,196.9712 − 8,672.6241) / 10,196.9712 = **14.95%**. PC-SW without Rule D: 8,729.2446 L, giving **14.39%**. Sources: `CAMPAIGN_V12_615_20261006/PC_RESULT_SUMMARY.md`; `RULE_D_GOVERNANCE_RECLASSIFICATION.md:35-36`.
- **Baseline ("control")** = PC-Control: same Planner-CF v1.2, same causal-NWP forecaster, governed EBR reserve with **no renewable credit**, 123 blind-window origins.
- **Status:** Rule D was originally recorded **"FAIL — SEMANTIC/IDENTITY CHECK"** (32 identity violations, max SoC divergence 28.97 pp). The same day, it was reclassified to PASS on S1/S2/S3 grounds (`RULE_D_GOVERNANCE_RECLASSIFICATION.md:10-43`). Rule D adds only **56.62 L** (0.56 pp) over PC-SW, and its reported 185.9 L direct recapture is mostly offset downstream (§5 of that record).
- **Benchmark caveats that shape every number:**
  - Each origin starts with **100 L fuel** and the executor starves diesel when it runs out (`run_diesel_reduction_campaign.py:96`; `research_realization_executor.py:168-191`).
  - Solar is a pyranometer proxy (min(51·GHI, 60 kW)), not PV telemetry. Wind and demand are synthetic.
  - Results are offline simulation evidence only.

## 4. Gap to 40%: what the evidence says

| Evidence (non-blind unless noted) | Saving vs that study's control | Gates |
|---|---|---|
| 2024 May–Aug, GAP19, **perfect solar foresight** (ARM_C) vs causal-NWP (ARM_B) | 25.0% (4,954.8 vs 6,604.0 L), from `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/aggregate_summary.json` | Reliability ARM_C 80.56% vs ARM_B 82.28%, so perfect foresight was *less* reliable |
| 2024 May–Aug, Candidate **S** (solar-credited reserve) | **27.25%** | **Passes all three gates + fuel gate** (`candidate_s_sw_campaign_2024/CANDIDATE_S_SW_123_ORIGIN_SAFETY_GATE.md`) |
| 2024 May–Aug, Candidate **SW** | 37.96% | **FAILS Gate 2** (proportional reliability −1.09 pp) |
| 2025 blind window, Planner-CF v1.2 (adds J_NC) | 10.4–14.4%; 14.95% with Rule D. T40 False for all arms | S1–S3 pass |
| 2025 non-blind replay, γ = 0.25 forecaster | 4.02% | Total unmet +1.40% |

**Reading:**
1. Forecasting alone is bounded. Even perfect solar knowledge bought ~25% under GAP19 on the 2024 window. A better forecaster can't close a 25-point gap by itself.
2. Much of the older 27–38% came from **shedding non-critical load to bank battery**. When Planner-CF added the J_NC penalty, savings fell to ~14% (handoff line 42).
3. Reliability in this benchmark is low to begin with: 2024 control critical-first reliability is 93.47%, proportional 83.69%; the 2025 non-blind GAP19 control leaves **27.7% of total demand unmet** (computed from the replay CSV). "Not worse than control" is therefore a weak guarantee.
4. No artifact shows a reliability-preserving path to 40%. That is a statement about the evidence, not proof it's impossible.

## 5. Best three diesel-reduction opportunities (compatible with the existing winner)

Ranked by expected value × evidence ÷ risk. All tests use **non-blind data only**: fit on 2024 and confirm on the 240 non-blind 2025 origins, or on the 2024 May–Aug 123-origin window.

### 1. Split the forecast: calibrated point for dispatch, conservative quantile for reserve
- **Evidence:** on 2024 training data, the winner's linear attenuation has daylight MAE 96.75 W/m² vs 70.94 W/m² with γ≈0.25 (`cloud_to_ghi_nonlinear_experiment_20261010/CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:31`). The winner systematically **under-predicts** solar, which makes the planner over-commit diesel. But using the higher forecast for everything (replay, γ=0.25) cut fuel 4.02% while raising unmet 1.40%, worse at 104 of 240 origins. The point forecast is biased, and full trust in it is unsafe.
- **Mechanism:** feed J3/J4 (fuel and curtailment economics) the calibrated point forecast. Size the EBR reserve from a lower quantile (for example P10, from split-conformal residuals; the AR(1)/conformal work at repo root is the starting point). The forecaster engine currently emits lower = point = upper (`causal_nwp_physics.py` header).
- **Benefit:** qualitative, moderate. The replay shows the fuel side exists; the reserve quantile is what should protect reliability.
- **Risk:** reserve too thin, hurting S1/S2.
- **Minimal test:** PC-SW with (point = γ-calibrated, reserve = P10) vs PC-SW as is, on the 240 non-blind 2025 origins. Fit γ and quantiles on 2024 only.
- **Pass/fail:** S1, S2, S3 all pass; **total unmet Δ ≤ 0**; E1 fuel test passes.
- **Containment:** new engine subclass in research code only, as done for the replay. No `system/` edits.

### 2. Reserve and terminal-target sizing (where most of the diesel is)
- **Evidence:** in the non-blind GAP19 replay, control ends each 24-h episode at **79.3% mean SoC after starting at 50%**, about 58 kWh/day banked, while 27.7% of demand goes unserved. Planner-CF forces `TERMINAL_TARGET_WH = 100,000` (`planner_cf_campaign_runner.py:50`), i.e. 140 kWh with the floor, 70% SoC (`DIESEL_REDUCTION_CONTROL_DESIGN.md` §2.3). The handoff reports hour-0 reserve commitment as >75% of the low-sun diesel gap (handoff line 81).
- **Mechanism:** replace the fixed terminal energy target with a value-based terminal cost, or a forecast-conditioned target. Size the EBR from net critical deficit, not a fixed constant (the "Variant S/SW" design already exists in `DIESEL_REDUCTION_CONTROL_DESIGN.md` §4).
- **Accounting must change first:** report fuel **adjusted for end-of-episode SoC difference**. Otherwise "saving" can just be draining the battery. The γ=0.25 replay ended 125 kWh lower in total across 240 origins, worth roughly 38–94 L at 0.30–0.75 L/kWh against its 686 L saving.
- **Risk:** the next day starts lower. Single-day episodes hide this, so test with multi-day continuous trajectories (`stage81_multi_trajectory_v2` infrastructure).
- **Pass/fail:** S1–S3, total unmet Δ ≤ 0, SoC-parity-adjusted E1.

### 3. Fewer, better-loaded diesel runs
- **Evidence:** fuel = 5.0 L/h base + 0.25 L/kWh + 2 L/start (`system/config/diesel.yaml`). That is 0.75 L/kWh at 10 kW and 0.30 L/kWh at 100 kW. Battery charge is capped at 50 kW (`battery.yaml`). In 2024, Candidate S cut diesel-on hours from 484 to 331 and starts from 324 to 232 while passing all gates.
- **Mechanism:** the MILP already minimizes J3, so the gain only appears when reserve constraints stop forcing short, low-load runs. This compounds with #2.
- **Note:** Rule D (an executor patch) is low value (+0.56 pp) and makes the trajectory diverge. I don't recommend building on it.

**Not recommended now:** swapping in Candidate F or Stage 8.1 HGB. Forecast value is bounded (§4), F has unresolved timing issues, and HGB's training window is unverified.

## 6. Three safety gates

**Source:** `experiments/stage4_planner_cf_consistency_2025/planner_cf_statistics.py:7-9` (Planner-CF), the same definitions as `candidate_s_sw_campaign_2024/CANDIDATE_S_SW_123_ORIGIN_SAFETY_GATE.md` (which cites `EXP_CANDIDATE_S_SW_PREREGISTRATION.md`). Reliability formulas are at `planner_cf_statistics.py:19-20`. The repo establishes exactly three safety gates (plus a separate fuel gate, E1).

| Gate | Official name | Protects against | Pass criterion | Winner (PC-SW, blind window) | γ=0.25 replay candidate |
|---|---|---|---|---|---|
| S1 / Gate 1 | Critical-first reliability | Losing critical load | ΔR_CF = R_CF(cand) − R_CF(PC-Control) ≥ 0.00 pp, aggregate | PASS (+0.026 pp) | **Unverified**: replay recorded only planned J1 (=0) and total unmet, not realized R_CF |
| S2 / Gate 2 | Proportional reliability | Critical load starved when total supply falls short | ΔR_P ≥ 0.00 pp | PASS (+0.008 pp) | **Unverified**, same reason |
| S3 / Gate 3 | Hard SoC floor | Battery over-discharge | Zero candidate hours with realized SoC < 20.00% | PASS (0 h) | PASS by assertion (`run_offline_optimizer_replay.py:433-441`, threshold 19.999%) |

- **E1 (fuel):** Wilcoxon (Holm-adjusted) p < 0.05 AND BCa 95% lower bound > 0 L/origin. Evaluated only if S1–S3 pass.
- **T40:** report-only; it is not a gate.
- **What passing means:** passing permits **research reporting and further research only**. Every record says promotion requires separate authorization (`RULE_D_GOVERNANCE_RECLASSIFICATION.md:58-60`; replay results "STRICTLY_PROHIBITED_RESEARCH_ONLY").
- **Gate weakness:** all three are relative to a control whose own reliability is 93–99% critical-first (blind window: R_CF ≈ 99.16%) and ~72% of total demand served (non-blind GAP19). None of the gates covers **non-critical / total unmet load**. That's why the replay needed an ad-hoc unmet-load check.

## 7. 240-origin replay and recovery: findings

| Fact | Verified |
|---|---|
| Population | 240 origins: 119 (2025-01-01→04-29) + 121 (09-01→12-30). 0 blind rows, Apr 30 and Dec 31 excluded, no duplicates, `origin_idx` 1–240 in order (checked from the CSV) |
| Original run status | `RUN_STATUS.json`: **FAILED**, "Final artifacts failed publication validation", 240/240 origins completed, 10:59:43 UTC |
| Original artifacts unchanged | SHA-256 of all 4 source files match `RECOVERY_MANIFEST.json` (`899d98…`, `ff29db…`, `8bc2c0…`, `ea16a5…`) |
| Recovered = original byte-for-byte | Yes. Recovered CSV = original `.csv.tmp`; recovered JSONL and RESULTS.json are identical to the source hashes. `RUN_STATUS.json` deliberately not copied |
| Row reconciliation | JSONL (240 unique) = CSV row-for-row on fuel and unmet (max difference 0) |
| Aggregates | Fuel 17,049.53 → 16,363.39 L (**−4.02%**), CI on Δfuel/origin [−4.65, −1.25] L. Unmet 23,894.1 → 24,227.7 kWh (**+1.40%**, worse at 104 origins, better at 73). Curtailment −42.9%. Diesel hours 1,037 → 1,028. 0 infeasible steps, 0 busbar/SoC violations. Mean final SoC −0.26 pp |
| By segment | Winter–spring: fuel −6.11%, unmet +1.72%. Autumn: fuel −2.03%, unmet +1.10% |

**Why this must not be promoted:** lower fuel came with more unserved load in both seasons, and S1/S2 were never computed. That is a fuel–reliability trade, not a reliability-preserving improvement. The recorded verdict, "NO SUPPORTED IMPROVEMENT", is correct.

**But the predeclared rule would have passed it.** Protocol §5.3 (`OFFLINE_OPTIMIZER_REPLAY_READINESS_PROTOCOL.md:96-99`) requires only a CI wholly below zero, zero optimizer failures and zero busbar violations. Unmet load isn't in it, and the candidate meets it. The unmet-load condition exists only in the run script (`run_offline_optimizer_replay.py:870-880`), and **that script was modified at 11:20 UTC, after the run finished**. No script hash was recorded in the results, so I can't establish which decision code actually ran. This should be recorded as a protocol gap, not quietly patched.

## 8. Authorization and integrity timeline (UTC)

| Time (2026-10-10) | Event | Source |
|---|---|---|
| 03:28 | Cloud→GHI protocol: γ fitted on 2024 only; validation on 242 non-blind origins authorized **conditionally** (data-use rights `UNKNOWN`) | `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:3,35-62` |
| 08:13 | Durability tests compiled (pycache) | file times |
| ~09:35 | Replay starts (run id 093458; 5,082 s wall clock) | RESULTS.json metadata |
| 10:59:43 | Replay ends **FAILED** | RUN_STATUS.json |
| 11:20 | `run_offline_optimizer_replay.py` modified (post-run) | file time |
| 11:29 | Readiness protocol last modified. It now contains post-run results (§8.1.5, line 254: "+333.5 kWh, +1.40%") and says recovery is **"PROPOSED — AWAITING PROJECT-LEAD APPROVAL… strictly blocked"** (lines 205, 257-258) | protocol |
| 11:39 | `reconcile_and_recover_run.py` and the durability tests written | file times |
| 11:49 | **Recovery executed**: recovered CSV + `RECOVERY_MANIFEST.json` | file times |

**Findings:**
1. **Replay authorization.** §6.5 (line 131) and §8 (line 200) say "APPROVED BY PROJECT LEAD (2026-10-10)" and "AUTHORIZED". But the §6 heading (line 103) still reads "PROPOSED — AWAITING PROJECT-LEAD APPROVAL", and the file's last save is 30 minutes after the run ended. **The repository does not document when that approval text was written.** It could predate the run or not. File mtimes show only the last save. `git log -p` on the protocol would settle it; I didn't run git.
2. **Recovery authorization.** The last saved protocol, written 20 minutes *before* recovery, says recovery is blocked pending explicit approval, and §8.1.2(1) requires a formal authorization naming the destination directory. **I found no such record in the files examined.** That is "not documented", not "did not exist".
3. **Recovery conduct** was otherwise faithful: original run left FAILED and untouched, outputs byte-identical, clear disclaimers.
4. **Rule D** verdict changed from FAIL to PASS on the same day by post-hoc reinterpretation (§3 above).
5. **Data-use rights** for the 2025 non-blind data are still `UNKNOWN` (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:60-61`).

**Proportionate correction (proposed, not done):** add a new dated, append-only note next to the protocol (not an edit to it) stating:
- the replay ran 09:35–10:59 and ended FAILED;
- the approval wording's timing is not established in the repo;
- recovery ran at 11:49 while the protocol marked it as awaiting approval, and no authorization record was found;
- the §5.3 rule lacked a reliability term, and the run script changed after the run;
- the project lead should either ratify the replay and the recovery retroactively, explicitly labelled as retroactive, or decline.

## 9. Pipeline integrity issues to fix before the next experiment
1. **Horizon-tail lookahead (all arms).** `closed_loop_causal_nwp_runner.py:183-218` and `planner_cf_campaign_runner.py:105-116` look up cloud cover by timestamp across the whole file. At step k > 0, the last k hours come from the **next day's** forecast run, not yet issued. Inferred from code: it assumes one 24-row run per day, which the runners assert.
2. **The full 2025 file, blind rows included, is loaded into memory** by the replay and validation scripts and filtered afterwards (`run_offline_optimizer_replay.py:398,663`; `run_cloud_to_ghi_validation.py:195-206`). No blind outcome is used in metrics, but a pre-filtered non-blind file would make the quarantine structural.
3. **Single-day episodes with SoC/fuel reset** hide carry-over effects. Use SoC-parity accounting and multi-day trajectories.
4. **No gate covers total unmet load.**
5. **The replay didn't compute S1/S2** (no realized critical-served fields).

## 10. Next experiment proposal (one, minimal)

**EXP: governed headroom bound on non-blind data.** Before testing any new forecaster or reserve rule, measure how much saving the governed benchmark can give at all.
- **Arms** (Planner-CF v1.2, PC-SW reserve, J_NC on):
  - (a) causal-NWP forecaster, as-is;
  - (b) perfect solar foresight (realized SW_IN as forecast), as the bound;
  - (c) γ-calibrated point plus P10 reserve (opportunity #1), fitted on 2024.
- **Data:** the 240 non-blind 2025 origins (if data-use rights are confirmed), otherwise the 2024 May–Aug 123 origins. **Never the blind window.**
- **Fixes required first:** horizon-tail lookahead fix, pre-filtered input file, recording of realized R_CF/R_P, SoC-parity fuel accounting.
- **Success criteria:**
  - (c) passes S1, S2, S3, plus **total unmet Δ ≤ 0** and SoC-parity-adjusted E1.
  - (b) is report-only and tells us whether 40% is reachable at all. If (b) < 40%, the forecasting route to 40% is closed, and the effort moves to the reserve and terminal design (#2).
- **Rollback:** research-only subclasses in a new experiment folder, no `system/` changes, and a preregistered protocol hashed *before* the run, including the decision code hash.

## 11. Decisions needed from the project lead
1. Declare the May–Aug 2025 window **spent as a blind test**, and name a new holdout to protect.
2. Confirm data-use rights for the 2025 non-blind data (currently `UNKNOWN`).
3. Ratify or decline, retroactively and labelled as such, the 10-10 replay and its recovery.
4. Decide whether **total unmet load** becomes a fourth gate (or part of S2).
5. Authorize (or not) the §10 experiment.

## Action table

| Action | Expected value | Evidence required | Safety risk | Authorization needed | Status |
|---|---|---|---|---|---|
| Declare blind window spent; pick new holdout | High (restores honest evaluation) | Already shown (`planner_cf_campaign_runner.py:180-188`) | None | Yes | Proposed |
| Fix horizon-tail lookahead + pre-filtered input | High (all results currently carry it) | Code review + unit test | None | Yes (code change) | Proposed |
| Add total-unmet gate + SoC-parity accounting | High (closes loophole seen in replay) | Protocol amendment | Lowers false "wins" | Yes | Proposed |
| Headroom bound experiment (§10) | High (decides if 40% is reachable) | Non-blind runs, preregistered | Low (offline) | Yes | Awaiting approval |
| Point/quantile split forecaster (#1) | Medium | §10 arm (c) | Medium (reserve thinning) | Yes | Not started |
| Reserve/terminal redesign (#2) | Potentially largest | Multi-day trajectories, SoC parity | Medium–high | Yes | Not started |
| Diesel loading (#3) | Medium, follows from #2 | Same | Low–medium | Yes | Not started |
| Append governance correction note for 10-10 replay/recovery | Integrity | `git log -p` of protocol | None | Yes (lead to ratify/decline) | Proposed |
| Promote γ=0.25 candidate | None | Unmet +1.40%, S1/S2 unverified | High | Prohibited | **Do not promote** |
| Build on Rule D | Low (+0.56 pp) | Identity FAIL then reclassified | Low | Yes | Not recommended |

**Next smallest safe step:** approve the §10 headroom-bound experiment on non-blind data, after the horizon-tail fix and with the total-unmet gate added. It tells us, cheaply and without touching the blind window, whether 40% is reachable under the governed benchmark, and whether the remaining effort should go to forecasting or to reserve design. I'll wait for your explicit authorization before running anything.
