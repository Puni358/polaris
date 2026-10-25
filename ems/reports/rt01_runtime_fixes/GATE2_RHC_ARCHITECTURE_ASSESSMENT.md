# GATE 2: RHC Architecture Feasibility Assessment (READ-ONLY AUDIT)

**Document ID:** `GATE2_RHC_ARCHITECTURE_ASSESSMENT.md`  
**Date:** 2026-10-20  
**Status:** COMPLETE (Read-Only Static Inspection & Governance Assessment)  
**Security & Governance Boundaries:** Fail-Closed Enforcement. Zero file mutations to code/tests/config/MDR; zero execution of models, simulations, or optimizers; zero access to quarantined 2025 blind data; baseline and Master Decision Register (`OD-02`) immutability strictly preserved.

---

## 1. Executive Verdict

1. **Path A (Rolling-Window Slicing of Existing 00:00 UTC Forecast Artifacts) is STRUCTURALLY INFEASIBLE under current contracts without external padding or optimizer refactoring:**
   - Slicing an existing midnight-origin 24-hour forecast at intra-day step $k \in \{1 \dots 23\}$ leaves a shrinking horizon of $24 - k$ steps (e.g., only 12 hours remain at 12:00 UTC).
   - `GAP19HighsNativeOptimizer` is **strictly hardcoded to a fixed horizon $H = 24$** (`num_base_vars = H * K = 360`, `num_total_vars = 408`, with explicit index arrays and loops bounded at 24). It cannot accept a shrinking horizon without raising unhandled `IndexError` or producing schema-invalid `DispatchPlan` payloads.
   - Extending the horizon back to 24 steps from existing artifacts requires either: (a) splicing data from the next day's 00:00 UTC forecast (which constitutes **future-origin data leakage**), or (b) padding with persistence, climatology, or zeros (none of which is governed, calibrated, or approved under frozen Decision `OD-02`).

2. **Path B (Re-engineering the Upstream Pipeline for Genuine Hourly Origins) is ARCHITECTURALLY SOUND but HEAVILY BLOCKED by upstream hardcoding and uncalibrated diurnal statistics:**
   - Existing feature-generation code explicitly hardcodes origins to midnight (`meps_wind_extractor.py:169` forces `origin_dt.replace(hour=0, minute=0, second=0, microsecond=0)`; `n6_operational_pipeline.py:128` queries a 347-row parquet file containing only 00:00 UTC records).
   - Meteorological data from MET Norway MEPS is issued on 6-hour cycles (18Z, 00Z, 06Z, 12Z). Intra-day rolling origins require a formal "as-of" causal selection policy mapping each hour $t_k$ to the latest available NWP run and variable lead times ($h \in [1, 24]$).
   - Candidate N6's split-conformal EBR uncertainty multiplier ($Q_{90\_W} = 1.5702$) was calibrated strictly on 00:00 UTC issuances on 2024-ODD. Conformal coverage is not statistically guaranteed for intra-day forecast distributions without full diurnal re-calibration.

3. **Status of Unresolved OD-02 Findings:**
   - **EBR Indexing:** The unshifted status of `ebr_target_wh` in `_align_n6_bundle_od02` is **NOT an unhandled bug**; it is the **formally frozen contract recorded in the Master Decision Register** (MDR v1.9.12, twenty-third pass, 2026-10-19). The register rationalizes this as preserving a forward lookahead window $[k, \min(k+6, 24))$ starting from the decision origin, while documenting the unverified empirical coverage limitation.
   - **Terminal Solar Point (0.0 W/m² Fallback):** Static inspection establishes that slot 23 is forced to zero, discarding Arctic polar-day midnight sun irradiance ($1.2 \dots 6.8\text{ W/m}^2$). However, whether this zero alters the first-hour dispatch decision $u_0$ or diesel fuel consumption remains **empirically unproven** and requires an authorized diagnostic run.

4. **Recommendation to Project Owner:**  
   Maintain `OD-02` and the single-shot dispatch harness as the authoritative reference baseline. Do **NOT** attempt Path A without an authorized redesign of GAP19. Commission a bounded, offline design specification (RFC) for Path B to define causal NWP cycle selection and diurnal conformal re-calibration before considering code implementation.

---

## 2. Evidence-Backed Findings

### 2.1 Path A: Forecast Slicing Feasibility

