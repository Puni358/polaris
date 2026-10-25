# POLARIS GATE-01 — Authority Source & Escalation Analysis

This document analyzes the authority boundaries required to resolve `OperatingMode.UNKNOWN_INVALID`.

## 1. Conceptual Authority Sources

| Authority Level | Authority Source | Description | Current Status |
| :--- | :--- | :--- | :--- |
| **Level 1** | Automatic EMS Policy | Pre-programmed algorithmic response inside EMS runner | **NOT GOVERNED** for `UNKNOWN_INVALID` |
| **Level 2** | Authenticated MFA Gate | Automated cryptographic payload override for horizon authority ($T_{\text{required}}$) | **SPECIFIED IN BASELINE** |
| **Level 3** | Authorized Human Operator | On-site or remote station engineer issuing manual dispatch override | **INTERFACE NOT DEFINED** |
| **Level 4** | Deployment Configuration | Site-specific configuration file defining default safety fallback | **NOT ESTABLISHED** |

---

## 2. Authority Resolution Requirements

1. **No Implicit Authority**: The EMS runtime must not assume authority to select operational actions without explicit governance authorization.
2. **Authority Blocker**: Because Level 1 (Automatic EMS Policy) is not governed for `UNKNOWN_INVALID`, and Level 3 (Human Operator interface) is not defined, authority for selecting an operational response remains **`UNRESOLVED`**.
3. **MFA Authority Gate Relationship**: Cryptographic MFA authentication exists for overriding $T_{\text{required}}$ horizon authority, but does not specify a physical dispatch override payload for invalid telemetry states.
