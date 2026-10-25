import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

base_dir = Path(".")

# 1. Generate updated ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.json
json_data = {
    "analysis_id": "POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "governance_flags": {
        "V4G_EXECUTION": "COMPLETE",
        "V4G_FORENSIC_AUDIT": "VALID",
        "V4G_MECHANISM_ANALYSIS": "COMPLETE",
        "NEW_EXPERIMENT": False,
        "V4G_RERUN": False,
        "V3_RERUN": False,
        "CONTROL_RERUN": False,
        "PARAMETER_TUNING": False,
        "SOURCE_FILES_MODIFIED": False,
        "RAW_EXECUTION_EVIDENCE_MODIFIED": False,
        "CAUSAL_OVERCLAIM_REMOVED": True
    },
    "frozen_experiment_recap": {
        "n_origins": 173,
        "arms": {
            "control": {
                "engine": "LocalBaselineForecastEngine",
                "gamma": 1.0,
                "weights": "w_t = 1.0, for all t",
                "total_fuel_l": 4671.0,
                "mean_fuel_l_per_origin": 27.0
            },
            "v3_reference": {
                "engine": "Stage81ForecastEngine",
                "gamma": 0.95,
                "weights": "w_t = 0.95^t",
                "total_fuel_l": 4149.97,
                "mean_fuel_l_per_origin": 23.99
            },
            "v4g_candidate": {
                "engine": "Stage81ForecastEngine",
                "weights": "w_13 = 0.5133, w_t = 1.0 for t != 13",
                "total_fuel_l": 5579.99,
                "mean_fuel_l_per_origin": 32.25
            }
        },
        "primary_paired_comparison_v4g_minus_v3": {
            "mean_difference_liters": 8.2660,
            "median_difference_liters": 5.1300,
            "bootstrap_95_ci_liters": [6.7356, 9.8166],
            "wilcoxon_stat": 15.0,
            "p_value": 8.645153e-18,
            "paired_counts": {
                "positive_v4g_higher": 96,
                "negative_v4g_lower": 3,
                "zero_equal": 74
            }
        }
    },
    "data_availability_audit": {
        "forecast_vectors": "AVAILABLE",
        "forecast_horizon_errors": "PARTIALLY_AVAILABLE",
        "forecast_differences": "AVAILABLE",
        "optimizer_objective_status": "AVAILABLE",
        "dispatch_plan": "PARTIALLY_AVAILABLE",
        "diesel_commitment": "AVAILABLE",
        "diesel_start_stop_events": "AVAILABLE",
        "diesel_power": "AVAILABLE",
        "diesel_runtime": "NOT_AVAILABLE",
        "battery_charge": "AVAILABLE",
        "battery_discharge": "AVAILABLE",
        "soc": "AVAILABLE",
        "battery_throughput": "AVAILABLE",
        "renewable_available": "PARTIALLY_AVAILABLE",
        "renewable_used": "AVAILABLE",
        "renewable_curtailment": "AVAILABLE",
        "load": "PARTIALLY_AVAILABLE",
        "served_load": "AVAILABLE",
        "unmet_load": "AVAILABLE",
        "cumulative_diesel_fuel": "AVAILABLE",
        "timestep_level_fuel_increment": "AVAILABLE",
        "initial_state": "AVAILABLE",
        "hidden_truth": "AVAILABLE",
        "optimizer_inputs": "AVAILABLE"
    },
    "objective_weight_comparison": {
        "v3_weights": [round(0.95**t, 6) for t in range(24)],
        "v4g_weights": [0.5133 if t == 13 else 1.0 for t in range(24)],
        "t13_comparison": {
            "w_v3_13": 0.513342,
            "w_v4g_13": 0.513300,
            "abs_difference": -0.000042,
            "rel_difference_pct": -0.0082
        },
        "horizons_where_v4g_differs_from_v3": "23 of 24 decision indices (all t except t=0 and t=13)",
        "compound_intervention_statement": "V4.G does not provide a causal isolation test of h=14 relative to V3, because the V3 and V4.G objective vectors differ at 23 of 24 decision indices. The t=13 weights themselves are essentially identical."
    },
    "timestep_dispatch_divergence": {
        "first_commitment_divergence_timestep_median": 9.0,
        "first_power_divergence_timestep_median": 9.0,
        "first_soc_divergence_timestep_median": 8.0,
        "total_diesel_commitment_steps": {
            "control": 346,
            "v3_reference": 233,
            "v4g_candidate": 312
        },
        "curtailment_kwh": {
            "control": 30686.74,
            "v3_reference": 3745.89,
            "v4g_candidate": 10131.06
        }
    },
    "mechanism_evidence_matrix": [
        {
            "mechanism": "Forecast Vector Identity (V3 == V4.G)",
            "evidence": "100% identical Stage8.1 solar forecast vectors across all 173 origins and 4,152 timesteps.",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Confirms identical inputs; differences are downstream of objective weights."
        },
        {
            "mechanism": "V4.G Objective Weight Structure",
            "evidence": "w_13 = 0.5133, w_t = 1.0 for t != 13 across all MPC solves.",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Pre-declared frozen parameter specification."
        },
        {
            "mechanism": "V3 / V4.G Difference at 23 of 24 Objective Indices",
            "evidence": "V3 uses w_t = 0.95^t whereas V4.G uses w_t = 1.0 for t != 13. The two vectors differ at 23 of 24 decision timesteps.",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Mathematical property of objective formulation."
        },
        {
            "mechanism": "t=13 Weight Equivalence",
            "evidence": "w_V3(13) = 0.95^13 = 0.513342 vs w_V4G(13) = 0.513300 (difference < 0.000042).",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Numerical value equality."
        },
        {
            "mechanism": "Earlier Diesel Commitment",
            "evidence": "V4.G exhibited earlier diesel commitment than V3 under the tested synthetic EMS environment (median divergence step k=9).",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Observed execution behavior in digital twin."
        },
        {
            "mechanism": "Increased Diesel Commitment Timesteps",
            "evidence": "Diesel commitment occurred over 312 timesteps in V4.G versus 233 timesteps in V3, a difference of +79 timesteps (+33.9%).",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Direct accounting quantity from raw telemetry."
        },
        {
            "mechanism": "Increased Renewable Curtailment",
            "evidence": "V4.G exhibited higher renewable curtailment than V3: 10,131.06 kWh versus 3,745.89 kWh (+170.5%).",
            "classification": "A — DIRECTLY OBSERVED",
            "limitation": "Direct accounting quantity from raw telemetry."
        },
        {
            "mechanism": "Specific Causal Attribution of Diesel Increase to Restored Late-Horizon Weights",
            "evidence": "Relative to V3, V4.G restores full objective weighting at all timesteps except t=13, associated with earlier diesel commitment.",
            "classification": "C — ASSOCIATION ONLY",
            "limitation": "The preserved evidence establishes their occurrence under the V4.G objective structure but does not by itself isolate which individual weight changes produced them."
        },
        {
            "mechanism": "Specific Causal Attribution to t=13 / h=14",
            "evidence": "V3 and V4.G assign virtually identical weight at t=13 (0.513342 vs 0.513300), while differing at the other 23 decision indices.",
            "classification": "E — NOT SUPPORTED",
            "limitation": "V4.G is a compound weight intervention relative to V3."
        },
        {
            "mechanism": "Global Statement that Distributed V3 Discounting Causes Lower Fuel",
            "evidence": "Distributed discounting in V3 is associated with lower fuel, but individual horizon contributions are unisolated.",
            "classification": "D — NOT IDENTIFIABLE FROM THIS EXPERIMENT",
            "limitation": "Experiment tested compound single-notch vector, not single-index isolated components."
        }
    ],
    "secondary_metric_validation": {
        "diesel_energy_kwh": {"status": "INDEPENDENTLY_RECONSTRUCTED", "v3": 9222.15, "v4g": 12399.98},
        "renewable_curtailment_kwh": {"status": "INDEPENDENTLY_RECONSTRUCTED", "v3": 3745.89, "v4g": 10131.06},
        "battery_throughput_kwh": {"status": "INDEPENDENTLY_RECONSTRUCTED", "v3": 17495.27, "v4g": 20019.28},
        "unmet_critical_load_kwh": {"status": "INDEPENDENTLY_RECONSTRUCTED", "v3": 0.00, "v4g": 0.00}
    },
    "hypothesis_assessment": {
        "hypothesis": "V3's lower fuel use is primarily caused by discounting the t=13/h=14 horizon.",
        "verdict": "E — NOT SUPPORTED",
        "explanation": "The V4.G result does not support attribution of V3's lower fuel use to the isolated t=13/h=14 weight. V3 and V4.G assign virtually identical weight at t=13, while differing at the other 23 decision indices. Therefore the observed V4.G increase in diesel use cannot be uniquely attributed to the t=13 weight from this experiment."
    },
    "final_scientific_interpretation": "V4.G was a valid controlled objective-weight intervention, but it was not a pure h=14 isolation test relative to V3. The V4.G and V3 weights are essentially identical at t=13, while differing at 23 of 24 decision indices. V4.G nevertheless produced a directly observed increase in diesel fuel use, earlier/more extensive diesel commitment, and higher renewable curtailment under the controlled synthetic EMS environment. These findings establish downstream differences associated with the V4.G objective structure, but the contribution of any individual horizon — including h=14 — is not causally isolated by this experiment."
}

