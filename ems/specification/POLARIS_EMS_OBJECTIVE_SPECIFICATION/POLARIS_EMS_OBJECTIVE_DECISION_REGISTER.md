# POLARIS EMS OBJECTIVE STAKEHOLDER DECISION REGISTER

**Document Version**: 1.0.0  
**Governance Status**: AWAITING_STAKEHOLDER_DECISIONS  
**Audit Timestamp**: 2026-09-21T21:20:00Z  
**Target Authority**: POLARIS Steering & Stakeholder Governance Board  

---

> [!IMPORTANT]
> **GOVERNANCE DIRECTIVE**: This register contains explicit decision questions that must be formally resolved and authorized by POLARIS stakeholders before any modifications to the EMS objective function, weights, coefficients, or constraints can be made. **DO NOT answer these questions in code or engineering documentation without formal stakeholder authorization.**

---

### DECISION_01: Maximum Acceptable Unmet Critical Load
What is the maximum acceptable unmet critical load (in total kWh per year or per 24-hour horizon) for the POLARIS microgrid under off-grid arctic operating conditions?

---

### DECISION_02: Maximum Continuous Critical Interruption
What maximum continuous critical-load interruption duration (in consecutive hours) is acceptable before emergency intervention or forced generator startup is mandatory?

---

### DECISION_03: Critical, Flexible, and Shed-able Load Definitions
Which specific research station electrical loads belong to the Critical (non-sheddable), Flexible (deferrable time-window), and Curtailable (sheddable) load classes?

---

### DECISION_04: Critical Load Formulation (Constraint vs. Objective)
Should critical-load service be formulated as a strict mathematical hard constraint ($P_{\text{unmet},t} = 0$) or as a soft penalized term in the objective function?

---

### DECISION_05: Fuel Consumption Target or Ceiling
What numerical fuel consumption target, annual ceiling (in liters), or percentage fuel reduction relative to baseline diesel generation applies to POLARIS?

---

### DECISION_06: Primary Fuel Objective Definition
Should POLARIS minimize absolute fuel volume (liters), generator operating hours (runtime), total operating cost ($), or fuel consumption subject to a hard reliability constraint?

---

### DECISION_07: Authorized Fuel-vs-Reliability Trade-off
What numerical exchange rate or penalty weight ratio between diesel fuel consumption ($/L) and unmet critical load ($/kWh) is authorized for the EMS objective function?

---

### DECISION_08: Required Renewable Utilization Target
What minimum renewable energy fraction (%) or annual renewable energy integration target is required for station operations?

---

### DECISION_09: Maximum Acceptable Renewable Curtailment
What maximum allowable renewable energy curtailment threshold (in kWh or % of available renewable generation) is acceptable?

---

### DECISION_10: Minimum Emergency Battery Reserve Floor
What minimum emergency BESS reserve floor (in kWh or % SOC above technical minimum) must be preserved exclusively for emergency station survival?

---

### DECISION_11: Horizon Terminal SOC Requirement
Is a terminal SOC requirement ($E_{H} \ge E_{\text{target}}$) at the end of each 24-hour MPC horizon mandatory to prevent systematic BESS depletion across consecutive days?

---

### DECISION_12: Diesel Runtime and Startup Limits
What maximum daily generator runtime, minimum continuous run hours, and maximum allowable generator startup frequency limits are required?

---

### DECISION_13: Governed Load-Shedding Priority Hierarchy
What explicit order of precedence must the EMS follow when executing load shedding during severe power deficits?

---

### DECISION_14: Forecast Uncertainty Handling Policy
How should the EMS respond to forecast uncertainty (e.g., maintaining dynamic spinning/battery reserves, stochastic MILP, chance constraints, or deterministic safety margins)?

---

### DECISION_15: Governance Approval Authority
Which specific individuals, board, or committee hold formal governance authority to approve and authorize changes to the POLARIS EMS objective specification and mathematical formulation?
