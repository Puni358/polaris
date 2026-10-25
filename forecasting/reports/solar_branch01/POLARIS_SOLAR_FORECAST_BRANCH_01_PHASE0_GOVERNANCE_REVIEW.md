# POLARIS_SOLAR_FORECAST_BRANCH_01 — PHASE 0 GOVERNANCE REVIEW REPORT

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `PHASE 0 GOVERNANCE REVIEW`  
**Authorization:** `PHASE 0 GOVERNANCE REVIEW ONLY`  
**Governance Decision:** `B = PHASE 1 SPECIFICATION CONDITIONALLY AUTHORIZED`  
**Next Governed Step:** `PHASE1_BRANCH_SPECIFICATION`  

---

## 1. Verified Phase 0 Artifact Provenance & Hashes

| Artifact Filename | Status | Size (Bytes) | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| `POLARIS_SOLAR_FORECAST_BRANCH_01_PHASE0_DATA_AUDIT.md` | `EXISTS` | 6471 | `da3e5d6e82cac010741327a2799ac4385bd758f123e34e3bb5c383efc44bef41` |
| `POLARIS_SOLAR_FORECAST_BRANCH_01_PHASE0_DATA_AUDIT.json` | `EXISTS` | 3425 | `499a3d9998c9c8f0e6e2a997d7e818ed7ab7a0930132cc9892cab7b8cfe53748` |
| `POLARIS_SOLAR_FORECAST_BRANCH_01_DATA_COVERAGE.csv` | `EXISTS` | 1223 | `7f6cd888754e916415f932b249ebbca78d555b6280367fa7820c2c72ac7bf660` |
| `POLARIS_SOLAR_FORECAST_BRANCH_01_FEATURE_SOURCE_AUDIT.csv` | `EXISTS` | 1244 | `77c61d0ad2e0f27c4e7d4c36b238cdd49aded0f71960f15d5ee53b51d6ef2adc` |
| `POLARIS_SOLAR_FORECAST_BRANCH_01_NWP_AVAILABILITY.csv` | `EXISTS` | 678 | `a8cbde0f932b1fcd1ef25b06d7c0fb99e1bb158d0006699d59f0a0eaf5cf721d` |

**Provenance Status:** `PROVENANCE_VERIFIED`

---

## 2. Primary Governance Question Evaluation

> **Primary Governance Question:**  
> *"Does the evidence establish that POLARIS can define a NEW causal solar forecasting branch capable of producing a complete 24-hour forecast at every intended hourly MPC origin, using only information that would actually have been available at that origin?"*

### Governance Finding:
**YES (CONDITIONALLY AUTHORIZED)**. The empirical evidence gathered during Phase 0 demonstrates that:
1. **Target Data Continuity**: 8,784 continuous hourly SW_IN observations exist for 2024 with 0% missingness.
2. **Deterministic Clear-Sky Inputs**: Astronomical clear-sky GHI, terrain obstruction, solar elevation, and solar zenith are 100% causally computable at any origin t.
3. **Causal Lookback Features**: SW_IN historical observations over [t-24h, t] are strictly available at origin t.
4. **NWP Issue-Time Bounding**: AROME 21x21 NWP issue runs occur once daily at 00:00 UTC. For intra-day forecast origins (t > 00:00), NWP features can be constructed causally by selecting the latest valid issue run (t_issue = 00:00 <= t) with an adjusted lead time H_effective = H + (t - t_issue).

---

## 3. Comprehensive Governance Gate Decision Matrix

