# POLARIS — Offline Optimizer Replay Readiness Protocol & Pre-Execution Specification

**Experiment Identifier:** `EXP-OFFLINE-OPTIMIZER-REPLAY-20261010`  
**Date:** 2026-10-10  
**Status:** Protocol Finalized; Phase A Readiness Audit Passed (Qualified).

---

## 1. Objective and Scope

This protocol governs the offline closed-loop optimizer replay evaluation of the frozen nonlinear Cloud→GHI candidate against the accepted production baseline under the POLARIS microgrid EMS architecture.

- **Baseline (Control):** Causal NWP + Physics solar forecaster ($\gamma = 1.00$, linear attenuation: $\text{GHI} = \text{clearsky\_GHI} \times (1 - \text{cloud\_fraction})$).
- **Candidate:** Non-linear Cloud→GHI corrected forecaster ($\gamma = 0.25$, frozen: $\text{GHI} = \text{clearsky\_GHI} \times (1 - \text{cloud\_fraction})^{0.25}$).
- **Optimizer:** `GAP19HighsNativeOptimizer` (lexicographic multi-objective MILP, 408 variables, 312 constraints: $J_1$ Deficit $\to$ $J_2$ Reserve Shortfall $\to$ $J_3$ Diesel Fuel $\to$ $J_4$ Curtailment).
- **Dispatch Router & Mode Propagation:** Canonical `EMSControlRouter` and `propagate_route_mode`.
- **Realization Execution:** `ResearchRealizationExecutor` enforcing hourly busbar balance ($\text{error} \le 10^{-3}\text{ W}$), battery bounds ($\text{SoC} \in [20\%, 95\%]$), and diesel generator dynamics.

---

## 2. Phase A — Readiness Audit Findings & Disclosures

### 2.1 GAP19 Production Baseline and Tests
- The canonical production optimizer is `GAP19HighsNativeOptimizer` (`system/optimization/implementations/gap19_highs_native.py`).
- Governed regression test suites:
  - `system/tests/test_gap19_j2_option_b.py` (verifies $N=408, M=312$, lexicographic priority $J_1 \to J_2 \to J_3 \to J_4$, and fail-closed inputs). Passed (`test_8_model_structure_N408_M312`).
  - Critical demand adaptation follows the canonical worker formula: $\text{critical\_demand}[t] = \min(\text{ceiling\_w}, \text{total\_demand}[t])$ via `adapt_critical_demand_vector`.

### 2.2 Offline Injection Pathway (Zero Production Code Modification)
- The offline simulation harness `AdaptedClosedLoopRunner` allows clean dependency injection of any `ForecastEngine` adhering to the `ForecastEngine` interface.
- Candidate forecast engine (`CausalNwpCandidateEngine`, $\gamma = 0.25$) is instantiated entirely in user-space offline research code without modifying `system/forecasting/implementations/causal_nwp_physics.py` or any file in `system/`.
- Both arms share identical canonical configurations:
  - `system/config/battery.yaml` (200 kWh, 20% min SoC, 95% max SoC, 92% efficiency)
  - `system/config/diesel.yaml` (10–100 kW, 5.0 L/h base, 0.00025 L/Wh marginal, 2.0 L startup)
  - `system/config/loads.yaml` (11.6 kW critical ceiling)
  - `system/config/solar_pv.yaml` (300 m², 20% efficiency, 0.85 PR, 60 kW cap)

### 2.3 Data Provenance & Physical Realization Qualifications (MANDATORY DISCLOSURE)
- **Solar Realization:** Uses pyranometer-measured downward shortwave irradiance (`actual_SW_IN`) from `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` (SHA-256: `2186382391b84ed5464982e036b0b7bc8208c6818b8131f29a382c6ee149dbb5`), converted to electrical power via the authorized D3 physical transformation ($\min(51.0 \times \text{GHI}, 60000.0\text{ W})$). As audited in Stage 2, physical inverter telemetry is unavailable at Nuolja Middle Station; solar realization is therefore a physical proxy.
- **Wind Realization:** Empirical anemometer/wind turbine power measurements do not exist in the 2025 weather dataset. Uses the canonical POLARIS benchmark synthetic sinusoidal wind profile ($h=1\dots 24$):
  $$\text{wind}[h] = \max(0.0, \text{round}(4500.0 + 5000.0 \sin(h\pi / 6), 2))$$
