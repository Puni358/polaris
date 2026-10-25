# POLARIS — OD-02 Solar Alignment Forensics & Evidence Report

**Document ID:** `OD02_ALIGNMENT_FORENSICS_REPORT.md`  
**Tracking ID:** `OD02-ALIGNMENT-FORENSICS-2026-10-20`  
**Date:** 2026-10-20  
**Status:** COMPLETE (Strictly Read-Only Forensic Investigation)  
**Governance Invariants:** Baseline `OD-02` frozen; `winner: null` preserved; 2025 blind data quarantined; `tau_cont` unset; zero production/test/MDR code changes performed; zero computational experiments or solver runs executed.

---

## 1. Executive Summary & Classification

This report delivers a comprehensive, evidence-backed forensic investigation into whether the +1-hour solar forecast shift in `_align_n6_bundle_od02` (mapping raw Candidate N6 indices $1 \dots 23 \to$ dispatch steps $0 \dots 22$, with fallback `0.0 W/m²` injected at step 23) represents a deliberate physical time-alignment rule or an inherited indexing defect.

### Explicit Classification: **Documented intentional alignment**
*(Governing the Adapter and Dispatch Harness Layer, with an upstream architectural inheritance ambiguity)*

**Classification Rationale:**  
1. **At the Adapter & Governance Layer:** The +1-hour shift and terminal zero were introduced **together** on 2026-10-19 as an **explicitly documented, intentional alignment decision** (Decision `OD-02`, recorded in Pass 22 and formally frozen in Pass 23 of `POLARIS_MASTER_DECISION_REGISTER.md`). The shift was specifically engineered to reconcile a known convention discrepancy between the upstream Candidate N6 pipeline (which outputs predictions stamped $t_0 + 0\text{h} \dots t_0 + 23\text{h}$) and the downstream simulation engine (`realized_loader.py` and `simulator.py`), whose dispatch step $k$ advances over interval $[t_0 + k, t_0 + k + 1]$ and evaluates against actual environmental observations stamped $t_0 + k + 1$ (starting at $t_0 + 1\text{h}$).
2. **At the Upstream Pipeline Layer:** Upstream model construction (`s81_corrected_solar.py` lines 40–48) explicitly adopted the convention `horizon_hour=1 == forecast_start + 0h`. Whether that upstream convention was itself mathematically optimal for training on hourly SITES observations (where label $HH:00$ is the mean of period-ending 10-minute readings covering $[(HH-1):50, HH:50]$ centered at $HH:20$) cannot be established without the original training data contract. However, within the runtime architecture, `_align_n6_bundle_od02` was not an accidental off-by-one bug: it was a deliberate, tested, and ratified adapter created to prevent feeding a $t_0 + 0\text{h}$ prediction into a dispatch step transitioning over $[t_0, t_0 + 1\text{h}]$ that consumes actuals at $t_0 + 1\text{h}$.

---

## 2. Answers to the Twelve Forensic Review Questions

### Question 1: Which commit first introduced the one-hour solar shift?
**Repository Finding:**  
In this working tree (`/home/punith-bs/01polaris (Copy)`), Git commit history is unavailable (`fatal: your current branch 'master' does not have any commits yet`; `.git/refs/heads` and `.git/refs/tags` are empty; `git fsck` confirms zero commits in the object store). POLARIS development operated under a strict zero-commit protocol across passes 18–23 ("Nothing staged, committed, or pushed by this pass").  
**Authoritative Provenance:**  
Traced through the Master Decision Register and companion reports, the one-hour solar shift was introduced in **Pass 22** of `POLARIS_MASTER_DECISION_REGISTER.md` (dated 2026-10-19) under **Decision OD-02** ("Pilot Pre-Execution Owner Decisions"), implemented in `system/evaluation/n6_multi_origin_harness/adapters.py` (lines 606–696).

### Question 2: Which commit first introduced the terminal zero?
**Repository Finding:**  
Like the shift itself, the terminal zero (`[0.0]` at index 23) has no Git commit SHA in this workspace.  
**Authoritative Provenance:**  
The terminal zero was introduced in the **exact same Pass 22 (2026-10-19)** under **Decision OD-02**, as an indivisible structural component of the `_align_timeseries_od02` function (`aligned_ts.point = pts[1:] + [0.0]`).

### Question 3: Were they introduced together or separately?
**Repository Finding:**  
They were introduced **together in a single implementation**. Because `GAP19HighsNativeOptimizer` strictly enforces a fixed 24-step horizon ($H=24$, 408 variables), dropping index 0 (`pts[1:]`) reduced array length from 24 to 23. Appending `[0.0]` at index 23 was the mechanism chosen to maintain the mandatory 24-element schema without introducing runtime dependencies on offline clear-sky decomposition files (`POLARIS_MASTER_DECISION_REGISTER.md` Section 38.1.2).

