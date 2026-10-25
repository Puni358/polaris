# DIESEL CORRECTION
## DIESEL GENERATOR LINEAR FUEL MODEL RECONCILED SPECIFICATION

### 1. SPECIFICATION CORRECTION
Any interpretation of $12.5\text{ L/h}$ as a static flat generator fuel consumption rate is **FORMALLY REMOVED**.

The synthetic fixture specification mandates the existing prototype linear fuel consumption equation:
$$\mathbf{F(P_{\text{gen}}) = 5.0 \cdot u_{\text{gen}}(t) + 0.25 \cdot P_{\text{gen}}(t) \quad [\text{L/h}]}$$

Where:
- $u_{\text{gen}}(t) \in \{0, 1\}$ is the generator binary operating state.
- $F_{\text{base}} = 5.0\text{ L/h}$ is the base idle fuel consumption rate when online ($u_{\text{gen}}=1$).
- $F_{\text{marginal}} = 0.25\text{ L/kWh}$ is the marginal fuel consumption slope per kW generated.

### 2. DERIVED OPERATING POINT EVALUATION
$12.5\text{ L/h}$ is established strictly as the derived consumption rate corresponding to the $30\text{ kW}$ baseline operating point:

| Generator Output Level ($P_{\text{gen}}$) | Operating State ($u_{\text{gen}}$) | Fuel Consumption Calculation | Fuel Consumption Rate ($F$) |
|---|---|---|---|
| **$0.0\text{ kW}$ (Generator OFF)** | $0$ | $5.0(0) + 0.25(0)$ | **$0.0\text{ L/h}$** |
| **$10.0\text{ kW}$ (Minimum Load)** | $1$ | $5.0(1) + 0.25(10) = 5.0 + 2.5$ | **$7.5\text{ L/h}$** |
| **$30.0\text{ kW}$ (Baseline Load)** | $1$ | $5.0(1) + 0.25(30) = 5.0 + 7.5$ | **$12.5\text{ L/h}$** |
| **$60.0\text{ kW}$ (Maximum Output)**| $1$ | $5.0(1) + 0.25(60) = 5.0 + 15.0$ | **$20.0\text{ L/h}$** |

### 3. FORMAL PROVENANCE CLASSIFICATION
- **Classification**: `REUSED_EXISTING_PROTOTYPE_PARAMETER`
- **Station Identity**: `NONE`
- **Empirical Status**: `NOT_ESTABLISHED`
- **Scientific Claim Firewall**: The linear fuel parameters ($5.0\text{ L/h}$ base, $0.25\text{ L/kWh}$ marginal) are synthetic prototype parameters. They MUST NOT be cited as measured fuel curves for a Nuolja diesel generator.

`DIESEL_PROVENANCE_STATUS = RECONCILED_AND_CLEARED`.
