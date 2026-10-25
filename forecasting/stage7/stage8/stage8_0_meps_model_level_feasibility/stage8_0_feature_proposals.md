# POLARIS Stage 8.0 — Candidate Feature Design Proposals

## Proposed Candidate Feature Set for Future Stage 8.1 (IF AUTHORIZED)

### Candidate Group 1: Free-Atmosphere Steering Wind (PRIMARY GO)
1. `u700_lead_h`: $U$ wind component at 700 hPa (m/s)
2. `v700_lead_h`: $V$ wind component at 700 hPa (m/s)
3. `wind_speed_700_lead_h`: $\sqrt{U_{700}^2 + V_{700}^2}$ (m/s)
4. `wind_dir_700_lead_h`: Steering wind direction (radians/degrees)

### Candidate Group 2: Cloud Geometry (CONDITIONAL GO)
5. `cloud_base_alt_km`: `cloud_base_altitude` clipped to $[0, 15000]$ m and converted to km.
6. `cloud_top_alt_km`: `cloud_top_altitude` clipped to $[0, 15000]$ m and converted to km.
7. `cloud_geometric_thickness_km`: $\max(0, \text{cloud\_top} - \text{cloud\_base}) / 1000.0$.
