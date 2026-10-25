# POLARIS GAP19 — ECD → Option D Minimal Implementation Design

## Design Overview
This package presents the **Minimal Implementation Design** for connecting the **Emergency Condition Detector (ECD)** core (`system/control/ecd.py`) and the sealed **Option D Protected Critical-Load Fallback** into the POLARIS EMS synthetic runtime framework (`system/runtime/runner.py`).

Following the **Correction-Only Forensic Review**, this design adheres to the **Absolute Minimality Principle**: reusing existing runtime objects, interfaces, and schemas without creating duplicate fields, unnecessary serialization, or policy override knobs.

## Baseline Governance & Evidence
This design strictly enforces the sealed baseline:
1. `POLARIS_EMS_GAP19_INFEASIBILITY_DECISION_SEAL` (Decisions D1–D4)
2. `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`
3. `POLARIS_EMS_GAP19_SYNTHETIC_ECD_OPTION_D_INTEGRATION_READINESS`
4. `POLARIS_EMS_GAP19_ECD_OPTION_D_IMPLEMENTATION_SPECIFICATION_CORRECTION`
5. `DEC004_FINAL_SELECTION / OPTION D GOVERNANCE RESOLUTION`
6. `POLARIS_EMS_ECD_CORE_IMPLEMENTATION` (`system/control/ecd.py`)

## Package Structure
- `README.md`: Package overview and navigation guide.
- `CURRENT_TO_TARGET_CONTROL_FLOW.md`: Step-by-step mapping of current vs target MPC control sequence.
- `ECD_INPUT_OUTPUT_MAPPING.md`: Parameter-by-parameter input and output mapping for ECD evaluation.
- `ROUTER_MINIMAL_INTERFACE.md`: Minimal state table and routing boundary for EMSControlRouter.
- `OPTION_B_PRESERVATION_AUDIT.md`: Audit confirming zero modifications to Option B native HiGHS optimizer.
- `MILP_INFEASIBILITY_INTERFACE.md`: Interface design routing solver status into ECD context.
- `OPTION_D_MINIMAL_INTERFACE.md`: Minimal dispatch interface for Option D Protected Critical-Load Fallback.
- `OPTION_D_DISPATCHPLAN_MAPPING.md`: Direct mapping of Option D outputs to existing DispatchPlan schema.
- `CRITICAL_LOAD_INTERFACE.md`: Representation of critical load trajectory without schema pollution.
- `STATION_STATE_MINIMALITY_AUDIT.md`: Minimality audit confirming zero extensions required for StationState.
- `AUTHORITY_ESCALATION_BOUNDARY.md`: Operational alert boundary for authority escalation.
- `UNKNOWN_INVALID_BOUNDARY.md`: Fail-closed boundary leaving operational action as NOT_ESTABLISHED.
- `EMERGENCY_RETURN_BOUNDARY.md`: Entry boundary for future governed return policy.
- `DIGITAL_TWIN_COMPATIBILITY.md`: Audit confirming 100% preservation of receding-horizon first-action execution.
- `MINIMAL_FILE_DELTA.md`: Table of exact file additions (2 new files, 1 modified file, 0 protected files touched).
- `IMPLEMENTATION_DEPENDENCY_ORDER.md`: Phased dependency order for future implementation.
- `FUTURE_TEST_DESIGN.md`: Test suite design (TEST-A through TEST-H).
- `GOVERNANCE_ENGINEERING_FIREWALL.md`: Firewall separating governance, engineering design, and input blockers.
- `MINIMALITY_CHALLENGE.md`: 7-question minimality challenge applied to every proposed software element.
- `IMPLEMENTATION_BLOCKER_REGISTER.md`: Register of unresolved governance and engineering design blockers.
- `FINAL_MINIMAL_IMPLEMENTATION_DESIGN_VERDICT.md`: Formal sealed verdict block.
- `HASH_AUDIT.json`: Cryptographic SHA-256 JSON hashes for all protected sources and design artifacts.

## Absolute Hard Stop
This audit is **DESIGN ONLY**. No code was implemented, no schemas modified, and no solvers or simulations executed. Implementation authorization is **NOT GRANTED**.
