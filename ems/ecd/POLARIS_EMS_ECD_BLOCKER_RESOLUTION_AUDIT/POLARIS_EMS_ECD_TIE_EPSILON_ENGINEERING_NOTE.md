# POLARIS EMS — FLOATING-POINT TIE EPSILON ENGINEERING NOTE (BLK-009)

## 1. Executive Summary

This engineering note establishes the resolution for **BLK-009** (Floating-Point Tie-Comparison Epsilon).

---

## 2. Numerical Context & Problem Definition

Under Case 5 of the canonical fixture ($SOC = 80.0\%, \text{Fuel} = 46.0\text{ L}$), the battery endurance $T_{\text{battery}}$ and diesel endurance $T_{\text{diesel}}$ are analytically equal to:

$$T_{\text{battery}} = 4.416000\text{ h}$$
$$T_{\text{diesel}} = 4.416000\text{ h}$$

Due to IEEE 754 floating-point arithmetic variations across Python runtime environments, strict binary equality (`M_battery == M_diesel`) may evaluate to `False` due to machine epsilon noise (e.g., `4.416000000000001` vs `4.416000000000000`).

---

## 3. Recommended Comparison Strategy

An absolute floating-point tolerance $\epsilon$ is established for tie detection:

$$\text{tie\_status} = |M_{\text{battery}} - M_{\text{diesel}}| \le \epsilon$$

Where:
$$\epsilon = 1.0 \times 10^{-6}\text{ hours} \quad (3.6\text{ milliseconds})$$

### Rationale:
1. **Precision**: $3.6\text{ ms}$ is orders of magnitude smaller than any operational control interval ($5\text{ min} - 1\text{ hour}$).
2. **Safety**: $3.6\text{ ms}$ will not falsely absorb meaningful physical fuel or battery energy differences (e.g., $1\text{ second}$ of $30\text{ kW}$ critical power is $8.33 \times 10^{-5}\text{ h}$).
3. **Determinism**: Ensures Case 5 strictly evaluates to `tie_status = True`, `preserved_resource = BOTH`, `limiting_resource = BOTH`.

---

## 4. Gating & Decision Summary

- **Classification**: `ENGINEERING_DEFINITION_REQUIRED` (Resolved herein).
- **Blocks Unit Implementation**: **NO**
- **Blocks Integration**: **NO**
- **Blocks Production Deployment**: **NO**

Status: `ENGINEERING_DEFINITION_COMPLETE`
