# UNKNOWN_INVALID Hard Operational Boundary

## Absolute Firewall Rule
```text
ECD Core returns UNKNOWN_INVALID
   ↓
EMSControlRouter recognizes UNKNOWN_INVALID
   ↓
DO NOT silently call Option B HiGHS
   ↓
DO NOT silently call Option D Fallback
   ↓
Operational Action = NOT_ESTABLISHED
```

## Prohibited Inferences
The design explicitly **REFUSES** to invent operational safe-state actions:
- No hardcoded shutdown
- No zero-dispatch
- No hold-last-plan
- No generator auto-start
- No load shedding
- No operator trip

The operational action remains **`NOT_ESTABLISHED`** pending explicit governance authorization.
