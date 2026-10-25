# POLARIS — Hybrid Fixture Generator Code Specification

> **Specification Identity:** `POLARIS_HYBRID_FIXTURE_GENERATOR_SPEC`  
> **Target Module:** `system.fixtures.hybrid_fixture_generator.PolarisHybridFixtureGenerator`  
> **Status:** `SPECIFICATION_DESIGN_ONLY_NOT_EXECUTED`  
> **Governance Date (UTC):** 2026-09-20  

---

## 1. Class Architecture Design

```python
"""
POLARIS Hybrid Fixture Generator (Specification & Code Design — NOT EXECUTED)
Deterministic generator for combining real, proxy, and synthetic input streams.
"""

import hashlib
import json
import math
from typing import Dict, List, Any

class PolarisHybridFixtureGenerator:
    """
    Deterministic generator for POLARIS Hybrid Engineering Fixture H1.0.
    DO NOT EXECUTE WITHOUT FORMAL GOVERNANCE EXECUTION AUTHORIZATION.
    """
    def __init__(
        self,
        solar_file_path: str = "data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv",
        wind_file_path: str = "research/wind_a2/smhi_188790_ws_full.csv",
        random_seed: int = 42,
        base_demand_w: float = 25000.0,
        turbine_rated_power_w: float = 60000.0
    ):
        self.solar_file_path = solar_file_path
        self.wind_file_path = wind_file_path
        self.random_seed = random_seed
        self.base_demand_w = base_demand_w
        self.turbine_rated_power_w = turbine_rated_power_w

    def generate_synthetic_demand(self, timestamps: List[str]) -> List[float]:
        """
        Generates deterministic 15-45 kW synthetic station demand.
        SYNTHETIC_STATION_DEMAND != NULLOJA_MEASURED_DEMAND.
        """
        demand_trace = []
        for ts in timestamps:
            # Diurnal hour extraction (0-23 UTC)
            hour = int(ts[11:13]) if "T" in ts else 0
            
            # Base diurnal profile shape
            if 0 <= hour <= 5:
                diurnal_w = 18000.0
            elif hour == 8:
                diurnal_w = 38000.0
            elif 9 <= hour <= 17:
                diurnal_w = 32000.0
            elif hour == 19:
                diurnal_w = 42000.0
            else:
                diurnal_w = 25000.0
            
            # Baseline H1.0 is 100% deterministic (zero noise)
            demand_trace.append(min(max(diurnal_w, 15000.0), 45000.0))
        return demand_trace

    def generate_synthetic_wind_power(self, wind_speeds: List[float]) -> List[float]:
        """
        Maps Abisko 10m proxy wind speed (m/s) to generic IEC 60 kW turbine curve.
        GENERIC ENGINEERING ASSUMPTION — NOT NULLOJA HARDWARE.
        """
        wind_power_trace = []
        for v in wind_speeds:
            if v < 3.0 or v >= 25.0:
                p_wind = 0.0
            elif 3.0 <= v < 12.0:
                p_wind = self.turbine_rated_power_w * ((v**3 - 3.0**3) / (12.0**3 - 3.0**3))
            else:
                p_wind = self.turbine_rated_power_w
            wind_power_trace.append(min(max(p_wind, 0.0), self.turbine_rated_power_w))
        return wind_power_trace

    def apply_d3_pv_mapping(self, sw_in: List[float]) -> List[float]:
        """
        Applies frozen D3 engineering PV conversion formula.
        P_raw = SW_IN * 300m^2 * 0.20 * 0.85; P_solar = min(P_raw, 60000 W)
        """
        p_solar_trace = []
        for sw in sw_in:
            p_raw = sw * 300.0 * 0.20 * 0.85
            p_solar_trace.append(min(p_raw, 60000.0))
        return p_solar_trace

    def compute_fixture_sha256_fingerprint(self, dataset: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 hash of output dataset dictionary."""
        serialized = json.dumps(dataset, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()
```

---

## 2. Determinism & Non-Execution Audit

- **Fixed Seed:** `random_seed = 42` (ensures 100% deterministic reproducibility).
- **Execution Status:** Specified as code architecture design ONLY. **Not executed** during Step 8.

---

## 3. Mandatory Safety & Governance Status Block

```
FROZEN_EVIDENCE_MODIFIED      = NO
MILP_SOLVES_EXECUTED          = 0
SIMULATIONS_EXECUTED          = 0
EXPERIMENT_RERUN              = NO
NEW_MODELING                  = NO
NEW_TUNING                    = NO
ARCHITECTURE_MODIFIED         = NO

REAL_DEMAND_DATA_STATUS       = DATA_BLOCKED
NUOLJA_WIND_ASSET_STATUS      = NOT_ESTABLISHED
NUOLJA_WIND_GENERATION_STATUS = NOT_ESTABLISHED
```
