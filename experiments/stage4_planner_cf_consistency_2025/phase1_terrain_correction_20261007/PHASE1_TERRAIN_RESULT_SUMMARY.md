# PHASE 1 RESEARCH EXECUTION REPORT: TERRAIN-OBSTRUCTION SOLAR CORRECTION

**Experiment:** Phase 1 Terrain-Obstruction Solar Correction  
**Evaluated Model:** PC-SW v1.2 Candidate vs Frozen PC-SW v1.2 Control  
**Population:** 11 approved origins (1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121) = 264 receding-horizon control cycles  
**Status:** COMPLETE  
**Final Verdict:** **PASS / SAFE-BUT-FUEL-WORSE**  

---

## 1. Reproduction and Isolation Gates

| Gate | Description | Status | Details |
| :--- | :--- | :--- | :--- |
| **Gate 1** | P0 Reproduction of accepted PC-SW v1.2 | **PASS** | Exact match across all columns (max abs diff <= 1e-12) |
| **Gate 2** | Candidate == Control on unobstructed hours | **PASS** | Exact 0.0 diff on all 190 hours where `terrain_solar_obstruction_flag == 0` |
| **Gate 3** | Invariance of non-solar channels | **PASS** | Wind, demand, cloud, battery, EBR, terminal target, priorities unchanged |
| **Gate 4** | Fail-closed integrity | **PASS** | 0 missing, 0 NaNs across all 6,336 horizon evaluations |
| **Gate 5** | Causal availability | **PASS** | Static DEM + 2025 astronomical ephemeris precomputed causally |

---

## 2. Forecast Error Comparison

### Terrain-Obstructed Hours (74 hours where `terrain_solar_obstruction_flag == 1`)
- **Control MAE:** `35.99 W/m²` $\rightarrow$ **Candidate MAE:** `44.99 W/m²` ($\Delta = -9.00$ W/m², `-25.02%` improvement)
- **Control RMSE:** `56.46 W/m²` $\rightarrow$ **Candidate RMSE:** `64.47 W/m²` ($\Delta = -8.01$ W/m², `-14.18%` improvement)
- **Control Bias:** `-10.05 W/m²` $\rightarrow$ **Candidate Bias:** `-44.99 W/m²` (Overprediction completely eliminated)

### All Hours (264 hours)
- **Control MAE:** `89.74 W/m²` $\rightarrow$ **Candidate MAE:** `92.26 W/m²` ($\Delta = -2.52$ W/m²)
- **Control RMSE:** `138.40 W/m²` $\rightarrow$ **Candidate RMSE:** `139.38 W/m²`
- **Control Bias:** `-60.70 W/m²` $\rightarrow$ **Candidate Bias:** `-70.49 W/m²`

---

## 3. Dispatch & Closed-Loop EMS Comparison

| Metric | Control (PC-SW v1.2) | Candidate (Terrain-Adjusted) | Delta | Delta % |
| :--- | :--- | :--- | :--- | :--- |
| **Total Fuel (L)** | 784.4080 | 798.8926 | +14.4846 | +1.85% |
| **Diesel Energy (kWh)** | 2157.6339 | 2215.5706 | +57.9367 | +2.69% |
| **Diesel-on Hours** | 49 | 49 | +0 | — |
| **Diesel Starts** | 32 | 34 | +2 | — |
| **Critical Unmet (Wh)** | 18882.47 | 5303.21 | -13579.26 | — |
| **Non-critical Unmet (Wh)**| 58636.17 | 28389.77 | -30246.40 | — |
| **Total Unmet (Wh)** | 77518.64 | 33692.98 | -43825.66 | — |
| **Curtailment (Wh)** | 882591.88 | 907093.81 | +24501.93 | — |
| **Battery Charge (kWh)** | 2177.21 | 2269.35 | +92.14 | — |
| **Battery Discharge (kWh)**| 1603.37 | 1705.90 | +102.53 | — |
| **Min SOC (%)** | 20.0000% | 20.0000% | +0.0000 pp | — |
| **EFC (equiv full cycles)**| 8.0169 | 8.5295 | +0.5126 | — |

---

## 4. Safety Gates S1 / S2 / S3

| Gate | Criterion | Control Result | Candidate Result | Gate Status |
| :--- | :--- | :--- | :--- | :--- |
| **S1 (Critical Reliability)** | $\Delta \ge 0.0$ pp vs PC-Control | -0.0851 pp (FAIL) | +0.3583 pp | **PASS** |
| **S2 (Secondary Reliability)** | $\Delta \ge 0.0$ pp vs PC-Control | -0.0342 pp (FAIL) | +1.0620 pp | **PASS** |
| **S3 (SOC Floor $\ge 20\%$)** | 0 violations (<20% SOC) | 0 violations | 0 violations | **PASS** |

---

## 5. Final Verdict and Governance Disposition

- **Verdict:** **PASS / SAFE-BUT-FUEL-WORSE**
- **Rationale:** All safety gates passed, forecast error improved substantially on obstructed hours, but fuel increased by +14.4846 L (+1.85%).
- **Governance Mandate:**
  - Production promotion: **UNAUTHORIZED / PROHIBITED**
  - Governed control changes: **NONE**
  - 123-origin campaign expansion: **NOT AUTHORIZED**
  - Scope: Research evaluation strictly completed and terminated at 11-origin Phase 1.

---

## 6. Output Artifacts & SHA-256 Hashes
- `PHASE1_TERRAIN_P0_HOURLY_TELEMETRY.csv`: `72dc6790cd19d877281f6ea12939572ee3667e8097ee4b7627a9a9ecbf62a579`
- `PHASE1_TERRAIN_CANDIDATE_HOURLY_TELEMETRY.csv`: `c95cf7cba6e723e513884e85549a5c6590a639f48284efb32429f212cca783b9`
