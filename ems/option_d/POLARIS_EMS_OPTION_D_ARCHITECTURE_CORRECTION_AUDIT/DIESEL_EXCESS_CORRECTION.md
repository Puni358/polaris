# DIESEL EXCESS CORRECTION

## 1. TOTAL BUSBAR EXCESS GENERATION FORMULATION

The audit corrected the formula $P_{\text{excess}} = P_{\text{diesel,min}} - P_{\text{crit,net}}$ used in earlier documents.

---

## 2. FORMULATION CORRECTION

### Previous Oversimplification:
$$P_{\text{excess}}[t] = \max\left(0, P_{\text{diesel,min}} \cdot u_{\text{diesel}}[t] - P_{\text{crit,net}}[t]\right)$$
*Flaw*: Ignored that generator power $P_{\text{diesel}}[t]$ can exceed $P_{\text{diesel,min}}$, and ignored renewable contributions to noncritical busbar.

### Corrected Busbar Excess Generation Formulation:
Excess generation on the busbar occurs whenever total non-curtailed generation exceeds served critical demand plus served flexible demand:

$$P_{\text{excess}}[t] = \max\left(0, P_{\text{sol,gen}}[t] + P_{\text{wind,gen}}[t] + P_{\text{diesel}}[t] - P_{\text{served,crit}}[t] - P_{\text{served,flex}}[t]\right)$$

When diesel is committed ($u_{\text{diesel}}[t] = 1$) to support critical load and noncritical loads are shed ($P_{\text{served,flex}}[t] = 0$), excess generation simplifies to:

$$P_{\text{excess,dies}}[t] = \max\left(0, P_{\text{diesel}}[t] - \left(P_{\text{critical}}[t] - P_{\text{sol,crit}}[t] - P_{\text{wind,crit}}[t] - P_{\text{dis}}[t]\right)\right)$$

This exact formulation ensures that all generation above net critical requirement is captured for battery charging under DEC-004 D6.
