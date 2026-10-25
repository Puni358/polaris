# Tolerance Firewall

## Firewall Declaration

The priority correction gate strictly forbids the introduction or modification of solver tolerances to mask priority issues.

```text
TOLERANCE_CHANGE_REQUIRED = NO
```

## Tolerance Audit & Governance Constraints

1. **No Policy Tolerances**: Do NOT introduce $0.01\text{ L}$ or any arbitrary non-zero value as a POLARIS governance tolerance.
2. **No False Mathematical Bounds**: Do NOT introduce $1e-5$ or similar arbitrary epsilon as a definition of mathematical exactness.
3. **Preservation of Native Tolerances**:
   - `obj1.abs_tolerance = 0.0`, `obj1.rel_tolerance = 0.0`
   - `obj2.abs_tolerance = 0.0`, `obj2.rel_tolerance = 0.0`
   - `obj3.abs_tolerance = 0.0`, `obj3.rel_tolerance = 0.0`
   - `obj4.abs_tolerance = 0.0`, `obj4.rel_tolerance = 0.0`

Lexicographic optimization relies on exact objective boundary preservation. Tolerances remain strictly at $0.0$.
