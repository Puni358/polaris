# POLARIS GAP19 — ECD → Option D Implementation Specification Audit

## Overview
This package contains the formal, read-only **Implementation Specification Audit** for integrating the **Emergency Condition Detector (ECD)** core (`system/control/ecd.py`) and the governed **Option D Protected Critical-Load Fallback** into the POLARIS EMS synthetic runtime framework (`system/runtime/runner.py`).

Building upon the **Synthetic ECD → Option D Integration Readiness Audit**, this specification defines the exact, minimal software interface delta, schema extensions, router state machine, and test harness contracts required to implement the integration without altering normal MPC optimization mathematics, ECD core logic, or sealed governance policies.

## Baseline Governance & Evidence
This specification strictly enforces the sealed baseline:
1. `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL` (Decisions D1–D4)
2. `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`
3. `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`
4. `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`
5. `POLARIS_EMS_GAP19_SYNTHETIC_ECD_OPTION_D_INTEGRATION_READINESS`
6. `DEC004_FINAL_SELECTION / OPTION D GOVERNANCE RESOLUTION`
7. `POLARIS_EMS_ECD_CORE_IMPLEMENTATION` (`system/control/ecd.py`)

## Package Structure
- `README.md`: Package overview and navigation guide.
- `GOVERNANCE_TERMINOLOGY_CORRECTION.md`: Explicit corrections separating governed policy from un-implemented runtime code.
- `EXACT_ECD_ROUTER_CONTRACT.md`: Complete specification of ECD core input parameters and adapter requirements.
- `NORMAL_OPTION_B_INTERFACE_CONTRACT.md`: Call contract for Option B native HiGHS MPC optimizer.
- `MILP_INFEASIBILITY_INTERFACE_CONTRACT.md`: Routing specification for MILP solver status into ECD context.
- `OPTION_D_INTERFACE_CONTRACT.md`: Option D Protected Critical-Load Fallback interface specification.
- `UNKNOWN_INVALID_INTERFACE_CONTRACT.md`: Fail-closed routing specification for UNKNOWN_INVALID states.
- `EMERGENCY_RETURN_INTERFACE_CONTRACT.md`: Analysis of return path from EMERGENCY to NORMAL mode.
- `SCHEMA_DELTA_SPECIFICATION.md`: Precise additive schema modifications for StationState and DispatchPlan.
- `ROUTER_STATE_MACHINE_SPECIFICATION.md`: State machine specification for EMSControlRouter.
- `FIRST_ACTION_MPC_COMPATIBILITY_AUDIT.md`: Verification of 24h receding-horizon first-action commitment.
- `AUTHORITY_ESCALATION_INTERFACE_SPECIFICATION.md`: Event payload specification for authority escalation.
- `SYNTHETIC_TEST_HARNESS_SPECIFICATION.md`: Specification for TEST-A through TEST-I synthetic validation suite.
- `FILE_LEVEL_IMPLEMENTATION_DELTA.md`: Table of exact file modifications required for future implementation.
- `PROTECTED_COMPONENT_REGISTER.md`: Register of protected source files and SHA-256 signatures.
- `IMPLEMENTATION_BLOCKER_REGISTER.md`: Blocker register for synthetic implementation vs real-station deployment.
- `SOURCE_INTEGRITY_AUDIT.md`: Verification of zero code/schema modifications during this audit.
- `HASH_AUDIT.json`: Cryptographic SHA-256 hashes of all protected sources and package artifacts.
- `FINAL_IMPLEMENTATION_SPECIFICATION_VERDICT.md`: Formal sealed verdict block.

## Absolute Hard Stop
This audit is **100% READ-ONLY**. No source code, schema, or configuration modifications were executed. No solvers or runtime simulations were run.
