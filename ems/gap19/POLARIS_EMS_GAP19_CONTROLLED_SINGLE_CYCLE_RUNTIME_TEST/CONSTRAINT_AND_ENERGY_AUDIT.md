# Constraint and Energy Balance Audit

```text
ENERGY_ACCOUNTING = PASS
MAX_ENERGY_BALANCE_ERROR = 0.000000e+00 W
CONSTRAINT_VALIDATION = PASS
```

## Physical Bounds Audit
- **Battery SOC:** Min 28.00%, Max 95.00% (Bound: [20.0%, 95.0%]) -> `PASS`
- **Battery Charge Power:** Max 47500.00 W (Bound: <= 50,000 W) -> `PASS`
- **Battery Discharge Power:** Max 15500.00 W (Bound: <= 50,000 W) -> `PASS`
- **Diesel Operating Range:** Min 0.00 W, Max 0.00 W (Range: [10,000 W, 100,000 W]) -> `PASS`
