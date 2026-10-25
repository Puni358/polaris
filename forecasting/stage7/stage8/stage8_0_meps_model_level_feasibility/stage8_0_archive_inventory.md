# POLARIS Stage 8.0 — MEPS Archive Inventory Audit Report

## 1. Executive Summary
This audit evaluated the exact 2024 MET Norway MEPS archive (`meps25epsarchive` on `thredds.met.no`) across all 347 POLARIS benchmark forecast origins.

## 2. Product Coverage Matrix

| Dataset Product | Standard Filename Pattern | Frequency Archived | 347 Benchmark Coverage (D-1 18Z) | 347 Benchmark Coverage (D-1 00Z) | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `meps_det_sfc` | `meps_det_sfc_YYYYMMDDTHHZ.ncml` | 6-hourly (00,06,12,18Z) | **347 / 347 (100.0%)** | 347 / 347 (100.0%) | **VERIFIED** |
| `meps_det_pl` | `meps_det_pl_YYYYMMDDTHHZ.ncml` | 6-hourly (00,06,12,18Z) | **347 / 347 (100.0%)** | 347 / 347 (100.0%) | **VERIFIED** |
| `meps_det_hl` | `meps_det_hl_YYYYMMDDTHHZ.ncml` | 6-hourly (00,06,12,18Z) | **347 / 347 (100.0%)** | 347 / 347 (100.0%) | **VERIFIED** |
| `meps_det_ml` | `meps_det_ml_YYYYMMDDTHHZ.ncml` | **00Z ONLY** | **0 / 347 (0.0%)** | **347 / 347 (100.0%)** | **CLAIM DISPROVED AT 18Z** |

> [!CAUTION]
> **GEMINI CLAIM AUDIT RESULT:** Gemini's research report claimed 100% causal availability of native model-level MEPS files (`meps_det_ml`) at D-1 18Z. Empirical scan of all 347 benchmark dates in the 2024 archive proves this claim **FALSE**. MET Norway archives `meps_det_ml` ONLY for the 00Z run each day. Using 00Z introduces an 18-hour forecast latency lag compared to the frozen POLARIS baseline.
