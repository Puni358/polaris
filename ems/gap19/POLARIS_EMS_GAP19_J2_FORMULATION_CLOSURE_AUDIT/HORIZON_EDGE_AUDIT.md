# Horizon-Edge Mathematical & Formulation Audit

## 1. The Horizon-Edge Problem Definition

The POLARIS EMS operates over a finite MPC forecast horizon $H = 24\text{ hours}$ (indexed $t = 0, 1, \dots, 23$).
The governed Emergency Battery Reserve (EBR) requires sustaining protected critical service over $T_{\text{REQUIRED}} = 6\text{ hours}$ ($N_{\text{req}} = 6\text{ timesteps}$).

At any timestep $t$, the full 6-hour lookahead window spans interval $[t, t+5]$.
When $t \ge 19$ (i.e. $t = 19, 20, 21, 22, 23$), the 6-hour lookahead window extends past the end of the 24-hour forecast horizon ($t = 23$):

- For $t = 19$: Lookahead spans $[19, 24]$ $\implies$ timestep 24 is OUTSIDE the 24h forecast bundle.
- For $t = 20$: Lookahead spans $[20, 25]$ $\implies$ timesteps 24, 25 are OUTSIDE.
- For $t = 21$: Lookahead spans $[21, 26]$ $\implies$ timesteps 24, 25, 26 are OUTSIDE.
- For $t = 22$: Lookahead spans $[22, 27]$ $\implies$ timesteps 24..27 are OUTSIDE.
- For $t = 23$: Lookahead spans $[23, 28]$ $\implies$ timesteps 24..28 (5 full hours) are OUTSIDE.

Because `ForecastBundle` currently terminates at $t = 23$, critical load forecasts $P_{\text{crit}}[k]$ for $k \ge 24$ do not exist in the active forecast object.

---

## 2. Analysis of Five Candidate Resolution Strategies

### Strategy 1: Truncated Window Summation (Naive Truncation)
Sum critical demand only over available horizon steps $k \in [t, 23]$:
$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{23} P_{\text{crit}}[k] \cdot \Delta t, \quad \text{for } t \in [19, 23]$$
- **Mathematical Effect**: Lookahead duration effectively shrinks from 6h at $t=18$ to 1h at $t=23$.
- **Operational Risk**: `HIGH RISK`. As $t$ approaches 23, the calculated EBR target drops sharply toward zero. The optimizer views this artificial drop as permission to discharge the battery during late night hours, depleting the reserve precisely when entering the next day.

### Strategy 2: Tail Persistence Extrapolation (Standing Load Extension)
Assume critical load for missing steps $k \in [24, t+5]$ equals the last available forecast step $P_{\text{crit}}[23]$:
$$E_{\text{EBR,target}}[t] = \frac{1}{\eta_{\text{dis}}} \left( \sum_{k=t}^{23} P_{\text{crit}}[k] \cdot \Delta t + (t + 5 - 23) \cdot P_{\text{crit}}[23] \cdot \Delta t \right)$$
- **Mathematical Effect**: Preserves a constant 6-hour lookahead window duration across all timesteps $t \in [0, 23]$.
- **Operational Risk**: `LOW RISK`. Safe, conservative zero-cost assumption. Avoids artificial target collapse at horizon boundary.

### Strategy 3: Standing Diurnal Profile Extension
Fill missing steps $k \in [24, t+5]$ using the standing historical critical load profile for hours $0..4$ of the station profile.
- **Mathematical Effect**: Uses realistic morning load expectations for hours $24..28$.
- **Operational Risk**: `LOW RISK`. Requires binding station diurnal profile metadata.

### Strategy 4: Extended Forecast Horizon Architecture (30-Hour ForecastBundle)
Extend the canonical `ForecastBundle` schema horizon from $H = 24\text{h}$ to $H_{\text{ext}} = H + N_{\text{req}} = 30\text{ hours}$.
- **Mathematical Effect**: Provides true predictive 6-hour lookahead for all 24 optimization decision timesteps $t \in [0, 23]$.
- **Operational Risk**: `ZERO ALGORITHMIC RISK`, but requires upstream forecasting pipelines (NWP / Chronos / Moirai) to produce 30-hour forecast horizons.

### Strategy 5: Terminal Reserve Hand-Off Coupling
At horizon edge $t \in [19, 23]$, bound the EBR target drop by coupling it directly to the Terminal Reserve target $E_{\text{term,target}}$:
$$E_{\text{stage2,target}}[t] = \max\left( \frac{1}{\eta_{\text{dis}}} \sum_{k=t}^{23} P_{\text{crit}}[k] \cdot \Delta t, \, E_{\text{term,target}} \right)$$
- **Mathematical Effect**: Ensures that Terminal Reserve prevents the EBR target from collapsing at horizon edge.

---

## 3. Comparison & Engineering Recommendation

| Strategy | Algorithmic Integrity | Data Requirement | Schema Extension Required | Governance Authorization Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Truncated Window** | `UNACCEPTABLE` (Artificial reserve drop) | None (Current 24h) | None | `NOT RECOMMENDED` |
| **2. Tail Persistence** | `GOOD` (Constant 6h duration) | None (Current 24h) | None | `ENGINEERING PROPOSAL` |
| **3. Diurnal Profile** | `EXCELLENT` (Realistic load shape) | Diurnal Profile | Additive Metadata | `ENGINEERING PROPOSAL` |
| **4. 30h Horizon** | `OPTIMAL` (True forecast lookahead) | 30h Forecast Bundle | `ForecastBundle` Horizon Extension | `GOVERNANCE DECISION REQUIRED` |
| **5. Terminal Coupling** | `GOOD` (Prevents collapse) | $E_{\text{term,target}}$ Policy | None | `DEPENDS ON TERMINAL POLICY` |

---

## 4. Audit Finding & Required Governance Choice

Horizon-edge handling MUST be explicitly resolved before implementation design.
Strategy 1 (Truncated Window) MUST be explicitly rejected as mathematically flawed.
Selecting between **Strategy 2 (Tail Persistence)**, **Strategy 4 (30h ForecastBundle)**, and **Strategy 5 (Terminal Coupling)** is a **GOVERNANCE DECISION** that remains open.