| Dimension | Verified Source Fact / Mechanism | Code Citation |
| :--- | :--- | :--- |
| **Available Midnight Timestamps** | Exactly 24 hourly steps: raw indices $0 \dots 23$ correspond to $t_0+0\text{h} \dots t_0+23\text{h}$ (`00:00:00Z` to `23:00:00Z`). Under OD-02 alignment, indices $0 \dots 23$ correspond to $t_0+1\text{h} \dots t_0+24\text{h}$ (`01:00:00Z` to `24:00:00Z`). | `n6_solar.py:537-540`<br>`adapters.py:647-650, 674-686` |
| **Remaining Horizon upon Slicing** | Slicing at intra-day step $k \in \{0 \dots 23\}$ yields a remaining horizon of $H_k = 24 - k$ steps. At $k=1$ (01:00), 23 steps remain; at $k=12$ (12:00), 12 steps remain; at $k=23$ (23:00), exactly 1 step remains. | `adapters.py:1663-1667` |
| **GAP19 Horizon Flexibility** | **Inflexible / Strictly Hardcoded:** GAP19 enforces $H = 24$ across all matrix dimensions (`num_base_vars = 24 * 15 = 360`, `num_total_vars = 408`). Loops (`for t in range(24)`), input length assertions (`len(cd_cfg) != 24`), and output lists (`[0.0]*24`) fail closed or raise `IndexError` if input length $< 24$. | `gap19_highs_native.py:45-62, 92-94, 119-124, 153-171` |
| **Horizon Extension Requirements** | Supplying 24 steps at $k > 0$ requires extending the horizon by $k$ hours past $23:00\text{Z}$. If drawn from day $D+1$'s 00:00Z forecast, it violates causality (future-origin leakage). If padded with persistence, climatology, or zeros, it violates existing frozen contracts. | `adapters.py:1641-1644` |
| **Channel Consistency under Slicing** | Under `OD-02`, solar generation is shifted by 1 hour (`pts[1:] + [0.0]`), whereas demand, wind, and `ebr_target_wh` are unshifted. Slicing at step $k$ without re-evaluating the 6-hour rolling EBR reserve leaves the EBR tail truncated from 6 hours down to 1 hour for indices $t \ge 18$. | `adapters.py:651-652, 1141-1144`<br>`n6_solar.py:465-470` |

### 2.2 Path B: Genuine Hourly Origins Feasibility

| Dimension | Verified Source Fact / Mechanism | Code Citation |
| :--- | :--- | :--- |
| **Upstream Feature Generation Restrictions** | Upstream pipelines are hardcoded to midnight. `build_n6_live_feature_matrix()` filters `df_base["forecast_start"] == origin_dt` against `candidate_k_2024_clean_matrix.parquet`, which strictly contains 347 rows stamped `00:00:00+00:00`. Queries for $k > 0$ raise `ValueError: got 0 rows`. | `n6_operational_pipeline.py:126-132`<br>`CANDIDATE_N_MANIFEST.json:148-150` |
| **NWP Cycle & Issue-Time Availability** | MET Norway MEPS runs on 6-hour cycles (18Z, 00Z, 06Z, 12Z). `fetch_untruncated_meps_wind()` explicitly hardcodes normalization to midnight: `origin_dt = origin_dt.replace(hour=0, minute=0, second=0, microsecond=0)` and assumes run initialization $t_0 - 6\text{h} = 18\text{Z}$. Genuine hourly origins require dynamic mapping across cycles. | `meps_wind_extractor.py:8-12, 168-171` |
| **Hourly Geometry & Context Features** | Solar geometry (`solar_elevation`, `clearsky_ghi`) can be computed for arbitrary hours via `pvlib`/NOAA formulas. However, the 14 context statistics (`compute_telemetry_context_features()`) require an active, streaming 24-hour buffer of preceding `SW_IN` observations. | `n6_operational_pipeline.py:59-103`<br>`n6_solar.py:100-125` |
| **Diurnal EBR Calibration** | Candidate N6's split-conformal calibration ($Q_{90\_W} = 1.5702$, $Q_{\text{hat\_norm}} = 1.8590$) was computed strictly on 00:00 UTC issuances. Forecast errors vary significantly between dawn, midday solar peak, and dusk; a midnight-calibrated reserve is statistically unverified for intra-day origins. | `n6_solar.py:94-96`<br>`POLARIS_MASTER_DECISION_REGISTER.json:5` |
| **Modules Requiring Redesign** | Substantial engineering footprint: (1) `meps_wind_extractor.py` (multi-cycle fetching), (2) `n6_operational_pipeline.py` (dynamic 8,760h feature matrix assembly), (3) `N6SolarForecastEngine` (intra-day context validation), (4) `s81_solar.py` / `n6_solar.py` (conformal recalibration). | Static code inspection across `stage7/` and `system/` |

