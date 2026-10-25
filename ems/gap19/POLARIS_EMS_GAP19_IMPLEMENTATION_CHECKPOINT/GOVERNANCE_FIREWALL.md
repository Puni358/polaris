# POLARIS GAP19 — Synthetic Values Governance Firewall

This document establishes the strict governance firewall separating synthetic engineering test fixtures from real-station operational policy.

## Synthetic Test Fixture Register

The following parameters in the codebase, test scripts, and scenario files are **SYNTHETIC ENGINEERING FIXTURES** created solely for closed-loop software unit and component testing:

1. **30 kW Prototype Critical Load**: Prototype synthetic demand floor scalar.
2. **15 / 10 / 5 kW Conceptual Protected Categories**: Synthetic test split values.
3. **72 h Prototype Survivability Test Horizon**: Synthetic long-horizon test scenario fixture.
4. **2 h ECD Logic Test Horizon**: Micro-horizon logic sanity test fixture.
5. **80% / 30% SOC Test Bands**: Synthetic battery state test bounds.
6. **50 L / 12.5 L Fuel Test Bands**: Synthetic fuel state test bounds.
7. **46 L Equal-Margin Test Value**: Synthetic tie-condition test fixture.
8. **Synthetic Generator Parameters**: Base 5.0 L/h and marginal 0.00025 L/Wh test parameters.
9. **Synthetic Solar / Wind Fixture Values**: Demo scenario environmental profiles.

## Hard Governance Firewall Rules

> [!CAUTION]
> **SYNTHETIC FIXTURE FIREWALL**:
> None of the synthetic engineering values listed above may ever be described or interpreted as:
> - Real Nuolja station measurements or site data;
> - Real station physical requirements;
> - POLARIS mission or operational policy;
> - Production deployment limits;
> - Validated station operational thresholds.

All real-station parameters remain `NOT_ESTABLISHED` pending actual station engineering data acquisition.
