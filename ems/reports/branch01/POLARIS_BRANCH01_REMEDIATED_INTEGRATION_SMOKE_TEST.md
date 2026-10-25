# POLARIS — Branch 01 Remediated Integration Smoke Test Audit Report

**Date**: 2026-09-21 07:35:07 UTC
**Trajectory**: `TRAJ_20240121` (`2024-01-21T00:00:00Z`)
**Result**: **SMOKE_TEST = PASS**

---

### Forensic Accounting & Non-Solar Inheritance Gates

| Gate / Requirement | Status | Verification Detail |
|---|---|---|
| **CONTRACT_PRESERVING_REMEDIATION** | **PASS** | Minimal Branch01 integration edit; 100% frozen model/control/optimizer/simulator/fixture |
| **EXACT_DEMAND_SOURCE** | **PASS** | `POLARIS_LOCAL_BASELINE_DEMAND_PERSISTENCE_V1` (`baseline.py` SHA `905c644...`) |
| **EXACT_WIND_SOURCE** | **PASS** | `POLARIS_LOCAL_BASELINE_WIND_PERSISTENCE_V1` (`baseline.py` SHA `905c644...`) |
| **DEMAND_CAUSALITY** | **PASS** | Evaluated causally at origin $t_0$ only |
| **WIND_CAUSALITY** | **PASS** | Evaluated causally at origin $t_0$ only |
| **DEMAND_CONTROL_TREATMENT_IDENTITY** | **PASS** | `MAX_ABS_DEMAND_DIFF` = 0.0 W |
| **WIND_CONTROL_TREATMENT_IDENTITY** | **PASS** | `MAX_ABS_WIND_DIFF` = 0.0 W |
| **DEMAND_CONTROL_TREATMENT_HASH_EQUAL** | **PASS** | 24/24 MPC cycles 100% hash equal |
| **WIND_CONTROL_TREATMENT_HASH_EQUAL** | **PASS** | 24/24 MPC cycles 100% hash equal |
| **DEMAND_REGENERATED_BY_TREATMENT** | **NO** | Passed directly from Control `ForecastBundle` |
| **WIND_REGENERATED_BY_TREATMENT** | **NO** | Passed directly from Control `ForecastBundle` |
| **FUTURE_TRUTH_ACCESS** | **NONE** | No ground-truth leakage into forecasting |
| **ZERO_PLACEHOLDER_FALLBACK** | **ABSENT** | Removed zero-array fallback; fail-closed enforced |
| **SOLAR_ONLY_INTERVENTION** | **PASS** | Branch01 solar forecast differs from Stage8.1 where models diverge |
| **ACTUAL_LOAD_ACCOUNTING** | **PASS** | Physical load served = actual demand - actual unmet load |
| **ENERGY_ACCOUNTING** | **PASS** | 0.0 kWh unexplained residual |
| **BATTERY_ACCOUNTING** | **PASS** | SOC bounds and efficiency preserved |

---

### 24-Step MPC Trajectory Accounting Summary

- **Control Diesel Generation**: 568.247 kWh
- **Treatment Diesel Generation**: 837.193 kWh
- **Control Load Served**: 469.74 kWh
- **Treatment Load Served**: 750.905 kWh

---

```
REMEDIATED_EMS_INTEGRATION =
READY_FOR_CAMPAIGN
```
