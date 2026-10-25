# D4 SYNTHETIC EXAMPLE

## 1. MATHEMATICAL ILLUSTRATION USING SYNTHETIC FIXTURE VALUES

> **CRITICAL FIREWALL NOTICE**: The numbers in this example ($15\text{ kW}, 10\text{ kW}, 5\text{ kW}, 30\text{ kW}, 18\text{ kW}$) are strictly **SYNTHETIC_ENGINEERING_FIXTURE_VALUES** used for mathematical demonstration only. They are NOT real Nuolja station load facts.

---

## 2. EXAMPLE CALCULATIONS

### Synthetic Minimum Viable Inputs:
- Heating Minimum Viable: $P_{\text{heating,min}} = 15.0$ kW
- Water Treatment Minimum Viable: $P_{\text{water,min}} = 10.0$ kW
- Emergency Comms Minimum Viable: $P_{\text{comms,min}} = 5.0$ kW
- Total Critical Minimum Viable Requirement: $\sum P_{i,\text{min}} = 30.0$ kW

### Insufficient Power Scenario:
Assume available power for critical service is restricted to $P_{\text{critical,available}} = 18.0$ kW.

### Step 1: Calculate Allocation Ratio $\alpha$
$$\alpha = \frac{18.0\text{ kW}}{30.0\text{ kW}} = 0.60 \quad (60.0\%)$$

### Step 2: Calculate Dispatched Power per Category
- Heating Dispatched: $P_{\text{heating,served}} = 0.60 \times 15.0\text{ kW} = 9.0$ kW
- Water Dispatched: $P_{\text{water,served}} = 0.60 \times 10.0\text{ kW} = 6.0$ kW
- Comms Dispatched: $P_{\text{comms,served}} = 0.60 \times 5.0\text{ kW} = 3.0$ kW

$$\text{Total Dispatched Critical Power} = 9.0 + 6.0 + 3.0 = 18.0\text{ kW}$$

---

## 3. VERIFICATION
- Demonstrates exact proportional degradation ($\alpha = 0.60$) across all categories.
- Zero priority distortion (Heating, Water, Comms all receive exactly $60\%$ of their minimum requirement).
