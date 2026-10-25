# Minimality Audit for Two-Blocker Resolution

## 1. Fuel State Minimality
- Adding optional `diesel_fuel_remaining_liters: Optional[float] = None` to `StationState` requires adding **ONE OPTIONAL ATTRIBUTE** to `StationState.__init__`.
- Requires **ZERO NEW FILES**, **ZERO NEW SCHEMAS**.
- Preserves 100% backward compatibility.

## 2. Infeasibility Routing Minimality
- Reuses ECD #1 assessment output without creating a second ECD evaluation call or duplicate solver calls.
- Requires **ZERO NEW OPTIMIZERS**.

---

## Summary
- `SOURCE_MODIFICATIONS` = **ZERO** (Design stage only)
- `SCHEMA_MODIFICATIONS` = **ZERO** (Design stage only)
- `RUNTIME_EXECUTION` = **NONE**
