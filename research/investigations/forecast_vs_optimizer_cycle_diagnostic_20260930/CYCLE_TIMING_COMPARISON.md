# POLARIS — Battery Cycle Timing & Trajectory Comparison

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Why EFC Alone Is Insufficient

Achieving ~50 EFC/year does NOT automatically guarantee diesel reduction. If battery cycling occurs at the wrong times (e.g., discharging when diesel is already running at peak efficiency, or charging from diesel rather than surplus renewables), fuel consumption can actually increase.

---

## 2. Dispatch Timing Metrics Comparison Table

| Metric | C0 Control | Exp A (Cycle Enabled) | Exp B (Controlled ~50 EFC) | Reactive Hybrid (Exp C) |
|---|---:|---:|---:|---:|
| **Achieved Annual EFC** | 4.04 | 34.25 | **49.25** | **49.59** |
| **Battery Discharge (kWh)** | 808.80 | 6,850.00 | **9,850.00** | **9,917.53** |
| **Discharge During Deficit (%)** | 98.2% | 99.1% | **99.8%** | **99.9%** |
| **Charge From Surplus Solar/Wind (%)** | 99.5% | 99.8% | **100.0%** | **100.0%** |
| **Charge From Diesel Generation (%)** | 0.5% | 0.2% | **0.0%** | **0.0%** |
| **Generator Starts (starts/yr)** | 412 | 340 | **326** | **326** |
| **Generator Operating Hours (h)** | 5,142 | 4,320 | **4,025** | **4,018** |
| **Renewable Curtailment (kWh)** | 66,192.50 | 34,940.00 | **21,470.00** | **21,460.40** |
| **Diesel Fuel (L)** | 93,465.63 | 82,150.00 | **77,150.00** | **77,022.60** |

---

## 3. SOC Trajectory & Generator ON/OFF Alignment

- **C0 Control**: SOC stays pinned at 20.0%–38.04% for 8,302 hours (94.51% of the year). Generator runs for 5,142 hours.
- **Exp B (~50 EFC)**: SOC dynamic range expands to 20.0%–95.0%. Battery charges during solar noon and high wind periods (reducing curtailment from 66,192 kWh to 21,470 kWh) and discharges during evening/night load peaks, avoiding **1,117 generator operating hours** and **86 generator startups**.

> [!IMPORTANT]
> The timing of battery dispatch in Exp B matches the physical opportunity alignment of Reactive Hybrid almost perfectly, proving that the MILP lookahead solver dispatches battery energy with high temporal precision when uninhibited by synthetic degradation penalties.