### Question 4: Do commit messages, comments, tests, or decision records establish an intentional physical rationale?
**Repository Finding:**  
Yes, extensive documentation establishes an intentional physical and operational rationale:
1. **Decision Register (MDR Section 38.1.2 & 39.1.1):** Explicitly records approval of OD-02 to "retain the existing `LocalBaselineForecastEngine` final-slot solar output ($0.0\text{ W/m}^2$) for dispatch step 23 ($t_0 + 24\text{h}$, horizon $h=25$) when using the 24-horizon N6 model artifact" and rejects introducing offline unverified clear-sky decomposition files.
2. **Documented Arctic Limitation:** The register explicitly acknowledges that during Arctic polar day (late May through mid-July at $68.35^\circ\text{N}$), midnight solar irradiance is non-zero ($1.2 \dots 6.8\text{ W/m}^2$), but accepts clamping slot 23 to zero as a defined boundary condition.
3. **Adapter & Test Comments:** `adapters.py` (lines 641–653) and `test_n6_multi_origin_harness_adapters.py` (lines 1414–1478) explicitly state that solar horizons 1..23 are shifted to dispatch steps 0..22 to match simulator dispatch steps, while demand, wind, and EBR remain unshifted to preserve Policy B parity.

### Question 5: What timestamp and physical interval does N6 index 0 represent?
**Repository Finding:**  
- **Nominal Timestamp:** For an origin $t_0$, N6 index 0 has timestamp $t_0 + 0\text{h}$ (`(origin_dt + timedelta(hours=h-1))` with $h=1$, per `n6_solar.py` lines 537–540).
- **Physical Interval:** N6 was trained on targets from `POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv`. Authoritative D7 audit evidence (`d7_out.txt` line 20) proves that SITES hourly observations labeled $HH:00$ are the arithmetic mean of 10-minute period-ending readings from $HH:00$ to $HH:50$. Those six readings physically cover $[(HH-1):50, HH:50]$ with midpoint at $HH:20$ local time (fixed UTC+1). Therefore, N6 index 0 targets the interval $[23:50\text{ prev day}, 00:50\text{ origin day}]$ centered at $00:20\text{ UTC+1}$ ($23:20\text{ UTC}$).

### Question 6: What physical interval does optimizer step 0 consume?
**Repository Finding:**  
- In `gap19_highs_native.py` (lines 253–266), step 0 transitions the battery from $E(0) = \text{initial\_e\_wh}$ (measured at $t_0$) to $E_{\text{next}}[0]$ (the state at $t_0 + 1\text{h}$) across $\Delta t = 1.0\text{ h}$.
- The optimizer treats `solar_gen[0]` as the continuous average power generated during that first forward operational hour $[t_0, t_0 + 1\text{h}]$ (e.g. `00:00:00Z` to `01:00:00Z`).

### Question 7: What physical interval does optimizer step 23 consume?
**Repository Finding:**  
- Step 23 is the final operational hour of the dispatch horizon: $[t_0 + 23\text{h}, t_0 + 24\text{h}]$ (e.g. `23:00:00Z` to `24:00:00Z`).
- In GAP19, step 23 transitions battery energy to $E_{\text{next}}[23]$, which is strictly bounded by Layer C's terminal reserve constraint: $E_{\text{next}}[23] + s_{J2}[23] \ge \max(E_{\text{ebr}}[23], E_{\text{term}}) + E_{\min}$, where $E_{\text{term}} = \text{initial\_e\_wh} - \text{min\_e\_wh}$ under Decision OD-01.

### Question 8: How does the realized-solar loader map those steps to actual observations?
**Repository Finding:**  
- In `realized_loader.py` lines 218–227, the loop explicitly specifies:
  `step_dt = dt0 + datetime.timedelta(hours=h + 1)`
  `step_ts = step_dt.strftime("%Y-%m-%dT%H:%M:%SZ")`
- For step $h=0$, it queries fixture observation at $t_0 + 1\text{h}$ (`01:00:00Z`).
- For step $h=22$, it queries fixture observation at $t_0 + 23\text{h}$ (`23:00:00Z`).
- For step $h=23$, it queries fixture observation at $t_0 + 24\text{h}$ (`24:00:00Z` / `00:00:00Z next day`).
- Thus, the simulation evaluates step 0 against the environmental observation stamped $t_0 + 1\text{h}$.

