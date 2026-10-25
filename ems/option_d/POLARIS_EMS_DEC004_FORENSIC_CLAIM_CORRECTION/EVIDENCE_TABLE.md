# POLARIS EMS — MASTER FORENSIC EVIDENCE TABLE (38 SUBCLAIMS)

## 1. Executive Summary

This document presents the master forensic evidence table detailing all 38 subclaims evaluated across Recovery (REC-001 to REC-015), Escalation (ESC-001 to ESC-012), and Objective Compatibility (OBJ-001 to OBJ-011).

---

## 2. Master Forensic Evidence Table

| Claim ID | Subclaim Statement | Previous Reported Status | Actual Executable Code Evidence | Governance Evidence Source | Correct Forensic Status |
|----------|-------------------|--------------------------|---------------------------------|----------------------------|-------------------------|
| **REC-001** | ECD `VALID` transition observed by runtime | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-002** | ECD `UNKNOWN_INVALID` consumed by runtime | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-003** | Option D degraded mode entered by runtime | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Option D Policy Doc | `NOT_ESTABLISHED_IN_CODE` |
| **REC-004** | Degraded Option D plan exists in runtime state | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-005** | Runtime stores/retains degraded plan cache | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-006** | Runtime detects ECD `VALID` return | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-007** | Runtime automatically resumes MPC | `ESTABLISHED` | Linear loop without mode switching | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-008** | Runtime generates new 24h MILP plan on return | `ESTABLISHED` | `milp.py` called unconditionally every step | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-009** | Degraded dispatch plan is discarded | `ESTABLISHED` | Absent from `system/runtime/runner.py` | None | `NOT_ESTABLISHED_IN_CODE` |
| **REC-010** | D5 escalation state exists in runtime code | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `NOT_ESTABLISHED_IN_CODE` |
| **REC-011** | D5 escalation requires SCADA reset | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **REC-012** | Operator acknowledgement is required | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **REC-013** | Battery/diesel state revalidated before recovery | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Architecture Contract | `PROPOSED_ARCHITECTURE` |
| **REC-014** | Critical fallback persists after ECD validity returns | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Architecture Contract | `PROPOSED_ARCHITECTURE` |
| **REC-015** | Documented as implemented contract vs proposal | `ESTABLISHED` | Code does not implement recovery | Architecture Proposal | `CONTRADICTED_BY_CODE` |
| **ESC-001** | D4 shortfall causes operator escalation | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D4 | `ESTABLISHED_BY_GOVERNANCE` |
| **ESC-002** | D5 time boundary causes operator escalation | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **ESC-003** | D5 resource boundary causes operator escalation | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **ESC-004** | Escalation creates `FaultEvent` | `ESTABLISHED` | Created for solver errors, not ECD | Architecture Proposal | `PROPOSED_ARCHITECTURE` |
| **ESC-005** | Fault class is `INVALID_SURVIVABILITY_ASSESSMENT` | `ESTABLISHED` | String 100% absent from Python code | Documentation files | `DOCUMENTATION_ONLY` |
| **ESC-006** | Escalation alerts an operator | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Architecture Proposal | `PROPOSED_ARCHITECTURE` |
| **ESC-007** | Escalation changes automated dispatch | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Architecture Proposal | `PROPOSED_ARCHITECTURE` |
| **ESC-008** | Escalation causes physical shutdown | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `CONTRADICTED_BY_GOVERNANCE` |
| **ESC-009** | Escalation requires SCADA reset | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Architecture Proposal | `PROPOSED_ARCHITECTURE` |
| **ESC-010** | Escalation requires operator acknowledgement | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **ESC-011** | Escalation permits continued critical support | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D3/D5 | `ESTABLISHED_BY_GOVERNANCE` |
| **ESC-012** | Escalation prevents noncritical load dispatch | `ESTABLISHED` | Absent from `system/runtime/runner.py` | Governance Decision D2/D3 | `ESTABLISHED_BY_GOVERNANCE` |
| **OBJ-001** | `milp.py` uses $10/\text{Wh}$ scalar unmet penalty | `ESTABLISHED` | Line 49: `unmet_penalty_per_wh = 10.0` | Prototype Config | `CURRENT_IMPLEMENTATION_FACT` |
| **OBJ-002** | `milp.py` uses single-pass scalar objective | `ESTABLISHED` | `scipy.optimize.milp` called once per step | Prototype Code | `CURRENT_IMPLEMENTATION_FACT` |
| **OBJ-003** | Governed target architecture is 4-stage lexicographic | `ESTABLISHED` | Absent from `milp.py` | Objective Governance | `GOVERNED_TARGET_ARCHITECTURE` |
| **OBJ-004** | Multi-pass sequential solver or HiGHS multi-obj path in code | `ESTABLISHED` | Absent from `milp.py` | Architecture Proposal | `NOT_ESTABLISHED_IN_CODE` |
| **OBJ-005** | $10/\text{Wh}$ scalar penalty guarantees Stage 1 reliability | `ESTABLISHED` | Single scalar weight combination | Math Property | `CONTRADICTED_BY_MATH` |
| **OBJ-006** | Option D noncritical load suppression representable | `ESTABLISHED` | Bound $P_{\text{flex,max}} = 0$ in `milp.py` | Policy D2 | `DIRECTLY_REPRESENTABLE` |
| **OBJ-007** | Option D dynamic $P_{\text{critical}}(t)$ representable | `ESTABLISHED` | Additive vector in `ForecastBundle` | Policy D1 | `REPRESENTABLE_WITH_ADDITIVE_CHANGES` |
| **OBJ-008** | Proportional critical shortfall allocation representable | `ESTABLISHED` | Additive linear constraints in `milp.py` | Policy D4 | `REPRESENTABLE_WITH_ADDITIVE_CHANGES` |
| **OBJ-009** | Battery discharge restricted to critical load representable | `ESTABLISHED` | Linear bound $P_{\text{dis},j} \le P_{\text{critical},j}$ | Policy D2 | `DIRECTLY_REPRESENTABLE` |
| **OBJ-010** | Unavoidable diesel excess battery charging representable | `ESTABLISHED` | Energy balance equation in `milp.py` | Policy D6 | `DIRECTLY_REPRESENTABLE` |
| **OBJ-011** | Blur scalar penalty with lexicographic guarantee | `ESTABLISHED` | Scalar weight vs lexicographic pass | Forensic Audit | `CORRECTION_REQUIRED` |

Status: `EVIDENCE_TABLE_SEALED`