json_path = base_dir / "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=2)

json_sha256 = hashlib.sha256(json_path.read_bytes()).hexdigest()

# 2. Generate updated ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.md
md_content = """# POLARIS Stage8.1 -> EMS V4.G Post-Execution Mechanism Forensic Analysis Report
## Authoritative Read-Only Forensic Analysis of Completed V4.G Empirical Experiment

```yaml
V4G_EXECUTION: COMPLETE
V4G_FORENSIC_AUDIT: VALID
V4G_MECHANISM_ANALYSIS: COMPLETE
NEW_EXPERIMENT: FALSE
V4G_RERUN: FALSE
V3_RERUN: FALSE
CONTROL_RERUN: FALSE
PARAMETER_TUNING: FALSE
SOURCE_FILES_MODIFIED: FALSE
RAW_EXECUTION_EVIDENCE_MODIFIED: FALSE
CAUSAL_OVERCLAIM_REMOVED: TRUE
```

---

## 1. Executive Summary

This report performs an independent, read-only forensic analysis of the completed **POLARIS V4.G empirical experiment** ($N=173$ paired 24-hour origins, 3 arms, 4,152 timesteps per arm).

The analysis investigates the physical and mathematical pathways underlying the primary empirical result: **V4.G Candidate ($w_{13}=0.5133, w_{t \\ne 13}=1.0$) produced $+8.2660\\text{ L/origin}$ higher mean diesel fuel consumption than V3 Reference ($\gamma=0.95$)**.

### Key Forensic Findings:
1. **Inputs Identity**: Arm 2 (V3 Reference) and Arm 3 (V4.G Candidate) received **100% identical Stage8.1 empirical solar forecast vectors** across all 173 origins and 4,152 timesteps.
2. **At $t=13$, V3 and V4.G Weights are Virtually Identical**: $w_{V3, 13} = 0.95^{13} \\approx 0.513342$ versus $w_{V4G, 13} = 0.513300$ (difference $< 0.000042$).
3. **Compound Weight Intervention**: V4.G does **not** provide a causal isolation test of $h=14$ relative to V3, because the V3 and V4.G objective vectors differ at **23 of 24 decision indices**. The $t=13$ weights themselves are essentially identical.
4. **Observed Dispatch Differences**: Relative to V3, V4.G restores full objective weighting at all timesteps except $t=13$. Under the V4.G execution, earlier diesel commitment was directly observed, with 312 diesel-commitment timesteps versus 233 under V3 (+33.9%). V4.G also exhibited higher renewable curtailment than V3: $10,131.06\\text{ kWh}$ versus $3,745.89\\text{ kWh}$ (+170.5%). The preserved evidence establishes an association between the V4.G objective-weight structure and the observed dispatch difference, but does not independently isolate a causal contribution from the restored late-horizon weights.

---

## 2. Frozen Experiment Recap

| Arm | Forecast Engine | Objective Weight Vector ($w_t$) | Mean Fuel (L / Origin) | Total Fuel (L) | Commitment Steps |
|---|---|---|---|---|---|
| **Arm 1 — Control** | `LocalBaselineForecastEngine` | $\gamma = 1.0 \\implies w_t = 1.0, \\forall t$ | $27.00\\text{ L}$ | $4,671.00\\text{ L}$ | 346 |
| **Arm 2 — V3 Reference** | `Stage81ForecastEngine` | $\gamma = 0.95 \\implies w_t = 0.95^t$ | $23.99\\text{ L}$ | $4,149.97\\text{ L}$ | 233 |
| **Arm 3 — V4.G Candidate** | `Stage81ForecastEngine` | $w_{13} = 0.5133, w_{t \\ne 13} = 1.0$ | $32.25\\text{ L}$ | $5,579.99\\text{ L}$ | 312 |

### Primary Paired Comparison (V4.G Candidate minus V3 Reference):
- **Mean Difference ($\bar{\delta}$)**: $+8.2660\\text{ L / origin}$
- **Median Difference**: $+5.1300\\text{ L / origin}$
- **95% Bootstrap Confidence Interval**: $[+6.7356\\text{ L}, +9.8166\\text{ L}]$
- **Wilcoxon Signed-Rank Test**: $W = 15.0, p = 8.645153 \\times 10^{-18}$
- **Paired Counts ($N=173$)**: Positive ($\delta_i > 0$): 96 | Negative ($\delta_i < 0$): 3 | Zero ($\delta_i = 0$): 74

---

## 3. Data Availability Audit

| Variable | Forensic Status | Telemetry Field Source |
|---|---|---|
| **Forecast Vectors** | `AVAILABLE` | `treatment_forecast_vector_24`, `control_forecast_vector_24` |
| **Forecast Horizon Errors** | `PARTIALLY_AVAILABLE` | `treatment_forecast_error_h1` (h=1 direct; h=2..24 reconstructable) |
| **Forecast Differences** | `AVAILABLE` | `forecast_difference_h1` |
| **Optimizer Objective / Status** | `AVAILABLE` | `optimizer_status`, `objective_value`, `constraint_status` |
| **Dispatch Plan** | `PARTIALLY_AVAILABLE` | Executed $h=1$ decisions in telemetry |
| **Diesel Commitment** | `AVAILABLE` | `diesel_commitment`, `v3_diesel_commitment`, `ctrl_diesel_commitment` |
| **Diesel Start / Stop Events** | `AVAILABLE` | `startup_event`, `shutdown_event` |
| **Diesel Power** | `AVAILABLE` | `h1_diesel_power`, `v3_h1_diesel_power`, `ctrl_h1_diesel_power` |
| **Diesel Runtime** | `NOT_AVAILABLE` | Continuous run duration not logged directly per step |
| **Battery Charge / Discharge** | `AVAILABLE` | `h1_battery_charge_power`, `h1_battery_discharge_power` |
| **State of Charge (SOC)** | `AVAILABLE` | `soc_before`, `soc_after`, `v3_soc_after`, `ctrl_soc_after` |
| **Battery Throughput** | `AVAILABLE` | `cumulative_battery_throughput_after` |
| **Renewable Available** | `PARTIALLY_AVAILABLE` | `actual_solar_truth` (wind modeled as deterministic sine) |
| **Renewable Used / Curtailment**| `AVAILABLE` | `h1_renewable_dispatch`, `h1_renewable_curtailment`, `v3_h1_renewable_curtailment` |
| **Served / Unmet Load** | `AVAILABLE` | `h1_served_load`, `h1_unmet_load` |
| **Cumulative Diesel Fuel** | `AVAILABLE` | `cumulative_diesel_fuel_after`, `v3_cumulative_diesel_fuel_after` |
| **Initial State & Hidden Truth** | `AVAILABLE` | `soc_before` at $k=0$, `actual_solar_truth` sequence |

---

## 4. V3 vs. V4.G Objective Weight Comparison

| Timestep $t$ | V3 Weight ($0.95^t$) | V4.G Weight | Absolute Diff ($w_{V4G} - w_{V3}$) | Relative Diff |
|---|---|---|---|---|
| $t = 0$ | $1.000000$ | $1.000000$ | $+0.000000$ | $0.0\%$ |
| $t = 1$ | $0.950000$ | $1.000000$ | $+0.050000$ | $+5.3\%$ |
| $t = 2$ | $0.902500$ | $1.000000$ | $+0.097500$ | $+10.8\%$ |
| $t = 5$ | $0.773781$ | $1.000000$ | $+0.226219$ | $+29.2\%$ |
| $t = 10$ | $0.598737$ | $1.000000$ | $+0.401263$ | $+67.0\%$ |
| $t = 12$ | $0.540360$ | $1.000000$ | $+0.459640$ | $+85.1\%$ |
| **$t = 13$** | **$0.513342$** | **$0.513300$** | **$-0.000042$** | **$-0.01\%$** |
| $t = 14$ | $0.487675$ | $1.000000$ | $+0.512325$ | $+105.1\%$ |
| $t = 18$ | $0.397214$ | $1.000000$ | $+0.602786$ | $+151.8\%$ |
| $t = 23$ | $0.307357$ | $1.000000$ | $+0.692643$ | $+225.4\%$ |

### Structural Weighting Analysis:
1. **Virtually Identical Weight at $t=13$**: At $t=13$, V3's exponential weight ($0.95^{13} \\approx 0.513342$) and V4.G's weight ($0.513300$) differ by less than $0.000042$.
2. **Compound Intervention**: V4.G does not provide a causal isolation test of $h=14$ relative to V3, because the V3 and V4.G objective vectors differ at 23 of 24 decision indices. The $t=13$ weights themselves are essentially identical.

---

## 5. Dispatch & Optimizer Divergence Analysis

- **Observed Earlier Commitment**: V4.G exhibited earlier diesel commitment than V3 under the tested synthetic EMS environment. Diesel commitment occurred over 312 timesteps in V4.G versus 233 timesteps in V3, a difference of 79 timesteps (+33.9%).
- **Observed Renewable Curtailment**: V4.G also exhibited higher renewable curtailment than V3: $10,131.06\text{ kWh}$ versus $3,745.89\text{ kWh}$ (+170.5%). These are directly observed downstream differences. The preserved evidence establishes their occurrence under the V4.G objective structure but does not by itself isolate which individual weight changes produced them.
- **Timing Distribution**: Median first commitment divergence occurred at $k = 9.0$.

---

## 6. Origin-Level Heterogeneity Analysis

- **Distribution of Paired Differences ($\delta_i = \\text{fuel}_{\\text{V4G}, i} - \\text{fuel}_{\\text{V3}, i}$)**:
  - 25th Percentile: $0.00\text{ L}$
  - Median (50th Percentile): $+5.1300\text{ L}$
  - 75th Percentile: $+16.5200\text{ L}$
  - Max Increase: $+39.5700\text{ L}$ (Origin 5)
  - Max Decrease: $-4.4700\text{ L}$ (Origin 136)

---

## 7. Critical Hypothesis Test

> **Hypothesis**: *"V3's lower fuel use is primarily caused by discounting the $t=13 / h=14$ horizon."*

### Forensic Verdict: **CLASSIFICATION E — NOT SUPPORTED**

### Calibrated Explanation:
The V4.G result does not support attribution of V3's lower fuel use to the isolated $t=13/h=14$ weight. V3 and V4.G assign virtually identical weight at $t=13$, while differing at the other 23 decision indices. Therefore the observed V4.G increase in diesel use cannot be uniquely attributed to the $t=13$ weight from this experiment.

---

## 8. Mechanism Evidence Matrix

| Mechanism / Claim | Forensic Evidence | Classification | Limitation / Calibration |
|---|---|---|---|
| **Forecast Vector Identity (V3 == V4.G)** | 100% identical Stage8.1 solar forecast vectors across all 173 origins and 4,152 timesteps. | `A — DIRECTLY OBSERVED` | Confirms identical inputs; differences are downstream of objective weights. |
| **V4.G Objective Weight Structure** | $w_{13} = 0.5133, w_t = 1.0$ for $t \\ne 13$ across all MPC solves. | `A — DIRECTLY OBSERVED` | Pre-declared frozen parameter specification. |
| **V3/V4.G Difference at 23 of 24 Objective Indices** | V3 uses $w_t = 0.95^t$ whereas V4.G uses $w_t = 1.0$ for $t \\ne 13$. The two vectors differ at 23 of 24 decision timesteps. | `A — DIRECTLY OBSERVED` | Mathematical property of objective formulation. |
| **$t=13$ Weight Equivalence** | $w_{V3}(13) = 0.95^{13} = 0.513342$ vs $w_{V4G}(13) = 0.513300$ (difference $< 0.000042$). | `A — DIRECTLY OBSERVED` | Numerical value equality. |
| **Earlier Diesel Commitment** | V4.G exhibited earlier diesel commitment than V3 under the tested synthetic EMS environment (median divergence step $k=9$). | `A — DIRECTLY OBSERVED` | Observed execution behavior in digital twin. |
| **Increased Diesel Commitment Timesteps** | Diesel commitment occurred over 312 timesteps in V4.G versus 233 timesteps in V3, a difference of +79 timesteps (+33.9%). | `A — DIRECTLY OBSERVED` | Direct accounting quantity from raw telemetry. |
| **Increased Renewable Curtailment** | V4.G exhibited higher renewable curtailment than V3: $10,131.06\text{ kWh}$ versus $3,745.89\text{ kWh}$ (+170.5%). | `A — DIRECTLY OBSERVED` | Direct accounting quantity from raw telemetry. |
| **Specific Causal Attribution of Diesel Increase to Restored Late-Horizon Weights** | Relative to V3, V4.G restores full objective weighting at all timesteps except $t=13$, associated with earlier diesel commitment. | `C — ASSOCIATION ONLY` | Preserved evidence establishes occurrence under V4.G structure but does not by itself isolate which individual weight changes produced them. |
| **Specific Causal Attribution to $t=13 / h=14$** | V3 and V4.G assign virtually identical weight at $t=13$ ($0.513342$ vs $0.513300$), while differing at the other 23 decision indices. | `E — NOT SUPPORTED` | V4.G is a compound weight intervention relative to V3. |
| **Global Statement that Distributed V3 Discounting Causes Lower Fuel** | Distributed discounting in V3 is associated with lower fuel, but individual horizon contributions are unisolated. | `D — NOT IDENTIFIABLE FROM THIS EXPERIMENT` | The intervention changes 23 of 24 objective weights relative to V3, preventing attribution of the downstream fuel difference to any single horizon. |

---

## 9. Secondary Metric Validation

| Secondary Metric | Status | V3 Reference Value | V4.G Candidate Value | Accounting / Physical Classification |
|---|---|---|---|---|
| **Diesel Energy (kWh)** | `INDEPENDENTLY_RECONSTRUCTED` | $9,222.15\text{ kWh}$ | $12,399.98\text{ kWh}$ | Physical energy delivered by generator |
| **Renewable Curtailment (kWh)** | `INDEPENDENTLY_RECONSTRUCTED` | $3,745.89\text{ kWh}$ | $10,131.06\text{ kWh}$ | Accounting quantity (Available Solar/Wind - Used) |
| **Battery Throughput (kWh)** | `INDEPENDENTLY_RECONSTRUCTED` | $17,495.27\text{ kWh}$ | $20,019.28\text{ kWh}$ | Accounting quantity (Sum of discharge kWh) |
| **Unmet Critical Load (kWh)** | `INDEPENDENTLY_RECONSTRUCTED` | $0.00\text{ kWh}$ | $0.00\text{ kWh}$ | Physical served load deficit |

---

## 10. Central Scientific Conclusion & Claim Boundary

V4.G demonstrates that replacing V3's exponentially discounted objective vector with a single-notch vector — $w_{13}=0.5133$ and all other weights equal to $1.0$ — does not reproduce V3's downstream fuel outcome. Under the tested synthetic EMS environment, V4.G produced higher diesel fuel use than V3 ($+8.266\text{ L/origin}$ mean paired difference). Because the two objective vectors differ at 23 of 24 indices, this result cannot be interpreted as an isolated causal test of $h=14$. The evidence instead indicates that the distributed structure of the V3 horizon weighting and/or its interaction with the remaining objective terms is associated with the observed downstream behavior, while the contribution of any individual horizon remains unisolated.

V4.G was a valid controlled objective-weight intervention, but it was not a pure $h=14$ isolation test relative to V3. The V4.G and V3 weights are essentially identical at $t=13$, while differing at 23 of 24 decision indices. V4.G nevertheless produced a directly observed increase in diesel fuel use, earlier/more extensive diesel commitment, and higher renewable curtailment under the controlled synthetic EMS environment. These findings establish downstream differences associated with the V4.G objective structure, but the contribution of any individual horizon — including $h=14$ — is not causally isolated by this experiment.

---

## 11. Governance Declaration

```yaml
V4G_EXECUTION: COMPLETE
V4G_FORENSIC_AUDIT: VALID
V4G_MECHANISM_ANALYSIS: COMPLETE
NEW_EXPERIMENT: FALSE
V4G_RERUN: FALSE
V3_RERUN: FALSE
CONTROL_RERUN: FALSE
PARAMETER_TUNING: FALSE
SOURCE_FILES_MODIFIED: FALSE
RAW_EXECUTION_EVIDENCE_MODIFIED: FALSE
CAUSAL_OVERCLAIM_REMOVED: TRUE
```

**HARD STOP AFTER MECHANISM FORENSIC WORDING CORRECTION.**
"""

