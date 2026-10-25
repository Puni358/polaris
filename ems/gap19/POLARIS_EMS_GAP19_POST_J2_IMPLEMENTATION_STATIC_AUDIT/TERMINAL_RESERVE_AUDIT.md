# Terminal Reserve Formulation Static Audit

## 1. Boundary Application Verification

Independent inspection confirms:

1. **Horizon Boundary Coupling**: Terminal reserve requirement $E_{\text{term,target}}$ enters the model exclusively at the final decision step $t = 23$.
2. **Pointwise Maximum Envelope**:
   ```python
   e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)
   ```
   For $t \in [0, 22]$, $e\_stage2\_target[t] = ebr\_target\_wh\_list[t]$. Terminal reserve has zero impact on intermediate timesteps $t < 23$.
3. **No Double Counting**: Shortfall slack $s_{J2}[23]$ measures total shortfall against the single combined target $\max(E_{\text{EBR,target}}[23], E_{\text{term,target}})$. No separate terminal shortfall variable or duplicate penalty exists.

---

## 2. Policy Firewall & Input Ingestion

- `terminal_target_wh` is an explicit input passed via `station_state.terminal_target_wh_override` or `config["terminal_target_wh"]`.
- Terminal target is **NEVER** fixed to a hardcoded constant (`0 Wh`, `56k Wh`, or `160k Wh`).
- Absence of explicit input causes hard failure (`ValueError("MISSING_GOVERNED_INPUT...")`).

---

## 3. Verdict

```
TERMINAL_RESERVE_APPLIED_AT_BOUNDARY_ONLY = YES
DOUBLE_COUNTING_ELIMINATED = YES
FIXED_SOC_POLICY_INVENTED = NO
TERMINAL_RESERVE_AUDIT_STATUS = PASS
```
