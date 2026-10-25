# ANTI PATTERN REGISTER

## 1. PROHIBITED ARCHITECTURAL ANTI-PATTERNS & IMPLEMENTATION HACKS

The audit established an explicit register of prohibited design anti-patterns that MUST NOT be used during Option D implementation.

---

## 2. PROHIBITION REGISTER

| Anti-Pattern ID | Prohibited Implementation Hack | Architectural Violation | Governed Directive |
| :--- | :--- | :--- | :--- |
| **AP-01** | Repurposing `demand.point` to mean critical demand | Distorts total station demand accounting in solver & simulator | **STRICTLY PROHIBITED**. Use additive `critical_demand` field. |
| **AP-02** | Hardcoding Option D rules directly inside `milp.py` | Binds policy to solver engine; creates technical debt for GAP19 | **STRICTLY PROHIBITED**. Use decoupled `OptionDPolicyLayer`. |
| **AP-03** | Writing a separate rule-based emergency dispatcher (Option B) | Duplicates solver physics; produces sub-optimal dispatch | **STRICTLY PROHIBITED**. Re-use common `EnergyOptimizer`. |
| **AP-04** | Running a second independent optimizer in parallel | Wastes compute; creates conflicting state plans | **STRICTLY PROHIBITED**. Use single common solver. |
| **AP-05** | Hardcoding critical load priority (e.g. heating > water > comms) | Violates DEC-004 D4 sealed governance | **STRICTLY PROHIBITED**. Use proportional allocation $\alpha$. |
| **AP-06** | Hardcoding station-specific critical kW values in code | Destroys station portability | **STRICTLY PROHIBITED**. Load parameters from config. |
| **AP-07** | Starting diesel generator solely to charge battery | Violates DEC-004 D6 sealed governance | **STRICTLY PROHIBITED**. Enforce deficit requirement constraint. |
| **AP-08** | Passing future actual ground truth ($t+1..t+24$) to controller | Violates Information Isolation Firewall | **STRICTLY PROHIBITED**. Pass forecast bundle predictions only. |
| **AP-09** | Merging `UNKNOWN_INVALID` and `EMERGENCY` operating modes | Conflates unvalidated telemetry with trusted resource deficit | **STRICTLY PROHIBITED**. Keep modes distinct. |
| **AP-10** | Simulating GAP19 lexicographic objectives via giant scalar weights | Creates ill-conditioned MILP matrices and numerical instability | **STRICTLY PROHIBITED**. Use structured bounds; leave GAP19 for GAP19. |
| **AP-11** | Modifying Stage8.1 scientific forecasting code for synthetic data | Contaminates scientific forecasting branch | **STRICTLY PROHIBITED**. Inject synthetic forecasts via adapter. |
