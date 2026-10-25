# POLARIS STAGE 8.24 — REPRODUCIBILITY MANIFEST

> **VERDICT: REJECTED_BY_EVEN_GATES**

## File Artifact Hashes

- `STAGE8_24_FAITHFUL_OROGRAPHIC_EVEN_RESULTS.json`: `daf167aecb4727eaa2f9fd6fed5f140240db7aa1bc479854edda3a723f98d662`
- `STAGE8_24_FAITHFUL_OROGRAPHIC_EVEN_RESULTS.md`: `c5f36cdf6a4700d4c316806f3456b157c2f3842d513ec13075495542270b287c`

## Code & Data Provenance

- **Candidate Features:** `ctx_u_perp`, `ctx_mountain_froude`
- **CV Protocol:** 5-fold forward-chaining EVEN-only cross-validation
- **Seed & Architecture:** `random_state=42`, `HistGradientBoostingRegressor(loss='absolute_error', max_depth=4, min_samples_leaf=30, l2_regularization=10.0)`
- **ODD Status:** **100% UNTOUCHED (`ODD_RUN = FALSE`)**