- **Demand Realization:** Microgrid load telemetry is absent from the weather dataset. Uses the canonical POLARIS benchmark synthetic diurnal load profile ($h=1\dots 24$):
  $$\text{demand}[h] = \max(10000.0, \text{round}(15000.0 + 3000.0 \cos(h\pi / 12), 2))$$
- **Qualification Statement:** This evaluation measures **closed-loop algorithmic and dispatch impact in an offline simulation benchmark**, NOT empirical microgrid field performance. Results must be qualified as *Offline Closed-Loop Simulation Replay on Benchmark Realization Profiles*.

---

## 3. Evaluation Population and Blind-Window Quarantine

- **Total 2025 Origins:** 365 origin days (`2025-01-01 00:00:00` to `2025-12-31 00:00:00`).
- **Protected Blind Period:** 123 origins from `2025-05-01 00:00:00` to `2025-08-31 00:00:00` inclusive.
  - **Quarantine Guarantee:** The blind period is strictly filtered out at data ingestion before any simulation or metric calculation occurs. Zero blind origins are simulated, inspected, or included in any evaluation metric.
- **Eligible Non-Blind Evaluation Population:** Exactly 242 origin days:
  - **Segment 1 (Winter–Spring):** 120 origins (`2025-01-01` to `2025-04-30`).
  - **Segment 2 (Autumn–Early Winter):** 122 origins (`2025-09-01` to `2025-12-31`).

---

## 4. Experimental Arms & Execution Details

| Parameter | Control Arm | Candidate Arm |
|---|---|---|
| Forecaster Model | Causal NWP + Physics ($\gamma = 1.00$) | Causal NWP + Nonlinear Physics ($\gamma = 0.25$) |
| Solar Formulation | $\text{GHI} = \text{CS} \times (1 - C)$ | $\text{GHI} = \text{CS} \times (1 - C)^{0.25}$ |
| Night Zeroing | $\text{Elev} \le 0 \implies \text{GHI} = 0$ | $\text{Elev} \le 0 \implies \text{GHI} = 0$ |
| Optimizer | `GAP19HighsNativeOptimizer` | `GAP19HighsNativeOptimizer` |
| Initial State ($t_0$) | 50% SoC (100 kWh), Diesel OFF, 100 L | 50% SoC (100 kWh), Diesel OFF, 100 L |
| Horizon & Steps | 24 hours rolling, 1 hour step | 24 hours rolling, 1 hour step |
| Evaluated Origins | 240 eligible non-blind origins (proposed amendment; see note below and §6) | 240 eligible non-blind origins (proposed amendment; see note below and §6) |
| Total Hourly Solves | 5,760 solves | 5,760 solves |

> [!NOTE]
> **Population Cross-Reference & Historical Preservation:**  
> The original protocol authorized 242 non-blind origins for static day-ahead evaluation. For this dynamic 24-step receding-horizon closed-loop simulation, 2 boundary origins (April 30 and December 31) are excluded to prevent rolling lookahead leaks into the quarantined blind window and beyond the dataset calendar boundary, respectively. See **Section 6** for the formal proposed scope amendment. This amendment applies strictly to the dynamic replay and explicitly preserves the historical 242-origin static day-ahead validation results and authorizations in Stage 1 and Stage 2 without modification.

---

## 5. Statistical Evaluation Methodology

1. **Paired Differences:** Evaluated per origin:
   $$\Delta \text{Metric} = \text{Metric}_{\text{Candidate}} - \text{Metric}_{\text{Control}}$$
   - Diesel Fuel Consumption (Liters and %)
   - Diesel Operating Hours and Engine Starts
   - Unmet Demand / Deficit ($J_1$ Wh)
   - Governed Reserve Shortfall ($J_2$ Wh)
   - Renewable Curtailment ($J_4$ Wh)
   - Battery Throughput (kWh) and Final SoC (%)
