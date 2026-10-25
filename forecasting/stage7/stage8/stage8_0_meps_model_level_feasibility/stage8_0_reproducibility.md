# POLARIS Stage 8.0 — Reproducibility Instructions

To reproduce the archive scan, variable metadata inspection, and point audits:

```bash
./.venv/bin/python scratch/fast_multithreaded_audit.py
./.venv/bin/python scratch/run_detailed_stage8_audits.py
```

All output JSON, CSV, and MD artifacts are stored atomically in `stage7/stage8/stage8_0_meps_model_level_feasibility/`.
