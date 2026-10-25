# POLARIS EMS GATE-07 — ROLLING DIESEL FUEL STATE TRACE

## 1. Executive Summary
This artifact documents the multi-cycle rolling state trace of diesel fuel propagation across consecutive Model Predictive Control (MPC) cycles within the POLARIS Energy Management System (EMS) Digital Twin infrastructure.

## 2. Multi-Cycle Rolling Fuel Propagation Trace

| Cycle $k$ | Origin Timestamp (UTC) | State $k$ Fuel ($L$) | $k=0$ Action ($P_{\text{diesel}}$ kW) | Fuel Consumed ($L$) | Next State $k+1$ Fuel ($L$) | Route Selected | State Advanced |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2026-09-24T00:00:00Z | 100.0000 | 18.25 | 9.5625 | 90.4375 | NORMAL | TRUE |
| 1 | 2026-09-24T01:00:00Z | 90.4375 | 15.10 | 8.7750 | 81.6625 | NORMAL | TRUE |
| 2 | 2026-09-24T02:00:00Z | 81.6625 | 12.00 | 8.0000 | 73.6625 | NORMAL | TRUE |
| 3 | 2026-09-24T03:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 4 | 2026-09-24T04:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 5 | 2026-09-24T05:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 6 | 2026-09-24T06:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 7 | 2026-09-24T07:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 8 | 2026-09-24T08:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 9 | 2026-09-24T09:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 10 | 2026-09-24T10:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |
| 11 | 2026-09-24T11:00:00Z | 73.6625 | 0.00 | 0.0000 | 73.6625 | NORMAL | TRUE |

> [!NOTE]
> All initial values are derived from the synthetic H1.0 fixture and labeled as synthetic.

## 3. Propagation Verification Checklist
- **Initial Fuel State**: Established once at $k=0$ ($100.0000$ synthetic liters).
- **First-Action-Only ($k=0$) Execution**: Only committed first-action $P_{\text{diesel}}[0]$ is evaluated by `DigitalTwinSimulator.step()`. Forecast actions at $k=1..23$ are discarded without fuel consumption.
- **Monotonic Non-Increasing State**: Fuel decreases or remains constant across all consecutive steps. Zero silent resets or unexplained fuel increases occurred.
- **Deterministic Replay**: Bitwise identical fuel traces across repeated execution passes.
