# POLARIS — Target Battery Parameter Matrix

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## Parameter Classification Matrix

| Parameter | Value | Unit | Evidence Tier | Status | Contradiction / Provenance |
|---|---|---|---|---|---|
| **Manufacturer** | NOT ESTABLISHED | N/A | NONE | NOT ESTABLISHED | Synthetic fixture leaves unassigned |
| **Model** | NOT ESTABLISHED | N/A | NONE | NOT ESTABLISHED | Synthetic fixture leaves unassigned |
| **Chemistry** | NOT ESTABLISHED | N/A | NONE | NOT ESTABLISHED | Generic literature assumes LFP/NMC |
| **Nominal Capacity** | NOT ESTABLISHED | kWh | TIER_SYNTHETIC | SYNTHETIC FIXTURE | Fixture specifies 200.0 kWh; site is weather station |
| **Usable Capacity** | NOT ESTABLISHED | kWh | TIER_SYNTHETIC | SYNTHETIC FIXTURE | Assumes 160.0 kWh usable (20–100% SOC) |
| **Continuous Power** | NOT ESTABLISHED | kW | TIER_SYNTHETIC | SYNTHETIC FIXTURE | Fixture specifies 50.0 kW |
| **Peak Power** | NOT ESTABLISHED | kW | NONE | NOT ESTABLISHED | Unspecified |
| **Efficiency (η_rt)** | NOT ESTABLISHED | % | TIER_SYNTHETIC | SYNTHETIC ASSUMPTION | Production uses 84.64% assumption |
| **SOC Minimum** | NOT ESTABLISHED | % | TIER_SYNTHETIC | SYNTHETIC ASSUMPTION | Production uses 20.0% safety reserve |
| **SOC Maximum** | NOT ESTABLISHED | % | TIER_SYNTHETIC | SYNTHETIC ASSUMPTION | Production uses 100.0% |
| **Operating Temperature** | NOT ESTABLISHED | °C | NONE | NOT ESTABLISHED | Ambient outdoor logged, cell temp log ABSENT |
| **BMS Interface** | NOT ESTABLISHED | N/A | NONE | VERIFIED ABSENT | Zero BMS logs present |
| **SOH Telemetry** | NOT ESTABLISHED | % | NONE | VERIFIED ABSENT | Zero capacity fade logs present |
| **Cycle Count** | NOT ESTABLISHED | cycles | NONE | VERIFIED ABSENT | Zero cycle counter logs present |
| **Cycle-Life Spec** | NOT ESTABLISHED | cycles | NONE | NOT ESTABLISHED | No OEM datasheet |
| **Replacement Cost** | NOT ESTABLISHED | $ | NONE | NOT IDENTIFIABLE | No procurement invoices |
| **Battery Lifetime** | NOT ESTABLISHED | years | NONE | NOT ESTABLISHED | Unspecified |
| **Degradation Cost** | NOT ESTABLISHED | $/kWh | TIER_SYNTHETIC | UNVALIDATED PROXY | Production uses $0.05/kWh linear proxy |

> [!IMPORTANT]
> All parameters listed as `NOT ESTABLISHED` must remain unassigned until direct Tier A target hardware evidence (e.g., official procurement invoice, OEM nameplate, or BMS telemetry stream) is acquired.
