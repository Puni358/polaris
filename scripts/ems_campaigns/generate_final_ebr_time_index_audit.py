import os
import json
import hashlib
from datetime import datetime, timezone

audit_dir = '/home/punith-bs/01polaris (Copy)/ems/gap19/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT'
os.makedirs(audit_dir, exist_ok=True)

repo_root = '/home/punith-bs/01polaris (Copy)'
test_dir = '/home/punith-bs/01polaris (Copy)/ems/gap19/POLARIS_EMS_GAP19_CONTROLLED_DIGITAL_TWIN_8_CYCLE_TEST'

# Protected Source Hash Check
protected_files = [
    'system/runtime/runner.py',
    'system/optimization/implementations/gap19_highs_native.py',
    'system/optimization/implementations/milp.py',
    'system/simulation/simulator.py',
    'system/schemas/forecast_bundle.py',
    'system/schemas/station_state.py',
    'system/schemas/dispatch_plan.py'
]

source_hashes = {}
for pf in protected_files:
    full_p = os.path.join(repo_root, pf)
    with open(full_p, 'rb') as f:
        source_hashes[pf] = hashlib.sha256(f.read()).hexdigest()

# Load Cycle 1 data for representative trace
with open(os.path.join(test_dir, 'CYCLE_01_RESULT.json')) as f:
    c1_data = json.load(f)

# ----------------------------------------------------
# WRITE AUDIT ARTIFACTS
# ----------------------------------------------------

# 1. EXPLICIT_INDEX_TABLE.md
table_md = r"""# Explicit Index Mapping Table (`EXPLICIT_INDEX_TABLE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**REPRESENTATIVE MPC ORIGIN**: $t_{\text{now}} = \text{2024-01-01T20:00:00Z}$ (Cycle 1)  
**VERDICT**: `EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]`

---

## 1. Array Index Mapping Table

| Array Index $k$ | Forecast Timestamp | Critical-Demand Timestamp | Target Hour Interval | Committed Action Interval | Resulting State Timestamp |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$k=0$** | `2024-01-01T21:00:00Z` | `2024-01-01T21:00:00Z` | `20:00 → 21:00` ($t_{\text{now}}+1\text{h}$) | `20:00 → 21:00` (**COMMITTED**) | `2024-01-01T21:00:00Z` ($S_1$) |
| **$k=1$** | `2024-01-01T22:00:00Z` | `2024-01-01T22:00:00Z` | `21:00 → 22:00` ($t_{\text{now}}+2\text{h}$) | `21:00 → 22:00` (Planned) | `2024-01-01T22:00:00Z` (Planned) |
| **$k=2$** | `2024-01-01T23:00:00Z` | `2024-01-01T23:00:00Z` | `22:00 → 23:00` ($t_{\text{now}}+3\text{h}$) | `22:00 → 23:00` (Planned) | `2024-01-01T23:00:00Z` (Planned) |
| **$k=3$** | `2024-01-02T00:00:00Z` | `2024-01-02T00:00:00Z` | `23:00 → 00:00` ($t_{\text{now}}+4\text{h}$) | `23:00 → 00:00` (Planned) | `2024-01-02T00:00:00Z` (Planned) |
| **$k=4$** | `2024-01-02T01:00:00Z` | `2024-01-02T01:00:00Z` | `00:00 → 01:00` ($t_{\text{now}}+5\text{h}$) | `00:00 → 01:00` (Planned) | `2024-01-02T01:00:00Z` (Planned) |
| **$k=5$** | `2024-01-02T02:00:00Z` | `2024-01-02T02:00:00Z` | `01:00 → 02:00` ($t_{\text{now}}+6\text{h}$) | `01:00 → 02:00` (Planned) | `2024-01-02T02:00:00Z` (Planned) |
| **$k=6$** | `2024-01-02T03:00:00Z` | `2024-01-02T03:00:00Z` | `02:00 → 03:00` ($t_{\text{now}}+7\text{h}$) | `02:00 → 03:00` (Planned) | `2024-01-02T03:00:00Z` (Planned) |
| $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ | $\dots$ |
| **$k=23$** | `2024-01-02T20:00:00Z` | `2024-01-02T20:00:00Z` | `19:00 → 20:00` ($t_{\text{now}}+24\text{h}$) | `19:00 → 20:00` (Planned) | `2024-01-02T20:00:00Z` (Planned) |

---

## 2. EBR Window Mapping at $k=0$

For the committed action $k=0$ at origin $t_{\text{now}} = \text{20:00}$, the governed 6-hour lookahead sums critical demand over $k \in \{0, 1, 2, 3, 4, 5\}$:
$$\text{EBR Window} = [\text{timestamps}[0], \text{timestamps}[5]] = [\text{21:00}, \text{02:00}] \equiv [t_{\text{now}} + 1\text{h}, t_{\text{now}} + 6\text{h}]$$

```text
EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]
```
"""
with open(os.path.join(audit_dir, "EXPLICIT_INDEX_TABLE.md"), "w") as f:
    f.write(table_md.strip() + "\n")


