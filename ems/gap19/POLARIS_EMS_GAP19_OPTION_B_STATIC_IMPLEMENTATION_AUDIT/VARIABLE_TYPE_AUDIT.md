# Variable Type Audit

Static inspection of integrality vector `integrality`:

- **Binary Variables ($96$ total)**: Indices `base + 11` ($u_{\text{chg}}$), `base + 12` ($u_{\text{dis}}$), `base + 13` ($u_{\text{diesel}}$), `base + 14` ($v_{\text{start}}$) for each timestep $t=0..23$. Total $= 4 \times 24 = 96$.
- **Continuous Variables ($313$ total)**: All remaining 264 base variables, plus 24 $P_{\text{unmet,critical}}$, 24 $s_{\text{EBR}}$, and 1 $s_{\text{terminal}}$. Total $= 264 + 24 + 24 + 1 = 313$.
- **$w_{\text{stop}}$ Absence**: Zero $w_{\text{stop}}$ binary variables exist in the codebase.

`VARIABLE_TYPES = PASS`
