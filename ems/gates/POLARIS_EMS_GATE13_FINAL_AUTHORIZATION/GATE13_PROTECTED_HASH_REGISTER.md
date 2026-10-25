# POLARIS EMS GATE-13 — PROTECTED HASH REGISTER

## 1. Register Overview
This register records the exact SHA256 checksums of all protected core system implementations and governance manifests immediately prior to final campaign pre-flight clearance.

## 2. Authoritative Protected System Hashes

| Component / Module | Relative System Path | SHA256 Checksum | Protection Status |
| :--- | :--- | :--- | :---: |
| **Option B Solver** | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | **PROTECTED / FROZEN** |
| **Option D Solver** | `system/optimization/implementations/option_d.py` | `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12` | **PROTECTED / FROZEN** |
| **Emergency Detector** | `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | **PROTECTED / FROZEN** |
| **EMS Control Router** | `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` | **PROTECTED / FROZEN** |
| **Digital Twin Simulator**| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | **PROTECTED / FROZEN** |
| **Orchestration Runner** | `system/runtime/runner.py` | `723635dad0b8e06ac579088252e2eab7959e1f2ef2cdf6eba59e5fa0dfacdf32` | **PROTECTED / FROZEN** |

> [!CAUTION]
> Any modification to the above files invalidates pre-flight clearance and automatically halts execution.
