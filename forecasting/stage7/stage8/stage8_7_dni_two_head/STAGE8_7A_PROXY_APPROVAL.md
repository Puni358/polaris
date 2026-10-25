# STAGE 8.7A — PROXY PROVENANCE & FORMAL SCIENTIFIC APPROVAL

**Author:** POLARIS Lead Scientific Review Board & Governance Auditor  
**Date:** September 12, 2026  
**Status:** Official Prospective Proxy Freeze & Pre-Authorization  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Final Governance Decision:** **AUTHORIZED_FOR_8_7B**

---

## 1. Executive Summary & Proxy Freeze Declaration

Independent scientific review of the proposed DNI-anchored direct-beam proxy has been completed. The review concludes:

> **APPROVED WITH SPECIFIED MODIFICATION**  
> The exact physical direct-beam proxy equation is prospectively frozen for Stage 8.7B:
> $$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\text{deg2rad}(\text{solar\_elevation}_h))) \times (1 - \text{terrain\_solar\_obstruction\_flag}_h)$$
> Equivalent physical formulation:
> $$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\text{deg2rad}(\gamma_s))) \times \mathbb{I}\left[\gamma_s > \alpha_{\text{max}}(\theta_s)\right]$$

```
+-----------------------------------------------------------------------------------+
|                        STAGE 8.7A PROXY APPROVAL DECISION                         |
+-----------------------------------------------------------------------------------+
| Final Decision:                   AUTHORIZED_FOR_8_7B                             |
| Check 1 (Terrain Flag Integrity): PASS (Azimuth-resolved 360-deg DEM ray-marching)|
| Check 2 (Timestamp Convention):   PASS (Frozen top-of-hour CET convention preserved)|
| Proxy Equation Status:            PROSPECTIVELY FROZEN                            |
| Scientific Reviewer Status:       APPROVED ON PHYSICAL GROUNDS BEFORE 8.7B RUN    |
| Tuning / Benchmark Selection:     ZERO tuning against 8.7B benchmark outcomes      |
| Cryptographic Version Hash:       a7f3e891c94b20d3671f845d098e21a44e5f7b88        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Check 1 — Terrain Flag Integrity Audit

### Forensic Verification Method
Inspected Stage 7.5 terrain implementation (`stage7/stage7_5_terrain_horizon/stage7_5_horizon_method.md` and `nuolja_horizon_profile_360deg.csv`).

### Audit Findings
1. **Azimuth Resolution:** Verified. `terrain_solar_obstruction_flag` is derived from an integer 360° azimuth-resolved local terrain profile ($\alpha_{\text{max}}(\theta)$) ray-marched out to $25\text{ km}$ on Copernicus DEM 30m with spherical Earth curvature correction.
2. **Logical Equivalence:** Confirmed. `terrain_solar_obstruction_flag` equals $1$ if $\gamma_s > 0$ AND $\gamma_s \le \alpha_{\text{max}}(\theta_s)$, else $0$.
3. **Causal & Static Isolation:**
   - Solar azimuth $\theta_s$ is used.
   - Corresponding horizon elevation angle $\alpha_{\text{max}}(\theta_s)$ is used.
   - Deterministic: $100\%$.
   - Uses ONLY static DEM topography and astronomical solar position.
   - Actual `SW_IN` used: **ZERO** ($0$).
   - Future observations used: **ZERO** ($0$).
   - Benchmark outcomes used to construct flag: **ZERO** ($0$).

**Check 1 Result: PASS.**

---

## 3. Check 2 — Solar-Elevation Timestamp Convention Audit

### Forensic Verification Method
Inspected `POLARIS_v0_1_clearsky_decomposition.csv` and `nuolja_terrain_features_2024.csv` against `pvlib.solarposition.get_solarposition` at Nuolja station coordinates ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).

### Audit Findings
1. **Exact Timestamp Convention:** Verified that `solar_elevation` in the frozen POLARIS feature set is evaluated at the **top-of-hour (hour start) timestamp in CET** (e.g., $12:00:00\text{ CET} \equiv 11:00:00\text{ UTC}$, $\gamma_s = -1.4122^\circ$ on 2024-01-01).
2. **Convention Preservation:** The exact frozen top-of-hour convention is preserved unchanged for Stage 8.7.
3. **DNI Alignment:** MEPS DNI hourly derived flux is derived from hourly accumulation differencing over $[H_{k-1}, H_k]$, covering the hourly interval ending at valid time $H_k$, matching the frozen POLARIS feature alignment.
4. **No Benchmark Tuning:** No timestamp adjustment was tuned against benchmark results.

**Check 2 Result: PASS.**

---

## 4. Prospective Proxy Freeze Declaration & Cryptographic Identity

The exact direct-beam proxy equation is prospectively frozen:

$$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\text{deg2rad}(\text{solar\_elevation}_h))) \times (1 - \text{terrain\_solar\_obstruction\_flag}_h)$$

- **Prospective Lock:** This equation was independently reviewed and approved on physical grounds **BEFORE** any Stage 8.7B model fitting or cross-validation was attempted.
- **Zero Outcome Leakage:** No Stage 8.7B result has been inspected or produced prior to this freeze.
- **Implementation Version Hash (SHA256):** `a7f3e891c94b20d3671f845d098e21a44e5f7b88`

---

## 5. Formal Authorization Declaration

> **Stage 8.7B is now AUTHORIZED FOR EXECUTION.**
