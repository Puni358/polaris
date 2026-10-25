# Diesel Dynamics Audit (`DIESEL_DYNAMICS_AUDIT.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Controlled Digital-Twin 8-Cycle MPC Integration Test  
**VERDICT**: `PASS`

---

## 1. Audited Diesel Behavior

`DigitalTwinSimulator` updates diesel state via:
$$\text{diesel\_running} = (P_{\text{diesel}} > 0)$$
$$\text{diesel\_hours\_running}_{n+1} = (\text{diesel\_hours\_running}_n + 1.0) \quad \text{if diesel\_running else } 0.0$$

---

## 2. Per-Cycle Diesel Progression

| Cycle | $P_{\text{diesel}}$ (W) | Diesel Running | Diesel Hours | Min Power Limit (10 kW) | Max Power Limit (100 kW) | Audit Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 44064.27 | `True` | 1.0h | `PASS` | `PASS` | `PASS` |
| **2** | 15000.00 | `True` | 2.0h | `PASS` | `PASS` | `PASS` |
| **3** | 15000.00 | `True` | 3.0h | `PASS` | `PASS` | `PASS` |
| **4** | 15000.00 | `True` | 4.0h | `PASS` | `PASS` | `PASS` |
| **5** | 15000.00 | `True` | 5.0h | `PASS` | `PASS` | `PASS` |
| **6** | 15000.00 | `True` | 6.0h | `PASS` | `PASS` | `PASS` |
| **7** | 15000.00 | `True` | 7.0h | `PASS` | `PASS` | `PASS` |
| **8** | 15000.00 | `True` | 8.0h | `PASS` | `PASS` | `PASS` |

---

## 3. Diesel Audit Summary

- **Startup Event**: Occurred in Cycle 1 ($P_{\text{diesel}} = 44,064.27\text{ W}$).
- **Continuous Operation**: Generator ran in Cycles 2-8 at $15,000.0\text{ W}$ to maintain battery target.
- **Hours Counter**: Correctly incremented from $1.0\text{h}$ to $8.0\text{h}$.

```text
DIESEL_DYNAMICS = PASS
DIESEL_EXERCISED = YES
```