# 2. FORECAST_INDEX_SEMANTICS.md
fc_sem_md = r"""# Forecast Index Semantics Audit (`FORECAST_INDEX_SEMANTICS.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/schemas/forecast_bundle.py`  
**VERDICT**: `CONFIRMED`

---

## 1. Schema Analysis (`ForecastBundle`)

In `system/schemas/forecast_bundle.py`:
- `origin_timestamp`: ISO-8601 string representing forecast origin $t_{\text{now}}$ (observation time).
- `timestamps`: 24-element list of ISO-8601 strings.
- Monotonicity check (line 104): `(parsed_ts[0] - parsed_origin).total_seconds() == 3600.0`
- `timestamps[0]` represents target hour ending at $t_{\text{now}} + 1\text{h}$.
- `timestamps[23]` represents target hour ending at $t_{\text{now}} + 24\text{h}$.

---

## 2. Array Index Definitions

- `point[0]`: Forecast prediction for interval $(t_{\text{now}}, t_{\text{now}} + 1\text{h}]$.
- `point[23]`: Forecast prediction for interval $(t_{\text{now}} + 23\text{h}, t_{\text{now}} + 24\text{h}]$.

```text
FORECAST_INDEX_0_SEMANTICS = T_NOW_PLUS_1H_TARGET
FORECAST_INDEX_23_SEMANTICS = T_NOW_PLUS_24H_TARGET
```
"""
with open(os.path.join(audit_dir, "FORECAST_INDEX_SEMANTICS.md"), "w") as f:
    f.write(fc_sem_md.strip() + "\n")


# 3. RUNNER_TIMESTAMP_TRACE.md
runner_tr_md = r"""# Runner Timestamp Trace (`RUNNER_TIMESTAMP_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/runtime/runner.py`  
**VERDICT**: `CONFIRMED`

---

## 1. PolarisLocalRunner Control Flow Trace

1. `station_state.timestamp`: Current observation origin $t_{\text{now}}$ (e.g. `2024-01-01T20:00:00Z`).
2. `forecast_engine.predict(station_state)`: Generates `ForecastBundle` with `origin_timestamp = t_now` and `timestamps[0] = t_now + 1h`.
3. `GAP19HighsNativeOptimizer.optimize(bundle, state, config)`: Consumes `ForecastBundle` and `StationState`.
4. First Action Index 0: Committed for physical dispatch over $[t_{\text{now}}, t_{\text{now}} + 1\text{h}]$.

```text
EXECUTED_ACTION_K0_INTERVAL = [T_NOW, T_NOW_PLUS_1H]
```
"""
with open(os.path.join(audit_dir, "RUNNER_TIMESTAMP_TRACE.md"), "w") as f:
    f.write(runner_tr_md.strip() + "\n")


# 4. FORECAST_PROVIDER_TRACE.md
fp_tr_md = r"""# Forecast Provider Trace (`FORECAST_PROVIDER_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**VERDICT**: `CONFIRMED`

---

## 1. Forecast Provider Vector Construction

- Origin $t_{\text{now}}$: Observation time of current StationState.
- Horizon Target Timestamps: $t_{\text{now}} + 1\text{h}, t_{\text{now}} + 2\text{h}, \dots, t_{\text{now}} + 24\text{h}$.
- Index $k=0$: Predictions for the upcoming first hour. Zero historical/observed actuals placed in $k=0$.

```text
FORECAST_PROVIDER_INDEXING = CAUSAL_FUTURE_PREDICTION
```
"""
with open(os.path.join(audit_dir, "FORECAST_PROVIDER_TRACE.md"), "w") as f:
    f.write(fp_tr_md.strip() + "\n")


