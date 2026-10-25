# POLARIS L2-EXP-08 — PRE-REGISTERED ADAPTIVE RISK-BUDGET POLICY
## Formal Pre-Registration Document & Governance Freeze Record

---

### Executive Governance Lock
```
PRE_REGISTRATION_LOCKED = TRUE
POLICY_HASH_SHA256 = 1a5da66efa73aba1a5cbe45e41573aba2cd7089a1cd866838440cc5615c73c96
LOCK_TIMESTAMP_UTC = 2026-10-04T06:17:00Z
STATUS = FROZEN_BEFORE_2024_EVALUATION
```

> **GOVERNANCE MANDATE COMPLIANCE NOTICE**:
> 
> *"This policy was designed, calibrated, and frozen using ONLY pre-2024 development and validation data (2020–2022). Absolutely zero 2024 operational data or simulation outcomes were used to select parameters, thresholds, or mathematical formulations. No production GAP19, Stage8.1, F, SKGBDT, or CQR artifact was modified."*

---

## 1. Scientific Objective & Motivation

In **L2-EXP-07**, static $q_{10}$ planning reduced realized critical-load unmet energy by **93.39%** ($p = 8.75 \times 10^{-20}$), proving that solar forecast uncertainty is vital to operational microgrid resilience. However, static $q_{10}$ planning incurred a significant operational penalty:
- **+38.18%** diesel fuel consumption (+16.36 L/origin).
- **+92.87%** renewable curtailment (+34.65 kWh/origin).

The objective of **L2-EXP-08** is to test whether an adaptive, uncertainty-dependent planning rule can capture most of the robustness gained by $q_{10}$ while avoiding the full fuel and curtailment penalties of always planning for the $10^{\text{th}}$ percentile.

---

## 2. Mathematical Formulation of the Adaptive Policy

The adaptive planning solar power $\hat{y}_{\text{plan}, t} \in \mathbb{R}_{\ge 0}$ (in Watts) is constructed via a single deterministic mapping:

$$\hat{y}_{\text{plan}, t} = \min\left(F_{w, t}, \, (1 - \lambda_t) \cdot F_{w, t} + \lambda_t \cdot q_{10, w, t}\right)$$

where:
- $F_{w, t}$ is the frozen Candidate F point forecast converted to power (W).
- $q_{10, w, t}$ is the calibrated L2-CQR $10^{\text{th}}$ percentile lower bound converted to power (W).
- $\lambda_t \in [0, 1]$ is the **adaptive risk-budgeting factor**.

### 2.1 Decomposition of the Risk-Budgeting Factor $\lambda_t$

The conservatism weight $\lambda_t$ is factored into three independent, physically meaningful terms:

$$\lambda_t = \lambda_{\text{uncert}, t} \times \gamma_{h, t} \times G_t$$

#### 1. Uncertainty Component ($\lambda_{\text{uncert}, t}$)
Measures the relative dispersion of the predictive interval at horizon hour $t$:

$$\tilde{W}_t = \frac{U_{t} - L_{t}}{\max(\text{clearsky\_ghi}_t, \, 25.0 \text{ W/m}^2)}$$

$$\lambda_{\text{uncert}, t} = \text{clip}\left(\frac{\tilde{W}_t - W_{\text{min}}}{W_{\text{max}} - W_{\text{min}}}, \, 0.0, \, 1.0\right)$$

- **$W_{\text{min}} = 0.15$**: Below 15% relative interval width, the forecast is highly confident; $\lambda_{\text{uncert}} \to 0$.
- **$W_{\text{max}} = 0.75$**: Above 75% relative interval width, forecast dispersion is severe; $\lambda_{\text{uncert}} \to 1.0$.
- **$25.0\text{ W/m}^2$ Clearsky Floor**: Prevents numerical singularity during twilight/solar transitions.
- **Empirical Basis (2022 Validation Data)**: On the 5,268 daytime validation rows in 2022, $\tilde{W}_t$ has a $20^{\text{th}}$ percentile of $\approx 0.18$ and an $80^{\text{th}}$ percentile of $\approx 0.71$. The $[0.15, 0.75]$ span maps linear conservatism across the middle 60% of empirical uncertainty.

