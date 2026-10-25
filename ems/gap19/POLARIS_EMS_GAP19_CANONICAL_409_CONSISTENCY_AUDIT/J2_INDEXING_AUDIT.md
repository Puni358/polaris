# J2 INDEXING AUDIT

## BATTERY ENERGY STATE INDEX ALIGNMENT FOR $J_2$

- **Battery Energy Decision Variables**: `E_next[t]` ($15t+6$) represents battery energy at the END of hour $t$.
  - `E_next[0]` ($t=0$): Energy state at end of hour 1.
  - `E_next[23]` ($t=23$): Energy state at end of hour 24 ($E(H)$).
- **Reserve Shortfall Alignment**:
  - Row $288+t$ connects `E_next[t]` and `s_EBR[t]` to $E_{\text{EBR\_target}}[t]$.
  - Row $312$ connects `E_next[23]` and `s_term` to $E_{\text{term\_target}}$.
- **Off-by-One Verification**: Verified exact 1-to-1 index matching for all 24 horizon steps. Zero boundary errors.