md_path = base_dir / "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

md_sha256 = hashlib.sha256(md_path.read_bytes()).hexdigest()

# 3. Create ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.json
corr_json_data = {
    "correction_id": "POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "governance_status": {
        "WORDING_CORRECTION_STATUS": "PASS",
        "SCIENTIFIC_RESULTS_CHANGED": False,
        "EXECUTION_RESULTS_CHANGED": False,
        "RAW_EVIDENCE_CHANGED": False,
        "CAUSAL_OVERCLAIM_REMOVED": True,
        "H14_CAUSAL_ISOLATION_CLAIM": "NOT_SUPPORTED",
        "V4G_VS_V3_COMPOUND_WEIGHT_DIFFERENCE": "ACKNOWLEDGED",
        "NEW_EXPERIMENT": False,
        "V4G_EXECUTION": "COMPLETE",
        "V4G_FORENSIC_AUDIT": "VALID"
    },
    "modified_artifacts_sha256": {
        "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.json": json_sha256,
        "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.md": md_sha256
    },
    "core_wording_changes": [
        {
            "target": "Causal claim on restored late-horizon weights ('forces MILP solver...')",
            "correction": "Replaced with calibrated observational statement: 'Relative to V3, V4.G restores full objective weighting at all timesteps except t=13. Under the V4.G execution, earlier diesel commitment was directly observed, with 312 diesel-commitment timesteps versus 233 under V3. The preserved evidence therefore establishes an association between the V4.G objective-weight structure and the observed dispatch difference, but does not independently isolate a causal contribution from the restored late-horizon weights.'"
        },
        {
            "target": "Interpretation of h=14 isolation",
            "correction": "Explicitly declared: 'V4.G does not provide a causal isolation test of h=14 relative to V3, because the V3 and V4.G objective vectors differ at 23 of 24 decision indices. The t=13 weights themselves are essentially identical.'"
        },
        {
            "target": "Hypothesis attribution for V3 lower fuel",
            "correction": "Updated explanation for CLASSIFICATION E: 'The V4.G result does not support attribution of V3's lower fuel use to the isolated t=13/h=14 weight. V3 and V4.G assign virtually identical weight at t=13, while differing at the other 23 decision indices. Therefore the observed V4.G increase in diesel use cannot be uniquely attributed to the t=13 weight from this experiment.'"
        },
        {
            "target": "Central Scientific Conclusion",
            "correction": "Added preferred scientific conclusion: 'V4.G was a valid controlled objective-weight intervention, but it was not a pure h=14 isolation test relative to V3. The V4.G and V3 weights are essentially identical at t=13, while differing at 23 of 24 decision indices. V4.G nevertheless produced a directly observed increase in diesel fuel use, earlier/more extensive diesel commitment, and higher renewable curtailment under the controlled synthetic EMS environment. These findings establish downstream differences associated with the V4.G objective structure, but the contribution of any individual horizon — including h=14 — is not causally isolated by this experiment.'"
        }
    ]
}

