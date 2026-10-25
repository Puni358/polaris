# EXP-THREE-ARM-2024: Review Package (PREPARATION ONLY, NOT EXECUTED)

_Prepared 2026-10-11 for project-lead review. No simulation, training, replay or patch was run. No repo file was modified. Repo root: `~/01polaris (Copy)`. Hashes are SHA-256 of the files as they were when I read them on 2026-10-11._

**Data touched while preparing:**
- Only 2024 files and code.
- The 2024 weather file was opened to verify structure and dates.
- One timestamp-convention check (§3, T1) used 2024 **non-evaluation** months only (Jan–Apr, Sep–Dec; May–Aug and 2-day buffers excluded).
- No 2025 data file was opened. The 2025 MANIFEST (metadata) was read.

---

## 1. Baseline and winner verification

| Claim | Verified? | Evidence |
|---|---|---|
| 14.95% = PC-SW + Rule D vs PC-Control | **Yes** | (10,196.9712 − 8,672.6241)/10,196.9712 = 14.949%. PC-Control and PC-SW fuel are in `experiments/stage4_planner_cf_consistency_2025/CAMPAIGN_V12_615_20261006/PC_RESULT_SUMMARY.md`; Rule D fuel in `pc_sw_true_curtailment_recapture_20261008/RULE_D_GOVERNANCE_RECLASSIFICATION.md:36` |
| Formal "winner" | **PC-SW** (E1 winner rule: highest saving among arms passing S1–S3 + E1) | `planner_cf_statistics.py:15`; V12 summary. Rule D is an executor add-on whose verdict was changed from "FAIL — identity" to PASS by later reinterpretation (`RULE_D_GOVERNANCE_RECLASSIFICATION.md:10-43`) |
| Forecaster = cloud-to-solar physics formula, not Stage 8.1 HGB | **Yes** | `system/forecasting/implementations/causal_nwp_physics.py` (`14e72d8a…cdeb710`, pinned at `run_rule_d_true_curtailment_recapture.py:64`). The default engine in `closed_loop_causal_nwp_runner.py:140`. `s81_corrected_solar.py` is never instantiated in any diesel campaign |
| 123-origin campaign = 2025-05-01…08-31 | **Yes** | `planner_cf_campaign_runner.py:180-188` (hard-coded, asserts 123) |
| S1/S2/S3 definitions | **Yes** | `planner_cf_statistics.py:7-9` (definitions), `:19-20` (R_CF, R_P formulas), `:29-35` (constants) |

**Baseline implementation (the components the experiment reuses unchanged):**

| Component | File | SHA-256 |
|---|---|---|
| Planner-CF v1.2 MILP | `experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py` | `a8dd9fc7…5093` |
| Frozen extractor it subclasses | `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py` | (record at prereg) |
| EBR equations (PC-Control `compute_governed_ebr`, PC-SW `compute_variant_sw_ebr`) | `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py:125-232` | `3427da6a…95d0` |
| Arm runner (logic to re-implement) | `planner_cf_campaign_runner.py:88-178` | `ea9400bf…0726` |
| Realization executor | `system/simulation/research_realization_executor.py` | `c1ab56bf…b6c8` |
| Adapted closed-loop runner | `system/research/research_critical_demand_adapter.py` | `0601e57c…6b85` |
| Wind/demand forecaster | `system/forecasting/implementations/baseline.py` | `905c644a…a7c3` |
| Configs and initial state | `experiments/run_diesel_reduction_campaign.py:71-97` | `0be61c4c…c00e` |
| Gate statistics | `planner_cf_statistics.py` | `1153bd61…bb9` |

**Objective (from code, `research_numerical_extractor_planner_cf_v1.py:5-14, 85, 323-370`).** Strict lexicographic order, solved by HiGHS with priorities:
1. J1 Σ unmet_crit·Δt (priority 5)
2. J_NC Σ unmet_nc·Δt (priority 4)
3. J2 Σ s_j2 (priority 3)
4. J3 Σ (0.00025·p_diesel + 5·u_diesel)Δt + 2·v_start (priority 2)
5. J4 Σ curtailment·Δt (priority 1)

