# D4 NO CATEGORY PRIORITY

## 1. EQUAL PRIORITY ACROSS PROTECTED CRITICAL CATEGORIES

DEC-004 D4 explicitly mandates:
> "Do NOT invent a fixed priority such as heating > water > communications."

---

## 2. GOVERNANCE RULES AGAINST ARTIFICIAL PRIORITY
1. **No Hierarchical Priority Ranking**: No code, document, solver weight, or documentation structure may assert that Heating > Water > Comms or Comms > Water > Heating.
2. **Document Order Non-Binding**: The sequence in which load categories appear in text or JSON arrays is arbitrary and carries **ZERO** governance priority meaning.
3. **Numerical Value Priority Non-Binding**: Higher numerical minimum load values ($15$ kW vs $5$ kW) represent physical load size, NOT higher emergency priority.
4. **Equal Proportional Degradation**: All protected critical categories scale down by the exact same scalar ratio $\alpha(t) \in [0, 1)$ during power deficits.
