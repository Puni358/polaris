# CRITICAL LOAD VECTOR REVIEW
## PROTECTED LOAD VECTOR RATIONALE & PROPORTIONAL ALLOCATION GOVERNANCE

### 1. EVALUATION OF CRITICAL LOAD REPRESENTATION
The proposed minimum fixture specifies a protected critical load $P_{\text{critical}}(t) = 30\text{ kW}$ broken into three synthetic components:
- **Heating**: $15\text{ kW}$
- **Water Treatment / Filtration**: $10\text{ kW}$
- **Emergency Communications**: $5\text{ kW}$

This review evaluated whether a 3-component vector is strictly necessary or whether a single aggregate scalar $P_{\text{critical}}(t) = 30\text{ kW}$ would be minimum-sufficient.

### 2. COMPARATIVE ARCHITECTURE AUDIT
- **Option A (Single Aggregate Scalar $P_{\text{critical}}$)**:
  - Demonstrates total critical load serving vs shedding.
  - *Deficiency*: Cannot exercise Option D's sealed requirement for **proportional allocation** across multiple protected critical sub-systems during a supply deficit.
- **Option B (3-Component Static Vector)**:
  - Demonstrates multi-subsystem aggregate load serving.
  - Exercises proportional allocation when available power $P_{\text{avail}} < P_{\text{critical\_min\_total}}$.
  - *Sufficient for Architecture Test*: Yes.
- **Option C (3-Component Dynamic Trajectories)**:
  - Adds time-varying individual subsystem load profiles.
  - *Excess Realism*: Adds unnecessary complexity for a minimum architectural test.

**Decision**: **Option B (3-Component Vector)** is minimum-sufficient and architecturally required to test Option D proportional allocation logic.

### 3. HARD GOVERNANCE BOUNDARY ON COMPONENT PRIORITY
Option D sealed governance explicitly states:
> *"Proportional allocation when available power is insufficient for all protected critical minimum levels."*

**CRITICAL RULE**: The synthetic fixture MUST NOT implement or imply any hierarchical component prioritization such as:
$$\text{Heating} > \text{Water Treatment} > \text{Emergency Communications}$$

Under Option D, all protected critical systems share equal statutory status. When available power is insufficient to meet full minimum levels, allocation across Heating, Water, and Communications MUST be strictly proportional to their minimum required baseline ratios:
$$\alpha_i = \frac{P_{\text{min}, i}}{\sum_j P_{\text{min}, j}}$$

### 4. FORENSIC REVIEW OF THE 30 kW MAGNITUDE
- **Origin**: Reused synthetic prototype value inherited from earlier simulation scripts.
- **Status**: `SYNTHETIC_TEST_VALUE_NOT_ARCHITECTURALLY_REQUIRED`.
- **Evaluation**: The exact numerical value of $30\text{ kW}$ is not architecturally mandated (e.g., $20\text{ kW}$ or $40\text{ kW}$ would function identically in code). However, retaining $30\text{ kW}$ is convenient as it aligns with the $200\text{ kWh}$ battery and $60\text{ kW}$ diesel capacity scaling.
- **Scientific Firewall**: $30\text{ kW}$ MUST NEVER be cited as Nuolja station demand. It must carry the explicit provenance tag:
  `P_critical_provenance: SYNTHETIC_ENGINEERING_ASSUMPTION`

### 5. CONCLUSION & RECOMMENDATION
`CRITICAL_LOAD_VECTOR_STATUS = QUALIFIED`.
Retain the 3-component vector ($15\text{ kW} / 10\text{ kW} / 5\text{ kW}$) strictly to exercise the Option D proportional allocation software layer. Explicitly document that proportional allocation operates without subsystem priority ranking.
