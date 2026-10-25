# POLARIS GATE-01 — UNKNOWN_INVALID GOVERNED-HYBRID POLICY
## OPERATIONAL POLICY SPECIFICATION FOR UNKNOWN_INVALID ASSESSMENT

---

## 1. GOVERNED-HYBRID OPERATIONAL INTENT

The human project owner has formally sealed the operational response policy for `UNKNOWN_INVALID`:

```text
GOVERNED_HYBRID INTENT:
"Stop automatic optimization, preserve protected-critical service, and involve authorized operator intervention under separately governed conditions."
```

```yaml
AUTOMATIC_OPTIMIZATION: STOP
PROTECTED_CRITICAL_SERVICE: PRESERVE
AUTHORIZED_OPERATOR_INTERVENTION: REQUIRED
OPERATOR_AUTHORITY_DETAILS: SEPARATELY_GOVERNED
UNKNOWN_INVALID_EQUALS_EMERGENCY: NO
AUTOMATIC_OPTION_D: NOT_IMPLIED
DIGITAL_TWIN_STATE_ADVANCEMENT: NO
AUTOMATIC_RECOVERY_TO_NORMAL: NOT_AUTHORIZED
```

---

## 2. DOMAIN SEPARATION: UNKNOWN_INVALID VS. EMERGENCY

It is an explicit governance mandate to maintain strict separation between `UNKNOWN_INVALID` and `EMERGENCY`:

```text
+-----------------------------------------------------------------------------------+
| UNKNOWN_INVALID                                                                   |
| ECD cannot establish a trustworthy physical survivability assessment              |
| (e.g., telemetry gap, sensor corruption, unclassifiable operating boundary).      |
+-----------------------------------------------------------------------------------+
                                          ≠
+-----------------------------------------------------------------------------------+
| EMERGENCY                                                                         |
| ECD has established a validated emergency survivability crisis                    |
| (e.g., fuel reserve depletion below minimum T_required endurance).                 |
+-----------------------------------------------------------------------------------+
```

- **`UNKNOWN_INVALID_EQUALS_EMERGENCY = NO`**
- **`AUTOMATIC_OPTION_D = NOT_IMPLIED`**: Option D is an emergency solver designed for validated physical crises. It MUST NOT be automatically invoked merely because an assessment is `UNKNOWN_INVALID`.

---

## 3. GOVERNED CONTROL FLOW

The authoritative operational sequence for `UNKNOWN_INVALID` is:

```text
ECD Assessment Output: UNKNOWN_INVALID
                 │
                 ▼
1. STOP AUTOMATIC OPTIMIZATION
   - Halt automatic EMS optimization loops.
   - Set DIGITAL_TWIN_STATE_ADVANCEMENT = NO.
                 │
                 ▼
2. PRESERVE PROTECTED-CRITICAL SERVICE
   - Maintain physical power supply to essential protected loads via local hardware fallbacks.
   - Do NOT invent un-governed software setpoints or zero-dispatch blackouts.
                 │
                 ▼
3. AUTHORIZED OPERATOR INTERVENTION
   - Surrender operational authority to an authorized human operator.
   - Require operator evaluation under separately governed procedures.
                 │
                 ▼
4. SEPARATELY GOVERNED RECOVERY
   - Require formal governance approval before returning to NORMAL or automatic optimization.
```

---

## 4. SOFTWARE CONTAINMENT VS. PHYSICAL SAFETY

- **Pre-Existing Software Containment**: In `runner.py` (lines 151–164), `UNKNOWN_INVALID` creates a `FaultEvent(severity="CRITICAL_TERMINATION", response="FAILED_TERMINATED", state_advanced=False)` and breaks out of the execution loop.
- **Governance Classification**: This software behavior is classified as **`PREEXISTING_FAILED_TERMINATED = TEMPORARY_SOFTWARE_CONTAINMENT`**.
- **Physical Safety Reality**: Halting the Python runner process prevents software state corruption, but **`PHYSICAL_SAFE_STATE = NOT_ESTABLISHED_BY_SOFTWARE_TERMINATION`**. Physical station safety relies on hardware protection relays and local microgrid governors until an integrated physical fallback is built.
