# POLARIS Research Implementation Audit: Candidate S & Candidate SW (Post-Audit Revision)

**Experiment Identifier:** `EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024`  
**Governance Status:** `IMPLEMENTATION READY FOR AI RE-REVIEW`  
**Execution Gate:** `BENCHMARK HARNESS VERIFIED — AWAITING PROJECT-MANAGER AUTHORIZATION FOR FULL 123-ORIGIN CAMPAIGN`  
**Audit Revision Date:** October 5, 2026  
**Implementation Modules:**
- `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py`
- `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/test_candidate_s_sw_implementation.py`
- `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace/origin_1_hourly_traces.json`
- `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace/CANDIDATE_SW_UNMET_FORENSIC_EXPLANATION.md`

---

## 1. Executive Summary & Resolution of Independent Audit Blockers

Following independent audit feedback from AI assistant (`BLOCKED — DO NOT RUN THE 123-ORIGIN CAMPAIGN`), all five technical blockers have been explicitly addressed, mathematically verified, and archived:

1. **Blocker 1 (Audit SOC Range Correction):** Corrected Origin-1 Control B realized SOC range from `[56.12%, 84.45%]` to the verified ground-truth values `[65.58%, 93.85%]`.
2. **Blocker 2 (Archival of Origin-1 Hourly Traces):** Executed and archived complete 24-hour hourly records for Control Frozen B, Candidate S, Candidate SW, and EBR-off diagnostic arm in `origin_1_hourly_traces.json` (`88ea4a0db60f4bb9582fe119a18df6e93b3fe817a2d0feef5841db9e3eca055c`), capturing all 21 required telemetry fields per hour.
3. **Blocker 3 (Forensic Explanation of Candidate SW Unmet Load):** Conducted hour-by-hour physical telemetry analysis proving that the exact equality of unmet load (`87,061.64 Wh`) between Candidate SW and EBR-off is an authentic physical consequence of dispatch structure (all unmet occurs exclusively in hours where diesel is off in both arms, and diesel runs only in hours 8 and 9 where unmet is 0.0 W while SW burns more fuel to cover its lookahead reserve target).
4. **Blocker 4 (GAP19 Solver Integration Test):** Implemented and verified `test_gap19_integration_candidate_s_and_sw_ebr_consumption`, directly intercepting the HiGHS C++ solver in the live GAP19 execution path. Verifies that Candidate S and SW trajectories reach GAP19 unmodified and that Layer-C constraint bounds match $E_{\mathrm{stage2\_target}}[t] + E_{\min}$ across all $t \in \{0 \dots 23\}$.
5. **Blocker 5 (Removal of Mislabelled Diagnostic):** Removed the mislabelled `stage2_target_23_wh` field from `CandidateEBROptimizerWrapper.call_history` and replaced it with `j2_shortfall_wh` (`plan.j2_objective`).

All 12 automated verification tests have **passed with zero errors**. Zero production code or frozen preregistration contracts have been altered.

---

## 2. Mathematical Mapping from Frozen Preregistration to Code