2. **Stationary Bootstrap:**
   - Calendar-gap-aware stratified stationary bootstrap respecting the seasonal segment boundary across the May–August gap:
     - For historical static day-ahead validation: 120 origins in Segment 1 / 122 origins in Segment 2.
     - For proposed dynamic receding-horizon replay (subject to §6 approval): 119 origins in Segment 1 / 121 origins in Segment 2.
   - Mean block length = 10 days.
   - Resamples = 2,000.
   - Seed = `20261010`.
   - 95% Percentile Confidence Interval on paired difference of mean diesel fuel and curtailment.
3. **Success Criteria:**
   - $\Delta \text{Fuel} < 0$ with 95% CI entirely below zero, OR $\Delta \text{Fuel} \le 0$ with reduced curtailment and zero $J_1$ deficit violations.
   - Zero optimizer failures (`OPTIMAL` or `FEASIBLE` on 100% of timesteps).
   - Zero busbar energy balance violations ($> 10^{-3}\text{ W}$).

---

## 6. Proposed Scope Amendment: Population Boundary Correction (PROPOSED — AWAITING PROJECT-LEAD APPROVAL)

### 6.1 Context & Historical Authorization
The overarching research protocol (`experiments/stage4_planner_cf_consistency_2025/cloud_to_ghi_nonlinear_experiment_20261010/CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md §2`) authorized validation on the **242 non-blind 2025 forecast origins** for *static day-ahead forecast evaluation*.

### 6.2 Why 242 Origins Are Unsuitable for Dynamic Receding-Horizon Replay
In dynamic 24-step closed-loop receding-horizon MPC simulation, every origin day executes 24 hourly cycles ($t = 0 \dots 23$). At each step, a forward 24-hour lookahead forecast is constructed:
- Step 0 requests: $[t_0 + 1\text{h}, \dots, t_0 + 24\text{h}]$
- Step 23 requests: $[t_0 + 24\text{h}, \dots, t_0 + 47\text{h}]$ (extending up to 47 hours past the origin day start).

This dynamic lookahead creates two structural boundary collisions:
1. **Origin 2025-04-30 (Summer Blind-Window Quarantine Breach):**  
   At step 23, the 24-hour forward lookahead extends to `2025-05-01 22:00:00`. This generates 276 hourly forecast queries falling into the protected May 1–August 31 blind window. While `actual_SW_IN` outcome values are not queried by the forecaster, querying cloud forecasts from May 1 violates the unconditional quarantine boundary.
2. **Origin 2025-12-31 (Calendar Dataset Termination):**  
   At step 23, the forward lookahead extends to `2026-01-01 22:00:00`. The 2025 weather dataset ends at `2025-12-31 23:00:00`. Looking ahead into 2026 unconditionally fails closed with `CAUSAL_DATA_UNAVAILABLE`.

### 6.3 Corrected Eligible Population (240 Origins)
To preserve 100% blind-window quarantine and respect dataset boundaries without synthetic lookahead wrapping, the eligible dynamic replay population is corrected to exactly **240 origin-days**:
- **Segment 1 (Winter–Spring):** 119 origins (`2025-01-01 00:00:00` to `2025-04-29 00:00:00` inclusive).
  - Maximum lookahead timestamp queried across all 24 steps: `2025-04-30 22:00:00` (zero blind-window queries).
- **Segment 2 (Autumn–Early Winter):** 121 origins (`2025-09-01 00:00:00` to `2025-12-30 00:00:00` inclusive).
  - Maximum lookahead timestamp queried across all 24 steps: `2025-12-31 22:00:00` (zero 2026 queries).
- **Excluded Boundary Seams:** 2 origins (`2025-04-30` and `2025-12-31`).

### 6.4 Scope of Amendment
This correction applies **only** to the dynamic receding-horizon offline optimizer replay (`EXP-OFFLINE-OPTIMIZER-REPLAY-20261010`). It does **not** alter or revise the historical static day-ahead validation population (242 origins) or its accepted results in Stage 1 and Stage 2.

### 6.5 Governance Status
**APPROVED BY PROJECT LEAD (2026-10-10).** Explicit project-lead authorization granted to execute the specific 240-origin dynamic receding-horizon offline optimizer replay under strict offline research boundaries and preserved May 1–August 31, 2025 quarantine. Production promotion, weight modification, and production EMS/MILP changes remain strictly prohibited.

---

## 7. Artifact Persistence, Durability Guarantees, and Failure Observability

