# POLARIS EMS — HD-03 T_required Source Evidence Map

**Audit Scope**: Detailed traceability map of all repository searches for $T_{\text{required}}$, resupply schedules, and station logistics.

---

## 1. Traceability & Inspection Matrix

| Category / Search Term | Inspected File Path | Relevant Line / Section | Finding / Content | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **MPC Decision Horizon ($H$)** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72) | L72 | `H = 24 # Horizon hours` | `DISAMBIGUATED` (Solver forecast decision horizon $H$; $T_{\text{required}} \neq H$) |
| **EBR Resilience Interval ($N$)** | [`POLARIS_EMS_HD01B_N6H_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01B_N6H_CLOSURE/POLARIS_EMS_HD01B_N6H_CLOSURE.md) | Section 1 | $N = 6\text{ HOURS}$ | `DISAMBIGUATED` (Normal-mode resilience target $N$; $T_{\text{required}} \neq N$) |
| **Generator Min Up-Time** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L9) | L9 | `min_up_time_hours: 2` | `DISAMBIGUATED` (Technical generator run bound; $T_{\text{required}} \neq 2\text{h}$) |
| **Sub-hourly UPS Autonomy** | Implementation Input Register | `INP_03` | `15 minutes (provisional)` | `DISAMBIGUATED` (Hardware ATS transfer hold-up time; $T_{\text{required}} \neq 15\text{m}$) |
| **Resupply Budget Allocation** | Policy Resolution AREA_05 | AREA_05 | "Seasonal/resupply fuel budget" | `DISAMBIGUATED` (Structure approved; volume/schedule `STATION_DATA_REQUIRED`) |
| **Detector Interface Schema** | Survivability Detector Audit | Sheet 06 | `t_required_hours` marked `ABSENT` | `CONCEPTUAL_SCHEMA` (Schema field defined; numerical value absent) |

---

## 2. Exhaustive Search Terms Log

The following terms were searched across all repository files and governance logs. **Zero instances of an authoritative numerical value for $T_{\text{required}}$ were found**:

- `T_required` / `T required`: Defined as a conceptual window parameter; **numerical value ABSENT**.
- `survival window` / `survival horizon`: Defined as operational concept; **numerical value ABSENT**.
- `refueling schedule` / `resupply schedule`: **ABSENT**
- `delivery interval` / `resupply cadence`: **ABSENT**
- `recovery window` / `mission recovery`: **ABSENT**
- `station autonomy`: UPS hold-up ($15\text{ min}$) only; no hourly station autonomy value.
- `guaranteed-recovery time`: **ABSENT**
