# Controlled 8-Cycle Rolling-MPC Test Specification

## 1. Test Objectives & Scope

The purpose of this test is to validate the receding-horizon control loop mechanics of the governed J2 Option-B optimizer (`GAP19HighsNativeOptimizer`) across 8 consecutive hourly control cycles.

Specifically, it verifies:
1. Receding-horizon state propagation ($S_{n+1} = f(S_n, a_{n, 0})$).
2. Fresh 24-hour forecast generation at each hourly observation origin.
3. Timestamp advancement & calendar midnight crossing (2024-01-01 23:00 to 2024-01-02 00:00).
4. Rolling EBR 6-hour lookahead window movement.
5. Rolling terminal reserve boundary movement ($t=23$ of each cycle).
6. Objective hierarchy $J_1 \succ J_2 \succ J_3 \succ J_4$ with `blend_multi_objectives = False`.
7. First-action-only commitment (committing timestep 0 action, discarding timesteps 1..23).

---

## 2. Test Execution Schedule

| Cycle | Origin Timestamp (UTC) | Horizon Window (24h) | Committed Action Timestep | Midnight Crossing |
| :---: | :---: | :---: | :---: | :---: |
| **Cycle 1** | `2024-01-01T20:00:00Z` | `2024-01-01T20:00:00Z` to `2024-01-02T19:00:00Z` | $t = 0$ (20:00) | No |
| **Cycle 2** | `2024-01-01T21:00:00Z` | `2024-01-01T21:00:00Z` to `2024-01-02T20:00:00Z` | $t = 0$ (21:00) | No |
| **Cycle 3** | `2024-01-01T22:00:00Z` | `2024-01-01T22:00:00Z` to `2024-01-02T21:00:00Z` | $t = 0$ (22:00) | No |
| **Cycle 4** | `2024-01-01T23:00:00Z` | `2024-01-01T23:00:00Z` to `2024-01-02T22:00:00Z` | $t = 0$ (23:00) | **Pre-Crossing** |
| **Cycle 5** | `2024-01-02T00:00:00Z` | `2024-01-02T00:00:00Z` to `2024-01-03T23:00:00Z` | $t = 0$ (00:00) | **Post-Crossing** |
| **Cycle 6** | `2024-01-02T01:00:00Z` | `2024-01-02T01:00:00Z` to `2024-01-03T00:00:00Z` | $t = 0$ (01:00) | No |
| **Cycle 7** | `2024-01-02T02:00:00Z` | `2024-01-02T02:00:00Z` to `2024-01-03T01:00:00Z` | $t = 0$ (02:00) | No |
| **Cycle 8** | `2024-01-02T03:00:00Z` | `2024-01-02T03:00:00Z` to `2024-01-03T02:00:00Z` | $t = 0$ (03:00) | No |

---

## 3. Input Parameters (Labelled: `SYNTHETIC_ENGINEERING_TEST_VALUE`)

- **Battery**: Capacity $200,000\text{ Wh}$, Initial SOC $80.0\%$ ($160,000\text{ Wh}$), Min SOC $20\%$, Max SOC $95\%$, Max Charge/Discharge Power $50,000\text{ W}$, Charge/Discharge Efficiency $0.92$.
- **Diesel**: Min Power $10,000\text{ W}$, Max Power $100,000\text{ W}$, Base Fuel $5.0\text{ L/h}$, Marginal Fuel $0.00025\text{ L/Wh}$, Startup Fuel $2.0\text{ L}$.
- **Demand**: Constant $20,000\text{ W}$ total, constant $20,000\text{ W}$ critical.
- **Terminal Reserve Target**: $100,000.00\text{ Wh}$ (synthetic test value).
