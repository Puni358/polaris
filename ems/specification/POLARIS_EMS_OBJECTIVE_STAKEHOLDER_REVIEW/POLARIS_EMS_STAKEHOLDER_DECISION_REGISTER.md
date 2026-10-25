# POLARIS EMS OBJECTIVE STAKEHOLDER DECISION REGISTER

**Document Version**: 1.0.0-FINAL  
**Governance Status**: AWAITING_STAKEHOLDER_DECISIONS  
**Audit Timestamp**: 2026-09-21T21:56:54Z  
**Target Authority**: POLARIS Steering & Stakeholder Governance Board  

---

> [!IMPORTANT]
> **GOVERNANCE DIRECTIVE**: This register contains 16 explicit decision questions that must be formally resolved and authorized by POLARIS stakeholders before any modifications to the EMS objective function, weights, coefficients, or constraints can be executed in code. **DO NOT answer these questions in code or engineering documentation without formal stakeholder authorization.**

---

### DECISION_01: Critical Load Classification
Which specific research station electrical loads belong to the non-sheddable Critical Load class essential for life support, communication, and key scientific instruments?

---

### DECISION_02: Curtailable and Shed-able Load Classification
Which research station electrical loads may be shed or deferred during severe power deficits, and under what operational conditions?

---

### DECISION_03: Minimum Service Level for Critical Loads
What minimum continuous service level (in kW or % of demand) is required for critical loads under normal and emergency operating modes?

---

### DECISION_04: Maximum Acceptable Unmet Critical Load
What is the maximum acceptable unmet critical load (in total kWh per year or per 24-hour horizon) for the POLARIS microgrid under off-grid arctic operating conditions?

---

### DECISION_05: Maximum Continuous Critical-Load Interruption Duration
What maximum continuous critical-load interruption duration (in consecutive hours) is acceptable before emergency intervention or forced generator startup is mandatory?

---

### DECISION_06: Reliability Mathematical Formulation (Hard Constraint vs. Objective Penalty)
Should critical-load service be formulated as a strict mathematical hard constraint ($P_{\text{unmet},t} = 0$) or as a soft penalized term in the objective function?

---

### DECISION_07: Definition of "Minimize Diesel Use"
What exact metric defines "minimizing diesel use" for POLARIS: absolute fuel volume (liters), generator operating hours (runtime), total operating cost ($), generator startup frequency, or carbon emissions?

---

### DECISION_08: Maximum Acceptable Diesel Consumption / Fuel Budget
Is there a maximum acceptable annual fuel consumption ceiling (in liters) or resupply budget limit for station operations?

---

### DECISION_09: Renewable Integration Target
What minimum renewable energy fraction (%) or annual renewable energy integration target is required for station operations?

---

### DECISION_10: Renewable Curtailment Objective Policy
Is renewable curtailment itself a governed objective (e.g. penalized in objective function), or an unpenalized spill outcome when storage and load capacity are full?

---

### DECISION_11: Minimum Emergency Battery Reserve Floor
What minimum emergency BESS reserve floor (in kWh or % SOC above technical minimum) must be preserved exclusively for emergency station survival?

---

### DECISION_12: Horizon Terminal BESS SOC Requirement
Is a terminal SOC requirement ($E_{H} \ge E_{\text{target}}$) at the end of each 24-hour MPC horizon mandatory to prevent systematic BESS depletion across consecutive days?

---

### DECISION_13: Forecast Uncertainty Handling Policy
How should the EMS respond to forecast uncertainty (e.g., maintaining dynamic spinning/battery reserves, stochastic MILP, chance constraints, or deterministic safety margins)?

---

### DECISION_14: Authorized Fuel-vs-Reliability Penalty Exchange Rate
What numerical exchange rate or penalty weight ratio between diesel fuel consumption ($/L) and unmet critical load ($/kWh) is authorized for the EMS objective function?

---

### DECISION_15: Governed Objective Priority Hierarchy
What explicit priority order should apply when critical reliability, fuel minimization, renewable utilization, battery preservation, and operating cost conflict during dispatch?

---

### DECISION_16: Governance Approval Authority Designation
Which specific individuals, board, or committee hold formal governance authority to approve and authorize changes to the POLARIS EMS objective specification and mathematical formulation?
