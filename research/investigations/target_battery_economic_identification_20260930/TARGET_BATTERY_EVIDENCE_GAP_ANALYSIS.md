# POLARIS — Target Battery Evidence Gap Analysis

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Structured Gap Categorization

### A. What is Known (Evidence-Backed Facts)
1. **SITES Nuolja Middle Station Ground Truth**: Nuolja is an atmospheric and meteorological field station in Abisko, Sweden, providing 2024 hourly solar radiation (`SW_IN`), temperature, and wind data (`POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv`).
2. **Synthetic Fixture Definition**: POLARIS uses a synthetic 200.0 kWh / 50.0 kW BESS fixture (`POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json`) for MILP microgrid dispatch benchmarking (`real_nuolja_data: false`).
3. **Synthetic Parameter Set**: Current production parameters are hardcoded synthetic proxies (`deg_penalty_per_wh = 0.00005`, `round_trip_efficiency = 0.8464`).
4. **Portability Invariance**: POLARIS MILP solver stability and energy balance hold invariant across synthetic battery envelopes B0–B7 (100–400 kWh, 25–100 kW).

---

### B. What is Unknown (Unestablished Parameters)
1. Physical battery manufacturer, model, and cell chemistry relevant to target site.
2. Target-specific nominal and usable energy capacity (kWh).
3. Target-specific continuous and peak power capability (kW).
4. Actual cell-level and pack-level round-trip efficiency under operational loads.
5. BMS telemetry logs (SOC, SOH, cell voltage, pack current, cell temperature).
6. Target battery replacement cost, transport/logistics fees to Abisko, and warranty structure.

---

### C. What is Contradicted (Mismatched Claims)
1. Treating the synthetic 200 kWh fixture as physical Nuolja site hardware.
2. Assuming outdoor ambient temperature equals internal battery cell temperature.
3. Interpreting the $0.05/kWh linear cost surrogate as an empirical physical degradation model.

---

### D. What is Required (Gap Resolution Requirements)

To close each evidence gap, the following specific documents, data streams, or artifacts are required:

| Gap Priority | Missing Component | Required Evidence Artifact | Impact Area |
|---|---|---|---|
| **Priority 1 (Critical)** | Target Hardware Identity | Official procurement invoice or nameplate photo | Target identity & sizing |
| **Priority 2 (Critical)** | Cell Specifications | OEM cell datasheet & degradation curves | Degradation model parameterization |
| **Priority 3 (High)** | BMS Telemetry | 30+ days continuous BMS log (SOC, SOH, temp, V, I) | Model calibration & validation |
| **Priority 4 (High)** | Economic Cost Inputs | Equipment invoice + Arctic freight quote + labor contract | Economic objective calibration ($/kWh) |
| **Priority 5 (Medium)** | Thermal Enclosure | BESS container HVAC spec & internal temp telemetry | Thermal aging modeling |

---

## 2. Prioritized Impact Assessment

```
Economic Objective Calibration (Priority 4)
        ↓
  Degradation Cost ($/kWh)
        ↓
Battery Dispatch Decision (MILP)
        ↓
Annual Diesel Reduction (L)
```

Without closing **Priority 1, 2, and 4 gaps**, any attempt to modify the $0.05/kWh degradation penalty in production would violate scientific defensibility and safety governance.
