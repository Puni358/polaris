# POLARIS PHASE S0.1 — SPATIAL NWP REPRESENTATION EXPERIMENT
## PROTOCOL CORRECTION & FINAL FREEZE CHECKPOINT

**Date:** September 14, 2026  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}, 702\text{ m ASL}$)  
**Benchmark Context:** POLARIS Phase S0.1 Protocol Correction & Final Freeze  
**Official Champion:** Stage 8.1 37-feature GBDT (`HistGradientBoostingRegressor`)  
**Official Benchmark Baseline:** ODD MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`, Night MAE `0.0 W/m²`  
**Governance Constraint:** NO MODEL TRAINING | NO ODD ACCESS | NO CHAMPION MODIFICATION | NO MODEL PREDICTIONS GENERATED

---

## 1. Executive Verdict

$$\mathbf{VERDICT: SPATIAL\ NWP\ S0.1\ PROTOCOL\ FROZEN}$$

### Summary of Four Protocol Corrections (S0 $\to$ S0.1):
1. **Physical Spatial Extent Clarified:** Explicitly distinguished grid cell counts ($N \times N$) from center-to-center spatial spans ($(N-1) \times 2.5\text{ km}$).
2. **$64\times 64$ Patch Anchor Geometry Clarified:** Reconfirmed anchor cell $(y_0=209, x_0=548)$ placed at zero-indexed position $(31, 31)$ yielding $y \in [178, 241]$, $x \in [517, 580]$. Documented that because 64 is even, the geometric center lies between indices 31 and 32, making the patch upper-left center biased by 1 cell as a fixed, deterministic rule.
3. **Training Loss Explicitly Frozen:** Frozen as **Daytime Mean Absolute Error (MAE) Loss** (`nn.L1Loss()`), directly matching POLARIS's primary benchmark metric. Night hours ($\text{solar elevation} \le 0^\circ$) contribute zero loss/gradient via daytime masking.
4. **Cross-Validation Wording Standardized:** Standardized to exact locked benchmark wording: **"5-fold GroupKFold by forecast origin."** Month is explicitly not the grouping variable.

---

## 2. Detailed Audit of Four Protocol Corrections

### Correction 1 — Physical Spatial Extent & Grid Geometry
To prevent ambiguity between total spatial grid dimensions and distance spans, S0.1 explicitly distinguishes:
- **Grid Cell Dimensions:** $N \times N$ array of cells, each with a $2.5\text{ km} \times 2.5\text{ km}$ native grid spacing.
- **Center-to-Center Spatial Span:** Distance between extreme cell centers along each axis, calculated as $(N - 1) \times 2.5\text{ km}$.

#### Frozen Spatial Footprint Ladder & Physical Spans:
| Footprint | Grid Cell Count ($N \times N$) | Grid Intervals ($N - 1$) | Center-to-Center Span | Physical Coverage Description |
| :-: | :-: | :-: | :-: | :--- |
| **$5\times 5$** | $5 \times 5 = 25\text{ cells}$ | $4\text{ intervals}$ | **$10.0\text{ km}$** | Abisko valley & Lake Torneträsk shoreline micro-neighborhood |
| **$9\times 9$** | $9 \times 9 = 81\text{ cells}$ | $8\text{ intervals}$ | **$20.0\text{ km}$** | Local Scandes mountain ridge advection zone |
| **$13\times 13$** | $13 \times 13 = 169\text{ cells}$ | $12\text{ intervals}$ | **$30.0\text{ km}$** | Sub-regional mountain terrain & valley system |
| **$21\times 21$** | $21 \times 21 = 441\text{ cells}$ | $20\text{ intervals}$ | **$50.0\text{ km}$** | Mesoscale cloud front tracking (Kiruna to Riksgränsen) |
| **$33\times 33$** | $33 \times 33 = 1,089\text{ cells}$ | $32\text{ intervals}$ | **$80.0\text{ km}$** | Broad mountain pass & regional cloud systems |
| **$49\times 49$** | $49 \times 49 = 2,401\text{ cells}$ | $48\text{ intervals}$ | **$120.0\text{ km}$** | Multi-scale mesoscale atmospheric flow |
| **$64\times 64$** | $64 \times 64 = 4,096\text{ cells}$ | $63\text{ intervals}$ | **$157.5\text{ km}$** | Regional atmospheric circulation (Norwegian Sea to Torne basin) |

> [!NOTE]
> For the $64\times 64$ footprint: 64 cells along each dimension, 63 center-to-center intervals, producing an exact **$157.5\text{ km}$ center-to-center span**.

---

### Correction 2 — $64\times 64$ Anchor Geometry & Centering Rule
- **Target Coordinates:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$).
- **AROME-Arctic Nearest Anchor Grid Cell $(y_0, x_0)$:** $(209, 548)$, distance $1.0074\text{ km}$.
- **Geometry Clarification:** Because $N=64$ is an even integer, there is no single center cell. The geometric center lies between zero-index positions 31 and 32.
- **Deterministic Anchor Rule:** The anchor cell $(209, 548)$ is placed at zero-indexed patch coordinate $(31, 31)$.
- **Patch Bounds:**
  - $y$-index bounds: $[209 - 31,\ 209 + 32] = [178,\ 241]$ (inclusive, 64 rows).
  - $x$-index bounds: $[548 - 31,\ 548 + 32] = [517,\ 580]$ (inclusive, 64 columns).
- **Governance Constraint:** This 1-cell upper-left center offset is a deliberate, fixed deterministic rule. The anchor position must **NOT** be shifted to $(32, 32)$ or altered based on model validation performance.
- **Odd Footprints:** All odd-sized patches ($5\times 5$ through $49\times 49$) remain strictly and symmetrically centered on anchor cell $(209, 548)$.

---

### Correction 3 — Frozen Training Loss Function

#### Frozen Loss Function: **Daytime Mean Absolute Error (MAE) Loss** (`torch.nn.L1Loss()`)

$$\mathcal{L}_{\text{daytime\_MAE}} = \frac{1}{N_{\text{daytime}}} \sum_{i \in \text{batch}} \sum_{t \in \text{daytime}} \left| \hat{y}_{i,t} - y_{i,t} \right|$$

#### Scientific Rationale:
1. **Metric Alignment:** POLARIS's primary optimization and evaluation metric across all stages and promotion gates (G1, G2, G3) is Daytime MAE ($\text{W/m}^2$). Training with `L1Loss` aligns the neural network gradient optimization objective directly with the primary evaluation metric.
2. **Empirical Codebase Proof:** Both PyTorch reference implementations in the POLARIS codebase (`phase10_candidate_a_train.py` line 315 and `phase10_candidate_c_train.py` line 348) explicitly define `loss_fn = nn.L1Loss()`.
3. **Outlier Robustness:** Unlike MSE, $L1$ loss penalizes deviations linearly, preventing extreme cloud transients or peak clear-sky spikes from dominating gradient steps.

#### Night Hours Handling & Daytime Masking:
- **Night Contribution:** Night hours ($\text{solar elevation} \le 0^\circ$) contribute **ZERO** loss and **ZERO** gradients during training.
- **Implementation:** For each origin sequence in a batch, hours with $\text{solar elevation} \le 0^\circ$ or clear-sky GHI $= 0$ are masked out before computing loss.
- **Post-Processing Override:** Night predictions are forced hard to $0.0\text{ W/m}^2$ post-inference based on deterministic solar geometry.
- **Loss Uniformity:** The daytime masked `L1Loss` function is 100% identical across all seven spatial footprints.

---

### Correction 4 — Standardized Cross-Validation Wording

- **Locked Benchmark Wording:** **"5-fold GroupKFold by forecast origin."**
- **Grouping Variable:** The forecast origin (each 24-hour forecast origin date is treated as an indivisible group in `sklearn.model_selection.GroupKFold`).
- **Correction:** "Month" is explicitly removed as a grouping descriptor. Grouping is performed strictly by forecast origin.
- **Fold Consistency:** All seven spatial footprints ($5\times 5$ through $64\times 64$) use **EXACTLY THE SAME FIVE EVEN FOLDS**.
- **Data Scope:** 173 EVEN development origins ONLY. 174 ODD test origins remain strictly firewalled.

---

## 3. Scientific Clarification — Spatial Shortwave Radiation Channel

The frozen 11-channel set includes `surface_downwelling_shortwave_flux_in_air` (AROME NWP shortwave radiation forecast).

### Scientific Clarification:
- This channel is a **causal numerical physical prediction** generated by the AROME D-1 18:00 UTC cycle and published on THREDDS at $\approx 20:45\text{ UTC Day } D-1$ ($>3.25\text{h}$ prior to $t_0$).
- The experiment tests whether **preserving the spatial topology of causal NWP fields** improves solar forecasting. It does **NOT** claim to isolate cloud-field spatial topology in isolation from NWP shortwave radiation fields.
- Prohibited inputs remain strictly enforced: future observed $SW\_IN$, future observed cloud/radiation measurements, and post-$t_0$ NWP cycles.
- The 11-channel set is locked. No channels are added or removed, no ablations are performed, and no secondary channel sets are created.

---

## 4. Frozen 11 Spatial Channel Inventory

| Channel Index | NetCDF Parameter Name | Level / Height | Classification | Description |
| :-: | :--- | :--- | :-: | :--- |
| **C1** | `surface_downwelling_shortwave_flux_in_air` | Surface | **REQUIRED** | Direct NWP shortwave radiation forecast field ($W/m^2$). |
| **C2** | `cloud_area_fraction` | Surface (Total) | **REQUIRED** | Total column cloud fraction ($0.0-1.0$). |
| **C3** | `high_type_cloud_area_fraction` | Surface (High) | **REQUIRED** | High-level cirrus cloud fraction ($0.0-1.0$). |
| **C4** | `medium_type_cloud_area_fraction` | Surface (Med) | **REQUIRED** | Mid-level altocumulus cloud fraction ($0.0-1.0$). |
| **C5** | `low_type_cloud_area_fraction` | Surface (Low) | **REQUIRED** | Low-level stratus cloud fraction ($0.0-1.0$). |
| **C6** | `atmosphere_mass_content_of_cloud_liquid_water` | Surface (LWP) | **REQUIRED** | Liquid Water Path ($kg/m^2$). |
| **C7** | `atmosphere_mass_content_of_cloud_ice` | Surface (IWP) | **REQUIRED** | Ice Water Path ($kg/m^2$). |
| **C8** | `x_wind_10m` | 10m Height | **REQUIRED** | Surface zonal wind ($m/s$). |
| **C9** | `y_wind_10m` | 10m Height | **REQUIRED** | Surface meridional wind ($m/s$). |
| **C10** | `x_wind_700hPa` | 700 hPa Level | **REQUIRED** | Steering zonal wind ($m/s$) over Scandes ridge (~3,000m ASL). |
| **C11** | `y_wind_700hPa` | 700 hPa Level | **REQUIRED** | Steering meridional wind ($m/s$) over Scandes ridge (~3,000m ASL). |

---

## 5. Frozen Architecture & Parameter Count Verification

### Architecture Definition:
```
Input Spatial Tensor: [B, T=24, C=11, H, W]
  │
  ├──► 2D CNN Spatial Encoder (shared across T=24)
  │      ├── Conv2d(11, 16, kernel_size=3, padding=1) + BatchNorm2d + ReLU
  │      ├── Conv2d(16, 32, kernel_size=3, padding=1) + BatchNorm2d + ReLU
  │      └── AdaptiveAvgPool2d((1, 1))  <── [Collapses spatial grid H x W to 32-dim vector]
  │
  ├──► Output Spatial Sequence: [B, T=24, 32]
  │
  ├──► Temporal GRU Encoder
  │      └── GRU(input_size=32, hidden_size=32, batch_first=True) ──► Hidden States [B, T=24, 32]
  │