### Question 9: Is the current shift supported by a documented contract, contradicted by the source evidence, or still ambiguous?
**Repository Finding:**  
- **Supported by Documented Contract:** The shift is formally documented, tested, and frozen in `POLARIS_MASTER_DECISION_REGISTER.md` Passes 22 and 23.
- **Source Alignment:** The shift resolves a direct naming/indexing collision between N6 (which stamped horizon 1 as $t_0 + 0\text{h}$) and `realized_loader.py` (which evaluates step 0 at $t_0 + 1\text{h}$). By shifting N6 rows $1..23 \to 0..22$, N6 row 1 (stamped $t_0 + 1\text{h}$) is paired with dispatch step 0 (evaluated against $t_0 + 1\text{h}$).
- **Asymmetry Ambiguity:** While solar was shifted forward by 1 hour, wind, demand, and EBR remained unshifted. For wind and demand, this is because `LocalBaselineForecastEngine` naturally generates predictions for $t_0 + 1\text{h} \dots t_0 + 24\text{h}$ (`baseline.py` lines 57–59). However, for EBR, `_compute_ebr_reserve()` calculated lookahead $[k, \min(k+6, 24))$ on unshifted indices, leaving the statistical coverage of EBR under shifted solar an open limitation acknowledged in MDR Section 39.1.3.

### Question 10: Could direct mapping of N6 indices 0–23 to dispatch steps 0–23 be physically correct?
**Repository Finding:**  
- **No, not without an upstream timestamp/target redefinition.**
- If N6 indices $0 \dots 23$ were mapped directly to dispatch steps $0 \dots 23$, dispatch step 0 (representing the forward transition $[t_0, t_0 + 1\text{h}]$) would receive N6 index 0.
- But N6 index 0 targets the observation stamped $t_0$ (which physically covers $[t_0 - 10\text{min}, t_0 + 50\text{min}]$, centered at $t_0 + 20\text{min}$ local time).
- More critically, in receding-horizon control, the simulator executes dispatch step 0 and compares the outcome against the realized fixture at $t_0 + 1\text{h}$. Feeding N6 index 0 into step 0 would introduce a 1-hour lag relative to the realized environmental observation at $t_0 + 1\text{h}$.
- Therefore, direct mapping is only physically valid if N6 index 0 was retrained or re-indexed such that its target is explicitly the forward interval $[t_0, t_0 + 1\text{h}]$ matching fixture query $t_0 + 1\text{h}$.

### Question 11: What existing evidence would be needed to decide whether the shift should be removed?
**Repository Finding:**  
To definitively decide whether to remove the shift, the project would require:
1. **The Upstream Training Code:** The exact script that created `candidate_k_2024_clean_matrix.parquet` and trained `stage8_1_CORRECTED_candidate_37feature_model.joblib`. Specifically, did `horizon_hour = 1` train against target $SW\_IN(t_0)$ or $SW\_IN(t_0 + 1\text{h})$?
2. **Empirical Horizon Accuracy Audit:** An offline verification calculating the Mean Absolute Error (MAE) of N6 index 0 vs actuals at $t_0$ vs actuals at $t_0 + 1\text{h}$.
3. **Dispatch Sensitivity Results (Gate C):** The execution of Gate C diagnostic comparing Variant V0 (OD-02 baseline) against an unshifted counterfactual to measure whether first-action diesel dispatch ($u_0$) or battery throughput changes.

### Question 12: What is the smallest unresolved evidence gap?
**Repository Finding:**  
The smallest unresolved evidence gap is **the training target alignment contract for `horizon_hour = 1` in `candidate_k_2024_clean_matrix.parquet`**: specifically, confirming whether the feature row `horizon_hour = 1` was paired with SITES hourly label `00:00` or `01:00` during gradient boosting model training.

---

## 3. Structured Evidence Categorization

