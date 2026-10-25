# DIESEL PROVENANCE REVIEW
## AUDIT OF GENERATOR MODEL & 12.5 L/H FUEL CONSUMPTION DERIVATION

### 1. FORENSIC AUDIT OF DIESEL PARAMETERS
The proposed minimum synthetic fixture specified:
- **Minimum Output Rating ($P_{\text{gen,min}}$)**: $10\text{ kW}$
- **Maximum Output Rating ($P_{\text{gen,max}}$)**: $60\text{ kW}$
- **Stated Fuel Consumption**: $12.5\text{ L/h}$

This review audited whether $12.5\text{ L/h}$ is a static flat fuel rate or a point calculation derived from the existing prototype linear fuel consumption model.

### 2. DERIVATION AUDIT OF THE 12.5 L/H FUEL RATE
Cross-referencing the prototype diesel generator formulation in the repository codebase revealed the exact linear fuel consumption equation:
$$F(t) = F_{\text{base}} \cdot u_{\text{gen}}(t) + F_{\text{marginal}} \cdot P_{\text{gen}}(t) \quad [\text{L/h}]$$

Where prototype parameters are:
- Base (no-load) consumption: $F_{\text{base}} = 5.0\text{ L/h}$
- Marginal consumption rate: $F_{\text{marginal}} = 0.25\text{ L/kWh}$

Evaluating this linear model at $P_{\text{gen}} = 30\text{ kW}$ (the exact baseline critical load of the synthetic fixture):
$$F(30\text{ kW}) = 5.0 + 0.25 \times 30 = 5.0 + 7.5 = 12.5\text{ L/h}$$

### 3. AMBIGUITY & BLOCKER RESOLUTION
- **Finding**: $12.5\text{ L/h}$ is NOT a universal flat fuel consumption rate across all operating levels. It is specifically the fuel consumption rate when the generator operates at $30\text{ kW}$ output.
- **Problem with Flat Assumption**: If the synthetic fixture generator assumed a flat $12.5\text{ L/h}$ regardless of output:
  - At minimum load ($10\text{ kW}$), real linear consumption is $5.0 + 0.25 \times 10 = 7.5\text{ L/h}$. A flat $12.5\text{ L/h}$ assumption would overstate fuel consumption by $66\%$.
  - At maximum rating ($60\text{ kW}$), real linear consumption is $5.0 + 0.25 \times 60 = 20.0\text{ L/h}$. A flat $12.5\text{ L/h}$ assumption would understate fuel consumption by $37.5\%$.
- **Resolution**: The synthetic fixture generator MUST implement the dynamic linear fuel consumption curve $F(P_{\text{gen}}) = 5.0 \cdot u_{\text{gen}} + 0.25 \cdot P_{\text{gen}}\text{ L/h}$ rather than a static $12.5\text{ L/h}$ scalar.

### 4. DIESEL PARAMETER PROVENANCE TABLE

| Parameter | Value | Source / Model | Provenance Status | Fixture Specification Rule |
|---|---|---|---|---|
| Minimum Generator Output | $10\text{ kW}$ | `system/config/generator.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | Enforce $P_{\text{gen}} \ge 10\text{ kW}$ when $u_{\text{gen}}=1$ |
| Maximum Generator Output | $60\text{ kW}$ | `system/config/generator.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | Enforce $P_{\text{gen}} \le 60\text{ kW}$ |
| Base Idle Fuel Rate | $5.0\text{ L/h}$ | Prototype Linear Model | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | Dynamic fuel curve intercept |
| Marginal Fuel Rate | $0.25\text{ L/kWh}$ | Prototype Linear Model | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | Dynamic fuel curve slope |
| Point Consumption @ 30 kW | $12.5\text{ L/h}$ | Calculated ($5 + 0.25 \times 30$) | `DERIVED_SYNTHETIC_POINT_VALUE` | Derived value for 30 kW dispatch |

### 5. CONCLUSION & RECOMMENDATION
`DIESEL_PROVENANCE_STATUS = QUALIFIED`.
The flat $12.5\text{ L/h}$ assumption is REJECTED as a static model parameter. The preflight recommendation mandates using the linear model equation $F(t) = 5.0 \cdot u_{\text{gen}}(t) + 0.25 \cdot P_{\text{gen}}(t)\text{ L/h}$ in the synthetic Digital Twin and optimizer accounting.
