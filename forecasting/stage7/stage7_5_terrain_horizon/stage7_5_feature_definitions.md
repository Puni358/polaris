# STAGE 7.5 — CANDIDATE TERRAIN / HORIZON RADIATIVE GEOMETRY FEATURES

The following 4 static/deterministic radiative geometry features were defined and extracted:

1. `terrain_horizon_elevation_deg`: Maximum terrain elevation angle ($\alpha_{\text{max}}(\theta_s)$, degrees) along current solar azimuth $\theta_s$.
2. `terrain_elevation_margin_deg`: Angular elevation difference ($\gamma_s - \alpha_{\text{max}}(\theta_s)$, degrees) between solar elevation $\gamma_s$ and terrain horizon.
3. `terrain_solar_obstruction_flag`: Binary indicator ($1$ if $\gamma_s > 0$ AND $\gamma_s \le \alpha_{\text{max}}(\theta_s)$, else $0$). Indicates physical mountain shading during daylight hours.
4. `clearsky_ghi_terrain_adjusted`: Physically derived transformation of clear-sky GHI ($\text{W/m}^2$) zeroed out during local terrain shading periods ($\text{clearsky\_ghi} \times (1 - \text{flag})$).

### Physical Novelty vs Derived Feature Distinction
- **New Physical Information Source:** Copernicus DEM 30m $\rightarrow$ local terrain elevation $\rightarrow$ azimuth-dependent horizon profile $\alpha_{\text{max}}(\theta)$.
- **Derived Feature:** `clearsky_ghi_terrain_adjusted` is a deterministic transformation combining existing astronomical clear-sky GHI with the new terrain horizon geometry, rather than an independent observational data stream.
- **Correlation Interpretation:** The high Spearman correlation ($\rho = 0.8810$) between `terrain_elevation_margin_deg` and `solar_elevation` indicates a strong statistical association. This correlation alone does not establish statistical non-redundancy. The physical novelty of the terrain feature family stems strictly from its **azimuth-dependent directional geometry**, which is unrepresented by scalar solar elevation alone.

### Causal Protocol Enforcement
- All 4 features are strictly deterministic functions of static Copernicus 30m DEM topography and astronomical solar geometry.
- **Zero reliance on future observations**, ground truth $y_{t+h}$, or weather model forecasts.
- **100% causal and leak-free**.