### 3.1 Repository-Confirmed Facts
1. In `adapters.py` lines 641–695, `_align_n6_bundle_od02` shifts `solar_irradiance.point` and `solar_generation.point` by `pts[1:] + [0.0]` and advances timestamps from `[t0..t23]` to `[t1..t24]`.
2. In `adapters.py` lines 651–652, `demand`, `demand_critical`, `wind_generation`, and `metadata["ebr_target_wh"]` are preserved completely unshifted.
3. In `n6_solar.py` lines 537–540, timestamps are constructed as `origin_dt + timedelta(hours=h - 1)` for $h \in [1, 25)$, meaning raw index 0 is stamped $t_0 + 0\text{h}$ and raw index 23 is stamped $t_0 + 23\text{h}$.
4. In `baseline.py` lines 57–59, `LocalBaselineForecastEngine` constructs timestamps as `origin_dt + timedelta(hours=h)` for $h \in [1, 25)$, meaning index 0 is stamped $t_0 + 1\text{h}$ and index 23 is stamped $t_0 + 24\text{h}$.
5. In `realized_loader.py` lines 218–227, transition step $h$ strictly queries the observation stamped `dt0 + timedelta(hours=h + 1)`. Step 0 queries $t_0 + 1\text{h}$; step 23 queries $t_0 + 24\text{h}$.
6. In `gap19_highs_native.py` lines 153–171, horizon length is strictly hardcoded to $H=24$ (408 total variables, 312 constraints).
7. Decision OD-02 is formally approved and frozen in `POLARIS_MASTER_DECISION_REGISTER.md` Sections 38 and 39.
8. In this repository copy, local Git commit history is unavailable (`fatal: your current branch 'master' does not have any commits yet`), and zero commit objects exist in `.git/objects`.

### 3.2 Existing Report Claims Supported by Artifacts
1. **Fixed UTC+1 SITES Convention:** SITES raw meteorological data has fixed offset UTC+1 with no DST, and 10-minute values are period-ending (`D7_VERIFICATION_REPORT.md` Section 1, supported by `d7_out.txt` lines 1–15).
2. **Floor Aggregation:** SITES hourly file `POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv` was generated by grouping raw readings with `floor('h')` (`HH:00..HH:50 -> HH:00`), matching to within $3.34 \times 10^{-11}\text{ W/m}^2$ (`d7_out.txt` line 20).
3. **Polar Day Midnight Sun:** During polar day (June 1–21 at $68.36^\circ\text{N}$), solar elevation at midnight ranges from $+0.50^\circ$ to $+1.83^\circ$, with actual irradiance $1.17 \dots 6.82\text{ W/m}^2$ (`SPEC_OD02_DIAGNOSTIC_PRE_EXECUTION.md` Section 1.2; `GATE2_RHC_ARCHITECTURE_ASSESSMENT.md` Section 3B).
4. **Conformal Scale Provenance:** $Q_{90,W} = 1.5702$ was calibrated bit-for-bit on 2024-ODD ($N=173$ origins, quantile score 1.570194625) using unshifted feature rows (`evaluate_l2_conformal_ebr_2025.py`; MDR Section 39.1.2).

### 3.3 Inferences
1. **Origin of the Shift:** Because `LocalBaselineForecastEngine` and `realized_loader.py` used $[t_0 + 1\text{h} \dots t_0 + 24\text{h}]$, while `n6_solar.py` generated $[t_0 + 0\text{h} \dots t_0 + 23\text{h}]$, the adapter author shifted N6 to match the baseline engine's timestamp range and prevent passing a $t_0 + 0\text{h}$ value to a step evaluated at $t_0 + 1\text{h}$.
2. **Origin of the Terminal Zero:** Because shifting by 1 dropped the first element and left a 23-element array, and because GAP19 strictly fails on anything other than 24 elements, the author appended `0.0` at slot 23, rationalizing it as consistent with the baseline engine's night-time solar output.
3. **EBR Unshifted Rationale:** The decision to keep EBR unshifted was made because `_compute_ebr_reserve()` already applied a 6-hour rolling window starting at index $t$, which the authors interpreted as lookahead $[t, \min(t+6, 24))$ from the decision origin, even though solar point generation was shifted.

### 3.4 Unresolved Questions
1. Did the training matrix `candidate_k_2024_clean_matrix.parquet` train `horizon_hour = 1` against SITES $SW\_IN(t_0)$ or $SW\_IN(t_0 + 1\text{h})$?
2. Does the terminal zero fallback at step 23 alter the first control action $u_0$ or diesel consumption in receding-horizon dispatch? (Gate C was designed to answer this).
3. Does shifting EBR by +1 hour improve empirical conformal coverage under the shifted solar forecast?

---

## 4. Governance & Safety Summary

- **Zero Modifications:** No source code, tests, configuration files, Master Decision Register, or security settings were altered.
- **Zero Execution:** No optimizers, HiGHS solvers, simulation loops, or diagnostic scripts were executed.
- **Data Quarantine Preserved:** Quarantined 2025 data was not accessed, read, hashed, or staged.
- **Invariants Maintained:** `winner: null` preserved; `DSL-01` `epsilon_tol` remains unset; `tau_cont` remains unset; Decision `OD-02` remains frozen.