| Preregistration Specification | Mathematical Formulation | Implementation Location | Verification Evidence |
| :--- | :--- | :--- | :--- |
| **Variant S Lookahead Deficit** | $E_{\mathrm{EBR\_S}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \text{crit}[k] - \text{solar}[k]\right) \Delta t$ | `candidate_s_sw_adapter.py:86-127` (`compute_variant_s_ebr`) | `test_variant_s_hand_calculated_values` (exact floating-point match with hand calculation) |
| **Variant S Zero Solar Identity** | Reverts to governed unconditional EBR when solar is 0 W | `candidate_s_sw_adapter.py:108-112` | `test_variant_s_zero_solar_identity` (diff $< 10^{-12}$ against `compute_governed_ebr`) |
| **Variant S Horizon Edge ($t=23$)** | $E_{\mathrm{stage2\_target}}[23] = \max\left(\frac{1}{\eta_{\mathrm{dis}}} \max(0, \text{crit}[23] - \text{solar}[23]) \Delta t, E_{\mathrm{term}}\right)$ | `candidate_s_sw_adapter.py:180-197` and GAP19 lines 147-151 | `test_gap19_integration_candidate_s_and_sw_ebr_consumption` (HiGHS row 311 bound check) |
| **Variant SW Lookahead Deficit** | $E_{\mathrm{EBR\_SW}}[t] = \frac{1}{\eta_{\mathrm{dis}}} \sum_{k=t}^{\min(t+5, 23)} \max\left(0, \text{crit}[k] - \text{solar}[k] - \text{wind}[k]\right) \Delta t$ | `candidate_s_sw_adapter.py:130-177` (`compute_variant_sw_ebr`) | `test_variant_sw_zero_renewables_identity` and `test_variant_sw_zero_wind_equals_variant_s` |
| **Direct PV Power Consumption** | Direct electrical PV power from `bundle.solar_generation.point` in Watts (no 51x conversion) | `candidate_s_sw_adapter.py:233` (`list(bundle.solar_generation.point)`) | `test_direct_pv_watts_input_no_scaling` (confirms 1:1 Watts subtraction) |
| **Critical Demand Ceiling** | $\text{crit}[k] = \min(11600.0\text{ W}, D_{\mathrm{forecast}}[k])$ | `candidate_s_sw_adapter.py:221-231` (via `adapt_critical_demand_vector`) | Inherits tested worker adaptation pattern |
| **Reserve Monotonicity** | $0 \le E_{\mathrm{SW}}[t] \le E_{\mathrm{S}}[t] \le E_{\mathrm{GOV}}[t]$ | Evaluated across all timesteps | `test_ordering_and_monotonicity` (verified across 24 dynamic hours) |

---

## 3. Test Suite Results (`test_candidate_s_sw_implementation.py`)

All 12 automated unit, integration, and solver-path tests executed under `.venv/bin/pytest`:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/punith-bs/01polaris (Copy)
collected 12 items

test_variant_s_zero_solar_identity                                PASSED [  8%]
test_variant_s_full_solar_zero_reserve                             PASSED [ 16%]
test_variant_s_hand_calculated_values                              PASSED [ 25%]
test_variant_sw_zero_renewables_identity                           PASSED [ 33%]
test_variant_sw_zero_wind_equals_variant_s                         PASSED [ 41%]
test_ordering_and_monotonicity                                     PASSED [ 50%]
test_horizon_edge_t23_terminal_target                              PASSED [ 58%]
test_direct_pv_watts_input_no_scaling                              PASSED [ 66%]
test_input_validation_errors                                       PASSED [ 75%]
test_deterministic_smoke_origin_1                                  PASSED [ 83%]
test_gap19_integration_candidate_s_and_sw_ebr_consumption         PASSED [ 91%]
test_immutable_baseline_and_production_hashes                      PASSED [100%]

============================= 12 passed in 45.03s ==============================
```

---

## 4. Origin-1 Diagnostic Execution & Ground-Truth Archival

The deterministic 24-hour closed-loop simulation was executed and archived for all candidate and control arms:

| Metric | Control Frozen B | Candidate S (Solar-Only) | Candidate SW (Solar + Wind) | EBR-Off Diagnostic |
| :--- | :--- | :--- | :--- | :--- |
| **Diesel Fuel Consumed** | **51.8493 L** (exact match) | **35.2992 L** (-31.92%) | **36.9372 L** (-28.76%) | **33.6496 L** (-35.10%) |
| **Total Unmet Load** | **66,790.10 Wh** (exact match) | **80,764.94 Wh** | **87,061.64 Wh** | **87,061.64 Wh** |
| **Total Served Load** | **293,209.90 Wh** | **279,235.06 Wh** | **272,938.36 Wh** | **272,938.36 Wh** |
| **Curtailment** | **145.01 kWh** | **172.93 kWh** | **27.17 kWh** | **14.02 kWh** |
| **Realized SOC Range** | **[65.58%, 93.85%]** | **[61.71%, 93.71%]** | **[44.32%, 94.02%]** | **[44.32%, 94.02%]** |
| **SOC Violations (<20%)** | **0** | **0** | **0** | **0** |
| **Max Busbar Residual** | $< 10^{-3}\text{ W}$ | $< 10^{-3}\text{ W}$ | $< 10^{-3}\text{ W}$ | $< 10^{-3}\text{ W}$ |
| **24-Step Solver Status** | 24 / 24 Optimal | 24 / 24 Optimal | 24 / 24 Optimal | 24 / 24 Optimal |

### Key Forensic Findings:
1. **Control B Reproduction:** Control Frozen B reproduced the frozen benchmark figures for Origin 1 to within floating-point precision ($51.8493\text{ L}$ fuel, $66,790.10\text{ Wh}$ unmet, and SOC range `[65.58%, 93.85%]`).
2. **Causal Explanation of SW Unmet Equality:** Unmet load occurs exclusively during 13 hours ($h \in \{0, 1, 2, 3, 4, 6, 17, 18, 19, 20, 21, 22, 23\}$) where diesel generation is zero in both SW and EBR-off. In those hours, battery state and discharge limits are identical, yielding mathematically identical unmet load. In hours 8 and 9 where diesel runs, unmet load is $0.0\text{ W}$ in both arms, but SW burns higher fuel ($36.9372\text{ L}$ vs $33.6496\text{ L}$) to satisfy the forward lookahead Stage-2 reserve envelope. Full analysis is archived in [`CANDIDATE_SW_UNMET_FORENSIC_EXPLANATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/origin_1_diagnostic_trace/CANDIDATE_SW_UNMET_FORENSIC_EXPLANATION.md).

