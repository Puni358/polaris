# Operating Mode Semantics & Multi-Objective Priority Interaction

## 1. Operating Mode Architecture & Boundary Separation

Under POLARIS EMS governance:
1. **Emergency Condition Detector (ECD)**: An external, deterministic detection module evaluates real-time grid availability, fuel reserves, and hardware alarms to establish the station operating mode ($\text{MODE} \in \{\text{NORMAL}, \text{EMERGENCY}\}$).
2. **Optimizer Role**: The optimizer NEVER decides the operating mode. It receives `operating_mode` as an input parameter in `StationState` or `config`.

---

## 2. Governed Operating Mode Semantics

### 2.1 NORMAL Mode Semantics
- **Objective Priority**: Standard economic dispatch under lexicographic hierarchy $J_1 \succ J_2 \succ J_3 \succ J_4$.
- **Battery Life Preservation**: In Stage 3 ($J_3$) and Stage 4 ($J_4$), battery degradation penalties and charge/discharge cycling limits prevent unnecessary battery wear when solar/grid resources are adequate.
- **Reserve Maintenance**: The optimizer enforces Stage 2 reserve shortfall penalties ($s_{J2}[t]$) to maintain the governed 6-hour EBR buffer ($E_{\text{stage2,target}}[t]$) in preparation for potential grid outages.

### 2.2 EMERGENCY Mode Semantics
- **Objective Priority**: Critical load service ($J_1$) dominates strictly.
- **Battery Usage Flexibility**: Stored battery energy MAY be discharged down to physical minimum floor $E_{\text{min}}$ whenever necessary to keep critical load shedding $J_1 = 0$.
- **No Hardcoded Priority**: There is NO hardcoded permanent priority of battery over diesel or diesel over battery during an emergency. The optimizer dispatches whichever asset minimizes Stage 1 shedding first, and then Stage 2 reserve deficit and Stage 3 fuel consumption lexicographically.

---

## 3. Mathematical Interaction with Lexicographic Objectives

The HiGHS native multi-objective priority ordering ($J_1 > J_2 > J_3 > J_4$) holds **IDENTICALLY in both NORMAL and EMERGENCY modes**:

- In **NORMAL Mode**: $J_1^* = 0$ (critical demand is met). The optimizer then minimizes $J_2$ (reserve shortfall) and $J_3$ (fuel).
- In **EMERGENCY Mode**: If generation is insufficient, Stage 1 ($J_1$) forces the optimizer to discharge battery energy below $E_{\text{stage2,target}}[t]$ (incurring $J_2 > 0$) because $J_1$ strictly dominates $J_2$.

### Layer D Emergency Constraints (Option D Reference)
In `gap19_highs_native.py` (lines 255-263):
If `operating_mode == "EMERGENCY"`, Layer D adds 24 critical-only discharge constraints ($P_{\text{dis}}[t] \le P_{\text{served}}[t]$) to prevent battery discharge from serving non-critical loads during an active emergency.

---

## 4. Mode Semantics Compliance Verdict

```text
ECD_MODE_AUTHORITY = PRESERVED
OPTIMIZER_MODE_ROLE = PASSIVE_RECIPIENT
BATTERY_VS_DIESEL_HARDCODING = ABSENT (ZERO HARDCODED PRIORITY)
LEXICOGRAPHIC_MODE_STABILITY = VERIFIED
```
