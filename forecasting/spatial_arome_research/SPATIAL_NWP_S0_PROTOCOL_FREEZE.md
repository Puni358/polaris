# POLARIS PHASE S0 — SPATIAL NWP REPRESENTATION EXPERIMENT
## PROTOCOL FREEZE & PRE-REGISTRATION CHECKPOINT

**Date:** September 14, 2026  
**Target Location:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}, 702\text{ m ASL}$)  
**Benchmark Context:** POLARIS Phase S0 Pre-Registration & Design Freeze  
**Official Champion:** Stage 8.1 37-feature GBDT (`HistGradientBoostingRegressor`)  
**Official Benchmark Baseline:** ODD MAE `36.188657 W/m²`, nMAE `28.0688%`, RMSE `64.219495 W/m²`, Bias `+1.439399 W/m²`, Night MAE `0.0 W/m²`  
**Governance Constraint:** NO MODEL TRAINING | NO ODD ACCESS | NO CHAMPION MODIFICATION | NO MODEL PREDICTIONS GENERATED

---

## 1. Executive Verdict

$$\mathbf{VERDICT: PROTOCOL\ FROZEN}$$

### Status Summary:
- **Research Question & Hypothesis:** Frozen.
- **Candidate Footprints:** Exactly 7 footprints pre-registered ($5\times 5$, $9\times 9$, $13\times 13$, $21\times 21$, $33\times 33$, $49\times 49$, $64\times 64$).
- **NWP Model Source:** AROME-Arctic 2.5 km Deterministic Archive (D-1 18:00 UTC cycle).
- **Channels & Levels:** 11 2D spatial channels across Surface, 10m, and 700 hPa levels.
- **Model Architecture:** Fixed 16,033-parameter 2D CNN + GRU spatial-temporal network with global adaptive spatial pooling (`AdaptiveAvgPool2d((1,1))`) ensuring strict parameter-count parity across all footprints.
- **Cross-Validation:** Locked 5-fold GroupKFold over 173 EVEN development origins ONLY.
- **Promotion & Winner Selection:** Locked POLARIS G1–G6 promotion gates + parsimony-based footprint selection rule.
- **Leakage Firewall:** 100% verified. Zero ODD access.
- **Training Status:** **NO MODEL TRAINING PERFORMED. ODD NOT ACCESSED. CURRENT CHAMPION UNTOUCHED.**

---

## 2. Research Question & Core Hypothesis

### Research Question:
> *"What spatial footprint around SITES Nuolja provides the most useful causal NWP spatial information for 24-hour solar irradiance forecasting, balancing predictive information against irrelevant/noisy spatial context?"*

### Core Hypothesis:
> *"POLARIS may be representation-limited because previous experiments either used point NWP features or collapsed spatial neighborhoods into scalar summaries. Preserving the spatial topology of causal NWP fields may retain predictive information that the current tabular representation destroys."*

> [!IMPORTANT]
> **Scientific Note:** POLARIS is **NOT** assumed to be definitely information-limited. Phase S0 is explicitly designed to **TEST** this hypothesis under strict experimental controls.

---

## 3. Locked POLARIS Benchmark Definition

The POLARIS benchmark protocol is locked and unchanged:
- **Target Variable:** SITES Nuolja 2024 hourly reconstructed surface downwelling shortwave radiation ($SW\_IN$) in $\text{W/m}^2$.
- **Forecast Input History:** Previous 24 hourly observations ($t_0 - 24\text{h}$ to $t_0 - 1\text{h}$).
- **Forecast Horizon:** Next 24 hourly values ($H1$ through $H24$).
- **Total Clean Origins:** 347 origins across 2024.
- **EVEN Development Set:** 173 even-indexed origins ($0, 2, 4, \dots, 346$) reserved for training, calibration, and cross-validation.
- **ODD Official Test Set:** 174 odd-indexed origins ($1, 3, 5, \dots, 345$) strictly firewalled for official final benchmark evaluation.
- **Benchmark Timing & Causal Lead Mapping:**
  - Forecast origin $t_0 = 00:00\text{ UTC Day } D$.
  - $H1 = 00:00\text{ UTC Day } D$ ($\text{Lead } +6\text{h}$ from D-1 18:00 UTC NWP run).
  - $H2 = 01:00\text{ UTC Day } D$ ($\text{Lead } +7\text{h}$).
  - $\dots$
  - $H24 = 23:00\text{ UTC Day } D$ ($\text{Lead } +29\text{h}$).
