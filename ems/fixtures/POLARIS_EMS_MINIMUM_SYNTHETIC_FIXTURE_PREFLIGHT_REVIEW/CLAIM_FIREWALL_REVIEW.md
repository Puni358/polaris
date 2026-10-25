# CLAIM FIREWALL REVIEW
## SCIENTIFIC & EMPIRICAL CLAIM FIREWALL RULES

### 1. FORENSIC AUDIT OF CLAIM BOUNDARIES
Because direct empirical evidence for Nuolja station equipment and critical load mapping is not yet established (`DIRECT_NUOLJA_EVIDENCE = 0`), the minimum synthetic fixture MUST enforce a strict Claim Firewall.

This preflight review established the formal rules preventing synthetic simulation outputs from being promoted to real-world station claims.

### 2. FORMAL PROVENANCE HEADERS
Every file, dataset, and parameter generated for the synthetic fixture MUST carry the following mandatory provenance metadata header:

```yaml
provenance:
  source_type: SYNTHETIC_ENGINEERING_ASSUMPTION # or REUSED_SYNTHETIC_ENGINEERING_PARAMETER
  station_identity: NONE
  empirical_status: NOT_ESTABLISHED
  deployment_status: NOT_AUTHORIZED
  real_nuolja_data: FALSE
```

### 3. ALLOWED VS PROHIBITED SCIENTIFIC CLAIMS

#### SCIENTIFICALLY ALLOWED CLAIMS (WHAT SYNTHETIC RUNS MAY PROVE)
1. "The POLARIS EMS software architecture executes closed-loop MPC cycles deterministically."
2. "The ECD correctly classifies Normal, Emergency, and UNKNOWN_INVALID states under configured baseline $T_{\text{required\_baseline}} = 6\text{h}$."
3. "The Option D policy layer strictly enforces protected critical load prioritization and noncritical shedding."
4. "The MILP optimizer satisfies hardware limits ($SOC_{\text{min}}, P_{\text{gen,min}}, P_{\text{gen,max}}$) and converges to optimal solutions."
5. "Energy accounting across the controller and Digital Twin is closed and mathematically exact."

#### PROHIBITED CLAIMS (WHAT SYNTHETIC RUNS MUST NEVER PROVE)
1. "Nuolja station protected critical demand is $30\text{ kW}$."
2. "Nuolja station fuel savings under POLARIS EMS are $X\%$ or $Y$ liters."
3. "Nuolja station reliability or survivability is guaranteed for $6\text{ hours}$."
4. "Nuolja battery storage is $200\text{ kWh}$ or has $90\%$ efficiency."
5. "Nuolja diesel generator consumes $12.5\text{ L/h}$."
6. "POLARIS EMS is ready for immediate live field deployment at Nuolja."

### 4. CONCLUSION & RECOMMENDATION
`CLAIM_FIREWALL_STATUS = ENFORCED`.
The claim firewall rules are complete, explicit, and unalterable.