To guarantee empirical artifact integrity and prevent partial-write or crash corruption during long-running parallel optimization replays, execution persistence follows a strict multi-tiered durability architecture.

### 7.1 Multi-Tier Durability Hierarchy

The replay runner implements four distinct persistence stages with explicit physical and operating-system semantics:

1. **Tier 1 — In-Memory Generation & Fail-Closed Validation:**
   - Worker processes generate candidate and control realization sequences in memory.
   - Upon receipt by the parent process, every record undergoes complete schema validation (`validate_origin_record`): all 24 expected keys (per `REQUIRED_METRIC_FIELDS`), strict type matching (rejecting boolean-as-int coercion), non-null enforcement on mandatory metrics, and strict finite-number verification (rejecting `NaN`, `+Inf`, and `-Inf`). Any malformed result halts execution immediately.

2. **Tier 2 — File-Level Flush and Media Synchronization (`flush()` + `os.fsync(fileno)`):**
   - For streaming records (`incremental_results.jsonl`), each completed record is written and followed immediately by `flush()` and `os.fsync(fileno)`.
   - For summary artifacts (`OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv` and `OFFLINE_OPTIMIZER_REPLAY_RESULTS.json`), data is written to dedicated temporary staging files (`.tmp`), flushed, and explicitly synchronized via `os.fsync(fileno)`.
   - **Guarantee:** Guarantees that file data and inode block pointers are physically written from OS page cache buffers to persistent non-volatile storage media.

3. **Tier 3 — Atomic Namespace Publication (`os.replace`):**
   - Staged temporary files (`RUN_STATUS.json.tmp`, `*.csv.tmp`, `*.json.tmp`) are swapped into their final publication paths via atomic POSIX rename (`os.replace`).
   - **Guarantee:** Guarantees atomic namespace publication. At no point can concurrent readers observe a partial, truncated, or half-written status file or final summary table.

4. **Tier 4 — Directory Metadata Synchronization (`sync_dir()` via `os.fsync` on directory fd):**
   - After creating, appending to, or replacing files within the run directory (`run_YYYYMMDD_HHMMSS`), the runner opens the directory descriptor (`os.O_RDONLY | os.O_DIRECTORY`) and executes `os.fsync(dfd)`.
   - **Guarantee:** Flushes parent directory entry tables to storage media, guarding against directory entry loss in the event of an abrupt host OS crash or power failure.

### 7.2 Best-Effort Directory Durability Policy (Non-Fatal)

While file-level data durability (Tier 2) and atomic publication (Tier 3) are mandatory, directory metadata synchronization (Tier 4) is governed by a **best-effort durability policy**:

- **Rationale:** Directory fsync support depends on filesystem capabilities and host platform semantics. On certain filesystems (e.g., specific network mounts, tmpfs, non-POSIX abstraction layers, or platforms returning `EINVAL`/`EBADF`), directory descriptor `fsync` may fail despite the underlying file contents and inodes being safely committed to storage.
- **Scientific Impact:** Failure of directory metadata synchronization does not corrupt or alter optimization solver calculations, physical realizations, or file contents. Halting an otherwise valid 240-origin simulation run solely due to a directory metadata fsync refusal would be mathematically unnecessary.
- **Policy:** Directory fsync failures are treated as non-fatal to the optimization process. However, the runner strictly avoids falsely asserting full crash durability when synchronization fails.

### 7.3 Structured Durability Observability & Machine-Readable Evidence

All directory synchronization results are explicitly captured, consumed, and logged:

1. **Immediate Diagnostic Stderr Logging:**
   - Any `OSError` encountered in `sync_dir()` emits an immediate diagnostic warning to `sys.stderr`, identifying the target directory, exception class, and OS error description.

2. **Structured Run Evidence (`RUN_STATUS.json`):**
   - Directory fsync failures are appended to a cumulative, append-only in-memory register `durability_warnings`.
   - Each record contains: `timestamp_utc`, `target_path`, `call_site` (e.g., `update_run_status`, `worker_jsonl_append`, `publish_per_origin_csv`, `publish_results_json`), and `reason`.
   - `RUN_STATUS.json` maintains structured durability state:
     - `"durability_status"`: Set to `"GUARANTEED"` if zero directory sync failures occurred, or `"DEGRADED_DIRECTORY_SYNC_FAILED"` if any failure occurred.
     - `"durability_warnings"`: Complete list of all recorded warning entries.
     - `"durability"` object: Structured summary containing `directory_sync_guaranteed: bool`, `status: str`, `warnings_count: int`, and `warnings: list`.

