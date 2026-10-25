# Execution Audit & Reproducibility Record

**Research Branch**: `POLARIS — FORECAST-ERROR CROSS-YEAR CONDITIONAL STABILITY AUDIT`  
**Execution Date**: 2026-10-05T07:28:00+05:30  
**Environment**: Linux 6.6.137+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.6.137-1+rpt1 (2026-02-17) aarch64  
**Python Runtime**: Python 3.12.8 (virtual environment at `.venv`)  
**Primary Script**: `scratch/execute_stability_audit.py` (checksum logged below)  

---

## 1. Input Provenance & Dataset Integrity

- **Path**: `candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv`
- **SHA256**: `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab`
- **Verification**: Dataset read directly in binary mode, verified match against frozen Candidate F historical reference.
- **Data Volume**: 1,369 forecast origins, 26,011 rows total, 15,730 daylight observations.

---

## 2. Governance Boundary Enforcement

| Governance Check | Status | Verification Detail |
|:---|:---:|:---|
| Production Files Modified | **NONE** | Git status confirms zero modifications to `production/`, `governance/`, or `stage8_1_station_tuning/` |
| GAP19 / EMS Modified | **NONE** | No MILP constraints, battery dispatch parameters, or controller code touched |
| Controller Experiments Run | **NONE** | Audit was 100% statistical and offline; zero simulation runs launched |
| Blind 2023 Tuning | **NONE** | 2023 was evaluated purely out-of-sample in LOYO tests; zero thresholds tuned on 2023 |
| Class B Telemetry Usage | **QUARANTINED** | `ctx_last_obs`, `ctx_std_3h`, `ctx_mean_24h` excluded from all conditioning regimes |
| Noncausal Target Usage | **FORBIDDEN** | Future observations (`actual`) strictly isolated to evaluation targets |
| Blocked Horizons | **ENFORCED** | Missing horizons $k \in [20..24]$ remain marked as BLOCKED |

---

## 3. Generated Artifact Integrity

| Filename | Size (Bytes) | SHA256 Checksum | Operational Description |
|:---|:---:|:---|:---|
| `CAUSAL_STATE_INVENTORY.csv` | 3,232 | `3ee01726bdecbdf3c66145f82929d0b01d65b3411dd37674d911e488d9549f13` | Audit classification of 22 dataset columns into causal classes A, B, and C. |
| `CAUSAL_STATE_INVENTORY.md` | 8,678 | `5d7fd619e51b95b47375d1213565f49c9bea23e4423374101bbd21b8e93f9f3a` | Comprehensive documentation of causal classifications and telemetry latency notes. |
| `YEARLY_ERROR_DISTRIBUTIONS.csv` | 1,070 | `4089cdd834c93ea890b3a163ece053704186806f849634fc6f06bceb302561b2` | Yearly moments, quantiles (q05..q99), run lengths, and cumulative error distributions (2020-2023). |
| `STATE_CONDITIONED_ERROR_SUMMARY.csv` | 10,247 | `95e53bdd1e0f315f1d1a44adfd22015c0cbdbe43c79b1c8030518b91e8177b1f` | Conditional error distributions partitioned by solar elevation, cloud fraction, clearness index, cs-ghi, and season. |
| `CROSS_YEAR_STABILITY_MATRIX.csv` | 2,890 | `39bc18bd0a6a71d425e6fcbbc84aa7bf8812d0c65fe28894235001ae1824c9f9` | Cross-year stability metrics (spreads, scale ratios, pairwise Wasserstein distances) across regimes. |
| `LEAVE_ONE_YEAR_OUT_TRANSFER.csv` | 11,226 | `09b412b2a38d3a7e71561d15497ddd5a10dededefa060770dddbd6469ab1d939` | Leave-one-year-out cross-validation transfer evaluation for 2020, 2021, 2022, and 2023. |
| `TEMPORAL_DEPENDENCE_CONDITIONAL.csv` | 2,386 | `5fd673dd573389689fe2e08748bcca4ce9d7a2dbd7ee924e4c7a63da6fa2913d` | Raw and post-AR(1) innovation autocorrelation structure within conditioned regimes. |
| `MULTI_YEAR_CALIBRATION_DIAGNOSTIC.csv` | 818 | `d073a964f180ec65e9ca3f89cc6d7cc8e2a327f3a703ac6480f1930440c8b4ea` | Diagnostic comparing single-year (2022) vs pooled multi-year (2020-2022) calibration evaluated on blind 2023. |
| `CROSS_YEAR_ERROR_STABILITY_RESULTS.json` | 44,748 | `56ff181f6a286f833951807c997e99ce00a58876bd1e9ef2d753e80d411daa97` | Machine-readable comprehensive results package for the stability audit. |
| `CROSS_YEAR_ERROR_STABILITY_AUDIT.md` | 25,879 | `bcaef4e1b1a6e21a18d265de506cd0649fd41c989bd4662e7d54906e42151d29` | Full research audit report synthesizing methodology, findings, and formal status block. |
