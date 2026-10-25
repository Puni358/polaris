# Required Human Governance Decisions

The human stakeholder must explicitly decide the following policy questions:

### Emergency Battery Reserve (EBR)
- **DEC-EBR-01:** What is the operational purpose of EBR (hardware health floor vs. emergency survivability buffer)?
- **DEC-EBR-02:** Should EBR be fixed (Wh/SOC%) or dynamic (coupled to 6h critical load forecast)?
- **DEC-EBR-03:** What physical quantity and unit defines EBR?
- **DEC-EBR-04:** How does EBR behave in `NORMAL` vs. `EMERGENCY` operating modes?
- **DEC-EBR-05:** Is EBR a hard mathematical constraint or a lexicographic objective ($J_2$)?

### Terminal Reserve
- **DEC-TR-01:** Is Terminal Reserve conceptually distinct from EBR, or is it redundant?
- **DEC-TR-02:** What operational boundary condition does Terminal Reserve protect at $t = 24\text{h}$?
- **DEC-TR-03:** What physical quantity and unit defines Terminal Reserve?
- **DEC-TR-04:** Is Terminal Reserve fixed or dynamic?
- **DEC-TR-05:** Is Terminal Reserve a hard constraint or a lexicographic objective ($J_2$)?

### Overlap & Numerical Authorization
- **DEC-RES-01:** How do EBR and Terminal Reserve interact with the authorized $T_{\text{REQUIRED}} = 6\text{h}$ baseline?
- **DEC-RES-02:** How should the formulation eliminate double-counting between technical minimum SOC, EBR, and terminal reserve?
- **DEC-RES-03:** What specific numerical values (if any) are authorized for production deployment?
