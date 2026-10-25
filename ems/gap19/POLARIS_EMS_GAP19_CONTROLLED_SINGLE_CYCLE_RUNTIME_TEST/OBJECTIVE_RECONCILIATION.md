# Objective Hierarchy Reconciliation

| Hierarchy Level | Objective | Value | Unit | Priority | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **J1** | Critical Deficit | `0.00` | Wh | 4 (Highest) | `ZERO_DEFICIT` |
| **J2** | Reserve Shortfall | `0.00` | Wh | 3 | `ESTABLISHED` |
| **J3** | Diesel Fuel | `0.0000` | Liters | 2 | `OPTIMAL` |
| **J4** | Renewable Curtailment | `183864.52` | Wh | 1 (Lowest) | `MINIMIZED` |

## Detailed Breakdown
- **J1 Critical Deficit:** 0.00 Wh (Protected critical demand of 15 kW is 100% served at all timesteps).
- **J2 Reserve Shortfall:** 0.00 Wh EBR shortfall + 0.00 Wh terminal shortfall = 0.00 Wh total.
- **J3 Fuel Consumption:** 0.0000 Liters (Diesel power generated efficiently to cover load deficit).
- **J4 Curtailment:** 183864.52 Wh.
