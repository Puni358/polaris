# Numerical Firewall & Unresolved Policy Register

## 1. Governance Numerical Firewall Principle

As mandated by POLARIS EMS GAP19 governance:
- No AI assistant, software engineer, or optimizer implementation may invent, assume, or hardcode numerical policy values.
- All unresolved policy parameters MUST remain strictly symbolic quantities until explicit human governance authorization is granted.
- The implementation design package must specify variable interfaces dynamically without embedding static numerical assumptions.

---

## 2. Unresolved Policy Parameters Register

The following parameters MUST remain symbolic and unresolved:

| Parameter ID | Parameter Description | Symbolic Variable Name | Current Code Status | Governance Status |
| :--- | :--- | :--- | :--- | :--- |
| **POL-J2-01** | EBR Numerical Target Scaling Factor | $\mu_{\text{EBR}}$ or $E_{\text{EBR,target}}[t]$ | Hardcoded default fallback in code | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-02** | Terminal Reserve Numerical Target | $E_{\text{term,target}}$ or $\alpha_{\text{term}}$ | Hardcoded default fallback in code | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-03** | Terminal State of Charge (SOC) Target | $SOC_{\text{terminal\_target}}$ | Hardcoded default fallback in code | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-04** | Forecast Uncertainty Margins | $\sigma_{\text{pv}}, \sigma_{\text{wind}}, \sigma_{\text{demand}}$ | Prototype 10% bounds in baseline | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-05** | Battery Degradation Cost Valuation | $\text{deg\_penalty\_per\_wh}$ | Default `0.00005` in config | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-06** | Diesel Fuel Price & Operational Budget | $\text{fuel\_cost\_per\_l}$ | Default `2.50` in config | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-07** | Emergency Reserve Minimum Floor | $E_{\text{reserve\_floor}}$ | Default SOC 20% in config | `UNAUTHORIZED / SYMBOLIC ONLY` |
| **POL-J2-08** | Stage Lock Numerical Tolerances | $\epsilon_1, \epsilon_2, \epsilon_3$ | `0.0` default in `highspy` | `UNAUTHORIZED / SYMBOLIC ONLY` |

---

## 3. Implementation Firewall Rule

When implementing Option B in Python (`gap19_highs_native.py`):
1. All target variables ($E_{\text{stage2,target}}[t]$, $E_{\text{term,target}}$) MUST be computed from runtime configuration inputs or schema parameters.
2. If a policy input is absent, the code MUST raise an explicit `GovernanceAuthorizationError` or require an explicit human-approved configuration file rather than silently injecting unapproved numerical constants.
3. Zero numerical policy values are authorized by this design package.
