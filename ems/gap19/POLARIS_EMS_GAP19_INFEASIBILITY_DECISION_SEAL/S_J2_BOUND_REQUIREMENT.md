# POLARIS EMS GAP19 — S_J2 BOUND REQUIREMENT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL`  
**Contract Status**: `SEALED_GOVERNANCE_REQUIREMENT`  

---

## 1. Governance Policy Classification (Decision D2)

* **Policy Classification**: `GOVERNED_MAXIMUM_SHORTFALL`
* **Numerical Value**: `NOT_ESTABLISHED`
* **Derivation Basis**: `STATION_SURVIVABILITY_REQUIREMENT`
* **Current $200\text{ kWh}$ Cap Status**: `IMPLEMENTATION_FACT / NOT_GOVERNED`

---

## 2. Requirement Analysis & Firewall Rules

1. **Rejection of Ad-Hoc Implementation Cap**:
   The current upper bound in `gap19_highs_native.py` (`ub[idx_s_j2_start + t] = capacity_wh = 200,000.0`) is an ad-hoc implementation artifact. It MUST NOT be treated as governed policy.
2. **Prohibition of Silent Edits**:
   * Do NOT silently preserve $200\text{ kWh}$ as governed policy.
   * Do NOT silently remove the upper bound or set it to infinity in codebase source files without explicit engineering authorization.
3. **Derivation Requirements for Future Bound**:
   The future governed upper bound $s_{\text{J2,max}}$ must be mathematically derived from station survivability requirements, critical load durations, and generator backup capabilities (Item **ENG-01**), rather than defaulted to nominal battery energy capacity.

---

## 3. Comparative Summary

| Parameter Aspect | Historical Prototype Code | Governed Decision D2 Requirement |
| :--- | :--- | :--- |
| **Bound Value** | $200,000.0\text{ Wh}$ ($200\text{ kWh}$) | `NOT_ESTABLISHED` (Pending station engineering) |
| **Source / Provenance** | Hardcoded `capacity_wh` variable | Station survivability analysis (ENG-01) |
| **Governance Status** | `IMPLEMENTATION_FACT` | `GOVERNED_MAXIMUM_SHORTFALL` |
| **Code Modification** | Preserved untouched in source | Blocked by Implementation Firewall |
