# POLARIS EMS — HD-03 T_required SEMANTIC DECISION MATRIX

## 1. AUTHORITATIVE DECISION MATRIX

The table below summarizes the evidence audit findings across all 11 governance dimensions of HD-03 $T_{\text{required}}$:

| Open Item | Repository Evidence | Current Status | Exact Human Decision Required |
| :--- | :--- | :--- | :--- |
| **Missing Input** | No default, fallback, or failure handling code exists in repository for Cases A–I | `GOVERNANCE_REQUIRED` | Decide exact behavior when inputs are missing, invalid, or corrupt (e.g. halt EMS vs fail closed vs fallback). |
| **Source Precedence** | Options P1–P4 evaluated; no evidence selects an override precedence rule | `GOVERNANCE_REQUIRED` | Select precedence rule (e.g. Option P1 operational override vs P3 conditional override vs P4 resolver condition). |
| **Conflict Resolution** | No tolerance, timestamp precedence, or manual gate exists for $T_{\text{config}} \ne T_{\text{oper}}$ | `GOVERNANCE_REQUIRED` | Decide how the resolver handles valid but conflicting values from configuration and operational sources. |
| **Validity** | No schema validation rules, positivity constraints, or duration bounds exist in code | `GOVERNANCE_REQUIRED` | Define exact validity criteria (finite, positive bounds, schema validation, payload signature). |
| **Freshness / Staleness** | No TTL, message age limit, or clock-drift threshold exists for operational inputs | `GOVERNANCE_REQUIRED` | Define maximum allowable operational data age (TTL seconds) and staleness transition policy. |
| **Source Authority** | No role hierarchy or cryptographic signing authority exists for operational inputs | `GOVERNANCE_REQUIRED` | Specify authorized operational source identity and message verification contract. |
| **Time Semantics** | Defined as survival window from current decision point until recovery; representation open | `GOVERNANCE_REQUIRED` | Decide whether operational messages supply relative duration $\Delta t$, absolute timestamp $t_{\text{recovery}}$, or both. |
| **Runtime Variability** | No rule specifies whether $T_{\text{required}}$ may change step-by-step during an EMS run | `GOVERNANCE_REQUIRED` | Decide whether $T_{\text{required}}$ is fixed per EMS run, fixed per MPC horizon, or dynamically refreshable per timestep. |
| **Resolver Boundary** | Emergency Detector established as `CONSUMER_ONLY`; resolver is separate component | `ESTABLISHED` | *Closed*: $T_{\text{required}}$ Resolver is an upstream data component; Emergency Detector consumes resolved output only. |
| **Provenance** | Standard POLARIS audit conventions exist; candidate provenance fields identified | `PARTIALLY_ESTABLISHED` | Formalize exact provenance schema fields to record for 100% execution reproducibility. |
| **Numerical Value** | Numerical audit confirms no authoritative survival hours exist; all proxies rejected | `NOT_ESTABLISHED` | Select numerical $T_{\text{required}}$ value for specific station deployments (e.g. site survival hours). |

---

## 2. EXPLICIT PROHIBITION OF DERIVED FALLBACKS

To protect system safety and governance integrity, the human decision process **MUST NOT** adopt any of the following arbitrary defaults without explicit policy reasoning:

1. **$6\text{ HOURS}$ (HD-01B EBR Interval)**: $N=6\text{h}$ is a fixed **normal-operation** battery buffer for critical loads. It is NOT an emergency survival window.
2. **$24\text{ HOURS}$ (MPC Optimization Horizon $H$)**: $H=24\text{h}$ is a rolling solver window for computational foresight, NOT a mission resupply guarantee.
3. **$30\text{ DAYS}$ (Provisional Resupply Cycle)**: Illustrative budget/logistics example only; not a microgrid operational guarantee.
4. **$2\text{ HOURS}$ (Generator Minimum Runtime)**: Thermal constraint for engine protection, not station survival window.
5. **$15\text{ MINUTES}$ (UPS Hold-Up Time)**: Electrical transition hold-up, not EMS emergency survival window.
6. **$6.67\text{ HOURS}$ (Battery Arithmetic)**: $100\text{ kWh} / 15\text{ kW}$ battery discharge arithmetic proxy; violates detector non-derivation directive.