3. **Invariants Preserved:**
   - **No State Masking:** A degraded durability status never overwrites the run outcome state (`RUNNING`, `COMPLETED`, or `FAILED`). Both run status and durability status are preserved honestly and orthogonally.
   - **Append-Only History:** Earlier durability warnings are never cleared or erased if a subsequent call to `sync_dir()` succeeds.
   - **Recursion Immunity:** When recording a durability warning to `RUN_STATUS.json`, directory synchronization is bypassed (`sync_directory=False`) to guarantee zero recursive error loops.
   - **Primary Exception Preservation:** Failures during status file updates or directory fsync never mask surrounding primary execution exceptions.
   - **Final Artifact Validation Is a Failure Path:** If the final CSV/JSON existence-and-size check fails, `RUN_STATUS.json` is written as `FAILED` (with the validation failure reason) before the exception is raised. `COMPLETED` is never reached on this path.

4. **Known Limitation — `OFFLINE_OPTIMIZER_REPLAY_RESULTS.json`'s Embedded Durability Block Is a Pre-Publication Snapshot:**
   - The results JSON's own `"durability"` object is computed and serialized *before* that same file's temp-write, `os.fsync`, `os.replace`, and directory-fsync attempt occur. It structurally cannot report the outcome of its own publication step — a results JSON cannot describe events that happen after its content is already finalized.
   - If the directory-fsync immediately following the results JSON's own publication fails, that failure is recorded in `RUN_STATUS.json` (which is rewritten after the fact) but will **not** appear in the already-published `OFFLINE_OPTIMIZER_REPLAY_RESULTS.json`'s own `"durability"` block.
   - **`RUN_STATUS.json` in the run directory is the sole authoritative, always-current durability record.** The results JSON's `"durability"` field is informational and may understate the true warning count by exactly this one final sync attempt; it is explicitly labelled as a pre-publication snapshot via its own `"snapshot_disclaimer"` field.
   - This is a deliberate, accepted limitation rather than a defect: no recursive rewrite of the results JSON is performed to make it self-referentially complete, since doing so would reintroduce the same recursion/ordering hazard this hardening is designed to avoid.

---

## 8. Governance and Execution Control Gate

**EXECUTION STATUS: AUTHORIZED FOR OFFLINE BENCHMARK REPLAY (2026-10-10).**  
Technical re-audit passed (32/32 tests), protocol §6 approved by project lead, and execution authorized strictly for the 240-origin offline simulation replay. All production safeguards, quarantine boundaries, and non-promotion constraints remain actively enforced.

---

## 8.1 Provenance-Preserving Artifact Recovery Governance Framework (PROPOSED — AWAITING EXPLICIT PROJECT-LEAD APPROVAL)

### 8.1.1 Separation of Recovery from Native Execution
1. **Permanent Failure State of Original Run:** If an authorized execution terminates with `RUN_STATUS.json = FAILED` due to an artifact publication defect (such as an omitted `os.replace`), that run directory remains permanently `FAILED`. Its status must **never** be retroactively edited, overwritten, or converted to `COMPLETED`.
2. **Distinct Derived Record:** A recovered artifact set is an independently audited, derived record produced in a distinct destination directory (`recovered_run_YYYYMMDD_HHMMSS/`). It is never an in-place mutation of the original run directory.
3. **No Claim of Native Completion:** Recovery documentation must never claim that the original run executed cleanly to completion, nor does recovery substitute for a fresh replay if the project lead mandates native end-to-end execution.

