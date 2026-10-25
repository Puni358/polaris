# First-Action-Only Commitment Audit Report

## 1. Receding Horizon Commitment Principles

In receding-horizon MPC, at each cycle $n$:
1. The optimizer solves a 24-hour horizon model, producing a planned dispatch $\boldsymbol{x}_{n}[0 \dots 23]$.
2. **ONLY** the first control action $\boldsymbol{x}_{n}[0]$ is committed to physical state propagation.
3. Planned actions for $t = 1 \dots 23$ are **DISCARDED**.
4. In cycle $n+1$, the optimizer receives the updated physical state $S_{n+1}$ resulting from $\boldsymbol{x}_{n}[0]$ and re-optimizes.

---

## 2. Forensic Commitment Trace Across All 8 Cycles

| Cycle | Committed Control Action ($t=0$) | Next Initial Energy ($E_{\text{next}}$) | Next Initial SOC | Discarded Planned Steps | Status |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | $P_{\text{chg}}=29,064.27\text{ W}, P_{\text{diesel}}=44,064.27\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **2** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **3** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **4** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **5** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **6** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **7** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |
| **8** | $P_{\text{chg}}=0\text{ W}, P_{\text{diesel}}=15,000.00\text{ W}$ | $186,739.13\text{ Wh}$ | $93.37\%$ | Steps $1 \dots 23$ discarded | **RECEDING COMMITMENT** |

---

## 3. Verdict

```
FIRST_ACTION_ONLY_COMMITTED = YES
OPEN_LOOP_EXECUTION_REJECTED = YES
FIRST_ACTION_ONLY_AUDIT_STATUS = PASS
```
