# POLARIS EXECUTION AUDIT: EXP-CONFORMAL-TRAJECTORY-OFFLINE

**Execution Timestamp:** 2026-10-05T02:39:48.502371+00:00  
**Elapsed Time:** 37.53 seconds  
**Python Executable:** `/home/punith-bs/01polaris (Copy)/.venv/bin/python`  
**Host / Platform:** Linux  
**Status:** COMPLETE / VERIFIED  

---

## 1. Verified Input Files & Hashes

| Input File | SHA-256 Hash | File Size (bytes) | Status |
|---|---|---|---|
| `CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv` | `1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab` | 5291213 | VERIFIED |
| `stage8_1_CORRECTED_2025_blind_predictions.csv` | `65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500` | 1169033 | VERIFIED |
| `stage8_1_full_37_feature_matrix_2025_CORRECTED.csv` | `9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087` | 4182036 | VERIFIED |
| `PREREGISTRATION.md` | `90d1fe2f7f654ed15536d0eda92a16ef427c9a7d803397a329e8c2f8feea88fa` | 9351 | FROZEN PRIOR TO EXECUTION |
| `PREREGISTRATION.json` | `6c085d8fb86254e9567286725f42d4b4e96e1768cb9dce8b07b87cd7c7477f31` | 3521 | FROZEN PRIOR TO EXECUTION |

---

## 2. Integrity Assurances & Firewalls

1. **Zero GAP19 Optimizer Modification:** Verified via git status.
2. **Zero Controller Runs:** No EMS closed-loop simulations were run.
3. **Zero 2025 Tuning:** Conformal multiplier $\hat{q}_{cal}$ was fit strictly on 2022 ($N = 365$) and frozen before 2025 evaluation.
4. **Physical PV Conversion:** $P_{pv} = \min(60000.0, 51.0 \times \max(0, I))$ enforced across all windows.
5. **Causal Operation:** Zero future pyranometer observations used in predictor terms.
