# POLARIS STAGE 8.21A — FEATURE DEFINITION REPORT

## 1. Feature Set Summary

- **Feature Set Name:** Stage 8.21A Compact 3D Solar Slant-Path Feature Set
- **Target Component:** 3D solar line-of-sight hydrometeor ray intersection
- **Number of Candidate Features:** **4 Compact Non-Redundant Features**

---

## 2. Feature Mathematical Specifications

### Feature 1: `slant_path_optical_depth_proxy` ($\tau_{\text{slant}}$)
- **Units:** Dimensionless
- **Mathematical Formula:**
  $$\tau_{\text{slant}} = \int_S \left( \beta_{\text{ext,liq}}(s) + \beta_{\text{ext,ice}}(s) \right) ds$$
  $$\beta_{\text{ext,liq}} = \frac{3 \rho_{\text{air}} q_l}{2 \rho_w r_{e,\text{liq}}}, \quad \beta_{\text{ext,ice}} = \frac{3 \rho_{\text{air}} q_i}{2 \rho_i r_{e,\text{ice}}}$$
- **Physical Meaning:** Integrated 3D solar line-of-sight cloud optical thickness.

### Feature 2: `slant_path_direct_transmittance` ($T_{\text{dir}}$)
- **Units:** Dimensionless ($0.0 \dots 1.0$)
- **Mathematical Formula:**
  $$T_{\text{dir}} = \exp(-\tau_{\text{slant}})$$
- **Physical Meaning:** Direct-beam solar transmittance proxy along 3D ray path.

### Feature 3: `slant_path_liquid_water_path` ($SLWP$)
- **Units:** $\text{kg/m}^2$ ($\text{g/m}^2$)
- **Mathematical Formula:**
  $$SLWP = \int_S \rho_{\text{air}}(s) q_l(s) \, ds$$
- **Physical Meaning:** Integrated 3D slant-path cloud liquid water content.

### Feature 4: `slant_path_ice_water_path` ($SIWP$)
- **Units:** $\text{kg/m}^2$ ($\text{g/m}^2$)
- **Mathematical Formula:**
  $$SIWP = \int_S \rho_{\text{air}}(s) q_i(s) \, ds$$
- **Physical Meaning:** Integrated 3D slant-path cloud ice water content.

---

## 3. Physical Bounding & Microphysical Assumptions

- **Microphysics Constants:** $r_{e,\text{liq}} = 10\,\mu\text{m}$, $r_{e,\text{ice}} = 30\,\mu\text{m}$, $\rho_w = 1000\text{ kg/m}^3$, $\rho_i = 917\text{ kg/m}^3$.
- **Explicit Labeling:** *PARAMETERIZED DIRECT-BEAM EXTINCTION PROXY — NOT FULL SW_IN RADIATIVE TRANSFER*.
- **Height Coordinate System:** Hydrostatic altitude reconstruction $z(p) = \text{hypsometric upward integration}$ from $P_{\text{sfc}}$ using MEPS $T, q_v, P$.
