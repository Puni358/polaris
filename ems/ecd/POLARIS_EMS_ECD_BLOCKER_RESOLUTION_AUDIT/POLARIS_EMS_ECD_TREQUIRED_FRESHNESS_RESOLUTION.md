# POLARIS EMS — T_REQUIRED & FRESHNESS RESOLUTION AUDIT (BLK-006 & BLK-007)

## 1. Executive Summary

This document establishes the resolution audit for **BLK-006** ($T_{\text{required}}$ TTL Numerical Value) and **BLK-007** (Telemetry / Command Maximum-Age Numerical Value).

---

## 2. Separation of Concerns & Classification

- **BLK-006 ($T_{\text{required}}$ TTL)**: Governs how long an operational override command remains valid before expiring.
- **BLK-007 (Telemetry Max-Age)**: Governs how old sensor data (SOC, fuel level, temperatures) can be before being rejected as stale telemetry.

These are **conceptually distinct contracts**. Both are classified as:
`CAN_BE_PARAMETERIZED_WITHOUT_POLICY_DECISION`

---

## 3. Parameterization & Software Architecture

The ECD software implementation accepts freshness and expiration constraints via a clean configuration injection model (`ECDConfig`):

```python
class ECDConfig:
    ttl_seconds: Optional[float] = None
    max_telemetry_age_seconds: float = 300.0  # Injected via deployment config
    max_override_age_seconds: float = 3600.0  # Injected via deployment config
```

The ECD internal logic evaluates freshness using generic comparison:
1. `if command.expires_at is not None and current_time > command.expires_at: return UNKNOWN_INVALID`
2. `if current_time - telemetry.timestamp > max_telemetry_age_seconds: return UNKNOWN_INVALID`

---

## 4. Gating & Decision Matrix

| Question | BLK-006 ($T_{\text{required}}$ TTL) | BLK-007 (Telemetry Max-Age) |
|----------|-------------------------------------|-----------------------------|
| **Can implementation be parameterized?** | **YES** | **YES** |
| **Can unit tests proceed?** | **YES** (passes test timestamps) | **YES** (passes test age bounds) |
| **Can integration proceed?** | **YES** (uses test environment config) | **YES** (uses test environment config) |
| **Can production deployment proceed?** | **NO** (requires site governance decision) | **NO** (requires site operator decision) |

---

## 5. Audit Conclusion

Neither BLK-006 nor BLK-007 blocks unit implementation or integration testing of the ECD module. Production deployment is gated by explicit site configuration.

Status: `PARAMETERIZED_AND_RESOLVED_FOR_IMPLEMENTATION`
