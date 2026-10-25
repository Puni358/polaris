# D6 CHARGING CORRECTION

## 1. D6 DIESEL REQUIREMENT FIREWALL & CHARGE ALLOCATION

Governance DEC-004 D6 mandates two distinct rules:
1. "If diesel is already required for protected critical service and its minimum output creates excess: diesel excess $\to$ battery charging $\to$ curtailment only after battery cannot accept more."
2. **"Diesel must NOT be started solely to charge battery."**

---

## 2. D6 FIREWALL CONSTRAINT FORMULATION

To mathematically enforce that diesel MUST NOT be started solely to charge the battery:

### Critical Deficit Requirement Condition:
Diesel commitment ($u_{\text{diesel}}[t] \in \{0, 1\}$) is allowed to be $1$ ONLY IF protected critical demand cannot be fully satisfied by available renewables plus maximum battery discharge:

$$u_{\text{diesel}}[t] \le \text{M} \cdot \left(P_{\text{critical}}[t] - P_{\text{sol,gen}}[t] - P_{\text{wind,gen}}[t] - P_{\text{dis,max}}[t]\right)_+$$

Where $(x)_+ = \max(0, x)$.

If available renewables + battery discharge capacity $\ge P_{\text{critical}}[t]$, the right-hand side is $0$, forcing $u_{\text{diesel}}[t] = 0$.

This constraint acts as an absolute mathematical firewall preventing the optimizer from starting the diesel generator for battery charging when critical load can be met without diesel.
