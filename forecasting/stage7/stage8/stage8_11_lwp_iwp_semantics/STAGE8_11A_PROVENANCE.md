# STAGE 8.11A — FEATURE SEMANTICS PROVENANCE MANIFEST

**Project:** POLARIS SIH Forecasting  
**Stage:** STAGE 8.11A LWP/IWP FEATURE SEMANTICS AUDIT  
**Date:** September 12, 2026  

---

## 1. Inspected Source Code Files & Line Ranges

1. **`stage6/stage6_6_lwp_iwp/run_stage6_6.py` (Lines 160–263):**
   - Implements the THREDDS data retrieval and surface-aware LWP/IWP integration.
   - Line 217: Fetches `surface_air_pressure` across 24 hourly forecast steps `[0:1:23]`.
   - Line 223: Fetches `mass_fraction_of_cloud_condensed_water_in_air_pl` across 24 forecast steps `[0:1:23]`.
   - Line 229: Fetches `mass_fraction_of_cloud_ice_in_air_pl` across 24 forecast steps `[0:1:23]`.
   - Line 239–260: Iterates over `h_idx in range(24)`, extracts `ql_data[h_idx]` and `qi_data[h_idx]`, computes trapezoidal vertical integration surface-truncated at $p_{\text{sfc}}$, and outputs `lwp_latest` and `iwp_latest` for each specific forecast horizon $h \in \{1 \dots 24\}$.

2. **`stage7/stage8/stage8_1_700hpa_wind/run_stage8_1.py` (Lines 188–190):**
   - Incorporates `lwp_latest` and `iwp_latest` into the candidate 37-feature inventory.
   - Inherits the exact per-horizon feature trajectories generated in Stage 6.6.

3. **`stage6/stage6_6_lwp_iwp/lwp_iwp_extracted_features.csv` (8,328 rows):**
   - Authoritative feature dataset containing 347 forecast origins $\times$ 24 forecast steps.
   - Confirms that `lwp_latest` and `iwp_latest` vary dynamically across horizons $H1 \dots H24$ for every single origin.

---

## 2. Verification Protocol & Immutability

* **Read-Only Inspection:** Feature semantics were verified via static code analysis and empirical inspection of existing EVEN-side feature CSV files.
* **No Rerun:** Zero extraction pipelines or model training scripts were executed.
* **ODD Firewall:** Zero ODD $SW\_IN$ target data loaded or evaluated.