The reserve is **soft**: `E_next[t] + s_j2[t] ≥ e_stage2[t] + E_min` (`:305-310`), with `e_stage2[23] = max(EBR[23], 100,000 Wh)` (`:190-193`). Diesel min-up time (2 h in `diesel.yaml`) is **not** modelled. A fuel-inventory constraint applies at hour 0 only (`:288-296`).

**Conflicts found:**
- **C1.** Two `PC_RESULT_SUMMARY.md` files (top-level vs `CAMPAIGN_V12_615_20261006/`) both declare PC-SW winner with different numbers. Neither is marked superseded.
- **C2.** `causal_nwp_physics.py` docstring says it "consumes MEPS 18Z", but the weather files are built from **Open-Meteo `previous-runs` API, `metno_seamless`, `*_previous_day1` variables, `timezone=Etc/GMT-1`** (`clear_sky/audit_clean_nwp_windows.py:25-38`; 2025 MANIFEST). The handoff warns this grid point is ~12 km from Nuolja (`POLARIS_MASTER_HANDOFF.md` §37).
- **C3.** Rule D's governing verdict was changed after results were known (above).

## 2. Dataset eligibility (May–Aug 2024)

| Property | Value | How verified |
|---|---|---|
| File | `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | |
| SHA-256 | `8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16` | computed |
| Size/shape | 663,057 B; 8,328 rows × 10 cols; 347 origins × 24 rows; 0 NaN | read |
| Columns | forecast_start, horizon_hour, timestamp, actual_SW_IN, fc_cloud_cover, fc_temperature_2m, fc_relative_humidity_2m, fc_precipitation, fc_surface_pressure, fc_wind_speed_10m | |
| Coverage | origins 2024-01-20 → 2024-12-31, all at 00:00. Timestamps = forecast_start + (0…23) h, unique, all in 2024. **Zero 2025 rows.** Jan 1–19 missing (NWP coverage FAIL, `data/POLARIS_v0_1_nwp_coverage_pass_fail.csv`) | read |
| Evaluation window | **123 origins, 2024-05-01 → 2024-08-31, consecutive** | read |
| Provenance | `clear_sky/audit_clean_nwp_windows.py` (Open-Meteo previous_day1 + SITES 2024 SW_IN, no imputation). **No manifest file exists for the 2024 dataset** (only for 2025) | code |
| Prior use | **Not pristine.** The same 123 origins were the evaluation set for `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` and `EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024`, and the existing γ=0.25 was fitted on all of 2024, including May–Aug (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:15`). It is eligible as a **non-blind development/validation set**, not as a fresh holdout | manifests |
| Protected-data exclusion | Structural: the file contains only 2024 rows. Still, the runner must read a **pre-filtered derived copy** (2024 only) and fail closed on any non-2024 row (`assert_no_protected_dates`, patch) | |

**Blocker for reusing existing scripts as-is:**
- `planner_cf_campaign_runner.py:214` constructs `SolarElevationProvider(DECOMPOSITION_2025_PATH)`, which `pd.read_csv`s the whole 2025 decomposition file, blind window included (`stage4_low_sun_adapter.py:80-90`).
- `planner_cf_hash_guards.py` (imported at `:42`) was not inspected and may hash protected 2025 artifacts.

So the experiment must **not import `planner_cf_campaign_runner`**. Its run loop is re-implemented in a new file, and `SolarElevationProvider(None)` (the pvlib fallback) is used.

## 3. Lookahead and timing audit