- **Causal NWP Cycle:** D-1 18:00 UTC initialization, published on THREDDS at $\approx 20:45\text{ UTC Day } D-1$ ($3.25\text{ to } 3.75\text{ hours}$ before $t_0$).
- **Causal Provenance Status:** $\mathbf{VERDICT: CAUSALLY\ VERIFIED}$.

---

## 4. Protected Champion Safeguards

- **Official Champion:** Stage 8.1 37-feature GBDT (`HistGradientBoostingRegressor`).
- **Official ODD Benchmark Metrics:**
  - MAE: $36.188657\text{ W/m}^2$
  - nMAE: $28.0688\%$
  - RMSE: $64.219495\text{ W/m}^2$
  - Bias: $+1.439399\text{ W/m}^2$
  - Night MAE: $0.0\text{ W/m}^2$
- **Protection Rules:**
  1. The champion model file and predictions are locked and read-only.
  2. No modifications, retrainings, or hyperparameter updates will be applied to Stage 8.1.
  3. No evaluation against ODD origins will be performed during Phase S0.

---

## 5. Distinction from Previous Experiments

Forensic audit of POLARIS history re-confirms:
1. **Stage 8.5 (MEPS 9x9 Summary Features):** Extracted a $9 \times 9$ MEPS grid but reduced it to 14 scalar summary statistics (spatial means, stds, upwind projections) fed into a tabular GBDT. Spatial grid topology $[C, H, W]$ was completely destroyed.
2. **Stage 8.17A (AROME-Arctic Disagreement Features):** Extracted single-point features at the nearest AROME-Arctic grid cell and constructed 3 point-level scalar disagreement features. Zero spatial neighborhood information was retained.

**Conclusion:** *"Raw 2D spatial NWP representation learning remains 100% untested in POLARIS."*

---

## 6. Spatial Footprints to Pre-Register

The pre-registered spatial footprint ladder contains **EXACTLY** the following 7 candidate matrix sizes:

$$\text{Candidate Footprints: } \{ 5\times 5,\ 9\times 9,\ 13\times 13,\ 21\times 21,\ 33\times 33,\ 49\times 49,\ 64\times 64 \}$$

### Pre-Registration Rules:
- **No Additions:** No intermediate matrix sizes ($3\times 3$, $7\times 7$, $11\times 11$, $17\times 17$, etc.) may be added post-hoc.
- **No Removals:** No footprint may be removed due to computational expense (all 7 are computationally feasible).
- **Physical Grid Coverage (at 2.5 km native spacing):**
  - $5\times 5$: $12.5\text{ km} \times 12.5\text{ km}$ ($156.25\text{ km}^2$) — Abisko valley & shoreline micro-neighborhood.
  - $9\times 9$: $22.5\text{ km} \times 22.5\text{ km}$ ($506.25\text{ km}^2$) — Local Scandes mountain ridge advection.
  - $13\times 13$: $32.5\text{ km} \times 32.5\text{ km}$ ($1,056.25\text{ km}^2$) — Sub-regional mountain terrain & valley system.
  - $21\times 21$: $52.5\text{ km} \times 52.5\text{ km}$ ($2,756.25\text{ km}^2$) — Mesoscale cloud front tracking (Kiruna to Riksgränsen).
  - $33\times 33$: $82.5\text{ km} \times 82.5\text{ km}$ ($6,806.25\text{ km}^2$) — Broad mountain pass & regional cloud systems.
  - $49\times 49$: $122.5\text{ km} \times 122.5\text{ km}$ ($15,006.25\text{ km}^2$) — Multi-scale mesoscale atmospheric flow.
  - $64\times 64$: $160.0\text{ km} \times 160.0\text{ km}$ ($25,600.0\text{ km}^2$) — Regional atmospheric circulation (Norwegian Sea to Torne basin).

---

## 7. Experimental Variable Isolation

