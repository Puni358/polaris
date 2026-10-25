# CANONICAL TARGET MODEL SPECIFICATION

## FOUR-LAYER CANONICAL TARGET MILP ARCHITECTURE

The canonical target MILP extends the base 360-variable model into four distinct mathematical layers:

1. **LAYER A (Physical Control & State Variables)**:
   - Retains 360 base variables ($P_{\text{pv,use}}, P_{\text{pv,curt}}, P_{\text{wind,use}}, P_{\text{wind,curt}}, P_{\text{batt,ch}}, P_{\text{batt,dis}}, E_{\text{batt}}, P_{\text{diesel}}, P_{\text{served}}, P_{\text{unmet}}, P_{\text{flex}}, u_{\text{ch}}, u_{\text{dis}}, u_{\text{diesel}}, v_{\text{start}}$).
   - Adds $24 \times w_{\text{stop}}(t)$ shutdown transition binaries to complete diesel status transition dynamics ($u_{\text{diesel}}(t) - u_{\text{diesel}}(t-1) - v_{\text{start}}(t) + w_{\text{stop}}(t) = 0$).
2. **LAYER B (Load Hierarchy & Critical Load Variables)**:
   - Adds $24 \times P_{\text{unmet,crit}}(t)$ continuous variables for protected critical load deficit.
   - Accepts dynamic critical load demand trajectory $P_{\text{demand,crit}}[t]$ from external inputs.
3. **LAYER C (Reserve & Objective Auxiliary Variables)**:
   - Adds $24 \times s_{\text{EBR}}(t) \ge 0$ continuous slacks for Emergency Battery Reserve shortfall.
   - Adds $1 \times s_{\text{term}} \ge 0$ continuous slack for Terminal Energy Reserve shortfall.
4. **LAYER D (Operating Mode & Option-D Policy Constraints)**:
   - Receives external operating mode parameter $\text{mode} \in \{\text{NORMAL}, \text{EMERGENCY}, \text{UNKNOWN\_INVALID}\}$.
   - Enforces proportional protected critical load allocation ($\alpha(t)$) during power deficits.
   - Restricts battery discharge to protected critical loads in EMERGENCY mode.
