# Environment Rollback Strategy

If environment restoration is required:

```bash
/home/punith-bs/01polaris (Copy)/.venv/bin/python -m pip uninstall -y highspy
```

This restores the project environment to its exact pre-installation state (Python 3.12.3, SciPy 1.18.1, NumPy 2.5.2, `highspy: NOT_INSTALLED`).
