# POLARIS EMS GAP19 — SYNTHETIC / PROXY FIREWALL

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Firewall Policy**: **STRICT PROHIBITION OF SYNTHETIC & PROXY PROMOTION**  

---

## 1. Explicit Firewall Rules

1. **PROHIBITION OF SYNTHETIC VALUE PROMOTION**:
   No synthetic engineering assumption ($30\text{ kW}$ load, $200\text{ kWh}$ battery, $100\text{ kW}$ diesel, $5\text{L/h}+0.25\text{L/kWh}$ fuel model) may be promoted to production station evidence simply because it appeared repeatedly in prototype tests or software scenarios.
   * `SYNTHETIC_VALUE_PROMOTION = NONE`

2. **PROHIBITION OF PROXY PROMOTION**:
   No regional proxy dataset or non-Nuolja research station publication (e.g. SANAE IV, Princess Elisabeth, Antarctic/Arctic regional proxies) may be promoted to `STATION_SPECIFIC_ESTABLISHED`.
   * `PROXY_PROMOTION = NONE`

3. **PRODUCTION BOUNDARY RESTRICTION**:
   If the only available data for an engineering quantity consists of generic specifications, regional proxies, or synthetic test fixtures, the production status MUST be declared:
   * `PRODUCTION_RESERVE_BOUND = NOT_ESTABLISHED`

---

## 2. Verification Statement

Zero synthetic values or regional proxies have been promoted to production evidence during this recovery audit pass.