### 8.1.2 Mandatory Recovery Prerequisites
Recovery execution is strictly blocked unless all of the following preconditions are independently verified:
1. **Explicit Project-Lead Authorization:** Formal authorization granting permission to execute the recovery procedure and specifying the exact destination directory.
2. **Verified Test Suite:** Successful synthetic tests demonstrating that the underlying publication logic functions atomically and fails closed across both success and fault-injected paths.
3. **Independent Technical Review:** Independent peer or automated review recorded, or formally documented as pending where external tools are offline.
4. **Source Hash Invariance:** Read-only verification that all source artifacts (`incremental_results.jsonl`, `*.csv.tmp`, `*.json`, `RUN_STATUS.json`) match their recorded SHA-256 baselines exactly.
5. **Full Population & Partition Reconciliation:** 100% verification of origin count (240 origins: 119 Segment 1, 121 Segment 2), sequential ordering, schema adherence, zero blind-window occurrences, and exact correspondence between streaming JSONL and temporary CSV rows.
6. **Aggregate Statistics Reproduction:** Independent verification that aggregate totals, paired differences, and stratified stationary bootstrap confidence intervals recomputed from source records match the results JSON identically.
7. **Failure Cause Documentation:** Verification that the source run failure reason is explicitly documented as a publication-step defect and that numerical solver/simulation integrity is uncompromised.
8. **Deterministic Recovery Tooling:** Execution via a dedicated, audited recovery script whose own source code and hash are recorded in the recovery provenance manifest.
9. **Quarantine Enforcement:** Zero access to quarantined May 1–August 31, 2025 observations or outcomes.

### 8.1.3 Recovery Artifact Requirements
A recovered run directory must contain exactly:
1. `OFFLINE_OPTIMIZER_REPLAY_PER_ORIGIN.csv`: Published atomically via `os.replace` from verified source records.
2. `incremental_results.jsonl`: Bit-identical copy of the source streaming records, preserving the source SHA-256 hash.
3. `OFFLINE_OPTIMIZER_REPLAY_RESULTS.json`: Bit-identical copy of the source aggregate metrics, preserving the source SHA-256 hash.
4. `RECOVERY_MANIFEST.json`: Machine-readable audit manifest specifying:
   - `recovery_id`: Distinct recovery run identifier (e.g., `recovered_run_20261010_093458`).
   - `recovery_status`: Explicit recovery status (e.g. `RECOVERED_AND_RECONCILED`), distinct from native replay completion.
   - `source_run_id` and `source_run_dir`.
   - `source_run_status` (`FAILED`) and `source_failure_reason`.
   - Source SHA-256 hashes for all input files (including source `RUN_STATUS.json`).
   - Published artifact SHA-256 hashes.
   - Recovery tool script path, version, and SHA-256 hash.
   - Timestamp (UTC) and runtime execution environment.
   - Exact verified origin count (240) and segment partitions (119 / 121).
   - Clear confirmation that zero simulations or optimizers were rerun.
   - Clear confirmation that the original source run remains `FAILED`.
   - Independent verification results (reconciliation, bootstrap reproduction, feasibility).
   - Clear statement of scientific decision (`NO SUPPORTED IMPROVEMENT`).

*Note on Status Isolation:* To prevent concurrent tools or automated pipelines from mistaking the recovered directory for a native successful execution, `RUN_STATUS.json` is not copied into the recovery directory root. All status and audit metadata reside authoritatively in `RECOVERY_MANIFEST.json`.


### 8.1.4 Fail-Closed Invariants
1. If any source file hash differs, any schema check fails, or any numeric reconciliation deviates, the recovery tool must abort immediately.
2. Partial publication is strictly prohibited; temporary staging and atomic POSIX replacement apply to all recovered artifacts.
3. Overwriting an existing recovery directory is prohibited (`exist_ok=False`).
4. Under no circumstances may the recovery procedure alter or delete any file in the original run directory.

### 8.1.5 Scientific Decision Rule & Promotion Boundary
1. **Decision Rule Invariance:** Artifact recovery does not alter the preregistered decision rule (§5.3). The candidate model's paired results demonstrate increased unmet load (+333.5 kWh, +1.40%), and the governance verdict remains **`NO SUPPORTED IMPROVEMENT`**.
2. **Non-Promotion:** Artifact recovery is an audit and provenance reconciliation procedure; it does **not** constitute candidate model promotion, production deployment approval, or validation of field microgrid performance.

### 8.1.6 Approval Boundary
**PROPOSED — AWAITING PROJECT-LEAD APPROVAL.** The inclusion of this recovery governance framework in the protocol does not grant permission to execute recovery. Recovery execution remains strictly blocked until explicit project-lead authorization is granted.


