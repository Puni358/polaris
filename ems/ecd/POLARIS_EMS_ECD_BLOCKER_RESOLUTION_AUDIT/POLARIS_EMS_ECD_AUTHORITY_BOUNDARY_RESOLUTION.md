# POLARIS EMS — AUTHORITY BOUNDARY RESOLUTION AUDIT (BLK-008)

## 1. Executive Summary

This document establishes the architectural boundary resolution for **BLK-008** (Cryptographic Signature/Authentication Scheme for Operational Override Payloads).

---

## 2. Architectural Boundary Determination

The repository governance model specifies:
> *"authenticated + explicitly authorized operational source"*

### Architectural Options Evaluated:
- **Option A (Cryptographic Verification inside ECD)**: Rejected. Embedded signature verification violates the Single Responsibility Principle and pollutes domain logic with security transport concerns.
- **Option B (Upstream Authority Boundary - SELECTED)**: Cryptographic signature verification, TLS token validation, and RBAC authentication occur at the API / Ingress / Command Handler layer. The ECD receives a pre-validated domain object `AuthorizedHorizon`:

```python
@dataclass(frozen=True)
class AuthorizedHorizon:
    t_required_hours: float
    is_authenticated: bool
    is_authorized: bool
    source_identity: str
    issued_at: float
    expires_at: Optional[float]
```

---

## 3. Gating & Decision Matrix

| Gate Question | Determination | Rationale |
|---------------|---------------|-----------|
| **Is cryptographic verification inside ECD?** | **NO** | Pure upstream boundary separation. |
| **Is authenticated-authorized input sufficient as ECD boundary?** | **YES** | ECD checks `is_authenticated` and `is_authorized` boolean flags. |
| **Blocks ECD Unit Implementation?** | **NO** | Unit tests inject `AuthorizedHorizon(t_required_hours=72.0, is_authenticated=True, is_authorized=True)`. |
| **Blocks ECD Integration?** | **NO** | Integration tests use mock command ingress handler. |
| **Blocks Production Deployment?** | **YES** | Production deployment requires upstream security infrastructure (Ed25519/mTLS ingress). |

---

## 4. Audit Conclusion

BLK-008 does **NOT** block ECD unit implementation or integration. The architectural boundary is cleanly established at the upstream ingress interface.

Status: `UPSTREAM_BOUNDARY_ESTABLISHED`
