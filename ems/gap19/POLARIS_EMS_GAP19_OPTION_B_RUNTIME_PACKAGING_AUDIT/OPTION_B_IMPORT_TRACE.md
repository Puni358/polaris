# Option B Import Trace

## Target Module
`system/optimization/implementations/gap19_highs_native.py`

## Import Inspection
```python
import numpy as np
import highspy
from system.optimization.interface.base import EnergyOptimizer
from system.schemas.forecast_bundle import ForecastBundle
from system.schemas.station_state import StationState
from system.schemas.dispatch_plan import DispatchPlan
```

- **Primary Dependency**: `highspy`
- **Package Requirement**: `highspy==1.15.1`