Spatial footprint ($H \times W$) is strictly isolated as the **SOLE** independent variable. All controlled variables remain invariant across all 7 runs:
- Same 173 EVEN development origins.
- Same 5-fold GroupKFold split assignment.
- Same causal NWP initialization cycle (D-1 18:00 UTC).
- Same target ($SW\_IN$ in $\text{W/m}^2$).
- Same 24-hour forecast horizon ($H1$ to $H24$).
- Same feature preprocessing and per-channel standard scaling.
- Same neural model architecture, filter counts, and hidden dimensions.
- Same optimizer ($\text{AdamW}$, $\text{lr}=10^{-3}$, $\text{weight\_decay}=10^{-4}$).
- Same loss function (Masked MSE over daytime hours).
- Same maximum epochs (300) and early stopping patience (20 epochs).
- Same random seed policy ($\text{seed}=42$).
- Same hard night-zero post-processing rule.
- Same G1–G6 promotion gates.

---

## 8. Scientifically Justified Channel Selection

11 spatial 2D channels are selected and frozen based on physical atmospheric relevance, 100% online archive availability in 2024, and causal integrity:

| Channel Index | NetCDF Parameter Name | Level / Height | Classification | Scientific Rationale |
| :-: | :--- | :--- | :-: | :--- |
| **C1** | `surface_downwelling_shortwave_flux_in_air` | Surface | **REQUIRED** | Direct NWP radiation forecast field ($W/m^2$). Causally derived from D-1 18Z run. |
| **C2** | `cloud_area_fraction` | Surface (Total) | **REQUIRED** | Total column cloud fraction ($0.0-1.0$), primary governor of solar extinction. |
| **C3** | `high_type_cloud_area_fraction` | Surface (High) | **REQUIRED** | Cirrus/high-level cloud fraction; high transmittivity, distinct optical properties. |
| **C4** | `medium_type_cloud_area_fraction` | Surface (Med) | **REQUIRED** | Mid-level altocumulus/altostratus cloud fraction; moderate optical thickness. |
| **C5** | `low_type_cloud_area_fraction` | Surface (Low) | **REQUIRED** | Low stratus/cumulus cloud fraction; dense optical extinction near mountain surface. |
| **C6** | `atmosphere_mass_content_of_cloud_liquid_water` | Surface (LWP) | **REQUIRED** | Liquid Water Path ($kg/m^2$); integrated liquid condensate optical depth. |
| **C7** | `atmosphere_mass_content_of_cloud_ice` | Surface (IWP) | **REQUIRED** | Ice Water Path ($kg/m^2$); integrated ice condensate optical depth. |
| **C8** | `x_wind` (10m) | 10m Height | **REQUIRED** | Surface zonal wind ($m/s$); captures low-level terrain-forced flow in Abisko valley. |
| **C9** | `y_wind` (10m) | 10m Height | **REQUIRED** | Surface meridional wind ($m/s$); captures valley advection towards Nuolja. |
| **C10** | `x_wind` (700 hPa) | 700 hPa Level | **REQUIRED** | Steering zonal wind ($m/s$) at ~3,000m ASL over Scandes ridge. |
| **C11** | `y_wind` (700 hPa) | 700 hPa Level | **REQUIRED** | Steering meridional wind ($m/s$) controlling cloud propagation speed/direction. |

### Explicitly Rejected Variables:
- **Surface Pressure (`surface_air_pressure`):** **REJECTED.** Smooth spatial gradient provides minimal independent local spatial information compared to 700 hPa winds and cloud fields.
- **3D Cloud Water/Ice at 13 Pressure Levels:** **REJECTED.** Column integrals (LWP/IWP) already capture total optical mass per 2D cell. 3D stacks introduce 13x tensor bloat and risk file lead truncation on certain MEPS dates.
- **65 Hybrid Model Levels:** **REJECTED.** Unnecessary computational complexity for S0 spatial scale evaluation.

---

## 9. Vertical Level Selection

Frozen vertical levels:
1. **Surface Level ($0\text{ m}$):** Radiation, cloud fractions (total, high, med, low), LWP, IWP.
2. **10m Height Level ($10\text{ m}$):** Surface wind components ($U_{10m}, V_{10m}$).
3. **700 hPa Pressure Level ($\approx 3,000\text{ m ASL}$):** Steering wind components ($U_{700}, V_{700}$).

