# POLARIS GATE-01 — OPERATOR REQUIREMENTS SPECIFICATION
## REQUIREMENTS FOR AUTHORIZED OPERATOR INTERVENTION UNDER UNKNOWN_INVALID

---

## 1. MANDATORY OPERATOR INTERVENTION MANDATE

```yaml
AUTHORIZED_OPERATOR_INTERVENTION: REQUIRED
OPERATOR_AUTHORITY_DETAILS: SEPARATELY_GOVERNED
OPERATOR_INTERFACE: ENGINEERING_GOVERNANCE_REQUIREMENT
```

### Governance Requirement
> *"When ECD reports `UNKNOWN_INVALID`, automatic EMS optimization MUST stop, and operational authority MUST be surrendered to an authorized human operator under separately governed conditions."*

---

## 2. EXPLICIT OPERATOR NON-INVENTIONS

The following engineering implementation mechanisms are **NOT INVENTED IN THIS GOVERNANCE TASK** and require separate specification:

1. **Authentication & Access Control**: No login system, OAuth2, RBAC, or MFA implementation is specified.
2. **Communication Protocol**: No SCADA, REST, WebSockets, or MQTT protocol is mandated.
3. **Manual Dispatch API**: No API endpoint for manual generator or battery override setpoints is defined.
4. **Timeouts & Acknowledgements**: No operator response timeout, alarm escalation timer, or acknowledgement window is invented.
5. **Hardware Authority Path**: No physical transfer switch or remote terminal unit (RTU) interlock protocol is specified.

---

## 3. SEPARATION FROM $T_{\text{required}}$ OVERRIDE AUTHORITY

- Under prior ECD governance, a specific override mechanism was authorized permitting operators to adjust the emergency lookahead parameter ($T_{\text{required}}$).
- **Rule**: The $T_{\text{required}}$ override authority MUST NOT automatically be interpreted as a complete manual dispatch authority protocol for `UNKNOWN_INVALID`.
- Manual control during `UNKNOWN_INVALID` requires a separate, comprehensive operator interface protocol.
