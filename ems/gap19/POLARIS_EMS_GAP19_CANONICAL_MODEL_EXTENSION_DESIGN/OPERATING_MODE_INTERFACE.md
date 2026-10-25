# OPERATING MODE INTERFACE

## EXTERNAL OPERATING MODE INGESTION FROM ECD

- **Authority Principle**: The Emergency Control Discriminator (ECD) is the SOLE authority that determines station survivability mode. The optimizer MUST NOT independently declare emergency mode.
- **Interface Structure**:
  - `config["operating_mode"]`: String parameter taking values `"NORMAL"`, `"EMERGENCY"`, or `"UNKNOWN_INVALID"`.
- **Mode Behavior**:
  - `"NORMAL"`: Full 4-stage $J_1..J_4$ multi-objective optimization across all loads.
  - `"EMERGENCY"`: Option D protected critical load fallback constraints active.
  - `"UNKNOWN_INVALID"`: Fail-safe zero-dispatch degraded safety plan returned.
