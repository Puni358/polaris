# D3 BATTERY BOUNDARY CORRECTION

## Correction Summary: Production Battery Boundary vs Synthetic 20% Floor

This document establishes the formal correction for **Governance Decision D3 (Battery Discharge Boundary)** and enforces the **Battery Terminology Firewall**.

---

## 1. Identified Issue in Prior Package Draft

Prior package drafts stated:
> "Battery supports critical load until minimum SOC (20%)."

This wording was **TOO STRONG** and incorrectly promoted a synthetic benchmark fixture value into production governance.

---

## 2. Sealed Governance Semantics (D3)

The authoritative, corrected D3 governance semantics are:

> **D3 Rule**:
> If combined renewable generation and diesel generation are insufficient to supply protected critical load, remaining battery capability is used to maintain protected critical systems while awaiting operator decision.
> 
> **Termination Criteria**:
> Option D battery support continues until either:
> 1. The operator resolves the condition, OR
> 2. The governed battery discharge boundary is reached.

```text
PRODUCTION_OPTION_D_BATTERY_DISCHARGE_BOUNDARY = NOT_ESTABLISHED
```

---

## 3. Synthetic Benchmark Fixture Distinction

- The synthetic fixture specifies: $\text{SOC}_{\text{min}} = 20.0\%$ ($40\text{ kWh}$).
- Classification: `SYNTHETIC_ENGINEERING_FIXTURE_VALUE`.
- Firewall Rule: The 20% value is strictly an engineering benchmark parameter for synthetic testing. It is **NOT**:
  - The production Option-D battery discharge boundary.
  - A real Nuolja station battery requirement.
  - An authorized production emergency reserve.
  - A universal POLARIS battery policy.

---

## 4. Battery Terminology Firewall

To prevent semantic confusion across engineering and governance documents, four distinct battery concepts are established:

| Terminology | Definition | Governance / Engineering Status |
| :--- | :--- | :--- |
| **Technical SOC Floor** | Physical/model lower boundary ($\text{SOC}_{\text{min}} = 20\%$ in fixture). | Benchmark Fixture Parameter |
| **Governed Battery Discharge Boundary** | Policy boundary at which Option D halts automated discharge. | `NOT_ESTABLISHED` (Open Input) |
| **Emergency Battery Reserve (EBR)** | Stage 2 multi-objective optimization target. | `DEFERRED_TO_GAP19` |
| **Terminal SOC** | End-state energy target at horizon boundary $H$. | `DEFERRED_TO_GAP19` |

> [!CAUTION]
> **PROHIBITED EQUIVALENCES**:
> - Do **NOT** write `20% SOC = EBR`.
> - Do **NOT** write `20% SOC = Option-D production discharge boundary`.
> - Do **NOT** write `20% SOC = station emergency reserve`.
