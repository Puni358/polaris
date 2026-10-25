# POLARIS EMS — D1–D6 CONSISTENCY & INTERACTION AUDIT

## 1. Executive Summary

This document presents the detailed pairwise interaction audit evaluating human decisions **D1 through D6** for **Option D**. Each decision pair was audited for mathematical consistency, logical coupling, and semantic integrity.

---

## 2. Pairwise Interaction Audit Matrix

| Interaction Pair | Tested Governance Boundary | Audit Result | Forensic Verification Proof |
|------------------|----------------------------|--------------|-----------------------------|
| **D1 $\leftrightarrow$ D2** | Dynamic Load vs Battery Discharge | `PASS` | D1 defines dynamic power demand $P_{\text{critical}}(t)$ for protected equipment. D2 permits battery discharge *solely* for protected equipment when generation is deficient. Restricting battery discharge to equipment membership prevents optimizer redefinition while allowing dynamic power tracking. |
| **D1 $\leftrightarrow$ D4** | Dynamic Load vs Minimum Viable Levels | `PASS` | D1 establishes dynamic critical load. D4 defines minimum viable operating levels ($P_{\text{min,viable}}$) for protected equipment. If available power is insufficient for all minimum levels, proportional allocation scales power across protected equipment without dynamic equipment reclassification. |
| **D2 $\leftrightarrow$ D3** | Restricted Battery vs Zero Resource | `PASS` | D2 restricts battery discharge to protected equipment. D3 specifies that when renewables + diesel are 0, battery continues supporting protected equipment until operator resolution or resource boundary. D3 is a consistent extension of D2; zero noncritical load discharge is authorized in either state. |
| **D3 $\leftrightarrow$ D4** | Zero Resource vs Critical Shortfall | `PASS` | If battery is the sole source under D3 and cannot cover all minimum viable levels ($P_{\text{BD}} < \sum P_{\text{min,viable}}$), D4 proportional allocation applies immediately alongside mandatory D4 operator escalation. No logical contradiction exists. |
| **D4 $\leftrightarrow$ D5** | Shortfall vs Escalation Boundary | `PASS` | D4 requires immediate operator escalation upon critical load shortfall. D5 enforces mandatory escalation upon reaching time/resource limits. D4 immediate escalation and D5 boundary escalation coexist cleanly; D4 handles instantaneous resource deficits, while D5 handles prolonged degraded operation. |
| **D5 $\leftrightarrow$ D3** | Escalation vs Continued Battery Support | `PASS` | Reaching a D5 escalation boundary triggers mandatory operator alerts, but does *not* automatically force critical load disconnection. Battery support under D3 may continue if physically feasible within the governed resource boundary while awaiting operator response. |
| **D5 $\leftrightarrow$ D6** | Escalation vs Diesel Excess Charging | `PASS` | D6 authorizes battery charging from unavoidable diesel minimum excess *while diesel is required for critical load*. D5 limits maximum degraded duration/resource bounds. Reaching D5 escalation alerts the operator without violating D6 excess energy absorption physics. |
| **D6 $\leftrightarrow$ D2** | Excess Diesel Charging vs Restricted Discharge | `PASS` | D6 authorizes battery *charging* ($P_{\text{BC}}$) from unavoidable diesel minimum excess. D2 restricts battery *discharging* ($P_{\text{BD}}$) to protected critical loads. Charging and discharging are opposite energy directions; charging from excess diesel conserves energy without violating D2 discharge restrictions. |
| **D6 $\leftrightarrow$ D3** | Excess Diesel Charging vs Diesel Unavailability | `PASS` | D6 applies when diesel is running. D3 applies when diesel is unavailable. D6 and D3 represent mutually exclusive generation states; no operational overlap or contradiction occurs. |
| **D6 $\leftrightarrow$ D4** | Excess Diesel Charging vs Critical Shortfall | `PASS` | D6 applies when diesel minimum output creates *excess* power ($P_{\text{excess}} > 0$). D4 applies when available generation has a *deficit* ($P_{\text{supply}} < P_{\text{critical}}$). Excess power and supply deficit are mutually exclusive conditions. |
| **Option D $\leftrightarrow$ A/B/C** | Distinctness from Options A, B, C | `PASS` | Option D is distinct: Option A holds prior full plan; Option B forces 0 controllable dispatch; Option C halts MPC pipeline (`CRITICAL_TERMINATION`); Option D executes degraded critical-only fallback. Option D is mathematically and behaviorally distinct from A, B, and C. |

---

## 3. Key Interaction Proofs

### Proof 1: D6 Excess Charging Does Not Authorize Diesel-Only Charging
- *Premise*: Does D6 allow starting diesel solely to charge the battery?
- *Proof*: D6 explicitly conditions charging on: *"If diesel is ALREADY running because it is required to maintain protected critical load"*. If $P_{\text{RE}} \ge P_{\text{critical}}(t)$, diesel is NOT required and MUST NOT be started. Thus, diesel-only-for-charging is strictly prohibited.

### Proof 2: Escalation $\neq$ Automatic Shutdown
- *Premise*: Does reaching a D5 escalation boundary force immediate blacking out of critical loads?
- *Proof*: D5 establishes an *operator escalation boundary* (raising alarms, logging fault events, seeking human intervention). Critical load power support continues under D3/D4 rules as long as physical generation/battery capability permits. Escalation alerts humans; physical capability governs electrical continuity.

Status: `CONSISTENCY_AUDIT_PASS`