| ID | Finding | Status | Evidence | Action |
|---|---|---|---|---|
| **L1** | Horizon-tail lookahead. t0 = forecast_start − 1 h (`planner_cf_campaign_runner.py:220`), so step k needs targets fs+k … fs+23+k. The lookup spans the whole file, so the last k targets come from the **next origin's** package, 276 target-hours per origin. Whether that package was actually issued before the decision time is **not established** (previous_day1 semantics + Etc/GMT-1 labelling) | **Confirmed structural defect** (availability unproven) | `planner_cf_campaign_runner.py:107,115`; `research_critical_demand_adapter.py:84,107-112`; `closed_loop_causal_nwp_runner.py:187,211-218` | Patch: use only the current origin's package and hold its last value. Affects all arms equally |
| L2 | `_previous_day1` builds each window from values of different runs, which breaks the handoff's same-run rule (`POLARIS_MASTER_HANDOFF.md` §40). Every value was issued about a day before its valid hour, so step-0 use is plausibly causal, but the run identity per hour isn't recorded | **Risk, unverified** | `audit_clean_nwp_windows.py:25-38` | Document. Can't fix without re-sourcing data. Same for all arms |
| T1 | Time zone. Open-Meteo fetched with `timezone=Etc/GMT-1`. Runners label timestamps "Z" (UTC). pvlib geometry uses UTC in `causal_nwp_physics` but `Etc/GMT-1` in `stage4_low_sun_adapter.py:69-97`. My diurnal check on 2024 non-evaluation months: SW_IN centroid at label hour 11.04, vs ≈10.4 (UTC) or ≈11.4 (UTC+1) expected under the hour-ending convention (`POLARIS_MASTER_HANDOFF.md` §7). **Inconclusive** | **Unverified risk (possible 1 h misalignment)** | as cited | Decision D7: resolve from SITES file metadata before running. Not patched |
| L3 | γ calibration. The existing γ=0.25 was fitted on all of 2024, including the evaluation window, so using it on May–Aug 2024 would be **in-sample** | Confirmed | `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:15,31`; `run_cloud_to_ghi_validation.py:153-182` | Arm C re-fits on a disjoint calibration window (§4) |
| L4 | The previous replay's script was modified at 11:20 UTC, after the run ended at 10:59, and no script hash is in its outputs. Its decision logic can't be reproduced exactly, so its numbers are usable only as descriptive records | Confirmed | file mtimes; `RECOVERY_MANIFEST.json` lists no runner hash | Preregister script hashes (§7) |
| L5 | Perfect-foresight lookup reads realized SW_IN by timestamp. That is intended for Arm B only. It must never be reachable from Arms A/C | By design | `run_diesel_reduction_campaign.py:38-68` | Separate engine class; per-arm provenance tag; static test that A/C bundles carry no `NONCAUSAL` metadata |
| L6 | The causal-NWP firewall rejects observation keys in runtime_context (`causal_nwp_physics.py` header). The executor uses realized values only *after* the plan is fixed (`research_realization_executor.py:136-206`). No other feature or normalization step crosses time | Checked, no defect | code | none |
| L7 | Wind/demand forecasts are persistence + diurnal wave restarted at each step (`baseline.py:74-80`). They don't match the synthetic realized profiles (`planner_cf_campaign_runner.py:197-198`): demand forecast ≈ last_obs + 3000·cos(hπ/12) double-counts the diurnal term. That's a systematic forecast error, not lookahead | Confirmed (not a leak) | code | Hold constant across arms; disclose |

**Proposed minimal patch:** `PROPOSED_PATCH.diff`. It adds new files only (lookup helper, isolated synthetic tests, static guard) and touches no existing file. **Not applied, not run.**

## 4. Three-arm protocol

**Common to all arms, held constant:**
- Planner-CF v1.2 (`reserve_enabled=True`, `fuel_inventory=True`), HiGHS threads=1.
- Executor `ResearchRealizationExecutor`; configs from `system/config/*.yaml` via `load_canonical_configs()`.
- Critical ceiling 11,600 W; terminal target 100,000 Wh (**unchanged**).
- Initial state `make_initial_state(fs − 1 h)`: 50% SoC, diesel off, 100 L fuel, last_obs demand 15 kW / wind 4.5 kW.
- Realized solar = 2024 `actual_SW_IN` → min(51·GHI, 60 kW). Realized wind/demand = the canonical synthetic profiles.
- Wind/demand forecasts = `LocalBaselineForecastEngine`.
- 24 hourly steps per origin; 123 origins; L1 patch active.
- Rule D **off** (see D3).

