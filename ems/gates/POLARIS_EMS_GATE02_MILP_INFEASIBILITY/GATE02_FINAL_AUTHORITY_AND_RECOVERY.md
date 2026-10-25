# POLARIS GATE-02 — FINAL AUTHORITY AND RECOVERY
## ANALYSIS OF OPERATIONAL AUTHORITY AND RECOVERY SEMANTICS

---

## 1. RECOVERY POLICY

```text
RECOVERY_POLICY = GOVERNANCE_REQUIRED
```

### Governing Rules
1. **No Invented Automatic Recovery**: POLARIS runtime code MUST NOT contain invented automatic recovery loops, watchdog timers, retry counters, or hysteresis logic for MILP infeasibility.
2. **State Freeze**: Upon detecting `OPTIMIZATION_INFEASIBLE`, the system holds the authoritative `StationState` at timestep $k$ without state advancement or automatic retry.
3. **Prerequisites for Automatic Recovery**: Any future proposal to automate recovery from MILP infeasibility must formally specify:
   - Max retry limit and backoff delay interval;
   - Allowable numerical solver tolerance adjustments;
   - Formal boundary conditions under which solver retry transitions to system fault escalation.

---

## 2. OPERATIONAL AUTHORITY

```text
AUTHORITY = GOVERNANCE_REQUIRED
```

### Governing Rules
1. **No Invented Authority Handover**: POLARIS code MUST NOT assume or simulate manual operator control or automated hardware takeover without an authorized control transfer specification.
2. **Current Authority Boundary**: The automatic EMS halts optimization dispatch when solver infeasibility occurs. Physical hardware governors operate independently under local hardware interlocks.
3. **Prerequisites for Operational Authority Transfer**: If Option E (Operator Intervention) or Option A (External Fallback) is selected in a future release, governance must define:
   - Authenticated operator API and command interface;
   - Microgrid hardware control transfer protocol;
   - Mandatory audit logging of manual override commands.
