# POLARIS EMS — HD-03 C+A T_required SOURCE ARCHITECTURE FORMAL GOVERNANCE CLOSURE

## 1. FORMAL GOVERNANCE CLOSURE STATEMENT

The human stakeholder has formally decided and approved the **HD-03 $T_{\text{required}}$ Source Architecture** for POLARIS EMS.

The authoritative source architecture model is:
$$\text{HD03\_SOURCE\_MODEL} = \text{C\_PLUS\_A}$$

This model combines:
- **PRIMARY PROTOTYPE / DEPLOYMENT MODEL (OPTION C)**: Deployment-specific configured $T_{\text{required}}$ value supplied through an authorized deployment configuration.
- **FUTURE OPERATIONAL EXTENSION (OPTION A)**: Authorized operational/mission input that may supersede the configured deployment baseline when valid operational communications and governance frameworks are active.

---

## 2. CORE ARCHITECTURAL PRINCIPLES OF THE C+A MODEL

1. **Deployment Configuration Baseline (Option C)**: Each POLARIS deployment may have an explicitly configured $T_{\text{required}}$ value supplied through an authorized deployment configuration file or manifest.
2. **Authorized Operational Input / Override (Option A)**: Future real-station deployments may additionally receive a $T_{\text{required}}$ value from an authorized operational/mission control source.
3. **Operational Precedence Capability**: An authorized operational input may supersede the deployment configuration when such an operational source exists and satisfies all governed authorization, freshness, and validity rules.
4. **Detector as Consumer Only**: The Emergency Condition Detector **CONSUMES** the resolved $T_{\text{required}}$ value provided by the $T_{\text{required}}$ Resolver.
5. **Strict Non-Derivation Directive**: The Emergency Condition Detector **MUST NOT** derive, invent, modify, estimate, or self-select $T_{\text{required}}$.
6. **Numerical Value Unresolved**: The numerical value of $T_{\text{required}}$ remains **UNRESOLVED** (`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`).
7. **Scope Limitation**: This governance decision closes the **SOURCE ARCHITECTURE ONLY**. It does NOT select the number of survival hours or establish runtime defaults.

---

## 3. AUTHORITATIVE DATA FLOW ARCHITECTURE

```
+-----------------------------------+        +-----------------------------------+
|     Deployment Configuration      |        |   Authorized Operational Input    |
|   (Prototype / Default Source)    |        |    (Future Real-Station Source)   |
+-----------------+-----------------+        +-----------------+-----------------+
                  |                                            |
                  | configured T_required                      | operational T_required
                  v                                            v
     +-------------------------------------------------------------------+
     |                       T_required Resolver                         |
     |                                                                   |
     |   Evaluates configured baseline + operational override input      |
     |   Outputs single resolved T_required to Emergency Detector        |
     +----------------------------------+--------------------------------+
                                        |
                                        | resolved T_required
                                        v
     +-------------------------------------------------------------------+
     |                    Emergency Condition Detector                   |
     |                                                                   |
     |   Evaluates station fuel & battery survivability over T_required  |
     |   Under stress scenario: P_solar = 0, P_wind = 0 (HD-04 Option A) |
     +----------------------------------+--------------------------------+
                                        |
                                        | NORMAL / EMERGENCY Mode Flag
                                        v
     +-------------------------------------------------------------------+
     |                              EMS / MPC                            |
     +-------------------------------------------------------------------+
```

---

## 4. CRITICAL SEMANTIC SEPARATIONS

To prevent architectural regression or scope drift, the following boundaries are strictly enforced:

1. **$T_{\text{required}}$ vs. EBR Interval ($N = 6\text{h}$, HD-01B)**:
   - $N = 6\text{h}$ is a fixed, separately governed **NORMAL-operation** battery buffer interval.
   - $T_{\text{required}}$ is the **OPERATIONAL SURVIVAL WINDOW** used strictly by the Emergency Condition Detector.
2. **$T_{\text{required}}$ vs. MPC Horizon ($H = 24\text{h}$)**:
   - $H = 24\text{h}$ is the rolling optimization horizon used by MPC MILP solver.
   - $T_{\text{required}}$ is independent of $H$ and represents mission-level resupply/recovery time.
3. **No Proxy Substitutions**:
   - $T_{\text{required}}$ is **NOT** derived from battery capacity, diesel fuel volume, generator minimum runtime ($2\text{h}$), UPS hold-up ($15\text{m}$), or provisional resupply cycles ($30\text{d}$).
4. **Prototype vs. Real Station**:
   - **Prototype**: Configured deployment value provides $T_{\text{required}}$; no real-time operational provider exists.
   - **Future Real Station**: Configured baseline supplemented by authorized operational input when online and valid.

---

## 5. PRESERVED GOVERNANCE BASELINE

All prior POLARIS EMS governance decisions remain fully preserved and unaltered:

- **HD-01A**: `EBR = CRITICAL_LOAD_BASED_DYNAMIC`
- **HD-01B**: `N = 6 HOURS` (Fixed normal-operation resilience interval)
- **HD-02**: `E_terminal_target = E_EBR_target(H)` (Terminal shortfall counted exactly once)
- **HD-04**: Option A Zero-Renewable Emergency Survivability Baseline ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$ in detector; normal MPC uses standard causal forecasts)
- **HD-05**: Normal extra-fuel tolerance $\le 5\%$ ($F_{\text{diesel}} \le 1.05 \cdot F_{\text{diesel}}^*$); Emergency battery degradation subordinate to critical service
- **Policy E3**: Dynamic preservation of resource with larger survivability margin during emergency mode

---

## 6. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

| Governance Key | Authoritative Classification | Notes / Scope |
| :--- | :--- | :--- |
| `HD03_SOURCE_MODEL` | `C_PLUS_A` | Configured default + Operational override |
| `HD03_DEPLOYMENT_CONFIG_SOURCE` | `CLOSED` | Prototype baseline source closed |
| `HD03_OPERATIONAL_SOURCE_EXTENSION` | `CLOSED` | Future operational extension closed |
| `HD03_NUMERICAL_VALUE` | `NOT_ESTABLISHED` | Numerical hours unresolved |
| `HD03_MISSING_INPUT_BEHAVIOR` | `GOVERNANCE_REQUIRED` | Missing input policy open |
| `HD03_OVERRIDE_PRECEDENCE` | `GOVERNANCE_REQUIRED` | Precedence rule open |
| `HD03_VALIDITY_RULE` | `GOVERNANCE_REQUIRED` | Input validity criteria open |
| `HD03_FRESHNESS_RULE` | `GOVERNANCE_REQUIRED` | Staleness threshold open |
| `HD03_CONFLICT_RULE` | `GOVERNANCE_REQUIRED` | Disagreement resolution open |
| `HD03_DETECTOR_OWNERSHIP` | `CONSUMER_ONLY` | Detector consumes resolved value only |
| `HD03_IMPLEMENTATION_AUTHORIZATION` | `NOT_GRANTED` | Code modification prohibited |
| `HD03_EXECUTION_AUTHORIZATION` | `NOT_GRANTED` | Simulation execution prohibited |