**Reference arm (denominator), PC-Control:** causal-NWP solar (γ=1), governed EBR `compute_governed_ebr` (no renewable credit). This is the formally defined baseline that S1/S2/S4 compare against.

| Arm | Solar forecast to planner | Solar used in EBR reserve | Purpose |
|---|---|---|---|
| **A — Current setup** | causal-NWP γ=1 (`14e72d8a…`) | same (PC-SW: `compute_variant_sw_ebr`) | Reproduce the current winner on non-blind data |
| **B — Perfect-solar diagnostic** | realized `actual_SW_IN` for targets t+1…t+24, revealed at each decision time t (`PerfectForesightDiagnosticEngine` pattern) | same realized values | **Upper bound on the value of solar forecasting under this controller. Not deployable.** Wind and demand forecasts are **not** revealed (same persistence as A), so B isolates solar alone |
| **C — Calibrated point + cautious reserve** | γ̂-calibrated point: clear-sky × (1 − c)^γ̂ | **lower bound** ŝ_k = max(0, min(point_k, point_k + q_α(bin_k))) | Test whether a less biased forecast lowers diesel without losing reliability |

**Arm C details (all fitted before any evaluation-window outcome is seen):**
- **Calibration window:** 2024 origins with forecast_start ≤ 2024-04-29 or ≥ 2024-09-02 (≈ 220 origins). The 1-day buffers each side limit leakage through autocorrelation.
- **γ̂:** grid [0.10, 1.00] step 0.01, minimizing daylight MAE (the existing protocol's criterion, `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:19-21`). Selection is on forecast error, **never on diesel**.
- **Uncertainty:** split-conformal residuals r = actual − point on the calibration window, binned by solar elevation (0–5°, 5–15°, 15–30°, >30°) × cloud fraction (<0.2, 0.2–0.8, >0.8). Bins with fewer than 20 origin-days merge into the neighbouring elevation bin (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:27` uses 20 as the minimum subgroup).
- **q_α** = empirical α-quantile of r in the bin. **α = 0.10 proposed; needs approval (D5).**
- **Reserve:** EBR_C[t] = (1/0.92) Σ_{k=t}^{min(t+5,23)} max(0, c_k − ŝ_k − w_k). This is the PC-SW form with point solar replaced by the lower bound, so it is never less cautious than using the point forecast. Night: ŝ = 0.
- **Information at decision time t:** the current origin's cloud package (L1 rule), clear-sky geometry (deterministic), and the frozen γ̂/q_α tables. No realized value of the current or future hours.
- **Known limitation:** the calibration months are non-summer, so the calibration may transfer imperfectly to May–Aug. This is the price of keeping the evaluation window untouched. Report calibration-window coverage only (in-sample) and evaluation-window coverage **after** the run, as a diagnostic.

**Unavoidable differences between arms:**
1. B gives the planner information A/C can't have.
2. The forecast feeds both the planner's solar bounds and the EBR, so arms differ in reserve as well as plan. That is inherent to PC-SW and is what's being tested.
3. Closed-loop trajectories diverge after the first differing decision.

**Does the simulator make the comparison meaningful?** Partly. (a) Wind/demand are synthetic and their forecasts biased (L7). (b) The executor never raises battery or diesel output above plan (§6). (c) Episodes reset daily. Results are offline-benchmark evidence only.

## 5. Safety gates

**S1–S3 (verified, unchanged; `planner_cf_statistics.py:7-9,19-20`):**
- **S1:** ΔR_CF = R_CF(arm) − R_CF(PC-Control) ≥ 0.00 pp, aggregate over the 123 origins. R_CF = 100·Σ served_crit_first / Σ critical_demand, with served_crit_first = min(d_crit, served_total) per hour and d_crit = min(11,600, realized demand).
- **S2:** ΔR_P ≥ 0.00 pp. R_P = 100·Σ served_crit_prop / Σ critical_demand, with served_crit_prop = served_total·d_crit/d_total.
- **S3:** zero arm-hours with realized SoC < 20.00%.
- **E1 (fuel):** Wilcoxon (Holm) adjusted p < 0.05 AND BCa 95% lower bound > 0 L/origin. Evaluated only if the safety gates pass.

**S4 (PROPOSED, not authoritative until approved). Total unmet-load non-regression:**

| Element | Definition |
|---|---|
| Variable | Executor `unmet_load_w` per executed hour (`research_realization_executor.py:207`) × 1 h = Wh (realized, not planned) |
| Aggregation | U(arm) = Σ_origins Σ_hours unmet_load_w·1 h over the identical 123 origins and 24 hours |
| Criterion | **U(arm) ≤ U(PC-Control)**, aggregate. Ties pass. No tolerance beyond the executor's own 0.01 W rounding (adding one would weaken the gate) |
| Per-origin | **Reported, not decision-bearing:** count of origins worse/equal/better, paired Δ distribution, worst 5 origins. Decision D6: whether to also require that the upper block-bootstrap 95% bound on mean ΔU ≤ 0 (stricter) |
| Uncertainty | Paired stationary block bootstrap of mean ΔU per origin (mean block 10 days, 10,000 resamples, seed preregistered) |
| Decomposition, reported every arm | critical unmet (first) = Σ(d_crit − served_crit_first); critical unmet (proportional) = Σ(d_crit − served_crit_prop); non-critical unmet = U − critical unmet (first) |
| Missing/failed | Any optimizer failure, exception, NaN, or missing origin/hour makes the **arm INVALID**. All gates read NOT EVALUABLE, which counts as **FAIL** for any candidacy. No imputation and no dropping of origins |
| Comparators | Decision-bearing vs PC-Control. Also reported vs Arm A |

**Reported for every arm:** fuel (L), absolute and % reduction vs PC-Control, U, critical-first and proportional critical unmet, non-critical unmet, R_CF, R_P, ΔR_CF, ΔR_P, hours with SoC < 20%, min SoC, curtailment (Wh), diesel-on hours, startups, fuel-starvation hours, optimizer status counts, busbar-balance violations, end-of-episode SoC, held-cloud-hour count (L1 telemetry).

**Rule:** lower fuel with any of S1–S4 failing = **not an improvement**.

## 6. Battery and reserve analysis

**Established from code:**
1. **The "end-of-day" target is a rolling soft target, not an end-of-day constraint.** At every hourly re-plan, the planner's last horizon hour (t+23) gets `e_stage2[23] = max(EBR[23], 100 kWh)` plus E_min 40 kWh, i.e. 140 kWh = 70% SoC. It is enforced via slack s_j2 at J2 priority (`research_numerical_extractor_planner_cf_v1.py:85, 190-193, 305-310, 334`). Since J2 outranks fuel (J3), the planner will burn diesel to meet it. The ~79% end SoC is **emergent**, not targeted.
2. **The executor can't raise output above plan.** Battery discharge = min(planned, 50 kW, energy above floor) (`research_realization_executor.py:201`). Diesel = planned only (`:175`). Unmet = demand − (solar + wind + diesel + planned discharge) (`:205-207`). **When realized solar or wind falls short of forecast, or realized demand exceeds it, the gap becomes unmet load even if the battery has energy and power headroom.** Surpluses, by contrast, charge the battery passively (`:210-223`).
3. In Planner-CF, J_NC (priority 4) outranks reserve and fuel, so **planned** non-critical shedding should occur only when infeasible. In GAP19 (the replay) there is no J_NC, so planned shedding is a fuel-saving choice.
4. Forecast errors in demand (L7) and solar (γ=1 under-forecasts on 2024 calibration data: daylight MAE 96.75 vs 70.94 W/m² at γ≈0.26) feed mechanism 2.

**Not established (hypothesis):**
- The "79% SoC / 28% unserved" figures come from the **GAP19** replay (no J_NC) on 2025 non-blind data. There is **no permitted aggregate for Planner-CF on non-blind data**, so they can't be transferred to the winner.
- Whether unmet load is mainly energy-limited, power-limited (50 kW), plan-limited (mechanism 2), or demand-forecast-driven is **not measured**.

**What this experiment will log to isolate it:** for each hour, SoC before, discharge headroom h_dis = min(50 kW, (E − E_min)·0.92) − p_dis_realized, planned vs realized solar/wind/demand, and unmet. Classify each unmet hour as:
- **plan-limited:** unmet ≤ h_dis;
- **power-limited:** unmet > h_dis and the 50 kW cap binds;
- **energy-limited:** E at floor.

These are descriptive only.

**Separate follow-up (FU-1, not part of this experiment):** "battery-follow executor" diagnostic. Identical planners. The executor may discharge beyond plan, up to min(50 kW − p_dis_plan, energy above E_min + the planned EBR for that hour), to cover realized shortfall. Applied to **all arms including PC-Control**. Then FU-2: a terminal-target sweep (100 kWh vs a forecast-conditioned value), both in multi-day continuous trajectories. Both change benchmark semantics: they need a new benchmark version label and their own authorization, and can't be compared with the 14.95%.

## 7. Evaluation plan

| Item | Rule |
|---|---|
| Denominator | PC-Control total fuel over the 123 origins (same run, same patch) |
| Origins | 2024-05-01 … 2024-08-31, 123, all required |
| SoC | Start 50% every origin. Terminal target fixed at 100 kWh, identical across arms, not optimized. **Primary** fuel = unadjusted (as historically preregistered). **Secondary** (report): SoC-parity-adjusted fuel = fuel + max(0, E_end,ctrl − E_end,arm)·(1/0.92)·f, with f ∈ {0.30, 0.75} L/kWh, the diesel's best/worst marginal efficiency from `diesel.yaml` (5 L/h base + 0.25 L/kWh at 100 kW and 10 kW). D4: whether the adjusted figure becomes decision-bearing |
| Calibration (C only) | Fitted and frozen (γ̂, q_α table, hashes) **before** evaluation outcomes are loaded. Calibration code may only read calibration-window rows (enforced by assertion) |
| Statistics | E1 as defined (Holm over decision-bearing comparisons: A vs Control, C vs Control). **Additionally reported:** stationary block bootstrap (mean block 10 days, justified by documented lag-4 residual autocorrelation, `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:22`) CIs for Δfuel and ΔU, because consecutive daily origins are correlated. D6: whether the block-bootstrap bound replaces the iid BCa in E1 |
| B | Gates computed and **reported, never decision-bearing.** B's saving answers "is 40% reachable by forecasting under this controller?" Any 40% claim needs a non-diagnostic arm passing all gates |
| Reproducibility | Preregistration file with SHA-256 of: runner, patch files, planner, adapter, executor, configs, derived input file, calibration tables. Hashes verified at start (fail-closed). Python/HiGHS versions + `pip freeze`. Deterministic single-thread solves. Repeat origin 1 for PC-Control and compare bit-for-bit (G7 precedent). Write-once run directory, status file, per-origin JSONL with fsync, final CSV/JSON via `os.replace`. **Results must embed the runner hash** |
| Physical feasibility | 0 optimizer failures, 0 busbar violations > 1e-3 W, 0 SoC outside [20, 95]%. Any violation invalidates the arm |
| Classes | **Diagnostic:** B, any classification of unmet hours. **Research-only candidate:** C passing S1–S4 + E1. **Promotion-eligible:** nothing from this experiment. Promotion would need a fresh holdout plus separate authorization |
| Resource limits | 5 arms (Control, A, B, C, + repeat) ≈ 123×4×24 ≈ 11.8k MILP solves, comparable to the 10-10 replay (11,520 solves, 5,082 s wall-clock). Cap: ≤ 4 worker processes, single attempt, no automatic retries |
| Containment / rollback | New folder `experiments/exp_three_arm_2024/` only. No `system/` or frozen-file edits. On any failure, the run stays FAILED. No recovery without separate authorization. To roll back, delete the new folder (nothing else changes) |

## 8. Governance checklist

| Item | Status |
|---|---|
| 10-10 replay `run_20261010_093458` | **FAILED** (keep). Recovery in a separate `recovered_run_…` directory (keep separate). Byte-identity verified |
| Replay approval text (§6.5/§8 of the readiness protocol) | **Timing not documented.** File last saved 11:29 UTC, after the run ended (10:59). The §6 heading still says "PROPOSED — AWAITING". Check with `git log -p` (not run). Not established either way |
| Recovery authorization | **No authorization record found.** The protocol, as last saved before recovery (11:49), says recovery is blocked pending explicit approval (lines 205, 257-258). That is not proof it was unauthorized |
| Replay decision rule | §5.3 had no reliability term. Unmet-load condition only in the post-run-edited script. Record as a gap |
| Data-use rights | 2024: none documented. 2025 non-blind: `UNKNOWN` (`CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:60-61`) |
| This experiment | Needs explicit lead approval of the exact configuration (AUTHORIZATION_SHEET.md). A CLI flag (`authorized=True`) is **not** approval |
| Governance docs | Not modified. Corrections proposed as new append-only notes only |

## 9. Summary table

| Item | Current finding | Required correction | Evidence | Ready for review? |
|---|---|---|---|---|
| Winner/baseline | PC-SW vs PC-Control, causal-NWP γ=1. 14.95% adds Rule D | Treat Rule D as optional (D3) | §1 | Yes |
| 2025 123-origin set | Spent (blind window used for selection) | Never reuse for selection/claims | `planner_cf_campaign_runner.py:180-188` | Yes |
| 2024 May–Aug set | Clean of 2025 data. 123 origins. Previously used. No manifest | Pre-filtered copy + manifest + assertion | §2 | Yes |
| Existing runner reuse | Loads 2025 decomposition file in full | New runner, pvlib elevation, no import of 2025 campaign modules | `planner_cf_campaign_runner.py:214` | Yes |
| L1 horizon tail | Confirmed structural lookahead (availability unproven) | Patch (new files) | §3 | Yes (patch drafted) |
| T1 time zone | Possible 1 h offset, inconclusive | Verify SITES TZ before run (D7) | §3 | **No, blocker to resolve** |
| L3 γ in-sample | γ=0.25 fitted on evaluation months | Re-fit on disjoint window | §3, §4 | Yes |
| L4 replay script | Edited post-run, unhashed | Embed hashes going forward | mtimes | Yes |
| Arms A/B/C | Fully specified | — | §4 | Yes |
| S1–S3 | Verified | — | `planner_cf_statistics.py:7-9` | Yes |
| S4 | Proposed | Lead approval (D2, D6) | §5 | Yes, for decision |
| Battery/reserve | Mechanisms verified in code, causality unproven | Hour classification + FU-1/FU-2 | §6 | Yes |
| Governance gaps | Replay/recovery authorization undocumented | Append-only note; lead ratify/decline | §8 | Yes |

## 10. Decisions the project lead must make before execution
1. **D1:** Approve the 2024 May–Aug 123 origins as the evaluation set, acknowledging prior use, with calibration on 2024 ≤ Apr 29 / ≥ Sep 2.
2. **D2:** Make S4 (as defined in §5) authoritative for this experiment.
3. **D3:** Rule D: keep it off for all arms (recommended: it's an executor add-on with a contested verdict), or add an "A+RuleD" sub-arm.
4. **D4:** Primary fuel metric stays unadjusted; SoC-parity-adjusted fuel is secondary (or make it decision-bearing).
5. **D5:** Arm C quantile α = 0.10 (P10) and the elevation × cloud binning.
6. **D6:** Whether S4 also requires the block-bootstrap upper bound ≤ 0, and whether E1 uses the block bootstrap.
7. **D7:** Resolve the timestamp convention (T1) from SITES metadata before running. If it's UTC+1, approve a uniform relabelling for all arms.
8. **D8:** Approve the L1 patch (new files only) and the new runner.
9. **D9:** Sign the authorization sheet for the exact hashes listed there.
10. **Separately:** ratify or decline, labelled retroactive, the 10-10 replay and its recovery.
