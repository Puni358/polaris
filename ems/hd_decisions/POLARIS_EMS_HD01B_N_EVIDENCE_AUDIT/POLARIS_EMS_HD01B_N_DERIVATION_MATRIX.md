# POLARIS EMS — HD-01B-N Derivation Matrix & Terminal Interaction Audit

**Audit Objective**: Systematic evaluation of candidate derivation pathways for numerical EBR resilience interval $N$ and interaction with HD-02 terminal reserve.

---

## 1. Candidate Derivation Evaluation Matrix

| Source / Pathway | Numerical Value | Authoritative? | Meaning / Context | Can Support $N$? | Missing Input | Governance Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. MPC Horizon** | $24\text{ h}$ | Yes (Tech) | Solver decision horizon $H$ | **No** | Architectural separation ($N \neq H$) | Governance selection of $N$ |
| **B. Critical-Load Trajectory** | $30\text{ kW}$ baseline | No | Synthetic baseline in `loads.yaml` | **No** | Station-measured critical load profile | Provision of station load data |
| **C. Battery Capacity** | $200\text{ kWh}$ | Yes (Tech) | Hardware battery rating | **No** | Critical load demand profile | Governance selection of $N$ |
| **D. Battery Efficiency** | $0.92$ | Yes (Tech) | Discharge efficiency $\eta_{\text{dis}}$ | **No** | Parameter $\eta_{\text{dis}}$ in EBR formula | Policy confirmation of efficiency |
| **E. Technical SOC Floor** | $20\%$ | Yes (Tech) | Hardware protection floor | **No** | Minimum energy $E_{\text{min\_tech}}$ | Technical floor definition |
| **F. Station Autonomy Spec** | Absent | No | Station backup requirement | **No** | Station electrical single-line spec | Provision of station autonomy data |
| **G. Generator Recovery Time** | $2\text{ h}$ min run | Yes (Tech) | Minimum continuous run hours | **No** | Equating generator run to $N$ | Governance selection of $N$ |
| **H. Resupply Interval** | Absent | No | Station diesel delivery schedule | **No** | $T_{\text{required}}$ resupply schedule | Provision of resupply schedule |
| **I. Survival Window ($T_{\text{required}}$)** | Absent | No | Operational survival window | **No** | Architectural separation ($N \neq T_{\text{req}}$) | Governance resolution of HD-03 |
| **J. Emergency Reserve** | Absent | No | Protected fuel reserve | **No** | Emergency reserve policy | Policy clarification |
| **K. Historical Telemetry** | Prototype runs | No | Fixed Wh reserve runs | **No** | Promoting prototype Wh to $N$ | Governance selection of $N$ |
| **L. Stakeholder Policy** | Unresolved | Yes (Policy)| HD-01B decision sheet | **No** | Stakeholder selection of $N$ | Stakeholder decision for $N$ |

---

## 2. HD-02 Terminal Target Interaction Analysis

Under closed policy HD-02:
$$E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H) = \sum_{k=H+1}^{H+N} \frac{D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}}$$

### Overlap & Double-Counting Audit
- **Independent $N$ Evaluation**: Evaluated at step $t=H$, $E_{\text{EBR\_target}}(H)$ sums forecasted critical demand over timesteps $H+1 \dots H+N$.
- **No Double Counting**: Because $E_{\text{EBR\_target}}(H)$ covers timesteps beyond $H$, it does not double-count critical demand from timesteps $1 \dots H$.
- **Independence Preserved**: Governed choice of $N$ (e.g. $N = 6\text{h}$) evaluates the terminal energy buffer over 6 hours beyond the MPC boundary ($H+1 \dots H+6$).

---

## 3. Derivation Conclusion

**`HD01B_N_DERIVATION = NOT_POSSIBLE_WITH_CURRENT_EVIDENCE`**.  
No derivation pathway exists in the current repository to calculate a numerical $N$ without introducing unbacked engineering assumptions.
