# POLARIS STAGE 8.21A — PRE-RUN GOVERNANCE CHECKLIST REPORT

## 1. Governance Checklist Verification Table

| Item # | Audit Governance Requirement | Verification Status | Notes / Evidence |
|---|---|---|---|
| **1** | $47 \times 47$ spatial extraction window locked | **`PASS / VERIFIED`** | $57.5\text{ km}$ cardinal radius, $81.32\text{ km}$ corner radius |
| **2** | Solar elevation $\ge 5.0^\circ$ domain scope locked | **`PASS / VERIFIED`** | $\theta_z \le 85.0^\circ$ feature domain boundary |
| **3** | $\ge 99.0\%$ coverage criterion satisfied | **`PASS / VERIFIED`** | $99.30\%$ empirically verified ($3,262 / 3,285$ rays) |
| **4** | Deterministic outside-window fallback locked | **`PASS / VERIFIED`** | $23$ rays ($0.70\%$) fallback to station 1D vertical column |
| **5** | F4 hydrostatic height reconstruction locked | **`PASS / VERIFIED`** | Hypsometric $z(p)$ upward integration algorithm |
| **6** | F6 microphysics parameter assumptions locked | **`PASS / VERIFIED`** | $r_{e,\text{liq}} = 10\,\mu\text{m}$, $r_{e,\text{ice}} = 30\,\mu\text{m}$ parameterized constants |
| **7** | Incremental addition to Stage 8.1 baseline | **`PASS / VERIFIED`** | 37 baseline features $+ 4$ candidate features $= 41$ total |
| **8** | EVEN/ODD split locked | **`PASS / VERIFIED`** | 173 EVEN train / 174 ODD test origins |
| **9** | Governance Firewall: NO model training executed | **`PASS / VERIFIED`** | Zero model fits or gradient updates executed |
| **10** | Governance Firewall: NO ODD targets accessed | **`PASS / VERIFIED`** | Zero target values or test metrics accessed |
| **11** | Operational champion & master handoff untouched | **`PASS / VERIFIED`** | Champion, handoff, and route registry files un-mutated |

---

## 2. Pre-Run Governance Verdict

**PRE-RUN VALIDATION VERDICT:** **ALL 11 GOVERNANCE CHECKS PASSED**. Stage 8.21A Experiment Specification is frozen and ready for implementation.
