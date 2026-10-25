# 365D CHECKPOINT SCHEMA & INTEGRITY SPECIFICATION

## Checkpoint Interval & Format
- **Default Interval**: Every 500 control cycles (and at step $k = N_{obs}-1$).
- **File Naming**: `checkpoints/cell_XX/checkpoint_000500.json`
- **Schema Version**: `CHECKPOINT_SCHEMA_VERSION = 1`

## Checkpoint Payload Schema

```json
{
  "schema_version": 1,
  "run_id": "polaris_365d_run_20260926_211325",
  "cell_id": "cell_1",
  "worker_id": "worker_01",
  "cycle_index": 499,
  "timestamp": "2024-01-21T20:00:00Z",
  "station_state": {
    "timestamp": "2024-01-21T20:00:00Z",
    "battery_soc_pct": 52.4,
    "battery_energy_wh": 104800.0,
    "diesel_running": false,
    "diesel_hours_running": 0.0,
    "last_observed_solar_irradiance": 0.0,
    "last_observed_demand": 24500.0,
    "last_observed_wind_generation": 12000.0
  },
  "cumulative_fuel_l": 610.2082,
  "cumulative_diesel_energy_kwh": 1840.0,
  "cumulative_battery_throughput_kwh": 3120.0,
  "integrity_counters": {
    "truth_leakage_count": 0,
    "state_reset_count": 0,
    "fuel_reset_count": 0,
    "soc_reset_count": 0,
    "infeasibility_count": 0,
    "unmet_critical_load_wh": 0.0,
    "power_balance_max_error_w": 0.0
  },
  "protected_hashes": { ... },
  "fixture_hash": "762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023",
  "previous_checkpoint_hash": "a5e8f...",
  "current_checkpoint_hash": "c89d1..."
}
```

## SHA256 Chaining Protocol
Each checkpoint file computes `current_checkpoint_hash` by taking the SHA256 of its JSON payload excluding `current_checkpoint_hash`. `previous_checkpoint_hash` links to the predecessor checkpoint hash, creating an immutable, cryptographically verifiable chain.
