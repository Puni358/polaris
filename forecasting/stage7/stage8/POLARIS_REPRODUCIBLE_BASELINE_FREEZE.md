# POLARIS — REPRODUCIBLE BASELINE FREEZE MANIFEST

**Date:** September 13, 2026  
**Selected Baseline:** Stage 8.1 700 hPa Steering Wind Model (37 Features)  
**Selection Rationale:** Highest-ranking pipeline stage with 100% real input artifacts, executable code, and verifiable numerical reproducibility.  
**Freeze Status:** FROZEN REPRODUCIBLE BASELINE  

---

## 1. Baseline Model Specification & Hyperparameters

Per Phase 1 of the POLARIS Reproducibility Protocol, the current reproducible baseline model architecture and parameters are strictly frozen:

| Configuration Property | Value / Setting |
| :--- | :--- |
| **Model Estimator** | `sklearn.ensemble.HistGradientBoostingRegressor` |
| **Target Variable** | Residual $y_{\text{true}} - y_{\text{pred, stage4}}$ ($\text{W/m}^2$) |
| **Loss Function** | `'absolute_error'` (MAE) |
| **Max Depth** | `4` |
| **Min Samples Leaf** | `30` |
| **L2 Regularization** | `10.0` |
| **Random Seed** | `42` |
| **Night Forcing Rule** | Causal zero forcing ($0.0\text{ W/m}^2$ when $\text{solar\_elevation} \le 0^\circ \lor \text{clearsky\_ghi} == 0.0$) |

---

## 2. Complete 37-Feature Matrix Inventory

The baseline model utilizes exactly 37 real features constructed from causally valid $t \le t_0$ data:

1. `horizon_hour`
2. `month`
3. `hour`
4. `solar_elevation`
5. `solar_zenith`
6. `clearsky_ghi`
7. `fc_cloud_cover`
8. `fc_temperature_2m`
9. `fc_relative_humidity_2m`
10. `cloud_frac`
11. `pred_stage3b_cloud_nwp`
12. `phys_pred_fold`
13. `pred_stage4_fold`
14. `disagreement_fold`
15. `ctx_std_3h`
16. `ctx_std_6h`
17. `ctx_std_12h`
18. `ctx_std_24h`
19. `ctx_abs_change_1h`
20. `ctx_abs_change_3h`
21. `ctx_abs_change_6h`
22. `ctx_max_diff_6h`
23. `ctx_mean_diff_6h`
24. `ctx_slope_6h`
25. `ctx_kt_std_6h`
26. `ctx_last_obs`
27. `ctx_mean_24h`
28. `ctx_max_24h`
29. `lwp_latest`
30. `iwp_latest`
31. `lwp_x_cloud`
32. `terrain_horizon_elevation_deg`
33. `terrain_elevation_margin_deg`
34. `terrain_solar_obstruction_flag`
35. `clearsky_ghi_terrain_adjusted`
36. `u700`
37. `v700`

---

## 3. Data Splits & Benchmark Protocol

- **Total Benchmark Origins:** 347 daily origins (8,328 forecast hours)
- **EVEN Training Origins:** 174 origins (indices 0, 2, 4, ...)
- **ODD Test Origins:** 173 origins (indices 1, 3, 5, ...)
- **ODD Total Hours:** 4,152 hours
- **ODD Daytime Hours ($\text{SW\_IN} > 0$):** 2,883 hours
- **ODD Night Hours ($\text{SW\_IN} == 0$):** 1,269 hours