---

## 5. Cryptographic Integrity Confirmation

All production files, forecaster modules, frozen baselines, and preregistration contracts were verified by SHA-256 hash checks:

| File Path | Governed / Expected SHA-256 | Current Verified SHA-256 | Status |
| :--- | :--- | :--- | :--- |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | **UNMODIFIED** |
| `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | **UNMODIFIED** |
| `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.md` | `1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5` | `1f018b1aba2651950b8cd5474ee9ea4dd2c6db6e9d9a584b1a5791eb59e80be5` | **UNMODIFIED** |
| `experiments/EXP_CANDIDATE_S_SW_PREREGISTRATION.json` | `3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4` | `3607876afea7cea169887faa3b92c7a21142e9fbc5bd38ac93a6b72351342ba4` | **UNMODIFIED** |
| `hourly_telemetry_123_frozen_b.json` | `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5` | `13359f2742a0eecce14dc1c506ce0a933a9a5a441082120f83adf21d8c3f48e5` | **UNMODIFIED** |
| `hourly_telemetry_123_frozen_b_summary.json` | `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f` | `46c412837c5713877c42aabb223b7d22be47bca09eeba25472aa675eb009396f` | **UNMODIFIED** |
| `HOURLY_BASELINE_RECONCILIATION_REPORT.md` | `70985bc3ba9e5909fb2ac43fa46feae3a81cc569b65c2a67c334ab40f3f6ce08` | `70985bc3ba9e5909fb2ac43fa46feae3a81cc569b65c2a67c334ab40f3f6ce08` | **UNMODIFIED** |
| `origin_1_hourly_traces.json` | `88ea4a0db60f4bb9582fe119a18df6e93b3fe817a2d0feef5841db9e3eca055c` | `88ea4a0db60f4bb9582fe119a18df6e93b3fe817a2d0feef5841db9e3eca055c` | **ARCHIVED** |
| `candidate_s_sw_adapter.py` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` | **REVISED** |
| `test_candidate_s_sw_implementation.py` | `e8b73fa1bfbde0f0f078195d0fb93780f5521e347a57de76b66c8eda9d558164` | `e8b73fa1bfbde0f0f078195d0fb93780f5521e347a57de76b66c8eda9d558164` | **EXPANDED** |

---

## 6. Audit Verdict

- **Production Modifications:** 0 files modified.
- **Simulator / Realization Modifications:** 0 files modified.
- **Preregistration Modifications:** 0 files modified.
- **Blockers Resolved:** 5 of 5 blockers completely resolved.
- **Test Suite Pass Rate:** 100% (12/12 tests passed).
- **GAP19 Integration Test:** PASSED (verified directly on HiGHS solver row entries and bounds).
- **Final Status:** **IMPLEMENTATION READY FOR AI RE-REVIEW**.
