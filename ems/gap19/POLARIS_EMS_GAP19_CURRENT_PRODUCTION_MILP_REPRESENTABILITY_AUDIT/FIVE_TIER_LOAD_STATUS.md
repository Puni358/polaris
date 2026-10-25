# FIVE TIER LOAD STATUS

## FIVE-TIER LOAD STRUCTURE REPRESENTABILITY AUDIT

- **Governed Concept**: 5-tier load classification (Tier 1 Protected Critical $\to$ Tier 5 Non-essential).
- **Current Production Implementation**: Single total demand variable `p_demand` plus a single boolean flexible load `p_flex`.
- **Finding**: Current production `milp.py` cannot distinguish 5 load tiers.

```text
FIVE_TIER_LOAD_REPRESENTATION = REQUIRES_ADDITIVE_MODEL_EXTENSION
```
