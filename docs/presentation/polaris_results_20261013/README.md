# POLARIS 10-Minute Presentation Graph Package

**Directory:** `presentation/polaris_results_20261013/`  
**Generated:** 2026-10-13  
**Status:** Complete, Verified, Ready for Presentation  
**Governed Baseline:** Stage 8.1 Corrected (`winner: null`)

---

## 1. Package Inventory

This directory contains high-resolution presentation graphs, a unified slidedeck PDF, an exhaustive evidence index, and defensible talking points prepared for immediate presentation use.

### Visual Deliverables
1. **`graph_a_model_leaderboard.png` (Slide 1)**: Model leaderboard on the 2025 blind holdout (n=5,978), comparing Stage 8.1 Control against Candidates C through J with explicit governance validity tags.
2. **`graph_b_stage_improvements.png` (Slide 2)**: Measured progression of daytime MAE and RMSE across project stages (5.2 → 6.6 → 7.5 → 8.1 → 8.1 Corrected) on identical 2024-ODD benchmark origins.
3. **`graph_c_feature_engineering_impact.png` (Slide 3)**: Controlled feature group impact (Microphysics, Topography, Steering Wind, Interaction) with scientific caveats and bootstrap confidence intervals.
4. **`graph_d_forecast_performance_horizons.png` (Slide 4)**: Per-horizon (H1–H24) error trajectory showing peak noon MAE (64.08 W/m²) and a representative 3-cycle actual vs. predicted irradiance trace.
5. **`graph_e_error_distribution_regimes.png` (Slide 5)**: Daytime forecast residual probability density and forensic breakdown by solar elevation regime (<10°, 10–30°, ≥30°).
6. **`graph_f_optimization_diesel_reduction.png` (Slide 6)**: Multi-arm diesel reduction vs. reliability trade-off from EXP-THREE-ARM-2024 (14,760 solves across 123 origins).
7. **`graph_g_pipeline_governance_evolution.png` (Slide 7)**: Architectural process diagram mapping the evolution from baseline NWP to candidate models, causality audits, and governance boundaries.

### Consolidated Documents
- **`POLARIS_PRESENTATION_SLIDES_20261013.pdf`**: Multi-page PDF containing all 7 slides in presentation sequence with structured executive talking points and governance caveats printed directly beneath each chart.
- **`RESULTS_EVIDENCE_INDEX.md`**: Exhaustive mapping connecting every graph, metric, and curve to exact repository files, JSON keys, line numbers, sample sizes, and SHA-256 hashes.
- **`PRESENTATION_TALKING_POINTS.md`**: 6 defensible talking points, explicit claims to avoid, disclosed limitations, and a concise 90-second executive script.
- **`generate_presentation_graphs.py`**: The fully self-contained Python script used to generate all assets from local repository artifacts.

---

## 2. Which Graphs are Safest to Present?

| Graph | Presentation Safety | Strategic Value | Key Presentation Rule |
|---|---|---|---|
| **Graph B (Stage Progress)** | **SAFEST / STRONGEST** | Highest | Highlight the -7.4% MAE reduction (-2.88 W/m²) on identical held-out 2024-ODD origins. |
| **Graph C (Feature Impact)** | **HIGHLY SAFE** | High | Highlight physical value of microphysics (-5.3%) and terrain (-2.0%); note MEPS 00Z latency caveat. |
| **Graph D (Horizon Error)** | **HIGHLY SAFE** | High | Shows diurnal reality and H20–H24 NaN handling transparently. |
| **Graph E (Error Regimes)** | **HIGHLY SAFE** | High | Demonstrates deep forensic understanding of high-elevation overprediction (+13.75 W/m² bias). |
| **Graph A (Leaderboard)** | **SAFE WITH GOVERNANCE** | Very High | **MUST** emphasize that Candidate F/J are tagged `CONTAMINATED` and governed status is `winner: null`. |
| **Graph F (Diesel/Optimization)** | **SAFE WITH GOVERNANCE** | Critical | **MUST** show that fuel savings cannot be claimed without reliability; Arm A_FIX fails reliability; Arm B is noncausal oracle. |
| **Graph G (Process Flow)** | **EXCELLENT FOR Q&A** | High | Clarifies that successor dataset v2 passed audit, but model training is intentionally held pending authorization. |

---

## 3. Governance Boundaries to Emphasize

1. **Governed Status:** `winner: null` (no arm or model is currently promoted).
2. **Production Baseline:** Frozen Stage 8.1 Corrected model (37 features) is the sole authorized control.
3. **Candidate F:** Reported -0.48 W/m² blind gain is NOT clean proof due to 2025-EVEN target leakage in ensemble parameters.
4. **Successor Dataset v2:** Has passed independent dataset audit; model training has NOT been executed.
5. **Diesel Optimization:** Arm A reported 14.39% fuel savings with a 1h clock defect; fixing the defect drops savings to 11.23% and fails reliability gates S1, S2, and S4.
