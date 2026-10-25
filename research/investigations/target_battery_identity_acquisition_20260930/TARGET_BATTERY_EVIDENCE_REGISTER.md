# Target Battery Evidence Register

```yaml
PHASE_ID: target_battery_identity_acquisition_20260930
PREVIOUS_CAMPAIGNS: FROZEN
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Verified Evidence Register Table

| Source ID | Title / Document | Source Type | Evidence Tier | Acquired in Workspace? | Battery Identity Referenced | Provenance / Limitations |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **EVD-ID-01** | SITES Nuolja Station Documentation | Station Documentation | **Tier A (Target)** | NO (Desk Verified) | Meteorological field station instruments | Official SITES Portal. Confirms Nuolja is weather research site, not BESS. |
| **EVD-ID-02** | POLARIS Minimum Synthetic Fixture V1 | Synthetic Fixture | **Synthetic Proxy** | **YES** | Generic 200 kWh / 50 kW BESS Fixture | Repository root. Header states `real_nuolja_data: false`. |
| **EVD-ID-03** | Abisko Research Station Safety Rules | Station Safety Regulation | **Tier A (Target)** | NO (Desk Verified) | Lithium battery storage restriction ($\ge 10\text{ Ah}$) | Swedish Polar Research Secretariat portal. Safety rule only. |

---

## 2. Epistemic Provenance Evaluation

- **Tier A (Target System Evidence)**: Direct station documentation establishes that SITES Nuolja Middle Station is an environmental research monitoring site. No physical utility-scale battery energy storage system (BESS) is installed at the weather monitoring mast.
- **Synthetic Proxy**: The 200 kWh capacity and 50 kW power rating used in POLARIS originate strictly from `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json`, which is a synthetic engineering test fixture.
