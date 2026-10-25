# POLARIS Stage 8.0 — Novelty & Redundancy Audit Matrix

## Comparison Against All Prior POLARIS Stages

| Proposed Feature Candidate | Underlying Variable | Prior Related Stage | Classification | Physical Distinction / Novelty Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **700 hPa Steering Wind** | `x_wind_pl`, `y_wind_pl` | Stage 5.4 (10m wind) | **NEW INFORMATION** | **HIGH**: 10m wind was surface-constrained. 700 hPa represents free-atmosphere cloud advection velocity. |
| **Cloud Base / Top Altitude** | `cloud_base_altitude`, `cloud_top_altitude` | Stage 6.6 / 7.4 (LWP/IWP) | **NEW REPRESENTATION** | **MEDIUM**: Direct cloud geometric boundaries vs vertically integrated water mass. |
| **Model-Level Cloud Water ($q_l$)** | `mass_fraction_of_cloud_condensed_water_in_air_ml` | Stage 6.6 / 7.4 (PL $q_l$) | **ALREADY TESTED / LATENCY MISMATCH** | **LOW / NO-GO**: Pressure-level $q_l$ was tested in Stage 7.4. Model-level $q_l$ lacks 18Z archive coverage. |
| **Model-Level Cloud Ice ($q_i$)** | `mass_fraction_of_cloud_ice_in_air_ml` | Stage 6.6 / 7.4 (PL $q_i$) | **ALREADY TESTED / LATENCY MISMATCH** | **LOW / NO-GO**: Pressure-level $q_i$ was tested in Stage 7.4. Model-level $q_i$ lacks 18Z archive coverage. |
| **Spatial Model-Level Cloud Neighborhood** | 3x3 / 5x5 spatial $q_l, q_i$ | Stage 5.4 (Spatial probes) | **NO-GO / ARCHIVE MISSING** | **NO-GO**: Fails 18Z archive existence and replicates failed spatial probing concept. |
