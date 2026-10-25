# POLARIS GATE-04 — MISSING INTERFACES
## DETAILED ANALYSIS OF MISSING CONTRACTS AND UNBUILT MODULES

---

## 1. REGISTER OF MISSING & GAPPED INTERFACES

Four interfaces exhibit missing contracts, unbuilt modules, or physical integration gaps:

```text
+-----------------------------------------------------------------------------------------+
| INTERFACE ID | INTERFACE NAME                   | STATUS             | MISSING CONTRACT  |
+--------------+----------------------------------+--------------------+-------------------+
| IF-09        | Emergency Return Notification    | MISSING            | Transport / UI API|
| IF-10        | Operator Override Routing        | MISSING            | Override API / Auth|
| IF-11        | UNKNOWN_INVALID Physical Fallback| DEFINED_WITH_GAPS  | Hardware Handshake|
| IF-12        | Option C Relaxation Re-Solve     | DEFINED_WITH_GAPS  | Multi-Pass Solver |
+-----------------------------------------------------------------------------------------+
```

---

## 2. DETAILED BREAKDOWN BY MISSING INTERFACE

### 1. Interface IF-09: Emergency Return Operator Notification
- **Current Status**: **`MISSING`**
- **Target Location**: `system/runtime/runner.py` / notification service.
- **Missing Contract Elements**:
  - Event publisher interface inside `runner.py` to trigger upon `EMERGENCY → NORMAL` state transition.
  - Notification payload formatter (schema encoding prior emergency state, current normal evaluation, auto-return flag).
  - Transport layer (REST API, WebSockets, SCADA RTU).
- **Implementation Prerequisites**: Can proceed without inventing policy because Gate-03 human decision explicitly specified mandatory notification payload requirements.

### 2. Interface IF-10: Operator Override Governed Routing
- **Current Status**: **`MISSING`**
- **Target Location**: `system/control/router.py` / `system/runtime/runner.py`.
- **Missing Contract Elements**:
  - Operator override payload schema (override flag, target fallback state, timestamp).
  - Authority validator handler inside `router.py` to intercept stateless ECD evaluation.
  - Stateful override interceptor and persistence layer.
- **Implementation Prerequisites**: Requires engineering specification of API endpoints, payload formats, and authentication contracts.

### 3. Interface IF-11: UNKNOWN_INVALID Physical Fallback (Gate-01)
- **Current Status**: **`DEFINED_WITH_GAPS`**
- **Current Code**: Software halt via `FaultEvent(severity="CRITICAL_TERMINATION")` (`TEMPORARY_SOFTWARE_CONTAINMENT`).
- **Missing Contract Elements**:
  - Physical hardware fallback controller interface to maintain protected-critical service (heating, water, communications) when software halts.
- **Implementation Prerequisites**: Requires electrical engineering station design for hardware fallback relays.

### 4. Interface IF-12: MILP Infeasibility Option C Relaxation Re-Solve (Gate-02)
- **Current Status**: **`DEFINED_WITH_GAPS`**
- **Current Code**: Safety halt via `FaultEvent(state_advanced=False)` (`GOVERNANCE_DECISION_REQUIRED`).
- **Missing Contract Elements**:
  - Multi-pass relaxation solver wrapper in `gap19_highs_native.py` / `milp.py` to soften Tier 2 non-critical load constraints.
  - Relaxation magnitude calculator and operator relaxation event formatter.
- **Implementation Prerequisites**: Requires human governance authorization of numerical relaxation penalty weights ($\lambda_i$) and non-critical load shedding priority order.