corr_json_path = base_dir / "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.json"
with open(corr_json_path, "w", encoding="utf-8") as f:
    json.dump(corr_json_data, f, indent=2)

corr_json_sha256 = hashlib.sha256(corr_json_path.read_bytes()).hexdigest()

# 4. Create ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.md
corr_md_content = f"""# POLARIS Stage8.1 -> EMS V4.G Mechanism Forensic Wording Correction Report
## Authoritative Scientific Claim Calibration & Governance Record

```yaml
WORDING_CORRECTION_STATUS: PASS
SCIENTIFIC_RESULTS_CHANGED: NO
EXECUTION_RESULTS_CHANGED: NO
RAW_EVIDENCE_CHANGED: NO
CAUSAL_OVERCLAIM_REMOVED: TRUE
H14_CAUSAL_ISOLATION_CLAIM: NOT_SUPPORTED
V4G_VS_V3_COMPOUND_WEIGHT_DIFFERENCE: ACKNOWLEDGED
NEW_EXPERIMENT: FALSE
V4G_EXECUTION: COMPLETE
V4G_FORENSIC_AUDIT: VALID
```

---

## 1. Executive Summary & Purpose

This document records the formal governance wording correction for the **POLARIS V4.G Post-Execution Mechanism Forensic Analysis**. 

No code, optimizer parameters, simulator logic, telemetry data, or empirical execution results were changed. The empirical execution ($N=173$ origins, 3 arms) and post-execution forensic audit remain **100% frozen and valid**.

The wording correction removes causal overclaims and strictly calibrates every statement to match the empirical evidence actually established by the experiment.

---

## 2. Core Wording Corrections Applied

### A. Removal of Causal Optimizer Claims
- **Replaced**: Statements claiming that restoring $w_t = 1.0$ *"forces the MILP optimizer to make earlier diesel commitments"*.
- **Substituted With**: 
  > *"Relative to V3, V4.G restores full objective weighting at all timesteps except $t=13$. Under the V4.G execution, earlier diesel commitment was directly observed, with 312 diesel-commitment timesteps versus 233 under V3. The preserved evidence therefore establishes an association between the V4.G objective-weight structure and the observed dispatch difference, but does not independently isolate a causal contribution from the restored late-horizon weights."*

### B. Explicit Clarification of $h=14$ Non-Isolation
- **Declared**:
  > *"V4.G does not provide a causal isolation test of $h=14$ relative to V3, because the V3 and V4.G objective vectors differ at 23 of 24 decision indices. The $t=13$ weights themselves are essentially identical ($0.513342$ vs $0.513300$)."*

### C. Revised Hypothesis Explanation
- **Hypothesis**: *"V3's lower fuel use is primarily caused by discounting the $t=13 / h=14$ horizon."*
- **Classification**: `CLASSIFICATION E — NOT SUPPORTED`
- **Revised Explanation**:
  > *"The V4.G result does not support attribution of V3's lower fuel use to the isolated $t=13/h=14$ weight. V3 and V4.G assign virtually identical weight at $t=13$, while differing at the other 23 decision indices. Therefore the observed V4.G increase in diesel use cannot be uniquely attributed to the $t=13$ weight from this experiment."*

### D. Calibrated Dispatch Mechanism Description
- **Substituted With**:
  > *"V4.G exhibited earlier diesel commitment than V3 under the tested synthetic EMS environment. Diesel commitment occurred over 312 timesteps in V4.G versus 233 timesteps in V3, a difference of 79 timesteps (+33.9%). V4.G also exhibited higher renewable curtailment than V3: $10,131.06\\text{{ kWh}}$ versus $3,745.89\\text{{ kWh}}$ (+170.5%). These are directly observed downstream differences. The preserved evidence establishes their occurrence under the V4.G objective structure but does not by itself isolate which individual weight changes produced them."*

---

## 3. Central Scientific Conclusion

> *"V4.G was a valid controlled objective-weight intervention, but it was not a pure $h=14$ isolation test relative to V3. The V4.G and V3 weights are essentially identical at $t=13$, while differing at 23 of 24 decision indices. V4.G nevertheless produced a directly observed increase in diesel fuel use, earlier/more extensive diesel commitment, and higher renewable curtailment under the controlled synthetic EMS environment. These findings establish downstream differences associated with the V4.G objective structure, but the contribution of any individual horizon — including $h=14$ — is not causally isolated by this experiment."*

---

## 4. Modified Artifact Provenance & SHA256 Hashes

| Artifact | Purpose | Recomputed SHA256 Hash |
|---|---|---|
| `ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.json` | Updated Analysis Manifest | `{json_sha256}` |
| `ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_FORENSIC_ANALYSIS.md` | Updated Analysis Report | `{md_sha256}` |
| `ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.json` | Governance Correction Manifest | `{corr_json_sha256}` |
| `ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.md` | Governance Correction Report | Self-referenced |

---

## 5. Governance Hard Stop

```yaml
WORDING_CORRECTION_STATUS: PASS
SCIENTIFIC_RESULTS_CHANGED: NO
EXECUTION_RESULTS_CHANGED: NO
RAW_EVIDENCE_CHANGED: NO
CAUSAL_OVERCLAIM_REMOVED: TRUE
H14_CAUSAL_ISOLATION_CLAIM: NOT_SUPPORTED
V4G_VS_V3_COMPOUND_WEIGHT_DIFFERENCE: ACKNOWLEDGED
NEW_EXPERIMENT: FALSE
V4G_EXECUTION: COMPLETE
V4G_FORENSIC_AUDIT: VALID
```

**HARD STOP AFTER DOCUMENTATION WORDING CORRECTION.**
"""

corr_md_path = base_dir / "ems/reports/stage81_ems_runs/POLARIS_STAGE8_1_EMS_V4G_MECHANISM_WORDING_CORRECTION.md"
with open(corr_md_path, "w", encoding="utf-8") as f:
    f.write(corr_md_content)

corr_md_sha256 = hashlib.sha256(corr_md_path.read_bytes()).hexdigest()

print("Applied all wording corrections successfully.")
print(f"Analysis JSON SHA256: {json_sha256}")
print(f"Analysis MD SHA256: {md_sha256}")
print(f"Correction JSON SHA256: {corr_json_sha256}")
print(f"Correction MD SHA256: {corr_md_sha256}")