#### 2. Horizon Component ($\gamma_{h, t}$)
Accounts for forecast lead-time and sensor persistence decay:

$$\gamma_{h, t} = \min\left(1.0, \, h_{\text{min\_weight}} + (1.0 - h_{\text{min\_weight}}) \cdot \frac{h - 1}{h_{\text{sat}} - 1}\right)$$

- **$h_{\text{min\_weight}} = 0.25$**: At $h=1$, immediate ground-station persistence ensures high accuracy (2022 validation MAE is only $5.48\text{ W/m}^2$ at $h=1$ vs $64.88\text{ W/m}^2$ at $h=12$). Near horizons do not require full conservatism.
- **$h_{\text{sat}} = 12$**: By $h=12$, lead-time error saturates into general NWP uncertainty, and full conservatism is permitted ($\gamma_h = 1.0$ for $h \ge 12$).

#### 3. Operational-Relevance Gate ($G_t$)
Ensures conservatism only activates when solar uncertainty actually threatens microgrid energy balance:

$$G_t = \text{clip}\left(\frac{P_{\text{crit}, t} - P_{\text{wind}, t}}{\max(P_{\text{crit}, t}, \, 1.0 \text{ W})}, \, 0.0, \, 1.0\right)$$

- When $P_{\text{wind}, t} \ge P_{\text{crit}, t}$: Anticipated wind generation covers 100% of critical load. Solar uncertainty cannot cause an unmet load deficit in this hour. $G_t = 0.0 \implies \lambda_t = 0 \implies \hat{y}_{\text{plan}} = F_w$.
- When $P_{\text{wind}, t} = 0$: $G_t = 1.0$, allowing full uncertainty-aware conservatism.
- When $0 < P_{\text{wind}, t} < P_{\text{crit}, t}$: $G_t$ scales proportionally to the remaining deficit.

---

## 3. Boundary & Ordering Proofs

1. **Monotonicity**:
   $$\frac{\partial \lambda_t}{\partial \tilde{W}_t} \ge 0, \quad \frac{\partial \lambda_t}{\partial h} \ge 0, \quad \frac{\partial \lambda_t}{\partial P_{\text{wind}, t}} \le 0$$
   Higher uncertainty or longer lead-time NEVER produces a less conservative planning value. Higher wind never increases solar conservatism.

2. **Strict Interval Bounds**:
   When $q_{10, w, t} \le F_{w, t}$:
   $$q_{10, w, t} \le \hat{y}_{\text{plan}, t} \le F_{w, t}$$

3. **Inversion Handling**:
   If $q_{10, w, t} > F_{w, t}$ (rare physical inversion), the $\min(F_{w, t}, \cdot)$ operator guarantees:
   $$\hat{y}_{\text{plan}, t} = F_{w, t}$$
   The planning signal NEVER inflates above the Candidate F point forecast.

4. **Night Causal Zeroing**:
   If $\text{solar\_elevation}_t \le 0$ or $\text{clearsky\_ghi}_t == 0$:
   $$\hat{y}_{\text{plan}, t} = 0.0 \text{ W}$$

---

## 4. Pre-Registration Verification Checkpoint

```
================================================================================
PRE-REGISTRATION VERIFICATION CHECKPOINT
================================================================================
  [X] Formula deterministic and fully specified
  [X] All parameters derived strictly from 2022 validation distribution
  [X] Zero 2024 outcomes inspected or utilized
  [X] Bound constraints mathematically verified
  [X] Inversion rule strictly enforced
  [X] Operational relevance gate firewalled to forecast-time information
  [X] pre_registered_policy.json written and hashed
  [X] PRE_REGISTRATION_LOCKED = TRUE
================================================================================
```