| Gate | Evidence Reviewed | Status | Bounded Condition / Blocker | Required Action |
| :--- | :--- | :--- | :--- | :--- |
| `TARGET_DATA` | Nuolja 2024 hourly SW_IN (8,784h, 100% coverage, 0 missing, UTC) | `PASS` | None | Proceed to Phase 1 Target Specification |
| `HOURLY_ORIGIN_SUPPORT` | Continuous 8,784 hourly target timestamps throughout 2024 | `PASS` | None | Specify hourly origin structure in Phase 1 |
| `FEATURE_CAUSALITY` | Lookback windows (1h-24h), astronomical clear-sky, and calendar features strictly causal at t | `PASS` | None | Freeze causal feature definitions in Phase 1 |
| `NWP_ISSUE_TIME` | AROME 21x21 NWP issue runs available at 00:00 UTC daily | `CONDITIONAL` | Sparse 00:00 UTC issue frequency for non-00:00 UTC origins | Phase 1 must specify deterministic NWP selection rule (t_issue <= t) |
| `NWP_RUN_SELECTION` | Latest available issue run t_issue <= t is deterministically selectable | `PASS` | None | Specify deterministic selection rule in Phase 1 |
| `NWP_LEAD_COVERAGE` | 00:00 UTC NWP runs cover H1..H24; intra-day origins require H_effective = H + (t - t_issue) | `CONDITIONAL` | Higher lead times (up to 42h) required for late afternoon origins (t=18:00 UTC) | Evaluate NWP lead-time degradation in Phase 1 specification |
| `24H_CAUSAL_HORIZON` | Complete H1..H24 horizon constructible causally via lookback, astronomical, and lead-shifted NWP | `CONDITIONAL` | NWP lead-time shifting required for intra-day origins | Formally specify multi-horizon causal structure in Phase 1 |
| `FUTURE_TRUTH_FIREWALL` | All proposed inputs satisfy t_available <= t; zero future truth used | `PASS` | None | Enforce strict fail-closed truth firewall in Phase 1 |
| `DATA_PROVENANCE` | Authoritative local source files (Nuolja SITES, Clearsky, AROME) verified with SHA-256 | `PASS` | None | Maintain complete dataset manifest in Phase 1 |
| `STAGE8_1_SEPARATION` | Stage 8.1 boundary confirmed frozen and immutable; Branch 01 is independent | `PASS` | None | Use distinct Branch 01 naming and artifact IDs |
| `REPRODUCIBILITY_REQUIREMENT` | 34-item reproducibility package and independent replay gate established | `ESTABLISHED` | None | Enforce 20-point governance rule for future training runs |
| `PHASE0_EVIDENCE_COMPLETENESS` | All 5 Phase 0 audit artifacts created with complete 19-question responses and hashes | `PASS` | None | Archive Phase 0 artifacts and proceed to Phase 1 |

---

## 4. Explicit Phase 1 Bounded Conditions

To advance to Phase 1 Branch Specification, the following explicit conditions are recorded:
1. **NWP Lead-Time Bounding**: Phase 1 specification must define the exact lead-time shift formula H_effective = H + (t - t_issue) when pairing 00:00 UTC NWP forecasts with intra-day origins (t in 01:00..23:00).
2. **Fail-Closed Policy**: If t_issue > t or if required lookback features are missing at origin t, the system must fail closed without zero-padding, forward-filling, or using synthetic values.
3. **Branch Independence**: Stage 8.1 artifacts remain untouched. Branch 01 shall use distinct manifest IDs and output locations (`artifacts/model_runs/POLARIS_SOLAR_FORECAST_BRANCH_01_...`).
4. **Replay Tolerance**: Numerical replay tolerance is marked `TO BE DETERMINED AT MODEL REPRODUCIBILITY GATE` based on the exact serialized model format chosen in later phases.

---

## 5. Required Final Status Block

```
BRANCH_ID =
POLARIS_SOLAR_FORECAST_BRANCH_01

PHASE0_RECONNAISSANCE =
COMPLETE

PHASE0_GOVERNANCE_REVIEW =
COMPLETE

STAGE8_1_MODIFIED =
NO

STAGE8_1_RETRAINED =
NO

STAGE8_1_REPLACED =
NO

CANDIDATE_A_IMPLEMENTED =
NO

CANDIDATE_A_EXECUTED =
NO

NEW_MODEL_TRAINED =
NO

NEW_MODEL_INFERRED =
NO

EMS_MODIFIED =
NO

EMS_EXECUTED =
NO

TARGET_DATA =
PASS

HOURLY_ORIGIN_SUPPORT =
PASS

FEATURE_CAUSALITY =
PASS

NWP_ISSUE_TIME_CAUSALITY =
CONDITIONAL

NWP_RUN_SELECTION =
PASS

NWP_LEAD_COVERAGE =
CONDITIONAL

24H_CAUSAL_HORIZON =
CONDITIONAL

FUTURE_TRUTH_FIREWALL =
PASS

DATA_PROVENANCE =
PASS

STAGE8_1_SEPARATION =
PASS

REPRODUCIBILITY_REQUIREMENT =
ESTABLISHED

PHASE0_EVIDENCE_COMPLETENESS =
PASS

GOVERNANCE_DECISION =
B

NEXT_GOVERNED_STEP =
PHASE1_BRANCH_SPECIFICATION
```
