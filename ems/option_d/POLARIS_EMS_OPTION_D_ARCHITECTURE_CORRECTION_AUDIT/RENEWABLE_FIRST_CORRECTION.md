# RENEWABLE FIRST CORRECTION

## 1. DECOUPLED SOLAR/WIND RENEWABLE-FIRST FORMULATION

The audit corrected the scalar aggregation $P_{\text{solar}} + P_{\text{wind}}$ used in earlier documents to ensure full physical validity across independent renewable sources.

---

## 2. FORMULATION CORRECTION

### Previous Scalar Aggregation (Oversimplified):
$$P_{\text{ren,crit}}(t) = \min(P_{\text{solar}}(t) + P_{\text{wind}}(t), P_{\text{critical}}(t))$$

### Corrected Decoupled MILP Formulation:
In the codebase, solar and wind generation are distinct physical inputs (`solar_generation` and `wind_generation` in `ForecastBundle`).

The decision variables are decoupled per renewable asset:
- $P_{\text{sol,crit}}[t]$: Solar power allocated to critical demand.
- $P_{\text{wind,crit}}[t]$: Wind power allocated to critical demand.
- $P_{\text{sol,flex}}[t]$: Solar power allocated to flexible demand.
- $P_{\text{wind,flex}}[t]$: Wind power allocated to flexible demand.
- $P_{\text{chg,ren}}[t]$: Renewable power allocated to battery charging.
- $P_{\text{curt,sol}}[t]$, $P_{\text{curt,wind}}[t]$: Asset-specific curtailment.

### Decoupled Physical Balance Equations:
$$\begin{aligned}
P_{\text{sol,gen}}[t] &= P_{\text{sol,crit}}[t] + P_{\text{sol,flex}}[t] + P_{\text{chg,sol}}[t] + P_{\text{curt,sol}}[t] \\
P_{\text{wind,gen}}[t] &= P_{\text{wind,crit}}[t] + P_{\text{wind,flex}}[t] + P_{\text{chg,wind}}[t] + P_{\text{curt,wind}}[t] \\
P_{\text{ren,crit}}[t] &= P_{\text{sol,crit}}[t] + P_{\text{wind,crit}}[t]
\end{aligned}$$

This decoupled formulation maintains exact asset-level tracking and respects separate solar and wind operational constraints.
