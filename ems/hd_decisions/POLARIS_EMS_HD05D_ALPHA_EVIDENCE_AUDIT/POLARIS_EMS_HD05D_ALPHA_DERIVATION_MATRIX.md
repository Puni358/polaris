# POLARIS EMS — HD-05D-α Derivation Matrix & Edge Case Audit

**Audit Objective**: Systematic audit of candidate derivation sources for relative extra-fuel tolerance $\alpha$ and edge-case behavior.

---

## 1. Candidate Derivation Evaluation Matrix

| Source | Repository Evidence | Authoritative? | Numerical? | Can Derive $\alpha$? | Required Unsupported Assumption | Governance Action Required? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Existing Fuel Budget** | Structure approved (D08) | No | No | **No** | Inventing unbacked fuel volume | Authorize fuel volume in Liters |
| **B. Resupply Interval** | $T_{\text{required}}$ unresolved | No | No | **No** | Equating MPC horizon to resupply interval | Authorize $T_{\text{required}}$ |
| **C. Fuel Survivability** | Reserve uncalibrated | No | No | **No** | Equating emergency reserve to normal slack | Define survivability reserve |
| **D. Fuel Tank / Reserve** | Tank capacity unbacked | No | No | **No** | Assuming tank fraction equals $\alpha$ | Provide station tank specs |
| **E. Generator Curves** | Idle $5\text{ L/h}$, min $10\text{ kW}$ | Yes (Tech) | Yes | **No** | Equating min run step to policy $\alpha$ | Governance selection of $\alpha$ |
| **F. Battery Preserv. Req.** | Prototype $c_{\text{deg}}$ only | No | No | **No** | Promoting regularizer to policy | Authorize battery preservation cap |
| **G. Battery Lifetime** | Repo has no aging curve | No | No | **No** | Importing textbook lithium aging | Calibrate battery chemistry |
| **H. Historical Telemetry** | Scalar MILP runs | No | No | **No** | Converting composite costs to $\alpha$ | Select policy $\alpha$ |
| **I. Stakeholder Policy** | HD-05B qualitative decision | Yes (Qual) | No | **No** | Turning qualitative words into a % | Human decision for numerical $\alpha$ |
| **J. Objective Parameters** | Prototype scalar weights | No | No | **No** | Translating scalar weights to $\alpha$ | Authorize lexicographic parameter |
| **K. Economic Parameters** | Prototype $\$2.50/\text{L}$ & $\$0.00005$ | No | No | **No** | Assuming prototype cost ratio equals $\alpha$ | Authorize economic parameters |

---

## 2. Zero-Fuel Edge Case Analysis ($F^* = 0$)

### 2.1 Edge Case Physics
On high-solar/wind days where renewable generation and battery storage fulfill all energy requirements without starting the diesel generator, the Stage-3a minimum fuel consumption is:
$$F^* = 0 \text{ Liters}$$

### 2.2 Mathematical Consequence
Substituting $F^* = 0$ into the governed relative constraint:
$$F_{\text{diesel}} \le (1 + \alpha) F^* = (1 + \alpha) \times 0 = 0 \text{ Liters}$$

This imposes a **strict zero-diesel bound** on zero-fuel days:
$$\text{When } F^* = 0 \implies F_{\text{diesel}} = 0$$

### 2.3 Operational Implications
- **Benefit**: Prevents the optimizer from starting the generator purely to save minor battery cycling on days when 100% renewable self-sufficiency is achievable.
- **Governance Requirement**: If human stakeholders intend to permit generator startup even on zero-diesel days (e.g. for battery maintenance or extreme cycle preservation), a separate zero-fuel exception policy or absolute floor must be governed.

---

## 3. Derivation Conclusion

**`HD05D_ALPHA_DERIVATION = NOT_POSSIBLE_WITH_CURRENT_EVIDENCE`**.  
No derivation pathway exists in the current repository to calculate a numerical $\alpha$ without introducing unbacked engineering assumptions.
