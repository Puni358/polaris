# Stage 7.4 Proposed Vertical Cloud Feature Definitions

To evaluate whether vertical cloud distribution contains useful non-redundant information beyond Stage 6.6 scalar LWP/IWP, we propose 8 physically motivated candidate features:

## 1. Layer LWP Fractions (`f_lwp_low`, `f_lwp_mid`, `f_lwp_high`)
Proportion of surface-aware Liquid Water Path residing in three atmospheric pressure tiers:
* **`f_lwp_low`**: Fraction of LWP at $p > 800	ext{ hPa}$ (boundary layer stratus / low cloud).
* **`f_lwp_mid`**: Fraction of LWP at $500 \le p \le 800	ext{ hPa}$ (altocumulus / mid-level cloud).
* **`f_lwp_high`**: Fraction of LWP at $p < 500	ext{ hPa}$ (cirrus / high-altitude cloud).
$$\sum f_{	ext{LWP}} = 1.0 \quad 	ext{when } 	ext{LWP} > 0, 	ext{ else } 0.0$$

## 2. Mass-Weighted Pressure Centroids (`p_centroid_lwp`, `p_centroid_iwp`)
Mass-weighted average pressure level ($	ext{hPa}$) of cloud liquid water and cloud ice water:
$$p_{	ext{centroid, LWP}} = rac{\sum_k 	ext{LWP}_k \cdot p_{	ext{mid}, k}}{\sum_k 	ext{LWP}_k} \quad (	ext{hPa})$$
$$p_{	ext{centroid, IWP}} = rac{\sum_k 	ext{IWP}_k \cdot p_{	ext{mid}, k}}{\sum_k 	ext{IWP}_k} \quad (	ext{hPa})$$
When cloud water/ice is zero, defaults to model surface pressure $p_{	ext{sfc}}$ (for LWP) and $300	ext{ hPa}$ (for IWP).

## 3. Liquid-vs-Ice Vertical Separation (`dp_ice_liquid_centroid`)
Distance in pressure coordinates ($	ext{hPa}$) between the liquid centroid and ice centroid:
$$\Delta p_{	ext{ice-liquid}} = p_{	ext{centroid, LWP}} - p_{	ext{centroid, IWP}}$$
*Physical Interpretation*: Positive value indicates cloud ice resides higher in the atmosphere (lower pressure) than cloud liquid water, capturing mixed-phase Arctic cloud stratification.

## 4. Layer Cloud Area Fractions (`cloud_frac_mid`, `cloud_frac_high`)
Maximum cloud area fraction ($0 \dots 1$) in the middle ($500 \le p \le 800	ext{ hPa}$) and upper ($p < 500	ext{ hPa}$) pressure tiers, resolving multi-layer cloud overlaps beyond total column cloud fraction.