**Rationale:** SITES Nuolja is situated at $702\text{ m ASL}$. The $700\text{ hPa}$ level represents the free-atmosphere steering flow over the Scandes mountain tops, controlling cloud advection into the Abisko valley basin.

---

## 10. NWP Model Source Selection

- **Frozen NWP Source:** **AROME-Arctic 2.5 km Deterministic Archive**.
- **Rationale:**
  1. Closer proximity to SITES Nuolja ($1.007\text{ km}$ vs $1.243\text{ km}$ for MEPS).
  2. Dedicated polar/Arctic physics parameterizations (HARMONIE-AROME).
  3. 100% online availability across all 366 days of 2024 with zero file fragmentation across all 67 lead hours.
  4. Single deterministic model prevents confounding multi-model ensemble blending.

---

## 11. Patch Extraction Geometry

### Coordinates:
- SITES Nuolja: $68.362074^\circ\text{N}, 18.738752^\circ\text{E}, 702\text{ m ASL}$.
- AROME-Arctic Nearest Anchor Grid Cell $(y_0, x_0)$: $(209, 548)$, coordinates $68.364774^\circ\text{N}, 18.715312^\circ\text{E}$, distance $1.0074\text{ km}$.

### Extraction Rules:
- **Odd Footprints ($N \in \{5, 9, 13, 21, 33, 49\}$):**
  - Symmetric half-width $k = (N - 1) / 2$.
  - $y$-index bounds: $[y_0 - k,\ y_0 + k]$.
  - $x$-index bounds: $[x_0 - k,\ x_0 + k]$.
- **Even Footprint ($64\times 64$):**
  - Anchor cell $(209, 548)$ placed deterministically at patch zero-indexed position $(31, 31)$.
  - $y$-index bounds: $[209 - 31,\ 209 + 32] = [178,\ 241]$ (inclusive, 64 cells).
  - $x$-index bounds: $[548 - 31,\ 548 + 32] = [517,\ 580]$ (inclusive, 64 cells).

---

## 12. Domain Boundary Audit

- AROME-Arctic Grid Extent: $y \in [0, 948]$ (949 rows), $x \in [0, 738]$ (739 columns).
- Largest Patch ($64\times 64$) Bounds: $y \in [178, 241]$, $x \in [517, 580]$.
- Margin to Grid Edges: $>170\text{ cells}$ on all sides.
- **Verdict:** Zero domain egress or edge clipping occurs. No spatial padding or origin rejection is required.

---

## 13. Temporal Representation

- For each forecast origin $t_0 = 00:00\text{ UTC Day } D$, the spatial tensor contains $T=24$ sequential hourly forecast frames corresponding to $H1\dots H24$ (leads $+6\text{h}$ to $+29\text{h}$ from D-1 18Z run).
- Tensor Shape: $[T=24, C=11, H, W]$.
- **Historical Station SW_IN Features:** 38 scalar features (14 static contextual + 24 historical station SW_IN observations) enter via a parallel Tabular Feature MLP and are concatenated with temporal spatial embeddings before the final horizon output head.

---

## 14. Target & Night Zero Handling

- **Target:** Hourly reconstructed $SW\_IN$ ($W/m^2$) for $H1\dots H24$.
- **Night Zero Rule:** Post-prediction hard zero override ($\hat{y}_h = 0$ for all hours where solar elevation $\le 0^\circ$ or clear-sky GHI $= 0$ based on deterministic solar geometry at Nuolja).
- **Loss Function:** Masked MSE loss evaluated strictly over daytime hours ($\text{solar elevation} > 0^\circ$).

---

## 15. Normalization Protocol

- Scalers fit **STRICTLY ON TRAINING ORIGINS ONLY** of each CV fold.
- Zero ODD or validation statistics used.
- Spatial channels: Standard Z-score scaling per channel $z = (x - \mu_c) / \sigma_c$, clipped to $[-5.0, +5.0]$.

---

## 16. Fixed Model Architecture (Parameter Count Parity)

A single spatial-temporal 2D CNN + GRU architecture is frozen:

```
Input Spatial Tensor: [B, T=24, C=11, H, W]
  │
  ├──► 2D CNN Spatial Encoder (shared across T=24)
  │      ├── Conv2d(11, 16, kernel_size=3, padding=1) + BatchNorm2d + ReLU
  │      ├── Conv2d(16, 32, kernel_size=3, padding=1) + BatchNorm2d + ReLU
  │      └── AdaptiveAvgPool2d((1, 1))  <── [Guarantees fixed 32-dim spatial vector regardless of H x W]
  │
  ├──► Output Spatial Sequence: [B, T=24, 32]
  │
  ├──► Temporal GRU Encoder
  │      └── GRU(input_size=32, hidden_size=32, batch_first=True) ──► [B, T=24, 32]
  │
Input Tabular Context: [B, 38]
  │
  ├──► Tabular MLP: Linear(38, 32) + ReLU ──► [B, 32]
  │
Horizon Output Head (for each t in 1..24):
  ├── Concatenate GRU step hidden state [32] + Tabular context [32] ──► [64]
  ├── Linear(64, 32) + ReLU + Dropout(p=0.2)
  └── Linear(32, 1) ──► Raw Predicted SW_IN [B, 24]
```

### Parameter Breakdown (100% Invariant across all 7 footprints):
- `Conv2d(11, 16, k=3, p=1)`: $1,600$
- `BatchNorm2d(16)`: $32$
- `Conv2d(16, 32, k=3, p=1)`: $4,640$
- `BatchNorm2d(32)`: $64$
- `AdaptiveAvgPool2d((1,1))`: $0$
- `GRU(32, 32)`: $6,336$
- `Linear(38, 32)` (Tabular): $1,248$
- `Linear(64, 32)` (Head): $2,080$
- `Linear(32, 1)` (Head): $33$
- **Total Trainable Parameters:** **16,033 parameters** (identical for $5\times 5$, $9\times 9$, $13\times 13$, $21\times 21$, $33\times 33$, $49\times 49$, $64\times 64$).

---

## 17. Training & Reproducibility Settings

- **Master Seed:** `42` (`torch`, `numpy`, `sklearn`).
- **Optimizer:** `AdamW` ($\text{lr}=10^{-3}$, $\beta_1=0.9, \beta_2=0.999$, $\text{weight\_decay}=10^{-4}$).
- **Batch Size:** 8 origins per batch.
- **Max Epochs:** 300 epochs.
- **Early Stopping:** Patience of 20 epochs based on inner 80/20 train-validation loss.

---

## 18. Cross-Validation Protocol

- **Dataset:** 173 EVEN development origins ONLY.
- **Splits:** 5-fold GroupKFold by origin date/month grouping.
- **Folds:** Identical fold assignments applied to all 7 spatial footprints.

---

## 19. Promotion Gates (G1–G6)

To be promoted, a candidate spatial model must pass:
- **G1:** Aggregated EVEN $\Delta\text{MAE} \le -0.50\text{ W/m}^2$ relative to control.
- **G2:** $\ge 4/5$ folds improved ($\Delta\text{MAE}_k < 0$).
- **G3:** Maximum fold degradation $\le +0.50\text{ W/m}^2$ ($\max_k \Delta\text{MAE}_k \le +0.50$).
- **G4:** Candidate $\text{nMAE} \le \text{control nMAE}$ AND candidate $\text{RMSE} \le \text{control RMSE}$.
- **G5:** 100% causal availability & parser compliance.
- **G6:** Exact control reproduction.

---

## 20. Winner Selection Rule

1. Filter footprints that pass ALL G1–G6 gates.
2. If NO footprint passes, NO spatial model is promoted.
3. If MULTIPLE footprints pass:
   - Prefer larger footprint only if its MAE is meaningfully superior ($\Delta\text{MAE} > 0.25\text{ W/m}^2$ over smaller passing footprints).
   - If performance between footprints is statistically/practically indistinguishable ($|\Delta\text{MAE}| \le 0.25\text{ W/m}^2$), **SELECT THE SMALLER FOOTPRINT** per the principle of parsimony.

---

## 21. Computational Feasibility Summary

