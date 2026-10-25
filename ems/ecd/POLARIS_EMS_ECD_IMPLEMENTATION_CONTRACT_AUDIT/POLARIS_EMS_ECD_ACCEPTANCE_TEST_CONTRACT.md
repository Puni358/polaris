# POLARIS EMS — ECD ACCEPTANCE TEST CONTRACT

## 1. Overview

This document specifies the mandatory acceptance test contract that any future implementation of the Emergency Condition Detector (ECD) must satisfy prior to deployment authorization.

---

## 2. Canonical Synthetic Fixture Reproduction Criteria

The implementation must achieve 100% exact reproduction of the 5 audited canonical test cases from `POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE` under $T_{\text{test}} = 2.0\text{ h}$ and $P_{\text{crit}} = 30,000\text{ W}$:

| Case | SOC (%) | Fuel (L) | Expected Mode | $T_{\text{battery}}$ (h) | $T_{\text{diesel}}$ (h) | $M_{\text{battery}}$ (h) | $M_{\text{diesel}}$ (h) | Preserved | Limiting | Tie? |
|------|---------|----------|---------------|--------------------------|-------------------------|-------------------------|------------------------|-----------|----------|------|
| **CASE 1** | 80.0 | 50.0 | `NORMAL` | 4.416000 | 4.303030 | +2.416000 | +2.303030 | `BATTERY` | `DIESEL` | False |
| **CASE 2** | 30.0 | 50.0 | `EMERGENCY` | 0.736000 | 4.303030 | -1.264000 | +2.303030 | `DIESEL` | `BATTERY` | False |
| **CASE 3** | 80.0 | 12.5 | `EMERGENCY` | 4.416000 | 1.075758 | +2.416000 | -0.924242 | `BATTERY` | `DIESEL` | False |
| **CASE 4** | 30.0 | 12.5 | `EMERGENCY` | 0.736000 | 1.075758 | -1.264000 | -0.924242 | `DIESEL` | `BATTERY` | False |
| **CASE 5** | 80.0 | 46.0 | `NORMAL` | 4.416000 | 4.416000 | +2.416000 | +2.416000 | `BOTH` | `BOTH` | True |

---

## 3. Mandatory Acceptance Requirements (A-L)

Future implementations MUST satisfy all of the following criteria:

- **Criterion A**: Canonical fixture reproduction without hardcoded expected outputs.
- **Criterion B**: Battery & diesel endurance equations verified against repository parameters ($\pm 10^{-6}$ float precision).
- **Criterion C**: E3 resource selection correctness (larger margin = preserved resource).
- **Criterion D**: Tie handling correctness ($M_{\text{battery}} == M_{\text{diesel}}$ produces `BOTH`, tie_status=True, preference=NONE).
- **Criterion E**: Invalid & missing input handling (fail-closed to `UNKNOWN_INVALID`).
- **Criterion F**: $T_{\text{required}}$ authority and freshness validation.
- **Criterion G**: Input provenance preservation in `EmergencyAssessment`.
- **Criterion H**: Zero policy mutation (ECD strictly outputs information, not actions).
- **Criterion I**: Zero optimizer mutation (ECD does not modify MILP model).
- **Criterion J**: Zero hidden station assumptions.
- **Criterion K**: 100% deterministic output for identical inputs.
- **Criterion L**: Fail-closed behavior where explicitly governed.

Status: `COMPLETE`
