# UNKNOWN_INVALID & Option D Compatibility

- **Sealed Option D Policy**: DEC-004 selected `OPTION_D_PROTECTED_CRITICAL_LOAD_FALLBACK`, which specifies that during emergency/fallback conditions, protected critical loads are supplied by renewable generation, battery, and diesel according to proportional allocation.
- **Implemented UNKNOWN_INVALID Behavior**: Bypasses solver and sets `load_served = 0.0`.
- **Analysis**: Bypassing optimization and shedding all load is an implementation fail-closed guard, not the active dispatch policy defined by Option D.
- **Classification**: `IMPLEMENTATION_FALLBACK_NOT_OPTION_D_DISPATCH`.
