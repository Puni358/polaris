# POLARIS EMS — HD-04 Adverse Renewable Decision Matrix

**Audit Objective**: Provide a clear, evidence-based decision matrix for Human Governance Decision HD-04 without choosing the policy.

---

## 1. Governance Decision Options Comparison

| Decision Dimension | Option A: Zero-Renewable Stress Scenario ($P=0$) | Option B: Derated / Quantile Forecast Scenario |
| :--- | :--- | :--- |
| **Mathematical Form** | $P_{\text{solar}} = 0, \ P_{\text{wind}} = 0$ in detector | $P_{\text{solar}} = P_{\text{quantile}}, \ P_{\text{wind}} = P_{\text{quantile}}$ |
| **Repository Status** | Recommended proposal; technically valid | No authoritative quantile data in repo |
| **Required Unbacked Inputs** | **None** | Requires authorizing quantile level (e.g. $P_{10}$) |
| **Causal Isolation** | Clean (Pre-solve detector isolation) | Requires probabilistic forecast pipeline |
| **Normal MPC Impact** | Zero impact (Normal MPC uses point forecasts) | Zero impact if isolated to detector |
| **Semantic Meaning** | Detector-local stress-test floor | Statistical lower-bound forecast |
| **Operational Risk** | Maximum conservative survivability floor | Risk of over-crediting renewables in storm |
| **Governance Status** | **Awaiting Stakeholder Approval** | **Requires New Evidence & Policy** |

---

## 2. Interaction Audit with Closed Governance Decisions

- **HD-01A & HD-01B ($N=6\text{h}$)**: In NORMAL mode, the optimizer enforces EBR reserve $N=6\text{h}$. If the detector under $P=0$ indicates station cannot survive $T_{\text{required}}$, it triggers EMERGENCY mode, where EBR is subordinated to critical service.
- **HD-02 (Terminal Target)**: Operates normally in normal mode; in emergency mode, critical service takes absolute precedence.
- **HD-03 ($T_{\text{required}}$)**: Detector uses $T_{\text{required}}$ to evaluate zero-renewable survival duration.
- **HD-05 (Battery Degradation)**: Normal 5% extra-fuel tolerance applies when detector signals NORMAL mode. In EMERGENCY mode, battery wear is subordinate to critical service.
- **Policy E3 (Emergency Resource Preservation)**: Active *after* detector signals EMERGENCY mode. Fully compatible.

---

## 3. Recommended Wording for Stakeholder Approval

If human governance selects **Option A**, the formal policy decision text shall be:

> **Formal Policy Statement HD-04**:  
> *"The Emergency Mode Detector shall evaluate station fuel and battery survivability through $T_{\text{required}}$ assuming zero future renewable generation ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$) as a detector-local stress scenario. Normal MPC optimization shall continue using standard causal forecasts without modification."*
