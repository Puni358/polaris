# Correction Register

| Audit Item | Expected | Actual | Status |
| :--- | :--- | :--- | :---: |
| **$J_1$ priority** | `4` | `4` | **PASS** |
| **$J_2$ priority** | `3` | `3` | **PASS** |
| **$J_3$ priority** | `2` | `2` | **PASS** |
| **$J_4$ priority** | `1` | `1` | **PASS** |
| **Effective order** | `J1>J2>J3>J4` | `J1>J2>J3>J4` | **PASS** |
| **Objective vectors** | unchanged | unchanged | **PASS** |
| **Objective weights** | unchanged | `1.0` | **PASS** |
| **Objective offsets** | unchanged | `0.0` | **PASS** |
| **Tolerances** | unchanged | `0.0` | **PASS** |
| **Blend mode** | `False` | `False` | **PASS** |
| **Variables** | `409` | `409` | **PASS** |
| **Constraints** | `313` | `313` | **PASS** |
| **Binary variables** | `96` | `96` | **PASS** |
| **Protected baseline** | unchanged | unchanged | **PASS** |
| **Option A** | unchanged | unchanged | **PASS** |
| **ECD** | unchanged | unchanged | **PASS** |
| **Option D** | unchanged | unchanged | **PASS** |
| **Schemas** | unchanged | unchanged | **PASS** |
| **Runtime version evidence** | reconciled | reconciled (`highspy` 1.15.1) | **PASS_WITH_QUALIFICATION** |
