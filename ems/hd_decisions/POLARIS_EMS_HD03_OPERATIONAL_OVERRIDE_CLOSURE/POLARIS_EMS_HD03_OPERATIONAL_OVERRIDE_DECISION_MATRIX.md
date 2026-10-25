# POLARIS EMS — HD-03 CONFLICT RESOLUTION & PRECEDENCE MATRIX

## 1. COMPACT CONFLICT RESOLUTION TABLE

| Config ($T_{\text{config}}$) | Operational ($T_{\text{oper}}$) | Resolution Behavior | Precedence Rationale |
| :--- | :--- | :--- | :--- |
| **valid** | **absent** | `configured candidate` | Configured baseline available; no operational override present. |
| **valid** | **valid** | `operational wins` | Operational override selected over configured baseline ($T_{\text{oper}}$ wins). |
| **valid** | **invalid** | `configured candidate` | Invalid operational input rejected; configured baseline candidate remains. |
| **invalid** | **valid** | `operational candidate` | Invalid config ignored; valid operational candidate selected. |
| **invalid** | **absent** | `fail closed` | No valid candidate available; fails closed. |
| **absent** | **valid** | `operational candidate` | Operational candidate selected. |
| **absent** | **invalid** | `fail closed` | No valid candidate available; fails closed. |
| **absent** | **absent** | `fail closed` | No valid candidate available; fails closed. |
| **valid** | **stale** | `DEFERRED TO FRESHNESS POLICY` | Unresolved staleness transition; deferred to future Freshness Policy. |
| **operational previously valid, now unavailable** | `DEFERRED TO FRESHNESS POLICY` | Unresolved loss-of-signal transition; deferred to future Freshness Policy. |

---

## 2. PROHIBITED RESOLVER ACTIONS

Under `HD03_CONFLICT_RULE = CLOSED_OPERATIONAL_WINS`, the $T_{\text{required}}$ Resolver is **STRICTLY PROHIBITED** from:
1. Averaging $T_{\text{config}}$ and $T_{\text{oper}}$ (e.g. $\frac{30 + 24}{2} = 27\text{h}$).
2. Automatically selecting the minimum value without governance policy.
3. Automatically selecting the maximum value without governance policy.
4. Interpolating between configuration and operational streams.
5. Delegating precedence choice to the Emergency Condition Detector (`CONSUMER_ONLY`).
