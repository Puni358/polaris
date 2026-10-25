# OPTION D REPRESENTABILITY AUDIT

## OPTION D (PROTECTED CRITICAL LOAD FALLBACK) REPRESENTABILITY

- **Sealed Option D Requirements**:
  1. Protected critical load proportional allocation during power deficit ($P_{i,\text{served}} = \alpha P_{i,\text{min}}$).
  2. Renewable-first dispatch constraint.
  3. Battery critical-only discharge mode (SOC $\le$ threshold).
  4. Excess diesel charging battery.
- **Current Production MILP Status**:
  - `milp.py` contains no variables for individual protected critical load sub-systems.
  - `milp.py` contains no mode binaries or constraints for battery critical-only discharge.

```text
OPTION_D_MODEL_EXTENSION_REQUIRED = YES
```