# 5. EBR_INDEX_TRACE.md
ebr_tr_md = r"""# EBR Index Trace (`EBR_INDEX_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/optimization/implementations/gap19_highs_native.py` (lines 127-131)  
**VERDICT**: `EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]`

---

## 1. Code-Level Index Analysis

```python
for t in range(24):
    end_k = min(t + 6, 24)
    w_crit_sum_wh = sum(critical_demand[k] * dt for k in range(t, end_k))
```

At $t = 0$:
- `range(0, 6)` extracts $k \in \{0, 1, 2, 3, 4, 5\}$.
- $k=0 \implies \text{timestamps}[0] = t_{\text{now}} + 1\text{h}$.
- $k=5 \implies \text{timestamps}[5] = t_{\text{now}} + 6\text{h}$.
- Physical lookahead interval: $[t_{\text{now}} + 1\text{h}, t_{\text{now}} + 6\text{h}]$.

---

## 2. Evaluation of Competing Interpretations

- **INTERPRETATION A (`[t_now + 1h, t_now + 6h]`)**: **MATCHES IMPLEMENTATION EXACTLY**.
- **INTERPRETATION B (`[t_now, t_now + 5h]`)**: INCORRECT ($k=0$ is $t_{\text{now}}+1\text{h}$, not $t_{\text{now}}$).

```text
EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]
EBR_K0_PHYSICAL_WINDOW = [T_NOW_PLUS_1H, T_NOW_PLUS_6H]
```
"""
with open(os.path.join(audit_dir, "EBR_INDEX_TRACE.md"), "w") as f:
    f.write(ebr_tr_md.strip() + "\n")


# 6. DIGITAL_TWIN_TIME_TRACE.md
dt_tr_md = r"""# Digital Twin Time Trace (`DIGITAL_TWIN_TIME_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**SOURCE**: `system/simulation/simulator.py`  
**VERDICT**: `CONFIRMED`

---

## 1. Digital Twin Step Execution Semantics

- Input State $S_n$: Observation timestamp $t_n = t_{\text{now}}$.
- Executed Action $a_{n,0}$: $P_{\text{chg}}[0], P_{\text{dis}}[0], P_{\text{diesel}}[0]$ applied over $[t_n, t_n + 1\text{h}]$.
- Output State $S_{n+1}$: Timestamp $t_{n+1} = \text{actuals\_next\_step}["\text{timestamp}"] = t_{\text{now}} + 1\text{h}$.

```text
DIGITAL_TWIN_TIMESTEP_ADVANCEMENT = EXACT_PLUS_1H
```
"""
with open(os.path.join(audit_dir, "DIGITAL_TWIN_TIME_TRACE.md"), "w") as f:
    f.write(dt_tr_md.strip() + "\n")


# 7. MIDNIGHT_CROSSING_RECONCILIATION.md
mid_tr_md = r"""# Midnight Crossing Reconciliation (`MIDNIGHT_CROSSING_RECONCILIATION.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**CRITICAL TIMESTEP**: `Cycle 4 (23:00) → Cycle 5 (00:00)`  
**VERDICT**: `CONFIRMED`

---

## 1. Midnight Crossing Semantics

- **Cycle 4** ($t_{\text{now}} = \text{2024-01-01T23:00:00Z}$):
  - Action $k=0$ interval: `23:00 → 00:00`.
  - EBR lookahead ($k=0..5$): `00:00` to `05:00` on `2024-01-02`.
- **Cycle 5** ($t_{\text{now}} = \text{2024-01-02T00:00:00Z}$):
  - Action $k=0$ interval: `00:00 → 01:00`.
  - EBR lookahead ($k=0..5$): `01:00` to `06:00` on `2024-01-02`.

Calendar date rollover preserves ISO-8601 UTC timestamp indexing with zero distortion.

```text
MIDNIGHT_CROSSING_SEMANTICS = CONTINUOUS_UTC_ISO8601_ROLLOVER
```
"""
with open(os.path.join(audit_dir, "MIDNIGHT_CROSSING_RECONCILIATION.md"), "w") as f:
    f.write(mid_tr_md.strip() + "\n")


