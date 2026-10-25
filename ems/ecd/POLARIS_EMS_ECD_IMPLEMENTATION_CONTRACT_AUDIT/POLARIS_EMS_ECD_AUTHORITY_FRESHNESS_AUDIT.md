# POLARIS EMS — ECD AUTHORITY & FRESHNESS AUDIT

## 1. Executive Summary

This document audits the authority and freshness requirements for operational inputs to the Emergency Condition Detector (ECD), with primary focus on the operational target horizon $T_{\text{required}}$ governed under HD-03.

---

## 2. HD-03 Authority Precedence & Fallback Cascade

The ECD is a **CONSUMER** of $T_{\text{required}}$ and does NOT own or generate it. $T_{\text{required}}$ must enter the system via an authenticated and authorized governance chain.

```
[Operational Source] ──(Signed Command)──► Authentication Layer
                                                   │
                                                   ▼
                                        Validity & Freshness Check
                                                   │
                            ┌──────────────────────┴──────────────────────┐
                        [VALID]                                      [INVALID]
                            │                                             │
                            ▼                                             ▼
                 Operational Override Wins                     Configured Baseline
                                                                          │
                                                       ┌──────────────────┴──────────────────┐
                                                   [VALID]                               [INVALID]
                                                       │                                     │
                                                       ▼                                     ▼
                                           Use Baseline Horizon                         FAIL CLOSED
                                                                                   (mode = UNKNOWN_INVALID)
```

---

## 3. Freshness Guard Rules

To prevent stale or replayed operational commands from misdirecting station emergency policy, two independent freshness controls must be satisfied:

1. **Explicit Expiry Timestamp**: The operational command payload must contain a UTC timestamp `expires_at`. If `current_time > expires_at`, the command is expired.
2. **Maximum-Age Guard**: The age `current_time - issued_at` must not exceed `max_age_seconds`.

---

## 4. Governance & Technical Open Items Register

The following parameter values remain **NOT ESTABLISHED** in the codebase and are flagged as governance/engineering blockers:

| Parameter | Category | Meaning / Impact | Status |
|-----------|----------|------------------|--------|
| `TTL` Numerical Value | `GOVERNANCE_REQUIRED` | Maximum validity duration of an operational override command | `NOT_ESTABLISHED` |
| `max_age_seconds` Numerical Value | `GOVERNANCE_REQUIRED` | Hard age cap for telemetry & override freshness | `NOT_ESTABLISHED` |
| Clock-drift threshold | `ENGINEERING_DEFINITION_REQUIRED` | Allowed clock skew tolerance between station and command source | `NOT_ESTABLISHED` |
| Cryptographic Mechanism | `GOVERNANCE_REQUIRED` | Specific signature scheme (e.g., Ed25519, RSA-4096, HMAC-SHA256) for operational override authorization | `NOT_ESTABLISHED` |
| Exact Unit Contract | `CLOSED` | Duration MUST be in hours (`float`) | `CLOSED` |

---

## 5. Audit Conclusion

Authority & Freshness Model Status: `ESTABLISHED` (Logic structure closed; exact numerical TTL/crypto parameters flagged in Blocker Register).
