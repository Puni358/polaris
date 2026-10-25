# ECD Boundary & Integration Status Correction

Inspection of `system/runtime/runner.py` confirms that `system/control/ecd.py` is **NOT** imported or called by `PolarisLocalRunner`.

```text
ECD_MODULE = system/control/ecd.py
ECD_RUNTIME_INTEGRATION = NOT_IMPLEMENTED
```

The existence of `ecd.py` does not imply runtime integration.
