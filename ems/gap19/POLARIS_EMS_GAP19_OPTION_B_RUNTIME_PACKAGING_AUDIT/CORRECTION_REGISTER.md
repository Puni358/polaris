# Correction Register & Environment Table

## Component Comparison

| Component | Main POLARIS `.venv` | Validated A/B Env | Required Target | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Python** | 3.12.3 | 3.12.3 | 3.12.3 | **MATCH** |
| **SciPy** | 1.18.1 | 1.18.1 | 1.18.1 | **MATCH** |
| **NumPy** | 2.5.2 | 2.5.2 | 2.5.2 | **MATCH** |
| **highspy** | NOT INSTALLED | 1.15.1 | 1.15.1 | **PROPOSED ADDITION** |
| **Native HiGHS** | 1.12.0 (SciPy) | 1.15.1 (highspy) | 1.15.1 | **MATCH** |
| **OS** | Linux | Linux | Linux | **MATCH** |
| **Architecture** | x86_64 | x86_64 | x86_64 | **MATCH** |

## Required Packaging Changeset

```text
PACKAGING_CHANGE = PROPOSED_ONLY
TARGET_FILE = requirements.txt / pyproject.toml
ADDITION = highspy==1.15.1
```