Input Tabular Context: [B, 38] (14 static + 24 station SW_IN history)
  │
  ├──► Tabular MLP: Linear(38, 32) + ReLU ──► [B, 32]
  │
Horizon Output Head (for each t in 1..24):
  ├── Concatenate GRU step hidden state [32] + Tabular context [32] ──► [64]
  ├── Linear(64, 32) + ReLU + Dropout(p=0.2)
  └── Linear(32, 1) ──► Raw Predicted SW_IN [B, 24]
```

### Exact Mathematical Parameter Calculation:
1. `Conv2d(11, 16, k=3, p=1)`: $16 \times 11 \times 3 \times 3 + 16 = 1,584 + 16 = 1,600$
2. `BatchNorm2d(16)`: $16 (\gamma) + 16 (\beta) = 32$
3. `Conv2d(16, 32, k=3, p=1)`: $32 \times 16 \times 3 \times 3 + 32 = 4,608 + 32 = 4,640$
4. `BatchNorm2d(32)`: $32 (\gamma) + 32 (\beta) = 64$
5. `AdaptiveAvgPool2d((1, 1))`: $0$
6. `GRU(input_size=32, hidden_size=32)`:
   - `weight_ih`: $3 \times (32 \times 32) = 3,072$
   - `weight_hh`: $3 \times (32 \times 32) = 3,072$
   - `bias_ih`: $3 \times 32 = 96$
   - `bias_hh`: $3 \times 32 = 96$
   - Total GRU = $3,072 + 3,072 + 96 + 96 = 6,336$
7. `Linear(38, 32)` (Tabular MLP): $38 \times 32 + 32 = 1,248$
8. `Linear(64, 32)` (Head Layer 1): $64 \times 32 + 32 = 2,080$
9. `Linear(32, 1)` (Head Output Layer): $32 \times 1 + 1 = 33$

$$\mathbf{Total\ Trainable\ Parameters} = 1,600 + 32 + 4,640 + 64 + 6,336 + 1,248 + 2,080 + 33 = \mathbf{16,033}$$

- **Parameter Count Parity Verdict:** **VERIFIED**. `AdaptiveAvgPool2d((1,1))` guarantees that all seven spatial footprints ($5\times 5$ through $64\times 64$) have **EXACTLY 16,033 trainable parameters**.

---

## 6. Training & Cross-Validation Protocol

- **Dataset:** 173 EVEN development origins ONLY.
- **Cross-Validation:** 5-fold GroupKFold by forecast origin. Identical folds across all seven footprints.
- **Batch Size:** 8 origins per batch.
- **Optimizer:** `AdamW` ($\text{lr}=10^{-3}$, $\text{weight\_decay}=10^{-4}$).
- **Loss Function:** Daytime Masked `L1Loss()` (`nn.L1Loss()`).
- **Max Epochs & Patience:** 300 max epochs, 20 epochs patience on inner 80/20 train-validation split.
- **Master Seed:** 42 (`torch`, `numpy`, `sklearn`).

---

## 7. Promotion Gates & Winner Selection Rule

### Locked Promotion Gates (G1–G6):
- **G1:** Aggregated EVEN $\Delta\text{MAE} \le -0.50\text{ W/m}^2$ relative to control.
- **G2:** $\ge 4/5$ folds improved ($\Delta\text{MAE}_k < 0$).
- **G3:** Maximum fold degradation $\le +0.50\text{ W/m}^2$ ($\max_k \Delta\text{MAE}_k \le +0.50$).
- **G4:** Candidate $\text{nMAE} \le \text{control nMAE}$ AND Candidate $\text{RMSE} \le \text{control RMSE}$.
- **G5:** 100% causal availability & parser compliance.
- **G6:** Exact control reproduction under identical folds.

### Winner Selection Rule:
1. Filter footprints that pass **ALL** G1–G6 gates.
2. If NO footprint passes, reject spatial models and retain champion Stage 8.1.
3. If MULTIPLE footprints pass:
   - Prefer a larger footprint ONLY if its MAE is practically superior ($\Delta\text{MAE} > 0.25\text{ W/m}^2$ over smaller passing footprints).
   - If performance is practically indistinguishable ($|\Delta\text{MAE}| \le 0.25\text{ W/m}^2$), **SELECT THE SMALLER FOOTPRINT** per the principle of parsimony.

---

## 8. Leakage Firewall Audit

| Potential Leakage Source | Allowed? | Prevention Mechanism | Status |
| :--- | :-: | :--- | :-: |
| **ODD test origins in training** | **NO** | Filtered strictly to 173 EVEN origins. | **INTACT** |
| **ODD test origins in scaling** | **NO** | Scalers fit strictly on training fold origins per CV split. | **INTACT** |
| **Post-$t_0$ NWP cycles used** | **NO** | Restricted to D-1 18:00 UTC cycle published at $\approx 20:45$ UTC D-1. | **INTACT** |
| **Future observed SW_IN used** | **NO** | Target SW_IN used exclusively as loss label. | **INTACT** |
| **Footprint selection using ODD**| **NO** | Footprint selection performed 100% on EVEN 5-fold CV. | **INTACT** |

---

## 9. Final Governance Declarations

$$\mathbf{SPATIAL\ NWP\ S0.1\ PROTOCOL\ FROZEN.}$$
$$\mathbf{NO\ MODEL\ TRAINING\ PERFORMED.}$$
$$\mathbf{NO\ ODD\ DATA\ ACCESSED.}$$
$$\mathbf{CURRENT\ CHAMPION\ UNTOUCHED.}$$
