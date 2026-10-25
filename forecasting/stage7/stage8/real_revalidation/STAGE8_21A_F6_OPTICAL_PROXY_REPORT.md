# POLARIS STAGE 8.21A — PART C: F6 OPTICAL ATTENUATION PROXY REPORT

## 1. MEPS Microphysics Variable Audit

- **Directly Observed MEPS Variables:**
  - `mass_fraction_of_cloud_condensed_water_in_air_pl` ($q_l$, Units: $\text{kg/kg}$)
  - `mass_fraction_of_cloud_ice_in_air_pl` ($q_i$, Units: $\text{kg/kg}$)
- **NOT Available in Pressure Level Archive:** Effective particle radius $r_e$, cloud optical depth $\tau$, extinction coefficient $\beta_{\text{ext}}$.

---

## 2. Parameterized Optical Extinction Proxy Derivation

Geometric optics / anomalous diffraction approximation for volume extinction coefficient $\beta_{\text{ext}}$ ($\text{m}^{-1}$):
$$\beta_{\text{ext,liq}} = \frac{3 \rho_{\text{air}} q_l}{2 \rho_w r_{e,\text{liq}}}, \quad \beta_{\text{ext,ice}} = \frac{3 \rho_{\text{air}} q_i}{2 \rho_i r_{e,\text{ice}}}$$
where $\rho_{\text{air}} = \frac{p}{R_d T_v}$, $\rho_w = 1000\text{ kg/m}^3$, $\rho_i = 917\text{ kg/m}^3$.

Total slant optical thickness along solar ray $S$:
$$\tau_{\text{slant}} = \int_S \left(\beta_{\text{ext,liq}}(s) + \beta_{\text{ext,ice}}(s)\right) \, ds$$

---

## 3. Microphysical Sensitivity Analysis Table (Feasibility Only)

Testing at $P=700\text{ hPa}$ ($\rho_{\text{air}} \approx 0.956\text{ kg/m}^3$), $q_l = 0.2\text{ g/kg}$, $q_i = 0.05\text{ g/kg}$ across $1\text{ km}$ layer thickness at $\theta_z = 60^\circ$:

| Microphysics Scenario | Liquid $r_{e,\text{liq}}$ | Ice $r_{e,\text{ice}}$ | $\beta_{\text{liq}}$ ($\text{km}^{-1}$) | $\beta_{\text{ice}}$ ($\text{km}^{-1}$) | $\beta_{\text{total}}$ ($\text{km}^{-1}$) | Layer $\tau$ ($60^\circ$, $1\text{ km}$) | Direct Transmittance ($T_{\text{dir}}$) |
|---|---|---|---|---|---|---|---|
| **Baseline Standard** | $10\,\mu\text{m}$ | $30\,\mu\text{m}$ | $0.0287$ | $0.0026$ | **$0.0313$** | **$0.0626$** | **$0.9393$** ($93.9\%$) |
| **Fine Droplets/Ice** | $6\,\mu\text{m}$ | $20\,\mu\text{m}$ | $0.0478$ | $0.0039$ | **$0.0517$** | **$0.1034$** | **$0.9018$** ($90.2\%$) |
| **Coarse Droplets/Ice** | $15\,\mu\text{m}$ | $45\,\mu\text{m}$ | $0.0191$ | $0.0017$ | **$0.0208$** | **$0.0416$** | **$0.9593$** ($95.9\%$) |

---

## 4. Conceptual Four-Level Distinction

1. **3D Hydrometeor Geometry:** Where $q_l / q_i$ exist along the solar vector.
2. **Integrated Condensate Path:** Slant Liquid/Ice Path ($\text{g/m}^2$).
3. **Parameterized Direct Extinction Proxy:** Direct beam transmittance $T_{\text{dir}} = \exp(-\tau_{\text{slant}})$.
4. **Full Radiative Transfer:** Multi-stream scattering for Global Downwelling Shortwave ($SW_{\text{IN}}$).

Stage 8.21A represents level #3 (**Parameterized Direct Extinction Feature Proxy**), NOT level #4.

---

## 5. F6 Gate Verdict & Resolution

- **Verdict:** **`CONDITIONAL — PARAMETERIZED ATTENUATION PROXY`**
- **Reasoning:** Microphysical effective radius ($r_{e,\text{liq}}=10\,\mu\text{m}, r_{e,\text{ice}}=30\,\mu\text{m}$) is a parameterized assumption, NOT an observed MEPS variable. F6 cannot be PASS as an observed variable, but is a **PHYSICALLY DEFENSIBLE PARAMETERIZED FEATURE PROXY**.
