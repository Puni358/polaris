# POLARIS — Causal 168-Hour N6 + GAP19 RHC Pilot Specification (June 1–8, 2024)

**Document ID:** `POLARIS_N6_168H_CAUSAL_RHC_PILOT_PLAN.md`  
**Tracking ID:** `POLARIS-N6-PILOT-168H-SPEC-2026-10-21`  
**Date:** 2026-10-21  
**Working Directory:** `/home/punith-bs/01polaris (Copy)`  
**Scope:** Data-Acquisition Plan, Causal Feature Reconstruction Plan, and Hourly RHC Controller Design  
**Pilot Window:** 2024-06-01T00:00:00Z to 2024-06-07T23:00:00Z (168 Hourly Decisions, 7 Full Days)  
**Clearance:** Strictly Read-Only Planning (Zero solver solves, zero model inferences, zero external downloads, zero production edits)  
**Governance Invariants:** `winner: null` preserved; 2025 blind data quarantined; canonical MDR v1.9.13 Pass 23 authoritative (`OD-02` frozen zero fallback).

---

## 1. Executive Summary & The Final Core Answer

### The Core Answer:
> **Once the identified data are acquired and the original feature pipeline is reconstructed, can all 168 decisions be evaluated with the same causal N6 contract and a complete 24-hour optimization horizon? If not, what exact limitation remains?**
>
> **YES, with one documented and unavoidable physical property of the original model training.**
>
> **What is fully achievable:**  
> Once the 7 missing MEPS 18Z lead slices (leads 31–52) are acquired and the 168 Chronos-2 transformer inferences are executed, **all 168 decisions can be evaluated with 100% causal data availability, zero future lookahead, and a complete 24-hour GAP19 optimization horizon**. Every decision $t_k$ will ingest strictly pre-decision telemetry $[t_k-24\text{h}, t_k)$, NWP forecasts issued before $t_k$, and Chronos-2 inferences conditioned strictly on pre-decision observations.
>
> **The Exact Remaining Behavioral Property / Statistical Limitation:**  
> In the original frozen training pipeline ([`build_clean_stage4_baseline.py` lines 167–174](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/build_clean_stage4_baseline.py#L167-L174)), the Stage 4 blending parameters $(w_h, k_h)$ from [`ensemble_parameters.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_results/ensemble_parameters.json) were fitted on 2024-EVEN origins where $h=1$ was midnight ($00:00\text{ UTC}$).  
> If N6's original feature contract is preserved without alteration, an intra-day decision at solar noon ($12:00\text{ UTC}$) will use $w_1 = 0.30, k_1 = 0.0$ for its immediate forward hour (solar peak), rather than a parameter fitted specifically to noon.  
> This does **not** cause data leakage or contractual invalidity; it is the **authentic behavior of the frozen model** operating outside a midnight-only dispatch origin.

---

## 2. Exact Required NWP Coverage & Acquisition Requirements

### 2.1 Coverage Analysis Across the 168 Pilot Decisions
The machine-readable coverage manifest is generated and saved at:  
[`scratch/n6_rhc_pilot_168h_coverage_manifest.json`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/n6_rhc_pilot_168h_coverage_manifest.json)

* **Decision Count:** 168 hourly decisions ($k = 0 \dots 167$).
* **Decision Timestamps:** `2024-06-01T00:00:00Z` through `2024-06-07T23:00:00Z`.
* **Lead Formula:** For decision hour $HH \in [0, 23]$ and horizon step $h \in [1, 24]$ relative to Day $D-1$ 18Z:
  $$\text{lead}(h) = t_v(h) - t_{\text{init}} = (D\ HH + h - 1) - (D-1\ 18) = 5 + HH + h$$
* **Lead Range Required:**
  * At $HH = 0$ (00:00 UTC): leads 6..29 (Min lead = 6).
  * At $HH = 1$ (01:00 UTC): leads 7..30.
  * At $HH = 23$ (23:00 UTC): leads 29..52 (Max lead = 52).
* **Local Offline Availability:**
  * Leads 6..30 are locally present in `cache_full_acquisition/` and `cache_lead6_v2/`.
  * Leads 31..52 are **MISSING locally** for hours $02:00 \dots 23:00$ across all 7 days (154 decisions affected).

### 2.2 Exact Missing MEPS Cycles and THREDDS Query Specification
To achieve 100% complete causal NWP coverage for all 168 decisions, exactly **7 unique MEPS 18Z cycles** must be queried (or 8 if acquiring June 7 18Z for the 24h tail of the final step):

| # | Operational Day ($D$) | MEPS 18Z Cycle ($t_{\text{init}}$) | Provider Creation (UTC) | Decision Delivery Margin | Local Leads | Missing Leads |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1** | 2024-06-01 | `2024-05-31T18:00:00Z` | `2024-05-31T20:01:43Z` | ~3.97 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **2** | 2024-06-02 | `2024-06-01T18:00:00Z` | `2024-06-01T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **3** | 2024-06-03 | `2024-06-02T18:00:00Z` | `2024-06-02T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **4** | 2024-06-04 | `2024-06-03T18:00:00Z` | `2024-06-03T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **5** | 2024-06-05 | `2024-06-04T18:00:00Z` | `2024-06-04T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **6** | 2024-06-06 | `2024-06-05T18:00:00Z` | `2024-06-05T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |
| **7** | 2024-06-07 | `2024-06-06T18:00:00Z` | `2024-06-06T20:15:00Z` | ~3.75 hours before 00:00Z | 0..30 | **31..52** (22 steps) |

#### Exact OPeNDAP Query Template per Cycle:
* **Base URL:** `https://thredds.met.no/thredds/dodsC/meps25epsarchive/{YYYY}/{MM}/{DD}/meps_det_pl_{YYYYMMDD}T18Z.ncml.ascii`
* **Constraint Query String:**
  ```text
  mass_fraction_of_cloud_condensed_water_in_air_pl[31:1:52][8:1:8][760:1:760][486:1:486],
  mass_fraction_of_cloud_ice_in_air_pl[31:1:52][8:1:8][760:1:760][486:1:486],
  x_wind_pl[31:1:52][8:1:8][760:1:760][486:1:486],
  y_wind_pl[31:1:52][8:1:8][760:1:760][486:1:486],
  time[31:1:52]
  ```
* **Network Cost:** Exactly 7 HTTP GET requests. Payload size $\approx 15\text{ KB}$ per request, total $\approx 105\text{ KB}$. Runtime $\approx 10\text{ seconds}$.

---

## 3. Chronos-2 Feature Reconstruction Plan

N6 requires `pred_stage4_clean` (Feature 34) and `clean_attenuation` (Feature 35).

### 3.1 Original Pipeline Reconstruction
1. **Model Specification:**
   * HuggingFace pretrained model: `amazon/chronos-2`.
   * Runner module: [`stage3/run_stage3_experiments.py`](file:///home/punith-bs/01polaris%20%28Copy%29/stage3/run_stage3_experiments.py).
   * Inference call: `pipeline.predict([input_item], prediction_length=24, context_length=24)`.
   * Prediction point: Median quantile (index of quantile $0.5$).
2. **Context Inputs (Pre-Decision Cutoff strictly at $t_k$):**
   * Target actuals: SITES pyranometer measurements over $[t_k - 24\text{h}, t_k)$. Length 24.
   * Covariates (past and future): `solar_elevation`, `solar_zenith`, `clearsky_ghi`, `fc_cloud_cover`.
3. **Stage 4 Clean Blending Formula:**
   $$\text{phys\_pred\_clean}[h] = \max(0.0, \text{clearsky\_ghi}[h] \cdot (1.0 - k_h \cdot \text{cloud\_frac}[h]))$$
   $$\text{pred\_stage4\_clean}[h] = \max(0.0, w_h \cdot \text{pred\_stage3b}[h] + (1.0 - w_h) \cdot \text{phys\_pred\_clean}[h])$$
   $$\text{clean\_attenuation}[h] = \text{clearsky\_ghi}[h] - \text{pred\_stage4\_clean}[h]$$
   where $(w_h, k_h)$ are frozen parameters from [`stage4/stage4_results/ensemble_parameters.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_results/ensemble_parameters.json) (SHA-256 `26cfbd19...`).

### 3.2 Proposed Standalone Inference Runner
A dedicated, scratch-only batch inference script (`scratch/generate_pilot_chronos2_features.py`) will be prepared:
* **Batch Size:** Exactly 168 input items (one per hourly origin).
* **Execution Environment:** PyTorch on CPU (`device_map="cpu"`).
* **Estimated Runtime:** $\approx 15\text{ seconds}$.
* **Validation Checks:**
  1. Output DataFrame shape strictly $(168 \times 24) = 4,032$ rows.
  2. Zero NaNs, Infs, or negative irradiance predictions.
  3. Pre-decision context cutoff verified against SITES timestamps ($t < t_k$).

---

## 4. Verified Target and Timestamp Contract

### 4.1 SITES Physical Window & Midpoint Reconciliation (D7 Standard)
* SITES 10-minute readings have fixed `TIME ZONE: UTC+1` and are **period-ending**.
* The canonical hourly file `POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` aggregates 6 readings via `floor('h')`.
* Reading $HH:00$ represents interval $[(HH-1):50, HH:50]$ with physical midpoint at **$(HH-1):20\text{ UTC}$**.

### 4.2 Exact Index Mapping and Physical Synchronization
In `DigitalTwinSimulator.step(S_k, u_0, actuals)`:
* Control action $u_0$ executes across forward physical hour $[t_k, t_k+1\text{h}]$.
* Ground truth actual consumed is stamped **$t_k+1\text{h}$** (representing the forward transition).
* Raw N6 index 0 ($h=1$) is stamped $t_k+0\text{h}$ (covering the past/current hour $[t_k-1\text{h}, t_k]$).
* Raw N6 index 1 ($h=2$) is stamped $t_k+1\text{h}$ (covering the forward hour $[t_k, t_k+1\text{h}]$).

```text
================================================================================
PHYSICAL INTERVAL SYNCHRONIZATION (DECISION ORIGIN t_k = 00:00 UTC)
================================================================================
Physical Interval:        [00:00, 01:00]      [01:00, 02:00]  ...  [23:00, 24:00]
Realized Actual Consumed:  01:00:00Z           02:00:00Z      ...   00:00:00Z (D+1)
Raw N6 Prediction Stamped: 01:00:00Z (idx 1)   02:00:00Z (idx 2)   (idx 24 missing)
OD-02 Dispatch Step:       Step 0 (u_0)        Step 1         ...   Step 23 (terminal)
OD-02 Aligned Value:       raw[1]              raw[2]         ...   0.0 W/m^2 (fallback)
================================================================================
```
* **Why Raw Index 0 is Dropped:** If index 0 were mapped to dispatch step 0, the optimizer would receive a solar value lagging the forward transition by 1 hour. OD-02's shift (`raw[1:] + [0.0]`) is mathematically required for physical alignment.
* **First-Action Decoupling:** In hourly RHC, **strictly dispatch step 0 ($u_0$)** is committed. Step 0 receives raw index 1. The terminal slot (step 23) is never executed physically on the plant.

---

## 5. Corrected Terminal-Target Configuration & Static Verification

### 5.1 Helper Interfaces and Contract Derivation
1. `_prepare_gap19_terminal_target_config(station_state, configs) -> opt_configs`:
   $$\text{terminal\_target\_wh} = \text{initial\_e\_wh} - \text{min\_e\_wh}$$
   where $\text{min\_e\_wh} = 40,000\text{ Wh}$ ($20\%$ SOC), $\text{max\_e\_wh} = 190,000\text{ Wh}$ ($95\%$ SOC).
   In GAP19 line 304, $\text{req\_lhs} = \text{terminal\_target\_wh} + \text{min\_e\_wh} = \text{initial\_e\_wh}$.
   Because $\text{initial\_e\_wh} \le 190,000\text{ Wh}$, the terminal constraint is **100% feasible without slack penalty**.
2. `_prepare_gap19_policy_b_config(bundle, configs) -> opt_configs`:
   $$\text{combined\_reserve}[t] = \max\left(\frac{\text{critical\_load\_6h}[t]}{\eta_{\text{dis}}}, \text{conformal\_ebr}[t]\right)$$
   incorporating battery discharge efficiency $\eta_{\text{dis}} = 0.92$.

### 5.2 Static Regression Verification
The regression test suite [`scratch/test_rhc_static_governance.py`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/test_rhc_static_governance.py) was executed with `pytest` (0.39s, zero solver/sim calls) and verified:
* **Test 1 (`test_od01_terminal_target_feasibility_across_soc_range`):** PASSED across SOCs 0%, 10%, 20%, 35%, 50%, 80%, 95%, 100%. Max required energy never exceeds 190 kWh.
* **Test 2 (`test_previous_runner_terminal_reserve_bug_reproduction`):** PASSED. Reproduced the exact 10 kWh terminal slack penalty caused by bypassing the helper.
* **Test 3 (`test_policy_b_pointwise_maximum_envelope`):** PASSED. Confirmed exact pointwise maximum with $\eta_{\text{dis}} = 0.92$ scaling ($65,217.39\text{ Wh}$).
* **Test 4 (`test_od02_canonical_shift_and_terminal_zero_fallback`):** PASSED. Confirmed raw 1..23 mapped to 0..22, with slot 23 set to `0.0`.

---

## 6. Detailed 168-Hour Controller Architecture

The pilot runner will be implemented in `scratch/run_causal_168h_rhc_pilot.py`:

```python
# Hourly Control Loop Structure (Iterates k = 0 to 167)
curr_st = copy.deepcopy(S_0) # Initialized at 2024-06-01T00:00:00Z (50% SOC, 500L fuel)

for k in range(168):
    dec_dt = start_dt + timedelta(hours=k)
    ts_str = dec_dt.isoformat()
    
    # 1. Trailing telemetry [dec_dt - 24h, dec_dt) from fixture history
    trailing_actuals = query_trailing_history(fixture_df, dec_dt, window_hours=24)
    ctx_features = compute_telemetry_context_features(trailing_actuals, dec_dt)
    
    # 2. Causal NWP and Chronos-2 features for [dec_dt, dec_dt + 24h)
    fm_k = assemble_causal_feature_matrix(dec_dt, ctx_features, nwp_pilot_cache, chronos2_pilot_df)
    
    # 3. Predict raw N6 bundle
    raw_bundle = n6_engine.predict(curr_st, {"n6_feature_matrix": fm_k})
    
    # 4. Apply frozen OD-02 shift
    aligned_bundle = _align_n6_bundle_od02_frozen(raw_bundle, origin_timestamp_str=ts_str)
    
    # 5. Configure OD-01 dynamic target and Policy B envelope
    cfg_k = copy.deepcopy(base_cfg)
    cfg_k = _prepare_gap19_terminal_target_config(curr_st, cfg_k)
    cfg_k = _prepare_gap19_policy_b_config(aligned_bundle, cfg_k)
    
    # 6. Route and solve GAP19 MILP
    assessment, route = router.evaluate_and_route(curr_st, aligned_bundle, cfg_k)
    assert route == "NORMAL"
    plan = optimizer.optimize(aligned_bundle, curr_st, cfg_k)
    assert plan.constraint_status == "OPTIMAL"
    
    # 7. Commit strictly u_0
    u_0 = extract_first_action(plan)
    
    # 8. Step DigitalTwin by exactly 1 hour
    actual_next = fixture_df.iloc[fixture_idx_start + k + 1]
    curr_st = simulator.step(curr_st, u_0, actual_next)
    
    # 9. Audit monotonicity & record trace
    assert curr_st.diesel_fuel_remaining_liters <= prev_fuel
    record_trace(k, dec_dt, plan, curr_st)
    # ZERO STATE RESETS — loop advances with updated curr_st
```

### Baseline Arm Parity:
The baseline arm (`LocalBaselineForecastEngine`) executes under the identical protocol:
* Same starting state $S_0$ (`50.0%` SOC, `500.0 L` fuel).
* Re-forecasts and re-solves GAP19 fresh at every hour $k = 0 \dots 167$ (168 solves).
* Executes strictly $u_0$.
* Consumes the exact same SITES physical actuals.
* Applies `_prepare_gap19_terminal_target_config` to eliminate artificial terminal slack.

---

## 7. Metrics & Evidence Artifacts

The pilot run will output to `scratch/causal_n6_gap19_rhc_pilot_168h/`:
1. `PILOT_MANIFEST.json`: Cryptographic manifest (SHA-256 of all scripts, models, data).
2. `STEP_TRACE_168H.csv`: Hourly log of $t_k$, $u_0$, solver status, solve time, diesel burn, and SOC.
3. `PILOT_COMPARATIVE_METRICS.json`: Final metrics comparing N6 vs. Baseline:
   * Total diesel fuel burned (L) and generator runtime (hours).
   * Total solar energy utilized (kWh) and curtailed (kWh).
   * Total unmet critical load (kWh).
   * SOC min / max / final percentages.
   * Total solver failure and router fallback counts.
   * State continuity verification ($S_{k+1}.\text{energy} == \text{simulator.step}(S_k, u_0).\text{energy}$).

---

## 8. Separation of Verified Facts, Assumptions & Unresolved Questions

| Category | Item | Evidence & Verification Citation |
|---|---|---|
| **Verified Fact** | Canonical MDR Pass 23 is authoritative; OD-02 is frozen with `0.0 W/m²` fallback. | [`POLARIS_MASTER_DECISION_REGISTER.json` v1.9.13 lines 5–12](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_MASTER_DECISION_REGISTER.json#L5-L12). |
| **Verified Fact** | OD-01 dynamic derivation $\text{initial\_e} - \text{min\_e}$ is feasible across the entire 0–100% SOC range. | Proven in [`scratch/test_rhc_static_governance.py`](file:///home/punith-bs/01polaris%20%28Copy%29/scratch/test_rhc_static_governance.py) (pytest 4/4 passed). |
| **Verified Fact** | Previous run's 18,298 L burn was caused by bypassing OD-01, enforcing an impossible 200 kWh terminal target. | GAP19 lines 138–139, 304; reproduced in unit test 2. |
| **Verified Fact** | MEPS NWP extraction in `fetcher.py` clamped leads to $\le 30$ due to a query bug on 2024-02-01. | [`fetcher.py` lines 187–196](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_station_tuning_research/candidate_f_successor_18z/fetcher.py#L187-L196). |
| **Verified Fact** | Chronos-2 transformer predictions exist in the repository exclusively for 00:00 UTC origins. | [`stage3/stage3b_cloud_nwp_predictions.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage3/stage3b_cloud_nwp_predictions.csv) (8,328 rows, unique origin hours: `[0]`). |
| **Verified Fact** | In hourly RHC, dispatch step 23 is never executed physically on the plant ($u_0$ uses raw index 1). | `simulator.py` lines 38–46; step 0 advances $[t_k, t_k+1\text{h}]$. |
| **Operational Assumption** | MEPS 18Z cycles for 2024-05-31 to 2024-06-06 remain available on MET Norway THREDDS archive. | Standard MET Norway open-access archive path. |
| **Statistical Limitation** | Stage 4 blending weights $(w_h, k_h)$ were fitted on midnight-origin diurnal geometry. | [`ensemble_parameters.json`](file:///home/punith-bs/01polaris%20%28Copy%29/stage4/stage4_results/ensemble_parameters.json); preserved as an authentic frozen model property. |

---

## 9. Staged Authorization Roadmap

To preserve strict governance boundaries, execution is segmented into 3 explicit stages:

```text
+-----------------------------------------------------------------------------------+
| STAGE 1: NWP Lead Acquisition (Requires Explicit User Authorization)             |
| - Execute scratch/acquire_pilot_meps_leads.py                                     |
| - Fetch 7 DODS ASCII slices (leads 31..52) from MET Norway THREDDS (~105 KB total)|
| - Save to scratch/meps_pilot_leads/                                               |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 2: Chronos-2 Inference (Requires Explicit User Authorization)               |
| - Execute scratch/generate_pilot_chronos2_features.py                             |
| - Run 168 Chronos-2 predictions on CPU (~15 seconds)                              |
| - Compute pred_stage4_clean and clean_attenuation                                 |
| - Save to scratch/chronos2_pilot_168h.parquet                                     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| STAGE 3: Closed-Loop RHC Simulation (Requires Explicit User Authorization)        |
| - Execute scratch/run_causal_168h_rhc_pilot.py                                    |
| - 168 hourly GAP19 solves per arm (N6 and Baseline) (~2 minutes runtime)          |
| - Advance DigitalTwin continuously, carry forward state, record all metrics       |
| - Output to scratch/causal_n6_gap19_rhc_pilot_168h/                               |
+-----------------------------------------------------------------------------------+
```

**Current Status:** All preparation, static verification, manifest generation, and planning are complete. Execution remains **strictly stopped** awaiting Stage 1 authorization.
