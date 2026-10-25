# PHASE 1 RESEARCH EXPERIMENT RESULTS
**Experiment:** Evening-independent cloud-fraction bias correction — Phase 1  
**Subset:** 11 approved origins (1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121) = 264 solves  

## 1. Control / Reproduction Gate (P0)
- **Status:** PASS (Exact 100% reproduction of accepted 11-origin PC-SW telemetry)
- **Max Absolute Difference:** 0.0 across all telemetry fields

## 2. Telemetry Comparison

| Metric | P0 (k=1.00) | C1 (k=0.70) | C2 (k=0.46) |
| :--- | :--- | :--- | :--- |
| **Total Fuel (L)** | 784.4080 | 594.8631 | 522.9167 |
| **Fuel Delta vs P0 (L)** | — | -189.5449 (-24.16%) | -261.4913 (-33.34%) |
| **Diesel Energy (kWh)** | 2157.6339 | 1579.4533 | 1451.6660 |
| **Energy Delta vs P0 (kWh)** | — | -578.1806 (-26.80%) | -705.9679 (-32.72%) |
| **Diesel-on Hours** | 49 | 40 (-9) | 32 (-17) |
| **Diesel Starts** | 32 | 22 (-10) | 19 (-13) |
| **Battery Charge Hours** | 92 | 107 | 114 |
| **S1 Delta vs PC-Control (pp)** | -0.0851 (FAIL) | -1.3919 (FAIL) | -4.2278 (FAIL) |
| **S2 Delta vs PC-Control (pp)** | -0.0342 (FAIL) | -3.0745 (FAIL) | -6.8282 (FAIL) |
| **S3 / SOC Violations (<20%)** | 0 (PASS) | 0 (PASS) | 0 (PASS) |
| **Min SOC (%)** | 20.0000 | 20.0000 | 20.0000 |
| **Critical Unmet (Wh)** | 18882.47 | 58903.15 | 145747.15 |
| **Noncritical Unmet (Wh)** | 58636.17 | 131835.19 | 187206.71 |
| **Total Unmet (Wh)** | 77518.64 | 190738.34 | 332953.86 |
| **Curtailment (Wh)** | 882591.88 | 374513.43 | 216383.29 |
| **EBR-Binding Count** | 1 | 1 | 2 |
| **EBR Split (Cloud $\ge 50\%$)** | 1 | 1 | 1 |
| **EBR Split (Cloud $< 50\%$)** | 0 | 0 | 1 |
| **Terminal-Binding Count** | 238 | 215 | 205 |

## 3. Decision & Mechanism Classification
- **Candidate C1 (k=0.70):** Disqualified by safety gate violation.
- **Candidate C2 (k=0.46):** Disqualified by safety gate violation.

## 4. Final Recommendation
**Phase 2 population testing IS NOT JUSTIFIED. Neither candidate satisfies all gate and genuine energy reduction criteria.**

## 5. Artifact Hashes
- `PHASE1_P0_HOURLY_TELEMETRY.csv`: `80c2b12e173b6bb35f38d9344f37ed1dca0e5be67ce7d48ea64ebb65f7de8438`
- `PHASE1_C1_HOURLY_TELEMETRY.csv`: `b0c1f767de5b0279953ee6c4575f09408f9e1eb0e1b2fd9f209939fddeeaf786`
- `PHASE1_C2_HOURLY_TELEMETRY.csv`: `6e3fe27bf05939297752efaf978f6a33ff31ce7588b472b4c6c2eeff359d9292`
