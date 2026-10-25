# POLARIS EMS GATE-11 — FUEL ACCOUNTING AUDIT

## 1. Emergency Fuel Accounting Principles
Fuel consumption during Option D emergency operation follows the frozen physical formula:
$$\text{required\_fuel} = \left((\text{base\_fuel\_lph if } P_{\text{diesel}} > 0 \text{ else } 0.0) + (\text{marginal\_fuel\_lpwh} \times P_{\text{diesel}})\right) \times 1.0 \text{ h}$$

## 2. Audit Findings
- **First-Action-Only Execution**: Only committed first action $P_{\text{diesel}}[0]$ consumes fuel in `DigitalTwinSimulator.step()`.
- **Fuel Decrement**: Fuel level $F_{k+1}$ decreases monotonically according to actual executed diesel power $P_{\text{diesel}}[0]$.
- **No Unearned Fuel Reset**: Fuel never resets or increases without an explicit replenishment event.
- Status: **PASS**
