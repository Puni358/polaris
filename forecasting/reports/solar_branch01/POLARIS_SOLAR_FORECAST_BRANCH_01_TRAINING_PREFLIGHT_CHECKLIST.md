# POLARIS_SOLAR_FORECAST_BRANCH_01 — TRAINING PREFLIGHT CHECKLIST

**Branch ID:** `POLARIS_SOLAR_FORECAST_BRANCH_01`  
**Phase:** `MANDATORY PRE-TRAINING PREFLIGHT CHECKLIST`  
**Rule:** `All 11 items MUST be verified PASS before any training process may begin.`  

---

## Pre-Training Verification Gate (11 Items)

| Item # | Preflight Gate Item | Verification Requirement | Preflight Status |
| :--- | :--- | :--- | :--- |
| `PREFLIGHT_01` | **Dataset SHA-256 Verification** | Hash of `(avg 1hr)POLARIS_v0_1_SITES_Nuolja_2024_hourly_SW_IN(1).csv` matches expected digest | `VERIFIED` |
| `PREFLIGHT_02` | **Data Schema & Monotonicity** | Timestamps strictly monotonic UTC increasing; zero duplicate timestamps | `VERIFIED` |
| `PREFLIGHT_03` | **Feature Contract Order** | Exactly 18 features matching `FeatureMatrixBuilder.ORDERED_FEATURE_NAMES` | `VERIFIED` |
| `PREFLIGHT_04` | **NWP Causality Rule** | $t_{\text{issue}} \le t_{\text{origin}}$ strictly enforced for 100% of origins | `VERIFIED` |
| `PREFLIGHT_05` | **Target Window Definition** | $Y(t) = [SW\_IN(t+1)...SW\_IN(t+24)]$, $t+0$ excluded | `VERIFIED` |
| `PREFLIGHT_06` | **Split Embargo Protection** | 24h embargo boundary excludes samples extending past split bounds | `VERIFIED` |
| `PREFLIGHT_07` | **Preprocessor Isolation** | `StandardScaler` fitted strictly on Training split ($X_{\text{train}}$) | `VERIFIED` |
| `PREFLIGHT_08` | **Stage 8.1 Firewall** | `s81_solar.py` SHA-256 hash verified unchanged (`8f2a1b0c...`) | `VERIFIED` |
| `PREFLIGHT_09` | **EMS Non-Intervention** | EMS code, optimizers, and simulator 100% untouched | `VERIFIED` |
| `PREFLIGHT_10` | **Candidate A Firewall** | Candidate A code 100% untouched and unexecuted | `VERIFIED` |
| `PREFLIGHT_11` | **Explicit Training Authorization** | Formal governance decision granting `MODEL_TRAINING_AUTHORIZATION` | `NOT_GRANTED` |

---

## Preflight Summary

Items 1 through 10 are **`PASS`**. Item 11 (`MODEL_TRAINING_AUTHORIZATION`) remains **`NOT_GRANTED`**. Training cannot start until Item 11 is authorized by a separate governance gate.
