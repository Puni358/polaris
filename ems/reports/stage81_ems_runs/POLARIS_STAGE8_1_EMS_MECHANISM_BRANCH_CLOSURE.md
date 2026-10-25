# POLARIS — STAGE8.1 → EMS V1
## FINAL MECHANISM BRANCH CLOSURE REPORT

```
============================================================
V1 MECHANISM BRANCH CLOSURE DETERMINATION
============================================================
V1_EXPERIMENT_STATUS: ACCEPTED_AND_FROZEN
V1_MECHANISM_BRANCH_STATUS: CLOSED
V2_ENGINEERING_STATUS: LOCKED
FINAL_MECHANISM_CLASSIFICATION: C — ONLY ASSOCIATIONS ESTABLISHED
MECHANISM_CAUSAL_CHAIN: NOT_ESTABLISHED
MAE_DISCREPANCY_STATUS: RECONCILED
V1_EXPERIMENT_RERUN: NO
V1_ORIGIN_RERUN: NO
V1_PILOT: NO
V1_RESULT_MODIFIED: NO
MODEL_RETRAINED: NO
FORECAST_MODIFIED: NO
EMS_MODIFIED: NO
OPTIMIZER_MODIFIED: NO
SIMULATOR_MODIFIED: NO
FORECASTBUNDLE_MODIFIED: NO
SCHEMA_MODIFIED: NO
V2_IMPLEMENTED: NO
V2_EXECUTED: NO
============================================================
```

---

### 1. FROZEN V1 EXPERIMENTAL BASELINE & ACCEPTED RESULT

The V1 Stage8.1 → EMS empirical replay experiment is formally completed, independently audited, accepted, and frozen:

- **Experimental Unit**: One complete 24-hour forecast-origin replay ($N = 173$ paired origins).
- **Primary Endpoint (`total_diesel_fuel_liters`)**:
  - **Control Total**: 4,671.00 Liters (Mean: 27.0000 L / origin)
  - **Treatment Total**: 6,447.44 Liters (Mean: 37.2684 L / origin)
  - **Mean Paired Difference ($\Delta = \text{Treatment} - \text{Control}$)**: **+10.2684 Liters / origin**
  - **95% Bootstrap CI (10,000 iter, seed=42)**: **[+5.4795 L, +15.2113 L]**
  - **Wilcoxon Signed-Rank Test**: $W = 5351.5, p = 1.3566 \times 10^{-3}$
- **Preregistered Forecast-Error Association**:
  - **Spearman $\rho$**: **-0.9198** ($p = 2.2830 \times 10^{-71}$, $N = 173$)
- **Secondary Frozen Differences**:
  - `diesel_energy_kwh`: **+58.1351 kWh/origin**
  - `renewable_energy_used_kwh`: **-79.4577 kWh/origin**
  - `renewable_curtailment_kwh`: **-120.4317 kWh/origin** (-10.12 percentage points)
  - `renewable_utilization_pct`: **+10.1204 percentage points**
  - `battery_throughput_kwh`: **-64.6521 kWh/origin** (-0.32 cycles/origin)
  - `unmet_critical_load_kwh`: **0.00 kWh**
  - `system_reliability_pct`: **0.00 percentage points**
  - `constraint_violations_count`: **0 violations**
- **Origin-Level Heterogeneity**:
  - Treatment $>$ Control: **95 origins (54.9%)**
  - Treatment $<$ Control: **77 origins (44.5%)**
  - Equal: **1 origin (0.6%)**

---

### 2. AUTHORITATIVE V1 SCIENTIFIC CONCLUSION

> **Authoritative V1 Scientific Conclusion**:
> "Empirical Stage8.1 solar forecasts replayed through the frozen POLARIS EMS under the controlled POLARIS synthetic station environment were associated with a mean increase of 10.2684 L/origin in diesel fuel relative to the frozen control forecast, alongside lower battery throughput and lower renewable curtailment."

**Causal Mechanism Status**: **`NOT_ESTABLISHED`**
The internal timestep-level causal chain ($\text{forecast difference} \rightarrow \text{MPC decision} \rightarrow \text{diesel commitment} \rightarrow \text{battery/SOC response} \rightarrow \text{curtailment} \rightarrow \text{fuel}$) is **not established** by preserved V1 evidence because hourly timestep telemetry fields were not recorded in V1 execution logs.

---

### 3. MAE DISCREPANCY RECONCILIATION

- **Official Stage8.1 OOD Benchmark MAE ($36.1887\,\text{W/m}^2$)**: Evaluates daytime-only hours (`daytime_flag == True`) across the official OOD benchmark evaluation dataset.
- **V1 Replay Subset All-Hours MAE ($25.13\,\text{W/m}^2$ Treatment, $174.25\,\text{W/m}^2$ Control)**: Evaluates all 24 horizon hours (including 12 nighttime zero-solar hours) across the 173 mechanically eligible V1 origins.
- `MAE_DISCREPANCY_STATUS`: **`RECONCILED`** (Official benchmark $36.1887\,\text{W/m}^2$ remains the authoritative forecast accuracy baseline).

---

### 4. ORIGIN-LEVEL HETEROGENEITY RECORD

The operational response varies significantly across origins:
- **Group P ($N=95$, Treatment consumed more fuel)**: Characterized by extreme clear-sky over-prediction by Control (Control Signed Error = $+222.19\,\text{W/m}^2$). Control's clear-sky assumption led it to refuse diesel commitment, whereas Treatment saw realistic low solar profiles and committed diesel to maintain reserves (Treatment fuel = 63.06 L vs Control 27.00 L).
- **Group N ($N=77$, Treatment saved fuel)**: Characterized by overcast/cloudy days where Stage8.1's accurate forecast enabled Treatment to run 100% on renewables/battery without starting diesel (Treatment fuel = 0.00 L in median Group N origin), saving 27.00 L relative to Control.

---

### 5. CLOSURE OF V1 MECHANISM BRANCH & V2 ENGINEERING LOCK

- **V1 Mechanism Branch**: **`CLOSED`**. No further statistical mining or reinterpretation of V1 evidence is permitted.
- **V2 Engineering**: **`LOCKED`**. No model retraining, forecast recalibration, EMS optimizer tuning, or constraint modifications are authorized.
- **Future Direction**: If timestep-level mechanism resolution becomes scientifically required, it must be addressed via a separately governed observability protocol with richer telemetry logging.

---

### 6. ARTIFACT LOCATION SUMMARY

1. **Markdown V1 Branch Closure Report**: [`POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.md)
2. **JSON V1 Branch Closure Manifest**: [`POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.json)