---

## 3. Unresolved OD-02 Findings

### A. EBR Indexing Semantics: Established vs. Unproven
- **Established Fact:** In `system/evaluation/n6_multi_origin_harness/adapters.py` lines 647–652 and 666–694, `solar_irradiance` and `solar_generation` are shifted by 1 hour (`pts[1:] + [0.0]`), while `ebr_target_wh` (and `metadata["ebr_target_wh"]`) is preserved completely unshifted. In `_prepare_gap19_policy_b_config` (line 1143), `combined_reserve[t] = max(critical_reserve[t], conformal_ebr[t])`, pairing unshifted critical reserve with unshifted conformal EBR, while the optimizer simultaneously consumes shifted solar generation.
- **Contract Definition:** This behavior is **explicitly governed by the Master Decision Register** (MDR v1.9.12, twenty-third pass, 2026-10-19):
  > *"Decision OD-02 is formally FROZEN. Point-forecast arrays are aligned by OD-02 (raw rows 1..23 -> dispatch steps 0..22, step 23 = 0.0 W/m^2 baseline fallback), while ebr_target_wh remains unshifted matching forward lookahead window [k, min(k+6, 24))."*
- **What Remains Unproven:** The register documents the following open limitation: *"reproducing calibration calculation does not independently establish empirical coverage after OD-02 changes point-forecast alignment."* It is **unproven** whether shifting EBR by $+1\text{h}$ to match solar alignment would improve or degrade battery reserve survivability, or alter diesel starts. This can only be resolved by an authorized empirical diagnostic run comparing shifted vs. unshifted EBR.

### B. Terminal Solar Point (0.0 W/m² Fallback): Established vs. Unproven
- **Established Fact:** Decision `OD-02` forces slot 23 ($t_0 + 24\text{h}$) of the aligned solar bundle to `0.0 W/m²` (0.0 W). At Nuolja station ($68.36^\circ\text{N}$) during polar day (June 1–2, 2024), midnight solar elevation is $+0.50^\circ \dots +0.63^\circ$ and actual irradiance is $1.17 \dots 6.82\text{ W/m}^2$. The native N6 model predicts $7.9 \dots 8.6\text{ W/m}^2$, which `OD-02` overwrites with `0.0`.
- **Contract Definition:** Formally approved in MDR Section 38 (twenty-second and twenty-third passes) to maintain baseline integrity with `LocalBaselineForecastEngine` and reject unverified offline clear-sky decomposition files at runtime.
- **What Remains Unproven:** In MILP receding-horizon dispatch, the immediate executed control action is **slot 0** ($u_0$). Actions at slot 23 are planned but discarded before replanning. Because battery energy and diesel state constraints mathematically couple slot 23 to slot 0 across the 24-hour horizon, changing slot 23 from `0.0` to $\approx 8\text{ W/m}^2$ ($\approx 400\text{ W}$ generation) could theoretically alter terminal battery target slack or diesel commitment. However, **zero empirical proof exists that this changes $u_0$ or diesel fuel consumption in practice**. Determining the actual delta requires an authorized OFAT (one-factor-at-a-time) sensitivity solve.

---

## 4. Decision Comparison: Path A vs. Path B