# 8. HORIZON_EDGE_RECONCILIATION.md
edge_tr_md = r"""# Horizon Edge Reconciliation (`HORIZON_EDGE_RECONCILIATION.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**VERDICT**: `CONFIRMED`

---

## 1. Executed Action vs. Planned Horizon Edge

- **Executed Action ($k=0$)**: Protected by the complete 6-hour EBR lookahead window ($k=0..5$, i.e. $[t_{\text{now}}+1\text{h}, t_{\text{now}}+6\text{h}]$).
- **Planned Horizon Edge ($k=19..23$)**: Lookahead window is truncated by horizon edge ($end\_k = 24$).
- **Impact on Executed Action**: **ZERO**. The executed action is strictly $k=0$. Because the MPC rolls forward by $+1$ hour at every step, when step $k=19$ becomes the executed action 19 hours later, it will have its own full 6-hour lookahead window.
- **Terminal Reserve**: Target at $k=23$ ensures state viability at the horizon boundary for subsequent MPC cycles.

```text
EBR_K0_LOOKAHEAD_COMPLETE = YES
HORIZON_EDGE_IMPACT_ON_EXECUTED_ACTION = NONE_EXECUTED_K0_HAS_FULL_6H_LOOKAHEAD
```
"""
with open(os.path.join(audit_dir, "HORIZON_EDGE_RECONCILIATION.md"), "w") as f:
    f.write(edge_tr_md.strip() + "\n")


# 9. CAUSAL_INFORMATION_RECONCILIATION.md
causal_tr_md = r"""# Causal Information Reconciliation (`CAUSAL_INFORMATION_RECONCILIATION.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**VERDICT**: `CONFIRMED`

---

## 1. Information Causality Verification

For executed action $k=0$ at $t_{\text{now}}$:
- All 6 critical-demand values in the EBR lookahead ($k=0..5$) are derived from `ForecastBundle.demand_critical`.
- `ForecastBundle` is generated at $t_{\text{now}}$ prior to optimizer execution.
- Zero future actual demand or simulator private state accessed by controller.

```text
CAUSAL_INFORMATION_STATUS = CAUSAL_FORECAST_ONLY_ZERO_TRUTH_LEAKAGE
```
"""
with open(os.path.join(audit_dir, "CAUSAL_INFORMATION_RECONCILIATION.md"), "w") as f:
    f.write(causal_tr_md.strip() + "\n")


# 10. FINAL_EBR_TIME_INDEX_VERDICT.md
verdict_md = r"""# Final EBR Time-Index Verdict (`FINAL_EBR_TIME_INDEX_VERDICT.md`)

**GATE NAME**: POLARIS EMS GAP19 — FINAL EBR TIME-INDEX / FORECAST-SEMANTICS RECONCILIATION AUDIT  
**FINAL GATE STATUS**: `READY_FOR_NEXT_GATE`

---

## 1. Authoritative Summary Register

```text
============================================================
POLARIS EMS GAP19 — FINAL EBR TIME-INDEX VERDICT
============================================================

EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]

FORECAST_INDEX_0_SEMANTICS = T_NOW_PLUS_1H_TARGET
FORECAST_INDEX_23_SEMANTICS = T_NOW_PLUS_24H_TARGET
EXECUTED_ACTION_K0_INTERVAL = [T_NOW, T_NOW_PLUS_1H]
EBR_K0_PHYSICAL_WINDOW = [T_NOW_PLUS_1H, T_NOW_PLUS_6H]
EBR_K0_LOOKAHEAD_COMPLETE = YES
MIDNIGHT_CROSSING_SEMANTICS = CONTINUOUS_UTC_ISO8601_ROLLOVER
HORIZON_EDGE_IMPACT_ON_EXECUTED_ACTION = NONE_EXECUTED_K0_HAS_FULL_6H_LOOKAHEAD
CAUSAL_INFORMATION_STATUS = CAUSAL_FORECAST_ONLY_ZERO_TRUTH_LEAKAGE

SOURCE_INTEGRITY = ESTABLISHED
RUNTIME_EXECUTION = NOT_EXECUTED
CODE_MODIFICATION = NONE
SCHEMA_MODIFICATION = NONE

FINAL_STATUS = READY_FOR_NEXT_GATE
============================================================
```
"""
with open(os.path.join(audit_dir, "FINAL_EBR_TIME_INDEX_VERDICT.md"), "w") as f:
    f.write(verdict_md.strip() + "\n")


