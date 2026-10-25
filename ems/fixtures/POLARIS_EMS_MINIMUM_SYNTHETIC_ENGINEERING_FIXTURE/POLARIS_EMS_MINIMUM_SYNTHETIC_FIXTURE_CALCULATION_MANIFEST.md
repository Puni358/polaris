# CALCULATION MANIFEST
## MATHEMATICAL & PHYSICAL MODEL SPECIFICATION

### 1. DIESEL GENERATOR FUEL CONSUMPTION MODEL
The synthetic generator fuel consumption rate $F(t)$ is calculated dynamically at every timestep $t$ using the frozen prototype linear equation:
$$F(t) = 5.0 \cdot u_{\text{gen}}(t) + 0.25 \cdot P_{\text{gen}}(t) \quad [\text{L/h}]$$

Where:
- $u_{\text{gen}}(t) \in \{0, 1\}$ indicates generator operating status (0 = OFF, 1 = ON).
- $P_{\text{gen}}(t)$ is the electrical output delivered ($10.0\text{ kW} \le P_{\text{gen}}(t) \le 60.0\text{ kW}$ when $u_{\text{gen}}(t) = 1$).

#### Derived Consumption Reference Points:
- $P_{\text{gen}} = 0.0\text{ kW} \implies F = 0.0\text{ L/h}$
- $P_{\text{gen}} = 10.0\text{ kW} \implies F = 5.0(1) + 0.25(10) = 7.5\text{ L/h}$
- $P_{\text{gen}} = 30.0\text{ kW} \implies F = 5.0(1) + 0.25(30) = 12.5\text{ L/h}$
- $P_{\text{gen}} = 60.0\text{ kW} \implies F = 5.0(1) + 0.25(60) = 20.0\text{ L/h}$

### 2. BATTERY ENERGY STATE TRANSITION MODEL
The battery state of charge $SOC(t)$ and stored energy $E_{\text{batt}}(t)$ transition according to:
$$E_{\text{batt}}(t+1) = E_{\text{batt}}(t) + \left( \eta_c \cdot P_{\text{batt,charge}}(t) - \frac{P_{\text{batt,dis}}(t)}{\eta_d} \right) \cdot \Delta t \quad [\text{kWh}]$$
$$SOC(t) = \frac{E_{\text{batt}}(t)}{E_{\text{cap}}} \times 100\%$$

Where:
- Nominal Capacity $E_{\text{cap}} = 200.0\text{ kWh}$.
- Charge/Discharge Efficiency $\eta_c = \eta_d = \sqrt{0.90} \approx 0.9487$ ($90\%$ Round-Trip Efficiency).
- Technical Minimum SOC Floor: $SOC_{\text{min}} = 20.0\%$ ($E_{\text{min}} = 40.0\text{ kWh}$).
- Technical Maximum SOC Ceiling: $SOC_{\text{max}} = 95.0\%$ ($E_{\text{max}} = 190.0\text{ kWh}$).
- Power Bounds: $0 \le P_{\text{batt,charge}}(t) \le 50.0\text{ kW}$, $0 \le P_{\text{batt,dis}}(t) \le 50.0\text{ kW}$.

### 3. PROTECTED CRITICAL LOAD VECTOR SUMMATION
Total protected critical load $P_{\text{critical\_total}}(t)$ is strictly equal to the sum of its three synthetic aggregate components:
$$P_{\text{critical\_total}}(t) = P_{\text{heating}}(t) + P_{\text{water}}(t) + P_{\text{comms}}(t) \quad [\text{kW}]$$
$$30.0\text{ kW} = 15.0\text{ kW} + 10.0\text{ kW} + 5.0\text{ kW}$$

Under Option D governance, all three subsystems have **equal statutory priority**. During supply deficits, available power is allocated proportionally according to baseline ratios:
$$\alpha_{\text{heating}} = 50.0\%, \quad \alpha_{\text{water}} = 33.33\%, \quad \alpha_{\text{comms}} = 16.67\%$$

### 4. FORECAST GENERATION FORMULATION
Synthetic lookahead forecast curves are generated using a deterministic $10\%$ persistence over-estimation rule:
$$\hat{P}_{\text{solar}}(t+k|t) = 1.10 \times P_{\text{solar,actual}}(t+k)$$
$$\hat{P}_{\text{wind}}(t+k|t) = 1.10 \times P_{\text{wind,actual}}(t+k)$$
$$\hat{P}_{\text{demand}}(t+k|t) = 1.10 \times P_{\text{demand,actual}}(t+k)$$

### 5. PHYSICAL CLOSED-LOOP CONSERVATION BALANCE
For every timestep $t$, energy conservation across generation, storage, load, and curtailment is strictly enforced:
$$P_{\text{PV,actual}}(t) + P_{\text{wind,actual}}(t) + P_{\text{gen,actual}}(t) + P_{\text{batt,dis}}(t) = P_{\text{critical,served}}(t) + P_{\text{flexible,served}}(t) + P_{\text{batt,charge}}(t) + P_{\text{curtail}}(t)$$
