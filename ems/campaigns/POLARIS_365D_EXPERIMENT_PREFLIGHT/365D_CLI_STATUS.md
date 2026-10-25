# 365D CLI INFRASTRUCTURE AUDIT & STATUS

## CLI Interface Status
- **Status**: `CLI_REPAIRED_AND_TESTED`
- **Implementation File**: [`system/orchestration/cli.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/orchestration/cli.py)

## Interface Specifications
Supports both positional subcommand (`run-annual-campaign`) and direct flag invocations:
```bash
python3 -m system.orchestration.cli run-annual-campaign \
  --year 2024 \
  --workers 2 \
  --checkpoint-interval 500 \
  --sleep-inhibit \
  --output-dir ./POLARIS_2024_ANNUAL_CAMPAIGN_RESULTS
```

## Governance Authorization Separation
- Executing without `--execute-authorized` or attempting to execute when authorization text is not granted halts with a clear error:
  `[GOVERNANCE ERROR] HUMAN_EXECUTION_AUTHORIZATION = NOT_GRANTED. Annual campaign execution is locked by governance.`
- `--dry-run` executes a 48-step 2-cell infrastructure validation without touching the 8,784-step annual run or making performance claims.
