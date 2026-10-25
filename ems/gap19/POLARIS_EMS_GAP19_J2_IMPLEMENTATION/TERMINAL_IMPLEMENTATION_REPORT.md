# Terminal Reserve Implementation Report

## 1. Technical Specification of Terminal Reserve Implementation

Terminal Reserve ($E_{\text{term,target}}$) represents the required end-of-horizon stored energy target at $t = 24\text{h}$ (end of timestep $t=23$, decision variable $E[24]$).

### 1.1 Ingestion of Terminal Reserve Engineering Inputs
In `gap19_highs_native.py`, $E_{\text{term,target}}$ is instantiated strictly from governed engineering inputs:
1. `station_state.terminal_target_wh_override` (if present).
2. `config["terminal_target_wh"]` (if present).
3. `config["terminal_reserve_model"] == "INITIAL_STATE"` $\implies E_{\text{term,target}} = E_{\text{bat}}[0]$ (`initial_e_wh`).
4. `config["terminal_reserve_model"] == "CAPACITY_RATIO"` $\implies E_{\text{term,target}} = E_{\text{min}} + \alpha_{\text{term}} (E_{\text{max}} - E_{\text{min}})$.

### 1.2 Strict Failure Mode for Absent Inputs
If no terminal reserve target or structural model input is specified:
- The solver raises an explicit exception:
  `ValueError("MISSING_GOVERNED_INPUT: Terminal reserve target (terminal_target_wh) is missing or unspecified.")`.
- **No silent substitution occurs**: The code does NOT silently substitute hardcoded 160,000 Wh, 56,000 Wh, zero, or arbitrary numbers.

---

## 2. Implementation Verification Verdict

```text
TERMINAL_INPUT_INGESTION = EXPLICIT
MISSING_INPUT_FALLBACK = REJECTED (RAISES EXPLICIT ERROR)
TERMINAL_TARGET_UNAUTHORIZATION_SAFETY = VERIFIED
TERMINAL_IMPLEMENTATION_STATUS = PASS
```