| Footprint | Tensor Shape $[T, C, H, W]$ | Size / Origin (float32) | Total EVEN Storage (173 Origins) | Total 347 Storage | Batch Memory (B=8) | Est. Train Time (5 Folds) | Feasibility Verdict |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **$5\times 5$** | $[24, 11, 5, 5]$ | $26.4\text{ KB}$ | $4.57\text{ MB}$ | $9.16\text{ MB}$ | $211.2\text{ KB}$ | $\sim 1.5\text{ min}$ | **FEASIBLE** |
| **$9\times 9$** | $[24, 11, 9, 9]$ | $85.5\text{ KB}$ | $14.80\text{ MB}$ | $29.68\text{ MB}$ | $684.3\text{ KB}$ | $\sim 2.5\text{ min}$ | **FEASIBLE** |
| **$13\times 13$** | $[24, 11, 13, 13]$ | $178.5\text{ KB}$ | $30.87\text{ MB}$ | $61.93\text{ MB}$ | $1.43\text{ MB}$ | $\sim 3.5\text{ min}$ | **FEASIBLE** |
| **$21\times 21$** | $[24, 11, 21, 21]$ | $465.7\text{ KB}$ | $80.57\text{ MB}$ | $161.60\text{ MB}$ | $3.73\text{ MB}$ | $\sim 5.0\text{ min}$ | **FEASIBLE** |
| **$33\times 33$** | $[24, 11, 33, 33]$ | $1.15\text{ MB}$ | $198.97\text{ MB}$ | $399.05\text{ MB}$ | $9.20\text{ MB}$ | $\sim 8.0\text{ min}$ | **FEASIBLE** |
| **$49\times 49$** | $[24, 11, 49, 49]$ | $2.54\text{ MB}$ | $438.63\text{ MB}$ | $879.80\text{ MB}$ | $20.28\text{ MB}$ | $\sim 14.0\text{ min}$ | **FEASIBLE** |
| **$64\times 64$** | $[24, 11, 64, 64]$ | $4.33\text{ MB}$ | $748.29\text{ MB}$ | $1.50\text{ GB}$ | $34.60\text{ MB}$ | $\sim 20.0\text{ min}$ | **FEASIBLE** |

---

## 22. Leakage Firewall Table

| Potential Leakage Source | Allowed? | Prevention Strategy | Firewall Status |
| :--- | :-: | :--- | :-: |
| **ODD test origins in training** | **NO** | Filtered to 173 EVEN origins ($0, 2, 4, \dots, 346$) only. | **INTACT** |
| **ODD test origins in scaler fitting** | **NO** | Standard scalers fit strictly on training fold origins within CV loop. | **INTACT** |
| **Post-$t_0$ NWP runs used** | **NO** | Strictly restricted to D-1 18:00 UTC cycle (published $\approx 20:45$ UTC D-1). | **INTACT** |
| **Future observed SW_IN used as input**| **NO** | Target SW_IN used exclusively as ground-truth label for loss evaluation. | **INTACT** |
| **Future observed cloud data used** | **NO** | Only NWP forecast cloud fields from D-1 18Z run used. | **INTACT** |
| **Footprint selection using ODD** | **NO** | Matrix selection performed strictly on EVEN 5-fold CV results. | **INTACT** |

---

## 23. Scientific Isolation Audit ("What We Are Testing")

- **Control:** Current tabular point representation (Stage 8.1 37-feature GBDT).
- **Experiment:** 2D spatial tensor representation learning across 7 spatial footprints.
- **Independent Variable:** Spatial footprint size ($H \times W$).
- **Dependent Variables:** Forecast MAE, RMSE, nMAE, Bias, and fold stability.
- **Controlled Variables:** Causal NWP run, origin set, CV folds, target, horizon, architecture, parameters (16,033), channels (11), optimizer, loss, seeds, night-zero rule, promotion gates.

> [!NOTE]
> This experiment isolates spatial scale to test: **"Does preserving 2D spatial topology improve solar forecasting, and what spatial footprint balances predictive signal against spatial noise?"**

---

## 24. Final Governance & Protocol Compliance Statements

$$\mathbf{NO\ MODEL\ TRAINING\ PERFORMED.}$$
$$\mathbf{ODD\ NOT\ ACCESSED.}$$
$$\mathbf{CURRENT\ CHAMPION\ UNTOUCHED.}$$

This protocol freeze checkpoint is fully recorded and pre-registered before training begins.
