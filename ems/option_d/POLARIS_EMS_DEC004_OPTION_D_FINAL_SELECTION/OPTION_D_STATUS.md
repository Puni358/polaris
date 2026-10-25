# POLARIS EMS — OPTION D STATUS BREAKDOWN

## Policy Selection vs. Implementation Status

This artifact documents the explicit separation between **Policy Governance Selection** and **Runtime Implementation Status** for Option D — Protected Critical-Load Fallback.

> [!IMPORTANT]
> Selecting Option D establishes human policy approval. It does **NOT** grant authorization to modify runtime code, adjust optimization objectives, alter system schemas, or deploy to production environments.

---

## Detailed Status Matrix

| Sub-System / Category | Status Value | Detailed Meaning |
| :--- | :--- | :--- |
| **OPTION_D_GOVERNANCE_STATUS** | `SELECTED_AND_SEALED` | Option D policy (D1–D6) is formally chosen and sealed by human authority. |
| **OPTION_D_RUNTIME_IMPLEMENTATION** | `NOT_IMPLEMENTED` | No software code implementing Option D exists in `system/` runtime. |
| **IMPLEMENTATION_AUTHORIZATION** | `NOT_GRANTED` | No authorization has been issued to begin implementation engineering. |
| **PRODUCTION_DEPLOYMENT** | `BLOCKED` | System is blocked from production deployment pending implementation gates. |
| **ECD_RUNTIME_INTEGRATION** | `NOT_IMPLEMENTED` | ECD output state `UNKNOWN_INVALID` is not yet wired to runner or state manager. |
| **OPTION_D_RECOVERY_RUNTIME** | `NOT_IMPLEMENTED` | Automated or manual recovery from Option D safe-state is not established in code. |
| **OPTION_D_OPERATOR_ESCALATION_RUNTIME** | `NOT_IMPLEMENTED` | Runtime operator notification / escalation signaling mechanism is not implemented. |
| **OPTION_D_CRITICAL_LOAD_ROUTING** | `NOT_IMPLEMENTED` | Dynamic critical vs noncritical breaker control & routing logic is not implemented. |
| **EMS_OBJECTIVE_HIERARCHY** | `NOT_IMPLEMENTED` | Multi-objective lexicographic optimization for critical load priority is not implemented. |

---

## Implementation Prerequisites (Required Before Authorization)

Before any code implementation of Option D can be authorized:

1. **Station Engineering Definition**: Formal mapping of physical circuits/breakers into $P_{\text{critical}}$ and noncritical loads.
2. **Parameter Selection**: Formal human governance authorization of production $T_{\text{required}}$, watchdog duration $T_{\text{max,degraded}}$, fuel reserve $F_{\text{reserve,min}}$, and telemetry TTL.
3. **Lexicographic Objective Formulation**: Formal mathematical definition of the multi-objective optimization hierarchy replacing the current scalar $10/Wh penalty in MILP.
4. **Integration Architecture Gate**: Review and authorization of the runtime architecture connecting ECD $\rightarrow$ FaultEvent $\rightarrow$ EMS Mode Manager $\rightarrow$ Optimizer $\rightarrow$ Actuators.
