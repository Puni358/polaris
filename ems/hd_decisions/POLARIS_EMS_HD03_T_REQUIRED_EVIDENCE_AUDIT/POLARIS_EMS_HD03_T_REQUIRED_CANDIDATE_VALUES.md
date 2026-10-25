# POLARIS EMS — HD-03 Candidate Value Analysis & Semantic Disambiguation

**Audit Objective**: Systematic audit and semantic classification of all numerical values in the repository that could be mistaken for $T_{\text{required}}$.

---

## 1. Candidate Values Disambiguation Table

| Candidate Value | Source Location | Actual Semantic Meaning | Is Authoritative $T_{\text{required}}$? | Rationale for Rejection |
| :--- | :--- | :--- | :---: | :--- |
| **24h** | [`milp.py:L72`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72) | MPC Decision & Forecast Horizon ($H$) | **NO** | Solver decision boundary; not operational survival window |
| **6h** | [`POLARIS_EMS_HD01B_N6H_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01B_N6H_CLOSURE/POLARIS_EMS_HD01B_N6H_CLOSURE.md) | HD-01B EBR Normal Resilience Interval ($N$) | **NO** | Normal-mode rolling resilience target inside MPC |
| **30 days** | Policy Resolution AREA_05 | Provisional resupply-cycle allocation example | **NO** | Long-term budget cycle example, not $T_{\text{required}}$ |
| **2h** | [`diesel.yaml:L9`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L9) | Generator Minimum Run Time (`min_up_time_hours`) | **NO** | Generator mechanical constraint, not station survival |
| **15 minutes** | Implementation Spec `INP_03` | Sub-hourly UPS hold-up autonomy duration | **NO** | Hardware ATS transfer latency, not hourly EMS window |
| **6.67h** | $200\text{ kWh} / 30\text{ kW}$ | Usable battery capacity divided by baseline load | **NO** | Derived physical discharge hours, not policy window |

---

## 2. Analysis of Critical Distinctions

### 2.1 Why $H = 24\text{h}$ is NOT $T_{\text{required}}$
The MPC horizon $H = 24\text{h}$ defines the finite optimization window over which forecasts are available and decision variables are computed. Equating $T_{\text{required}}$ to $H$ would artificially truncate emergency survivability assessment at 24 hours, even if the next resupply is days away.

### 2.2 Why $N = 6\text{h}$ is NOT $T_{\text{required}}$
$N = 6\text{h}$ is the governed resilience interval for normal operation (HD-01B). It tells the optimizer how much critical load energy to buffer in the battery during normal mode. $T_{\text{required}}$ is the full-horizon operational survival window used by the Emergency Mode Detector outside the MPC loop.

### 2.3 Why 30 Days is NOT $T_{\text{required}}$
The 30-day figure in Decision 08 documents is a provisional engineering example used to illustrate seasonal resupply accounting. It is explicitly labeled `STATION_DATA_REQUIRED` and is not an authorized station resupply schedule.

---

## 3. Candidate Audit Conclusion

None of the numerical candidates in the repository represent an authoritative value for $T_{\text{required}}$.  
**`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`**.
