# Controlled Digital-Twin 8-Cycle MPC Integration Test Specification (`TEST_SPECIFICATION.md`)

## 1. Test Objectives & Scope

The primary objective of this gate is to validate the receding-horizon control loop mechanics of the governed J2 Option-B optimizer (`GAP19HighsNativeOptimizer`) integrated with the existing physical `DigitalTwinSimulator` lifecycle across **exactly 8 consecutive hourly cycles**.

Specifically, this gate verifies:
1. Physical state-transition integration using `DigitalTwinSimulator.step()` instead of synthetic energy equations.
2. First-action-only MPC semantics ($a_{n,0}$ committed to simulator, $a_{n,1\dots 23}$ discarded).
3. 24-hour causal forecast bundle rolling at each hourly observation origin.
4. Governed 6-hour EBR lookahead window movement ($T_{\text{REQUIRED}} = 6\text{h}$).
5. Terminal reserve horizon boundary movement ($t=23$ boundary).
6. Calendar midnight crossing (`2024-01-01 23:00` to `2024-01-02 00:00`).
7. Objective priority hierarchy $J_1 \succ J_2 \succ J_3 \succ J_4$ with `blend_multi_objectives = False`.
8. Information firewall isolation between controller and simulator.

---

## 2. Test Execution Schedule

| Cycle | Origin Timestamp (UTC) | Horizon Window (24h) | Committed Action Timestep | State Propagation Source | Midnight Crossing |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Cycle 1** | `2024-01-01T20:00:00Z` | `20:00` to `19:00` next day | $t = 0$ (`20:00`) | `DigitalTwinSimulator` | No |
| **Cycle 2** | `2024-01-01T21:00:00Z` | `21:00` to `20:00` next day | $t = 0$ (`21:00`) | `DigitalTwinSimulator` | No |
| **Cycle 3** | `2024-01-01T22:00:00Z` | `22:00` to `21:00` next day | $t = 0$ (`22:00`) | `DigitalTwinSimulator` | No |
| **Cycle 4** | `2024-01-01T23:00:00Z` | `23:00` to `22:00` next day | $t = 0$ (`23:00`) | `DigitalTwinSimulator` | **Pre-Crossing** |
| **Cycle 5** | `2024-01-02T00:00:00Z` | `00:00` to `23:00` next day | $t = 0$ (`00:00`) | `DigitalTwinSimulator` | **Post-Crossing** |
| **Cycle 6** | `2024-01-02T01:00:00Z` | `01:00` to `00:00` next day | $t = 0$ (`01:00`) | `DigitalTwinSimulator` | No |
| **Cycle 7** | `2024-01-02T02:00:00Z` | `02:00` to `01:00` next day | $t = 0$ (`02:00`) | `DigitalTwinSimulator` | No |
| **Cycle 8** | `2024-01-02T03:00:00Z` | `03:00` to `02:00` next day | $t = 0$ (`03:00`) | `DigitalTwinSimulator` | No |

---

## 3. Synthetic Input Parameters (Labelled: `SYNTHETIC_ENGINEERING_TEST_VALUE`)

- **Battery**: Capacity $200,000\text{ Wh}$, Initial SOC $80.0\%$ ($160,000\text{ Wh}$), Min SOC $20.0\%$, Max SOC $95.0\%$, Max Power $50,000\text{ W}$, Charge/Discharge Efficiency $0.92$.
- **Diesel**: Min Power $10,000\text{ W}$, Max Power $100,000\text{ W}$, Base Fuel $5.0\text{ L/h}$, Marginal Fuel $0.00025\text{ L/Wh}$, Startup Fuel $2.0\text{ L}$.
- **Demand**: Constant $20,000\text{ W}$ total, constant $20,000\text{ W}$ critical.
- **Wind Generation**: Constant $5,000\text{ W}$.
- **Solar Generation**: Diurnal sine curve peaking at $15,000\text{ W}$ between 06:00 and 18:00 UTC.
- **Terminal Reserve Target**: $100,000.00\text{ Wh}$ (synthetic target value).

> [!NOTE]
> All values listed above are strictly classified as `SYNTHETIC_ENGINEERING_TEST_VALUE` and are not promoted to production policy.
