# POLARIS EMS — HD-01B-N Source Evidence Map

**Audit Target**: Exhaustive traceability map of all repository searches for numerical resilience interval $N$ and reserve hours.

---

## 1. Traceability & Inspection Matrix

| Search Category / Term | Inspected File Path | Line Range | Findings / Content | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **MPC Horizon $H$** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72) | L72 | `H = 24 # Horizon hours` | `IMPLEMENTATION_FACT` (Solver forecast decision horizon $H$; $N \neq H$) |
| **Critical Load Baseline** | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml#L3-L5) | L3-L5 | `baseline_power_w: 30000.0` | `PROTOTYPE_ASSUMPTION` ($30\text{ kW}$ synthetic baseline; no hourly profile) |
| **Battery Capacity** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L3) | L3 | `capacity_wh: 200000.0` | `PROTOTYPE_ASSUMPTION` ($200\text{ kWh}$ hardware rating) |
| **UPS Autonomy** | Implementation Input Register | `INP_03` | `15 minutes (provisional)` | `PROVISIONAL_ENGINEERING` (Sub-hourly hardware ATS hold-up duration) |
| **HD-01B Architecture** | HD-01 Audit Register | `HD-01C` | $N$ is fixed, separately governed interval | `CLOSED_ARCHITECTURE` (Structure closed; numerical $N$ open) |
| **Terminal Target Interaction** | HD-02 Audit Report | Section 4 | $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ | `CLOSED_ARCHITECTURE` (Terminal reserve uses $E_{\text{EBR\_target}}$ at $t=H$) |

---

## 2. Exhaustive Search Terms Log

The following terms were searched across repository files and governance logs. **Zero instances of an authorized numerical value for $N$ were found**:

- `resilience interval`: Defined as open parameter in governance registers; **no numerical value**.
- `resilience horizon`: **ABSENT** as a quantitative value.
- `autonomy hours`: **ABSENT**
- `reserve hours`: **ABSENT**
- `ride-through`: Found only in sub-hourly ATS hardware latency notes (`15 min`).
- `backup duration`: **ABSENT** as an hourly EMS policy value.
- `critical load duration`: **ABSENT**
- `N_hours`: **ABSENT**
