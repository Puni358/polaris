# Fuel State Classification Correction

## Current Implementation Facts vs Future Design

The previous package over-claimed `FUEL_FIRST_ACTION_ONLY = ESTABLISHED`. This is corrected to distinguish current codebase reality from future implementation design.

### Current Implementation Facts (Codebase Today):
1. `StationState` currently does **NOT** contain `diesel_fuel_remaining_liters`.
2. `DigitalTwinSimulator.step()` currently does **NOT** physically decrement diesel fuel volume across steps.
3. `configs["diesel"]["initial_fuel_l"]` exists as an initial configuration parameter ($100.0	ext{L}$).
4. ECD core accepts `fuel_remaining_liters`, but the current runtime does **NOT** yet provide a rolling physical fuel state to it.

---

## Corrected Classification Matrix

| Terminology / Metric | Corrected Classification | Meaning |
| :--- | :--- | :--- |
| `CURRENT_FUEL_STATE` | **`NOT_ESTABLISHED`** | Current runtime state lacks dynamic fuel tracking. |
| `CURRENT_FUEL_PHYSICAL_PROPAGATION` | **`NOT_IMPLEMENTED`** | `DigitalTwinSimulator.step()` does not decrement fuel. |
| `PROPOSED_FUEL_STATE_ARCHITECTURE` | **`RESOLVED_FOR_IMPLEMENTATION_DESIGN`** | Target design is resolved for future implementation. |
| `FUEL_FIRST_ACTION_RUNTIME` | **`NOT_IMPLEMENTED`** | First-action fuel subtraction is not yet in code. |
| `FUEL_FIRST_ACTION_DESIGN` | **`DEFINED`** | Target design specifies $k=0$ fuel subtraction. |
