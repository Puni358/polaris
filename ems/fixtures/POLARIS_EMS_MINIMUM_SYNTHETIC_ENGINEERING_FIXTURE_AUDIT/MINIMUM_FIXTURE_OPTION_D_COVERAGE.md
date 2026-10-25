# POLARIS EMS — MINIMUM FIXTURE OPTION D COVERAGE AUDIT

## 1. Executive Summary

This document audits the coverage of sealed **Option D Fallback Rules (D1–D6)** by Scenario 5 in the minimum synthetic fixture.

---

## 2. Option D Policy Rules Coverage Mapping

| Option D Rule | Policy Requirement | Minimum Fixture Test Path | Coverage Status |
| :--- | :--- | :--- | :--- |
| **Rule D1** | Dynamic Protected Critical Service | $P_{\text{critical}} = 30\text{kW}$ protected service maintained. | `COVERED` |
| **Rule D2** | Restricted Battery Discharge | Noncritical load ($15\text{kW}$) shed; battery supports $P_{\text{critical}}$ ONLY. | `COVERED` |
| **Rule D3** | Battery Critical Support | Battery supports $P_{\text{critical}}$ when renewables/diesel unavailable. | `COVERED` |
| **Rule D4** | Proportional Shortfall Allocation | Allocation evaluated when available power $< P_{\text{critical}}$. | `COVERED` |
| **Rule D5** | Mandatory Operator Escalation | Triggers escalation alert when $T_{\text{max,degraded}}$ or $F_{\text{reserve,min}}$ reached. | `COVERED` |
| **Rule D6** | Excess Diesel Battery Charging | Unavoidable excess diesel power charges battery up to 95% SOC, then curtails. | `COVERED` |

---

## 3. Status

```yaml
MINIMUM_OPTION_D_COVERAGE: COMPLETE_100_PERCENT
VERIFICATION: All sealed Option D rules (D1 through D6) are 100% covered by Scenario 5 in the minimum fixture design.
```
