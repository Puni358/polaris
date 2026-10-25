# POLARIS Stage 4: 2025 SW Low-Sun Protection Research Freeze Record

**Experiment Identifier:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`  
**Freeze Status:** `FROZEN — AUTHORITATIVE RESEARCH CHECKPOINT`  
**Date (UTC):** 2026-10-05  
**Governing Preregistration (MD):** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md`  
(SHA-256: `9cb2d5459894be8add07a3bd01595f40ab2485c2a18510765c4d8f0264fe4e46`)  
**Governing Preregistration (JSON):** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.json`  
(SHA-256: `9a16ccc8c28267331da2816fe0c7c04aeb9afd6f963e49673eb6c3872d892623`)  
**Holdout Governance Resolution (MD):** `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.md`  
(SHA-256: `22e67a16a90ef90fa88b248614a83d853511a33619548272535e05615314d7a7`)  
**Holdout Governance Resolution (JSON):** `experiments/STAGE4_2025_HOLDOUT_GOVERNANCE_RESOLUTION.json`  
(SHA-256: `f96fd97c812f44e88455c966c500a3874a99f07b8ae94744759d0fac6b461bf7`)  
**Artifact Directory:** `experiments/stage4_sw_low_sun_2025_holdout/`  

---

## 1. Executive Purpose & Scope

This document represents the formal and authoritative research freeze for the POLARIS Stage 4 Low-Sun Stored-Energy Protection experiment evaluated on the 2025 holdout population.

The purpose was to test whether restoring stored-energy reserve protection specifically during low-sun conditions ($e_k < 15.0^\circ$) resolves the proportional critical-reliability safety failure of Candidate SW while preserving statistically significant diesel reduction.

This is a **research-only checkpoint**. It does NOT authorize production promotion and does NOT constitute physical deployment validation.

---

## 2. Confirmatory Holdout Population & Execution Totals

- **Holdout Selection Rule:** Deterministic calendar rule — every 00:00 UTC `forecast_start` from 2025-05-01 through 2025-08-31 inclusive.
- **Origins Count:** Exactly 123 origins.
- **Origin Exclusions:** Exactly 0.
- **Arms Executed:** 5 arms (`Control_Frozen_B`, `Candidate_S`, `Candidate_SW`, `Candidate_SL`, `Candidate_SWL`).
- **Hours Per Arm:** 2,952 origin-hours.
- **Total Arm-Hours:** 14,760 hours.
- **Execution Failures:** 0.
- **Optimizer Infeasibilities:** 0.
- **Genuine Simultaneous Charge/Discharge Violations (> tau = 0.055 W):** 0.
- **Campaign Elapsed Runtime:** 3,640.85 seconds (~60.7 minutes).

---

## 3. Authoritative Performance & Safety Results (2025 Holdout)

All candidates were evaluated against **Control Frozen B** re-executed on the identical 2025 holdout population under identical execution machinery:

| Arm | Description | Total Fuel (L) | Saving vs B (%) | Critical-First Rel (%) | ΔR_CF (pp) | Gate 1 (≥0.00) | Proportional Rel (%) | ΔR_P (pp) | Gate 2 (≥0.00) | Realized Min SOC (%) | SOC <20% | Gate 3 | All Safety Gates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Control_Frozen_B** | Unconditional 6h EBR | 6,117.9691 | — | 93.669482% | — | — | 83.823383% | — | — | 54.99% | 0 | PASS | **REFERENCE** |
| **Candidate_S** | Solar Net (Prot OFF) | 4,648.3272 | 24.02% | 94.327168% | +0.657686 | PASS | 84.604885% | +0.781502 | PASS | 20.00% | 0 | PASS | **PASS** |
| **Candidate_SW** | Solar+Wind (Prot OFF) | 3,885.0225 | 36.50% | 94.090514% | +0.421032 | PASS | 83.467189% | **-0.356194** | **FAIL** | 20.00% | 0 | PASS | **SAFETY FAILURE** |
| **Candidate_SL** | Solar Net (Prot ON) | 5,334.1331 | 12.81% | 94.455173% | +0.785691 | **PASS** | 85.150455% | +1.327072 | **PASS** | 20.00% | 0 | **PASS** | **PASS** |
| **Candidate_SWL** | Solar+Wind (Prot ON) | 5,221.3152 | 14.66% | 94.484413% | +0.814931 | **PASS** | 85.264223% | +1.440840 | **PASS** | 20.00% | 0 | **PASS** | **PASS** |

---

## 4. Authoritative Statistical Diesel Gate Results

Evaluated origin-paired against Control B with BCa 95% bootstrap CI (10,000 resamples, seed 42) and two-sided paired Wilcoxon signed-rank test with Holm FWER correction:

### Candidate SW-L (Decision Candidate)
- **Total Fuel Saved:** 896.65 L (14.66% reduction vs Control B)
- **Mean Paired Saving:** 7.2899 L/origin
- **Median Paired Saving:** 7.3848 L/origin
- **BCa 95% Bootstrap CI:** [4.9970, 9.5583] L/origin (strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1564.0, raw p = $2.2831 \times 10^{-8}$
- **Holm-Adjusted p-value:** $4.5662 \times 10^{-8}$ (significant at $\alpha = 0.05$: True)
- **Diesel Gate Status:** **PASS**

### Candidate S-L (Efficiency Reference)
- **Total Fuel Saved:** 783.84 L (12.81% reduction vs Control B)
- **Mean Paired Saving:** 6.3727 L/origin
- **Median Paired Saving:** 5.9488 L/origin
- **BCa 95% Bootstrap CI:** [4.1057, 8.5926] L/origin (strictly > 0: True)
- **Wilcoxon Signed-Rank Test:** statistic = 1662.0, raw p = $6.9037 \times 10^{-7}$
- **Holm-Adjusted p-value:** $6.9037 \times 10^{-7}$ (significant at $\alpha = 0.05$: True)
- **Diesel Gate Status:** **PASS**

---

## 5. Authoritative Factorial Contrast Results & C4 Interaction

Factorial $2 \times 2$ contrast on per-origin paired differences with BCa 95% bootstrap CI (10,000 resamples, seed 42):

$$C_4 = (SW\text{-}L - SW) - (S\text{-}L - S) \equiv (SW\text{-}L - S\text{-}L) - (SW - S)$$

| Contrast | Formulation | Primary Outcome: Proportional Reliability (pp) | BCa 95% Bootstrap CI | Secondary Outcome: Diesel Fuel (L) | BCa 95% Bootstrap CI |
|---|---|---|---|---|---|
| **C1** | $SW - S$ | -1.1377 pp | [-1.5910, -0.7184] pp | -6.2057 L | [-8.3797, -4.0875] L |
| **C2** | $SW\text{-}L - SW$ | +1.7970 pp | [+1.4205, +2.1995] pp | +10.8642 L | [+8.7244, +13.0813] L |
| **C3** | $S\text{-}L - S$ | +0.5456 pp | [+0.2755, +0.8331] pp | +5.5757 L | [+3.8971, +7.4640] L |
| **C4** | **Interaction** | **+1.2515 pp** | **[+0.8683, +1.6546] pp** | **+5.2885 L** | **[+3.2317, +7.3345] L** |

### Frozen Mechanism Statement:
> "Factorial evidence supports the hypothesized low-sun protection mechanism on the 2025 synthetic holdout."

The BCa 95% CI for the interaction $C_4$ ($[+0.8683, +1.6546]\text{ pp}$) strictly excludes zero. This demonstrates that restoring stored-energy protection during low-sun conditions disproportionately recovers proportional reliability for solar+wind credit compared to solar-only credit.

---

## 6. Scientific Interpretation & Governance Classifications

### Authoritative Interpretation:
Unprotected SW achieved the largest diesel reduction among the tested candidate arms (36.50%) but failed the proportional critical-reliability safety gate ($\Delta R_P = -0.356194\text{ pp}$ below Control B).

Low-sun protection restored the safety deficit:
- **SW (Unprotected):** 36.50% diesel reduction, but proportional critical reliability = 83.467189% (below Control B).
- **SW-L (Protected):** 14.66% diesel reduction, and proportional critical reliability = 85.264223% (above Control B by $+1.440840\text{ pp}$).

Therefore:
- **SW-L is a SAFE, statistically diesel-reducing RESEARCH CANDIDATE.**
- However, **SW-L DOES NOT achieve the project's $\ge 40\%$ diesel-reduction target.**
- The 40% target is NOT a safety gate and NOT a statistical gate, but it remains an unachieved efficiency target.

### Final Governance Classifications:
- **Candidate S-L:** `SUCCESS` (all safety gates passed, diesel gate passed, 12.81% diesel reduction)
- **Candidate SW-L:** `SUCCESS` (all safety gates passed, diesel gate passed, 14.66% diesel reduction)
- **Candidate SW:** `SAFETY FAILURE` (proportional reliability gate failed)
- **40% Target Status:** `NOT ACHIEVED` (14.66% < 40%)
- **Production Promotion:** `NOT AUTHORIZED`
- **Physical Deployment Validation:** `NOT ESTABLISHED`
- **Stage 4 Research Status:** `SUCCESSFUL CONFIRMATORY RESEARCH EXPERIMENT`

---

## 7. Important Boundaries & Caveats (Unmodified)

1. **Demand and realized wind inputs are synthetic benchmark components.** Results represent research evidence and do not generalize to physical wind turbine aerodynamics or live commercial operations.
2. **Release-time semantics for `previous_day1` NWP are assumed under the frozen benchmark convention** and are not validated against live operational telemetry feeds.
3. **Solar elevation retains the frozen one-hour offset** relative to UTC instant $T-1\text{ h}$.
4. **The 15° threshold is a research regime convention**, not a universal physical invariant.
5. **Stage 4 is research evidence**, not physical deployment validation.
6. **SW-L requires further prospective validation** before any operational consideration.
7. **No production code was modified.**

---

## 8. Production Integrity Hashes

| Path | SHA-256 | Status |
|---|---|---|
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | **VERIFIED UNCHANGED** |
| `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` | **VERIFIED UNCHANGED** |
| `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` | **VERIFIED UNCHANGED** |
| `experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS/candidate_s_sw_adapter.py` | `a3ba73ad32ed2be20c0f197689081abf64402da41205a674fe76a15767e40de4` | **VERIFIED UNCHANGED** |

---

## 9. Stage 4 Authoritative Artifact Inventory

| Artifact | File Path | SHA-256 Hash |
|---|---|---|
| Execution Manifest | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_EXECUTION_MANIFEST.json` | `ad8c0ab22a26e53639441d6137d76bb653da6e97190c11baa3a821d61095805b` |
| Campaign Summary | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_CAMPAIGN_SUMMARY.md` | `bb6c7d4b740b9ec9b3796c8a563d12701816b9ff359684936a98f90dd1759db4` |
| Execution Audit | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_EXECUTION_AUDIT.md` | `0f7c1e8b2c3cc514d3d0d3dbdf36a1bdb08801ce15af8ecb0c2959fad2b6c1b3` |
| Safety Report (MD) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_SAFETY_REPORT.md` | `322229daf9596d624e6cb23b336ef01e4483ed85441185e9202c3649c6fc17e3` |
| Safety Report (JSON) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_SAFETY_REPORT.json` | `40df13e347234990b92b94e9644c18bb714d8cfd62203def2c123d820be101f0` |
| Statistical Report (MD) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_STATISTICAL_REPORT.md` | `0e601788a78eeb7567dc782cca7635e59824c255c3c2526c35860f47effee63a` |
| Statistical Report (JSON) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_STATISTICAL_REPORT.json` | `f2c35311dd387cda99cea0cdffc5d8fc48252dc1e48a2348cf59179de80143f5` |
| Factorial C4 Report (MD) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_FACTORIAL_C4_REPORT.md` | `57d302c3925ee127c8514fcbe18bab05764b165131ac72d5d2787103c6513d16` |
| Factorial C4 Report (JSON) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_FACTORIAL_C4_REPORT.json` | `99ce51b22a3b33f3eb2390a923a0bda2202959e341930430e8c9797c0f9df8b7` |
| 2025 Origin Manifest | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_ORIGIN_MANIFEST.json` | `7a6c791ff64cf8c8b85d27e061aba94e8d6515f32efb418789d5f0b9b56cc288` |
| 123-Origin Results (CSV) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.csv` | `18d13dec71eab82919c900da52b5248699e4b5b8fa4c4ed8499aff494f4fa62b` |
| 123-Origin Results (JSON) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.json` | `d1710b8345a4ee21de8d4fc696cc189ea2508ff038a3ff42281560457eac4376` |
| 14,760-Hour Telemetry (CSV) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_HOURLY_TELEMETRY.csv` | `90c71d58fdf6fbfd5cbe9ffe5f27367e558f2650aeb31cdd340691c6e3587007` |
| 14,760-Hour Telemetry (JSON) | `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_HOURLY_TELEMETRY.json` | `7fcd8ba9df2f925ad6137e4893124e3c833a907b26d1ca7ab37b7b4af7944de3` |
| Checkpoint File | `experiments/stage4_sw_low_sun_2025_holdout/CANDIDATE_STAGE4_CHECKPOINT.jsonl` | `cfcdc65cc7f6ea2ac88ee69c02d94c218f16a7e96324028f1d454dbf2b4d7371` |
| Stage 4 Adapter | `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py` | `3427da6a7b1d7763f8fa655e541cd2a344aeefdd33379137c6311501799395d0` |
| Stage 4 Campaign Runner | `experiments/stage4_sw_low_sun_2025_holdout/run_stage4_sw_low_sun_2025_campaign.py` | `8a62feb30a09a9bae7bab1261c73a1f33b857c585f2af5a37c757e29c2f0c312` |
| Stage 4 Test Suite | `experiments/stage4_sw_low_sun_2025_holdout/test_stage4_implementation.py` | `80e3a3e1b88a8d34e0716912bd82c4db4bc297b7d6bc51098fbe1a9a574080e9` |

---

## 10. Immutability Declaration

This freeze record is authoritative and immutable. Stage 4 is closed. No further execution, tuning, or optimization may be conducted under Stage 4.
