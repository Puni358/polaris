# MODEL SOURCE AUDIT

## SOURCE MAPPING TO POLARIS IMPLEMENTATION

This audit traces every decision variable, bound, constraint, and objective in the frozen 385-variable test model back to the production POLARIS formulation defined in `system/optimization/implementations/milp.py`.

### 1. MODEL COMPONENT MAPPING TABLE

| Component | POLARIS Source File | Lines/Range | Formulation Variable/Equation | Units | Notes |
|---|---|---|---|---|---|
| Horizon $H$ | `milp.py` | Line 42 | $H = 24$, $\Delta t = 1.0$ | Hours | Standard 24h lookahead |
| Diesel Power | `milp.py` | Lines 88-92 | $P_{\text{diesel}}(t) \in [0, 5000]$ | W | Continuous variable |
| Diesel Status | `milp.py` | Lines 94-96 | $u_{\text{diesel}}(t) \in [0, 1]$ | Binary | Commitment binary |
| Diesel Start | `milp.py` | Lines 98-100 | $v_{\text{start}}(t) \in [0, 1]$ | Binary | Startup transition |
| Diesel Stop | `milp.py` | Lines 102-104 | $w_{\text{stop}}(t) \in [0, 1]$ | Binary | Shutdown transition |
| Battery Charge | `milp.py` | Lines 106-110 | $P_{\text{batt,ch}}(t) \in [0, 2500]$ | W | Continuous variable |
| Battery Discharge| `milp.py` | Lines 112-116 | $P_{\text{batt,dis}}(t) \in [0, 2500]$ | W | Continuous variable |
| Battery Ch Binary| `milp.py` | Lines 118-120 | $u_{\text{ch}}(t) \in [0, 1]$ | Binary | Mode binary |
| Battery Dis Binary| `milp.py` | Lines 122-124 | $u_{\text{dis}}(t) \in [0, 1]$ | Binary | Mode binary |
| State of Charge | `milp.py` | Lines 126-130 | $E_{\text{batt}}(t) \in [2000, 10000]$ | Wh | Energy capacity |
| PV Used | `milp.py` | Lines 132-135 | $P_{\text{pv,use}}(t) \in [0, P_{\text{pv,avail}}(t)]$ | W | Renewable output |
| PV Curtailed | `milp.py` | Lines 136-139 | $P_{\text{pv,curt}}(t) \in [0, P_{\text{pv,avail}}(t)]$ | W | Renewable curtailment |
| Wind Used | `milp.py` | Lines 140-143 | $P_{\text{wind,use}}(t) \in [0, P_{\text{wind,avail}}(t)]$ | W | Renewable output |
| Wind Curtailed | `milp.py` | Lines 144-147 | $P_{\text{wind,curt}}(t) \in [0, P_{\text{wind,avail}}(t)]$ | W | Renewable curtailment |
| Unmet Load | `milp.py` | Lines 148-151 | $P_{\text{unmet}}(t) \in [0, P_{\text{load}}(t)]$ | W | Critical deficit |
| Flex Served | `milp.py` | Lines 152-155 | $P_{\text{flex,served}}(t) \in [0, P_{\text{flex,avail}}(t)]$ | W | Flexible load |
| EBR Slack | Stage 2 Formulation | Reference | $s_{\text{EBR}}(t) \ge 0$ | Wh | Emergency reserve slack |
| Terminal Slack | Stage 2 Formulation | Reference | $s_{\text{term}} \ge 0$ | Wh | Terminal energy slack |

### 2. GOVERNED TARGET VS CURRENT IMPLEMENTATION CLASSIFICATION

- `CURRENT_MODEL_SUPPORTS_GOVERNED_J1_J4` = `PARTIAL`
- **Explanation**: The historical scalar `milp.py` implementation combines terms into a single cost function. The GAP19 multi-objective target decomposes this into $J_1..J_4$. The model constructed here is labelled `GOVERNED_REFERENCE_TEST_MODEL` to evaluate solver architecture equivalence without modifying production `milp.py`.