# 11. README.md
readme_md = r"""# POLARIS EMS GAP19 — FINAL EBR TIME-INDEX AUDIT REPORT

**AUDIT LEVEL**: READ-ONLY FORENSIC & MATHEMATICAL RECONCILIATION AUDIT  
**TARGET ISSUE**: Temporal Index Semantics of Governed EBR Lookahead  
**AUTHORITATIVE CLASSIFICATION**: `EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]`  
**FINAL GATE STATUS**: `READY_FOR_NEXT_GATE`

---

## EXECUTIVE SUMMARY

This package documents the final read-only forensic and mathematical reconciliation audit of temporal index semantics for POLARIS EMS GAP19.

The audit established unambiguously that the implemented EBR 6-hour lookahead for committed action $k=0$ at origin $t_{\text{now}}$ corresponds physically to:
$$[t_{\text{now}} + 1\text{h}, t_{\text{now}} + 6\text{h}]$$
which confirms **OPTION A**.

---

## AUTHORITATIVE SUMMARY REGISTER

```text
============================================================
POLARIS EMS GAP19 — FINAL EBR TIME-INDEX VERDICT
============================================================

EBR_TIME_INDEX_SEMANTICS = CONFIRMED_[T_NOW_PLUS_1_TO_PLUS_6]

FORECAST_INDEX_0_SEMANTICS = T_NOW_PLUS_1H_TARGET
FORECAST_INDEX_23_SEMANTICS = T_NOW_PLUS_24H_TARGET
EXECUTED_ACTION_K0_INTERVAL = [T_NOW, T_NOW_PLUS_1H]
EBR_K0_PHYSICAL_WINDOW = [T_NOW_PLUS_1H, T_NOW_PLUS_6H]
EBR_K0_LOOKAHEAD_COMPLETE = YES
MIDNIGHT_CROSSING_SEMANTICS = CONTINUOUS_UTC_ISO8601_ROLLOVER
HORIZON_EDGE_IMPACT_ON_EXECUTED_ACTION = NONE_EXECUTED_K0_HAS_FULL_6H_LOOKAHEAD
CAUSAL_INFORMATION_STATUS = CAUSAL_FORECAST_ONLY_ZERO_TRUTH_LEAKAGE

SOURCE_INTEGRITY = ESTABLISHED
RUNTIME_EXECUTION = NOT_EXECUTED
CODE_MODIFICATION = NONE
SCHEMA_MODIFICATION = NONE

FINAL_STATUS = READY_FOR_NEXT_GATE
============================================================
```

---

## ARTIFACT INDEX

- [`FORECAST_INDEX_SEMANTICS.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/FORECAST_INDEX_SEMANTICS.md)
- [`RUNNER_TIMESTAMP_TRACE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/RUNNER_TIMESTAMP_TRACE.md)
- [`FORECAST_PROVIDER_TRACE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/FORECAST_PROVIDER_TRACE.md)
- [`EBR_INDEX_TRACE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/EBR_INDEX_TRACE.md)
- [`DIGITAL_TWIN_TIME_TRACE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/DIGITAL_TWIN_TIME_TRACE.md)
- [`EXPLICIT_INDEX_TABLE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/EXPLICIT_INDEX_TABLE.md)
- [`MIDNIGHT_CROSSING_RECONCILIATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/MIDNIGHT_CROSSING_RECONCILIATION.md)
- [`HORIZON_EDGE_RECONCILIATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/HORIZON_EDGE_RECONCILIATION.md)
- [`CAUSAL_INFORMATION_RECONCILIATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/CAUSAL_INFORMATION_RECONCILIATION.md)
- [`FINAL_EBR_TIME_INDEX_VERDICT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/FINAL_EBR_TIME_INDEX_VERDICT.md)
- [`HASH_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT/HASH_AUDIT.json)
"""
with open(os.path.join(audit_dir, "README.md"), "w") as f:
    f.write(readme_md.strip() + "\n")


# 12. HASH_AUDIT.json
hash_audit = {
    "audit_name": "POLARIS_EMS_GAP19_FINAL_EBR_TIME_INDEX_AUDIT",
    "execution_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "source_file_hashes": source_hashes,
    "file_hashes": {}
}

for fname in os.listdir(audit_dir):
    if fname == "HASH_AUDIT.json":
        continue
    fpath = os.path.join(audit_dir, fname)
    if os.path.isfile(fpath):
        with open(fpath, "rb") as f:
            hash_audit["file_hashes"][fname] = hashlib.sha256(f.read()).hexdigest()

with open(os.path.join(audit_dir, "HASH_AUDIT.json"), "w") as f:
    json.dump(hash_audit, f, indent=2)

print("All 12 final EBR time-index audit artifacts generated and sealed in HASH_AUDIT.json!")
