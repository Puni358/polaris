# POLARIS EMS — HD-03 Architectural Option Matrix & Evaluation

**Audit Objective**: Detailed side-by-side evaluation of Options A, B, and C across 10 core architectural criteria without ranking or selecting one.

---

## 1. Ten-Criteria Architectural Option Comparison Table

| Criterion | Option A: Operational Input | Option B: Fixed Governed Parameter | Option C: Configurable Parameter |
| :--- | :--- | :--- | :--- |
| **1. Source** | Mission / Station Operations API | Central POLARIS System Config | Station Deployment Manifest Config |
| **2. Runtime Variability** | Dynamic (Can change per timestep/run) | Static (Constant across all runs) | Static per deployment instance |
| **3. Station Portability** | High (Adapts dynamically to resupply updates) | Low (Fixed across all stations globally) | High (Each station sets custom window) |
| **4. Governance Dependency**| High (Requires ops API interface contract) | High (Requires central policy approval) | High (Requires site manager approval) |
| **5. Missing-Data Issue** | Must fail-closed or use governed fallback | Defined in central YAML default | Boot fails if config parameter missing |
| **6. Reproducibility** | Requires logging provider ID & timestamp | Recorded via config git hash | Recorded in station manifest git hash |
| **7. Schema Impact** | Requires field in `StationState` schema | No `StationState` schema change needed | Requires station deployment YAML schema |
| **8. Detector Integration**| Consumes `state.t_required_hours` | Reads central system config parameter | Reads station deployment YAML parameter |
| **9. Prototype Suitability** | Low (Requires mock ops provider) | High (Simple static YAML value) | High (Simple deployment YAML value) |
| **10. Future Station Suitability**| Maximum flexibility for real operations | Restricted for multi-site deployment | High for multi-site deployment |

---

## 2. Evaluation of Core Architectural Criteria

### 2.1 Schema Impact Analysis
- **Option A**: Requires adding `t_required_hours: float` to `StationState` ([`system/state/state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/state/state.py)) and telemetry loggers ([`system/telemetry/v2_logger.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/telemetry/v2_logger.py)).
- **Option B**: Requires adding `t_required_hours: float` to central configuration ([`system/config/optimizer.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/optimizer.yaml)). No `StationState` changes needed.
- **Option C**: Requires adding `t_required_hours: float` to station deployment config (`system/config/station.yaml`). No `StationState` changes needed.

### 2.2 Reproducibility Analysis
- **Option A**: Simulation replay requires recording the provider ID, effective timestamp, and exact $T_{\text{required}}$ value for every execution step in telemetry logs.
- **Option B & C**: Simulation replay requires only the git hash of the configuration file.

### 2.3 Detector Ownership Boundary
Across all three options, the Emergency Mode Detector **consumes** $T_{\text{required}}$ as a read-only parameter. The detector does **not** generate, infer, or modify $T_{\text{required}}$.
