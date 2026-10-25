# POLARIS EMS — HD-03 C+A T_required SOURCE MAP & INTERFACE ARCHITECTURE

## 1. COMPONENT & INTERFACE MAP

Under the approved **C+A Source Architecture Model**, $T_{\text{required}}$ originates from two potential channels and flows through a dedicated resolver before being consumed by the Emergency Condition Detector.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SOURCE ARCHITECTURE C+A                                │
├───────────────────────────────────────┬────────────────────────────────────────────────┤
│ OPTION C: DEPLOYMENT CONFIGURATION    │ OPTION A: AUTHORIZED OPERATIONAL INPUT          │
│ (Primary Prototype / Default Source)  │ (Future Real-Station Extension / Override)     │
│                                       │                                                │
│ Source: Static Deployment Config File │ Source: Mission Control / Station Telemetry    │
│ Target: Configured T_required Field   │ Target: Operational Mission Parameter Stream   │
└───────────────────┬───────────────────┴───────────────────────┬────────────────────────┘
                    │                                           │
                    │ configured T_required                     │ operational T_required
                    v                                           v
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  T_required RESOLVER                                   │
│                                                                                        │
│ Function: Validates & resolves T_required from configuration and operational input     │
│ Output: Single authoritative resolved_T_required value + provenance metadata           │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            │ resolved T_required
                                            v
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              EMERGENCY CONDITION DETECTOR                              │
│                                                                                        │
│ Role: CONSUMER ONLY                                                                    │
│ Constraint: MUST NOT derive, invent, modify, or fallback T_required internally         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DETAILED SOURCE SPECIFICATIONS

### 2.1 Option C — Deployment Configuration (Prototype Baseline)
- **Nature**: Explicit, version-controlled deployment configuration parameters.
- **Provenance**: Attached to site deployment profile (e.g. site manifest, deployment YAML/JSON).
- **Semantics**: Provides the default baseline $T_{\text{required}}$ when no operational override is active or present.
- **Current Repository Status**: Schema and configuration field for $T_{\text{required}}$ do **NOT** currently exist in production deployment schemas. Must be added in future additive schema updates.

### 2.2 Option A — Authorized Operational Input (Future Real-Station Extension)
- **Nature**: Dynamic, operational message payload received from authorized mission control or field operations.
- **Provenance**: Signed operational payload with source identity, timestamp, validity period, and authorization key.
- **Semantics**: Supersedes configured baseline when valid, fresh, and authorized according to future governance rules.
- **Current Repository Status**: Operational messaging protocol and input schemas do **NOT** currently exist. Must be designed under future governance items.

### 2.3 $T_{\text{required}}$ Resolver
- **Nature**: Decoupled resolver component sitting between data sources and the Emergency Condition Detector.
- **Function**:
  1. Inspects deployment configuration for configured baseline $T_{\text{required}}$.
  2. Inspects operational input channel for active operational $T_{\text{required}}$.
  3. Applies precedence, freshness, and authorization rules (to be governed).
  4. Passes resolved value to Emergency Condition Detector.
- **Constraint**: Must never derive values from battery capacity, diesel fuel volume, generator runtimes, or EBR intervals.

### 2.4 Emergency Condition Detector
- **Nature**: Downstream consumer of resolved $T_{\text{required}}$.
- **Function**: Evaluates station fuel & battery energy sufficiency over $T_{\text{required}}$ under HD-04 Option A stress scenario ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$).
- **Strict Non-Derivation Constraint**: The detector possesses **zero ownership** over $T_{\text{required}}$ value selection or default derivation.

---

## 3. FUTURE ADDITIVE SCHEMA & INTERFACE REQUIREMENTS (AUDIT ONLY)

The implementation of Model C+A will eventually require the following additive schema updates (NO changes authorized at present):

1. **Deployment Configuration Schema**:
   - `deployment_id`: string
   - `configured_T_required`: optional float (hours)
   - `config_version`: string
2. **Operational Input Interface Payload**:
   - `operational_source_id`: string
   - `operational_T_required`: float (hours)
   - `issue_timestamp`: ISO-8601 string
   - `validity_window_seconds`: integer
   - `authorization_signature`: string
3. **Resolver Audit / Provenance Schema**:
   - `resolved_T_required`: float (hours)
   - `winning_source_type`: enum [`DEPLOYMENT_CONFIG`, `OPERATIONAL_OVERRIDE`]
   - `winning_source_id`: string
   - `resolution_timestamp`: ISO-8601 string
   - `override_active`: boolean
4. **Emergency Detector Input Interface**:
   - Accepts `resolved_T_required` as a required input parameter from Resolver.

---

## 4. CODEBASE BOUNDARY AUDIT

| Module / Area | Current State | Required C+A Adaptation | Implementation Status |
| :--- | :--- | :--- | :--- |
| **`StationState`** | No $T_{\text{required}}$ field | Additive optional operational context field | `NOT_AUTHORIZED` |
| **`ForecastBundle`** | Independent causal forecasts | Remains independent of $T_{\text{required}}$ | `UNCHANGED` |
| **`EmergencyDetector`** | Not implemented / placeholder | Consumes `resolved_T_required` from resolver | `NOT_AUTHORIZED` |
| **`T_required_Resolver`** | Does not exist | Additive new resolver component | `NOT_AUTHORIZED` |
| **MPC / MILP Solver** | Solves 24h horizon ($H$) | Consumes detector mode flag only | `UNCHANGED` |
