# POLARIS EMS — OPEN PARAMETER REGISTER FOR OPTION D

## 1. Executive Summary

This register lists all parameters, thresholds, circuit mappings, and telemetry rules that remain unestablished and require explicit governance authorization or site engineering definition before Option D could be implemented or deployed.

---

## 2. Parameter Category Registers

### A. GOVERNANCE DECISIONS STILL REQUIRED
1. **DEC-004 Final Selection**: Formal human selection of the operational response to `UNKNOWN_INVALID` across Options A (Hold Plan), B (Zero Dispatch), C (Operator Trip), and D (Protected Critical Fallback).
2. **DEC-001 / BLK-006 Production $T_{\text{required}}$**: Production value and TTL for minimum survivability horizon.
3. **DEC-002 / BLK-007 Telemetry Max-Age**: Production maximum allowable age for SCADA telemetry payloads.
4. **DEC-003 / BLK-008 Ingress Cryptographic Scheme**: Production authentication and signature verification scheme.
5. **Option D Watchdog Duration ($T_{\text{max,degraded}}$)**: Maximum allowed time in degraded Option D before mandatory operator escalation.
6. **Minimum Fuel Reserve Floor ($F_{\text{reserve,min}}$)**: Minimum fuel reserve level triggering mandatory escalation.

### B. STATION ENGINEERING INPUTS REQUIRED
7. **Protected Critical Equipment Inventory**: Site-specific list of physical equipment belonging to Heating, Water, and Comms categories.
8. **Electrical Breaker / Panel Mapping**: Hardware mapping connecting physical load switches to critical categories.
9. **Dynamic Load Calculation Model ($P_{\text{critical}}(t)$)**: Thermal and operational functions defining required critical power under varying ambient conditions.
10. **Minimum Viable Operating Levels ($P_{\text{min,viable}}$)**: Minimum power threshold below which each critical system cannot safely operate.
11. **Inrush / Surge Current Tolerance**: Generator and battery surge capacity requirements for motor startup.
12. **Generator Turndown Ratio & Minimum Power ($P_{\text{D,min}}$)**: Site-specific continuous minimum loading limit for physical diesel generator.
13. **Generator Fuel Burn Curve**: Measured or nameplate fuel consumption curve ($F = f(P)$) for physical generator set.
14. **Battery Charge Acceptance Limit ($P_{\text{BC,max}}$)**: Maximum continuous active charge power allowable for battery bank.
15. **Battery Reserve Floor ($SOC_{\text{min}}$)**: Hard minimum SOC boundary for battery discharge.
16. **Battery Maximum SOC Ceiling ($SOC_{\text{max}}$)**: Hard maximum SOC boundary to halt charging.
17. **Battery Thermal Cutoff Limits**: Temperature thresholds for charge/discharge lockout.

### C. RUNTIME / TELEMETRY DEFINITIONS REQUIRED
18. **Telemetry Validity Rules for Degraded Mode**: Criteria determining whether battery/generator telemetry is sufficiently valid to permit charging/discharging during `UNKNOWN_INVALID`.
19. **Diesel Fault Detection Criteria**: Telemetry logic establishing when diesel is "unavailable" or "faulted".
20. **Excess Energy Absorption Acceptance Signal**: Real-time signal indicating whether battery BMS can accept excess diesel output.

### D. IMPLEMENTATION DEFINITIONS REQUIRED
21. **Critical Load Shedder Control Interface**: Software interface and hardware protocol for actuating load shed relays.
22. **DispatchPlan Metadata Schema Extensions**: Formal schema definition for `protected_critical_load_w` and `shed_noncritical_load_w`.
23. **FaultEvent Classification Extensions**: Standardized fault class codes for degraded mode logging.
24. **Runner State Handler Wiring**: Integration of Option D fallback logic into `PolarisLocalRunner`.

### E. PRODUCTION AUTHENTICATION & FRESHNESS DEFINITIONS REQUIRED
25. **SCADA Command Signature Verification**: Protocol for authenticating operator override commands clearing `UNKNOWN_INVALID`.
26. **Ingress Payload Freshness Window**: Maximum allowed time skew between SCADA timestamp and local runner clock.
27. **Operator Re-Authentication Deadline**: Periodic re-authentication requirement during prolonged degraded operation.
28. **Cryptographic Key Management Scheme**: Key rotation and revocation infrastructure for station telemetry payloads.

---

## 3. Register Summary

```text
TOTAL_OPEN_PARAMETERS_REGISTERED      = 28
GOVERNANCE_DECISIONS_REQUIRED         = 6
STATION_ENGINEERING_INPUTS_REQUIRED   = 11
RUNTIME_TELEMETRY_DEFINITIONS          = 3
IMPLEMENTATION_DEFINITIONS            = 4
PRODUCTION_AUTH_FRESHNESS_DEFINITIONS = 4
```

None of these parameters have been assumed or pre-filled. They remain open for future authorized engineering/governance input.

Status: `OPEN_PARAMETER_REGISTER_SEALED`
