# CURRENT OBJECTIVE RECONSTRUCTION

## EXACT HISTORICAL SCALAR OBJECTIVE IN `milp.py`

In `system/optimization/implementations/milp.py` (Lines 107-114), the historical scalar objective function is:

$$\min \text{Cost} = \sum_{t=0}^{23} \left( c_2 p_{\text{curt\_sol}}(t) + c_3 p_{\text{curt\_wind}}(t) + c_4 p_{\text{chg}}(t) + c_5 p_{\text{dis}}(t) + c_7 p_{\text{diesel}}(t) + c_9 p_{\text{unmet}}(t) + c_{13} u_{\text{diesel}}(t) + c_{14} v_{\text{start}}(t) \right)$$

where:
- $c_2 = c_3 = \text{curt\_penalty\_per\_wh} \cdot \Delta t \cdot w_t$
- $c_4 = c_5 = \text{deg\_penalty} \cdot \Delta t \cdot w_t$
- $c_7 = \text{fuel\_cost\_per\_l} \cdot \text{marg\_fuel\_l\_wh} \cdot \Delta t \cdot w_t$
- $c_9 = \text{unmet\_penalty\_per\_wh} \cdot \Delta t$ (unweighted, $w_t=1.0$)
- $c_{13} = \text{fuel\_cost\_per\_l} \cdot \text{base\_fuel\_l\_h} \cdot \Delta t \cdot w_t$
- $c_{14} = \text{startup\_cost} \cdot w_t$

This is a single weighted scalar sum combining economic cost ($), reliability penalties ($), battery degradation ($), and curtailment penalties ($).
