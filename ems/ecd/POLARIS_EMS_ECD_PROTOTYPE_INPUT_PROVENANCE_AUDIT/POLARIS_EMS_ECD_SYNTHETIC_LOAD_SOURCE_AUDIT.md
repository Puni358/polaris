# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## SYNTHETIC LOAD SOURCE & SEMANTICS AUDIT (RE-AUDIT)

**Audit Date**: 2026-09-23  
**Status**: COMPLETE — RE-AUDITED LOAD & DEMAND SEMANTICS  

---

### 1. LOAD SEMANTICS AUDIT & CRITICAL-LOAD SEPARATION

- **`demand.point` Semantics**: In [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py), `demand.point` strictly represents **TOTAL STATION DEMAND** (24-hour horizon). It CANNOT be relabeled as critical load without violating semantic contracts.
- **Prototype Parameter vs 72h Trajectory**:
  - `system/config/loads.yaml` contains `critical_load.baseline_power_w: 30000.0` ($30\text{ kW}$). This is a **prototype scalar configuration parameter** (`PROTOTYPE_ASSUMPTION`), with `STATION_MEANING = NONE`.
  - A $30\text{ kW}$ scalar parameter is **NOT** automatically a 72-hour critical load trajectory. These concepts MUST be kept strictly separate.
  - Silent promotion of a scalar parameter into a 72-hour forecast trajectory is **STRICTLY PROHIBITED**.
- **Real Station Status**: Real station critical-load classification is **NOT_ESTABLISHED_IN_CURRENT_EVIDENCE_BASE**.

---

### 2. 72H CRITICAL LOAD TRAJECTORY STATUS

- **Finding**: A governed 72-hour critical load trajectory is **NOT_ESTABLISHED** in the POLARIS repository.
- **Rules Enforced**:
  1. DO NOT extend a 24h trajectory automatically.
  2. DO NOT repeat the final 24h value automatically.
  3. DO NOT interpolate future demand automatically.
  4. DO NOT use Digital Twin future truth.
- **Required Next Step**: Construction of a 72-hour synthetic critical load test trajectory requires formal governance authorization (`CRITICAL_LOAD_SOURCE = NEW_SYNTHETIC_REQUIRED`).
