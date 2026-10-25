# POLARIS EMS GAP19 — OPEN DECISION AND BLOCKER REGISTER

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`  

---

## 1. Status of Governance Decisions

```text
NEW_GOVERNANCE_DECISION_REQUIRED = NO
```

### Explanation:
Human governance policy decisions **D1 through D4** and **DEC-004 (Option D)** are **SELECTED AND SEALED**. No new policy decision is required from human governance at this stage.

---

## 2. Partitioned Register of Open Items

| Item ID | Item Category | Item Description | Status | Active Dependency / Blocker |
| :--- | :--- | :--- | :---: | :--- |
| **DEC-D1** | `ALREADY_SEALED` | $J2$ reserve semantics = HYBRID / MODE-DEPENDENT. | `SEALED` | None. Policy sealed. |
| **DEC-D2** | `ALREADY_SEALED` | $s_{\text{J2}}$ policy = GOVERNED MAXIMUM SHORTFALL. | `SEALED` | None. Policy sealed. |
| **DEC-D3** | `ALREADY_SEALED` | ECD = SOLE EMERGENCY AUTHORITY. | `SEALED` | None. Policy sealed. |
| **DEC-D4** | `ALREADY_SEALED` | MILP INFEASIBLE $\to$ ECD ASSESSMENT. | `SEALED` | None. Policy sealed. |
| **DEC-004** | `ALREADY_SEALED` | Option D Protected Critical-Load Fallback. | `SEALED` | None. Policy sealed. |
| **ENG-01** | `ENGINEERING_INPUT_REQUIRED` | Derivation of numerical $s_{\text{J2,max}}$ bound. | `PARTIALLY_RESOLVED` | Blocked by missing station $P_{\text{critical}}(t)$ & BESS specs. |
| **ENG-02** | `ENGINEERING_INPUT_REQUIRED` | Data inventory for reserve calculation. | `ESTABLISHED` | Data categories cataloged; data acquisition blocked. |
| **BLK-01** | `DATA_BLOCKED` | Missing measured site electrical demand. | `DATA_BLOCKED` | Custodian dataset delivery required. |
| **BLK-02** | `DATA_BLOCKED` | Missing Nuolja BESS hardware spec sheet. | `DATA_BLOCKED` | BESS site hardware survey required. |
| **BLK-03** | `DATA_BLOCKED` | Missing diesel generator engine fuel curve. | `DATA_BLOCKED` | Engine bench test report required. |
| **BLK-04** | `DATA_BLOCKED` | Missing fuel tank calibration & resupply SLA. | `DATA_BLOCKED` | Tank inspection & logistics contract required. |
