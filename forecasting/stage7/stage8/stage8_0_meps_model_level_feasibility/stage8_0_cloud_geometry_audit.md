# POLARIS Stage 8.0 — Cloud Geometry Audit (Base & Top)

## 1. Audit Findings
- **Variables:** `cloud_base_altitude`, `cloud_top_altitude` in `meps_det_sfc`.
- **Availability:** 100% (347/347 origins) at D-1 18Z.
- **Fill Value Behavior:** Clear sky hours populate both variables with $9.96921 \times 10^{36}$.
- **Geometric Thickness:** $\text{Thickness} = \max(0, \text{cloud\_top} - \text{cloud\_base})$.

## 2. Preprocessing & Guardrails
- Clear-sky fill values MUST be mapped to 0 (or station height) to prevent numerical corruption.
- Derived feature: $\text{cloud\_thickness}$ provides cloud vertical depth, which directly correlates with solar radiation attenuation.
