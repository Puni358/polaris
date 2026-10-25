# CORRECTION REGISTER

## 1. MASTER CORRECTION REGISTER (C0 THROUGH C5 FINDINGS)

This register catalogs all 12 forensic corrections identified during the audit of `POLARIS_EMS_OPTION_D_IMPLEMENTATION_ARCHITECTURE_AUDIT/`.

---

## 2. DETAILED CORRECTION LOG

| ID | Severity | Original Claim | Repository / Governance Evidence | Problem Identified | Corrected Claim | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CORR-01** | **C3** (Governance) | D4 is $P_{i,\text{served}} = \alpha P_{i,\text{min}}$ | DEC-004 D4 text ("proportionally allocate") | Governance text does not uniquely select $P_{\text{min}}$ vs $P_{\text{req}}$ basis | `D4_FORMULATION_STATUS = GOVERNANCE_AMBIGUITY_REMAINS`. Needs decision between Form A & B | Log human decision requirement |
| **CORR-02** | **C1** (Math) | $P_{\text{ren,crit}} = \min(P_{\text{solar}}+P_{\text{wind}}, P_{\text{crit}})$ | Solar and wind are separate inputs | Scalar sum oversimplifies separate solar/wind assets | Decoupled variables $P_{\text{sol,crit}} + P_{\text{wind,crit}} = P_{\text{ren,crit}}$ | Update math formulation |
| **CORR-03** | **C1** (Math) | $0 \le P_{\text{dis}} \le P_{\text{critical}}$ forces battery to critical | Busbar balance allows battery leakage to flex load | Upper bound alone does not prevent battery flow to flex load | Omit $P_{\text{dis}}$ from flexible busbar equation $P_{\text{serv,flex}} = P_{\text{ren,flex}} + P_{\text{dies,flex}}$ | Update busbar constraints |
| **CORR-04** | **C1** (Math) | $P_{\text{excess}} = P_{\text{dies,min}} - P_{\text{crit,net}}$ | Diesel output can exceed $P_{\text{dies,min}}$ | Ignores total busbar excess when renewables are high | $P_{\text{excess}} = \max(0, P_{\text{ren}}+P_{\text{diesel}}-P_{\text{serv,crit}}-P_{\text{serv,flex}})$ | Update excess formulation |
| **CORR-05** | **C1** (Math) | MILP has $K_{\text{ext}} = 19$ vars/timestep | `milp.py` has 15 vars; Option D needs split load vectors | 19 vars creates ambiguous busbar balances | **$K_{\text{ext}} = 21$ variables per timestep** (504 total vars for 24h) | Update MILP variable table |
| **CORR-06** | **C0** (Wording) | `SafeStateFallbackRouter` is active | `runner.py` does not contain fallback router | Described proposed architecture as existing code | Mark as **`PROPOSED_IMPLEMENTATION_ARCHITECTURE`** | Correct wording in docs |
| **CORR-07** | **C0** (Wording) | ECD is wired into runner | `runner.py` does not call `ECD.evaluate()` | Described proposed wiring as active | Mark as **`NOT_ESTABLISHED_IN_CODE`** | Correct wording in docs |
| **CORR-08** | **C2** (Engineering) | 15kW / 10kW / 5kW are critical load values | Synthetic fixture CSV columns | Synthetic numbers promoted to production site facts | Mark strictly as **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | Quarantine synthetic values |
| **CORR-09** | **C2** (Engineering) | 6h / 50L escalation thresholds | Illustrative example values | Examples promoted to authorized engineering thresholds | Mark strictly as **`ILLUSTRATIVE_ONLY`** / **`NOT_AUTHORIZED`** | Quarantine examples |
| **CORR-10** | **C0** (Wording) | Recovery state machine is implemented | No recovery machine exists in `system/` | Described proposed state machine as existing code | Mark as **`PROPOSED_RECOVERY_ARCHITECTURE`** | Correct wording in docs |
| **CORR-11** | **C0** (Wording) | Schema extensions are implemented | Proposed fields absent from `system/schemas/` | Described proposed schema fields as existing code | Mark as **`PROPOSED_ADDITIVE_FIELD`** | Correct wording in docs |
| **CORR-12** | **C0** (Wording) | Architectural readiness equals coding authorization | Governance authorization process | Conflated design readiness with code authorization | Explicitly separate `ARCHITECTURAL_READINESS` from `IMPLEMENTATION_AUTHORIZATION` | Enforce firewall boundary |

---

## 3. SEVERITY CLASSIFICATION LEGEND
- **C0**: Documentation / wording clarification.
- **C1**: Mathematical formulation correction.
- **C2**: Engineering definition / quarantine required.
- **C3**: Governance ambiguity / decision required.
- **C4**: Architecture correction required.
- **C5**: Implementation blocker.