| Evaluation Dimension | Path A: Forecast Slicing | Path B: Genuine Hourly Origins |
| :--- | :--- | :--- |
| **1. Causal Data Availability** | **High within $24-k$ h; Zero beyond:** Reuses existing 00:00 UTC feature matrices. However, data past $24-k$ hours does not exist in the issuance and cannot be fetched causally. | **High across full 24 h:** Fetches actual NWP runs available at each hour. Requires operational rules for NWP transmission delays. |
| **2. Horizon Completeness** | **Fails Closed:** Horizon shrinks from 24 down to 1 hour. GAP19 cannot solve shrinking horizons without code refactoring or unapproved synthetic padding. | **Fully Complete:** Produces a full $(24, 36)$ matrix at every step, directly satisfying GAP19's fixed 24-step contract. |
| **3. EBR & Timestamp Alignment** | **Severely Distorted:** Slicing an unaligned EBR trajectory further truncates lookahead windows ($t \ge 18$), compounding OD-02 index mismatch. | **Fully Synchronized:** Re-evaluates point forecast, uncertainty scale $s$, and rolling EBR trajectory at each rolling origin $t_k$. |
| **4. Required Upstream Changes** | **Zero upstream changes:** Modifies only adapter/optimizer layer (requires GAP19 shrinking-horizon refactor or padding adapter). | **Massive upstream overhaul:** Requires un-hardcoding `meps_wind_extractor.py`, building an 8,760h feature pipeline, and streaming telemetry buffers. |
| **5. Validation Burden** | **High Governance Burden:** Must prove that synthetic padding does not leak future data or distort economic dispatch comparisons. | **High Statistical Burden:** Must re-run 2,000-draw bootstrap evaluations, NWP latency audits, and diurnal conformal re-calibrations. |
| **6. Risk to Frozen Baseline** | **Low risk to baseline code; High risk to experimental validity:** Preserves existing files, but shrinking horizons produce non-comparable dispatch plans. | **Zero risk to baseline code; Independent pipeline:** Builds a separate operational pipeline, preserving frozen 00:00 artifacts untouched. |

---

## 5. Recommended Next Owner Decision

### Recommendation:
**Reject Path A for immediate implementation; Defer Path B to a formal Phase RFC.**

1. **Path A is fundamentally blocked by the optimization contract:** Because `GAP19HighsNativeOptimizer` requires $H = 24$, slicing existing 00:00 UTC forecasts cannot function without an arbitrary padding heuristic or a major refactoring of GAP19's MILP constraint formulation. Implementing ad-hoc padding (e.g., repeating persistence or borrowing $D+1$ data) violates governance and introduces unquantifiable data leakage.
2. **Path B is the only mathematically and operationally rigorous long-term architecture:** However, because the repository currently possesses feature matrices strictly for midnight origins, Path B cannot be executed without substantial data engineering and diurnal conformal recalibration.
3. **Actionable Owner Decision Proposal:**
   - **Decision 1 (Baseline Integrity):** Formally reaffirm that Gate 2 benchmarking and official model selection remain anchored to the frozen 00:00 UTC single-shot evaluation harness under Decision `OD-02`.
   - **Decision 2 (Exploratory Authorization):** Authorize a strictly bounded, non-mutating feasibility spike (Phase RFC) to evaluate whether GAP19 can be refactored to support variable horizon length $H \in [1, 24]$, or whether an offline rolling feature generator can be constructed for Path B.

---

## 6. Permissions Required Before Implementation or Diagnostic Execution

Under current fail-closed governance, neither Path A nor Path B can proceed without the following explicit, prior Project Owner authorizations:

1. **Permission for GAP19 Variable-Horizon Formulation:**  
   Formal authorization to modify `system/optimization/implementations/gap19_highs_native.py` to parameterize horizon length $H$ dynamically, including adjusting variable index layout (`num_base_vars = H * 15`), constraint loops, and terminal target enforcement.
2. **Permission for EBR / OD-02 Diagnostic Execution:**  
   Formal authorization to run an offline, single-origin OFAT simulation comparing:
   - Aligned solar vs. unaligned solar (`pts[1:] + [0.0]` vs. `pts[0:24]`)
   - Aligned EBR vs. unshifted EBR (`ebr[1:] + [0.0]` vs. unshifted `ebr`)
   - Terminal zero vs. clear-sky polar-day continuation at slot 23
   *(Strictly gated: requires temporary exemption from the zero-execution boundary).*
3. **Permission for Upstream Multi-Cycle NWP Acquisition:**  
   Formal authorization to lift the midnight restriction in `meps_wind_extractor.py:169` and fetch non-midnight historical MEPS forecasts from MET Norway THREDDS for 2024 evaluation windows.
4. **Permission for Diurnal Conformal Re-Calibration:**  
   Formal authorization to re-calibrate split-conformal coverage multipliers ($Q_{90\_W}$, $Q_{\text{hat\_norm}}$) across intra-day origin splits on 2024-ODD.

---
*Report produced under strictly read-only static inspection. No repository files modified. No execution performed. Awaiting explicit Project Owner instructions.*
