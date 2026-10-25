# POLARIS EMS — ECD CORE IMPLEMENTATION

## 1. Executive Summary

This package documents the authorized core software implementation and isolated unit-test suite for the **Emergency Condition Detector (ECD)** within the POLARIS Energy Management System (EMS).

---

## 2. Source & Test File Locations

- **Core Module**: [`system/control/ecd.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py)
- **Unit Test Suite**: [`system/tests/test_ecd_core.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/tests/test_ecd_core.py)
- **Canonical Fixture**: [`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json)

---

## 3. Mathematical Principles & Governance

### 3.1 Usable AC Battery Energy
$$E_{\text{bat,avail,AC}} = \max\left(0, C_{\text{nominal}} \cdot \frac{\text{SOC} - \text{SOC}_{\text{min}}}{100}\right) \cdot \eta_{\text{dis}}$$

### 3.2 Generator Fuel Rate & Endurance
$$\dot{F} = \alpha + \beta P_{\text{crit}}$$
$$T_{\text{diesel}} = \frac{F_{\text{remaining}}}{\dot{F}}$$

### 3.3 Emergency Mode Classification
$$\text{operating\_mode} = \begin{cases}
\text{NORMAL}, & \text{if } M_{\text{battery}} \ge 0 \text{ AND } M_{\text{diesel}} \ge 0 \\
\text{EMERGENCY}, & \text{otherwise}
\end{cases}$$

---

## 4. Test Execution Instructions

Run the isolated test suite using pytest:
```bash
PYTHONPATH=. .venv/bin/pytest system/tests/test_ecd_core.py -v
```

All 7 test modules (5 canonical cases, fail-closed safety tests, boundary conditions, tie epsilon, trajectory integration, and 100-iteration determinism) pass cleanly.

Status: `PASS`
