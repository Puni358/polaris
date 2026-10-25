# POLARIS PHASE S1 — SPATIAL NWP REPRESENTATION EXPERIMENT
## 49×49 COMPUTE-BUDGET AUTO-STOP CHECKPOINT

**Date:** September 14, 2026  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}, 702\text{ m ASL}$)  
**Execution Context:** Authorized Compute-Budget Auto-Stop Post-49×49 Completion  
**Official Champion:** Stage 8.1 37-feature GBDT (`HistGradientBoostingRegressor`)  
**Official Benchmark Baseline:** ODD MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`, Night MAE `0.0 W/m²`  
**Governance Constraint:** NO ODD ACCESS | NO POST-HOC TUNING | CHAMPION UNTOUCHED | NO PROMOTION PERFORMED

---

## 1. Executive Verdict & Stop Declaration

$$\mathbf{VERDICT:\ 49\times 49\ COMPLETED\ |\ S1\ STOPPED\ |\ 64\times 64\ NOT\ EXECUTED}$$

### Status Summary:
- **Compute-Budget Auto-Stop:** Executed cleanly immediately after the $49\times 49$ footprint finished writing `metrics.json` and `fold_summary.csv`.
- **Completed Footprints:** 6 footprints completed ($5\times 5$, $9\times 9$, $13\times 13$, $21\times 21$, $33\times 33$, $49\times 49$).
- **$64\times 64$ Footprint Status:** **INTENTIONALLY NOT EXECUTED.**
- **Protocol Adherence:** The S0.1 frozen protocol remained 100% unchanged throughout execution.
- **Architecture & Parameter Compliance:** All six models used the exact frozen 2D CNN + GRU spatial-temporal architecture with `AdaptiveAvgPool2d((1,1))` pooling (16,033 trainable parameters).
- **Control Reproduction (Gate G6):** **PASSED**. Control Stage 8.1 GBDT EVEN MAE = `26.356310 W/m²`.
- **ODD Firewall Status:** **INTACT. ZERO ODD ORIGINS/PREDICTIONS ACCESSED.**
- **Promotion Status:** **NO SPATIAL FOOTPRINT PROMOTED.** Results are recorded for human review. Next action requires explicit human authorization.

---

## 2. Completed Footprint Directory Inventory

All six completed footprint result directories exist and contain valid `metrics.json` and `fold_summary.csv` files:

1. [`spatial_arome_research/SPATIAL_NWP_S1/5x5/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/5x5/) (Span: 10.0 km, Elapsed: 151.01 s)
2. [`spatial_arome_research/SPATIAL_NWP_S1/9x9/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/9x9/) (Span: 20.0 km, Elapsed: 175.94 s)
3. [`spatial_arome_research/SPATIAL_NWP_S1/13x13/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/13x13/) (Span: 30.0 km, Elapsed: 297.59 s)
4. [`spatial_arome_research/SPATIAL_NWP_S1/21x21/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/21x21/) (Span: 50.0 km, Elapsed: 534.20 s)
5. [`spatial_arome_research/SPATIAL_NWP_S1/33x33/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/33x33/) (Span: 80.0 km, Elapsed: 1065.78 s)
6. [`spatial_arome_research/SPATIAL_NWP_S1/49x49/`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/SPATIAL_NWP_S1/49x49/) (Span: 120.0 km, Elapsed: 4418.64 s) — **Completed at 2026-09-14T05:04:00Z**

---

## 3. Summary of EVEN Cross-Validation Results

| Footprint | Grid Span (km) | Parameter Count | EVEN MAE (W/m²) | EVEN ΔMAE (W/m²) | EVEN nMAE (%) | EVEN RMSE (W/m²) | Bias (W/m²) | Folds Improved | Max Degradation (W/m²) | G1 | G2 | G3 | G4 | G5 | G6 | PASS / FAIL |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Control** | — | — | **26.356310** | **0.000000** | **29.6088%** | **55.884041** | **-2.045438** | — | — | — | — | — | — | — | — | **BASELINE** |
| **$5\times 5$** | 10.0 km | 16,033 | 33.129507 | +6.773197 | 37.2019% | 65.853318 | -5.979508 | 0/5 | +8.088379 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$9\times 9$** | 20.0 km | 16,033 | 34.017923 | +7.661613 | 38.2839% | 65.629166 | -6.651449 | 0/5 | +9.361003 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$13\times 13$** | 30.0 km | 16,033 | 33.299844 | +6.943534 | 37.4619% | 65.718401 | -6.343905 | 0/5 | +8.470893 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$21\times 21$** | 50.0 km | 16,033 | 33.251522 | +6.895212 | 37.3144% | 65.646173 | -6.642579 | 0/5 | +8.195488 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$33\times 33$** | 80.0 km | 16,033 | 33.321818 | +6.965508 | 37.4687% | 65.579344 | -5.377251 | 0/5 | +7.880096 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$49\times 49$** | 120.0 km | 16,033 | 32.638970 | +6.282660 | 36.6136% | 64.207044 | -6.311735 | 0/5 | +7.864101 | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | **FAIL** |
| **$64\times 64$** | 157.5 km | — | — | — | — | — | — | — | — | — | — | — | — | — | **UNEXECUTED** |

---

## 4. Governance & Safety Compliance Declarations

1. **Protocol Integrity:** The S0.1 frozen protocol (channels, levels, folds, loss, optimizer, architecture, seeds) was strictly followed without alteration or post-hoc tuning.
2. **Compute-Budget Auto-Stop:** Execution was stopped cleanly via process interruption immediately following successful completion of the $49\times 49$ footprint.
3. **Unexecuted Matrix Size:** Footprint $64\times 64$ was **NOT** executed.
4. **ODD Firewall:** Zero ODD test origins (174 origins) were loaded, evaluated, or accessed. ODD remains 100% sealed.
5. **Champion Protection:** Official champion Stage 8.1 GBDT remains unchanged and protected.
6. **No Winner Selection / No Promotion:** No spatial footprint was promoted. All raw spatial neural models evaluated failed G1–G4 promotion gates relative to the tabular GBDT control baseline.
7. **Human Authorization Requirement:** Next actions require explicit human authorization.
