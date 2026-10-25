# SYNTHETIC VS PRODUCTION CORRECTION

## 1. PRODUCTION vs SYNTHETIC VALUE FIREWALL

The audit systematically cataloged every numerical value appearing in fixture files or design documents and established its authoritative classification.

---

## 2. COMPREHENSIVE VALUE CLASSIFICATION MATRIX

| Numerical Value | Context / Usage | Authoritative Classification | Production Status |
| :--- | :--- | :--- | :--- |
| **$15.0$ kW** | Heating load in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$10.0$ kW** | Water load in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$5.0$ kW** | Comms load in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$30.0$ kW** | Total critical demand in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$15.0$ kW** | Flexible demand in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$45.0$ kW** | Total demand in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | NOT ESTABLISHED for real Nuolja site |
| **$60.0$ kW** | Generator rating in fixture | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | Config has $100.0$ kW default |
| **$50.0$ kW** | Battery max power in fixture/config| **`ENGINEERING_UNRESOLVED`** | Baseline config default |
| **$200.0$ kWh** | Battery capacity in fixture/config | **`ENGINEERING_UNRESOLVED`** | Baseline config default |
| **$500.0$ L / $20.0$ L** | Initial fuel in fixture scenarios | **`SYNTHETIC_ENGINEERING_FIXTURE_VALUE`** | Scenario initial values only |
| **$6.0$ HOURS** | $T_{\text{required}}$ survivability duration | **`SEALED_GOVERNANCE_VALUE`** | **SEALED GOVERNANCE** (DEC-004) |
| **$72.0$ HOURS** | Prototype test horizon | **`SYNTHETIC_ENGINEERING_TEST_VALUE`**| Synthetic test value only |
| **$6.0$h / $50.0$L** | Escalation threshold examples | **`ILLUSTRATIVE_ONLY`** | NOT AUTHORIZED |

---

## 3. GOVERNED FIREWALL STATEMENT
> **AUTHORITATIVE DIRECTIVE**: Zero synthetic fixture values ($15$ kW, $10$ kW, $5$ kW, $30$ kW, $60$ kW, $500$ L, $20$ L, $10$ L) may be cited as empirical Nuolja station facts or production site ratings.
