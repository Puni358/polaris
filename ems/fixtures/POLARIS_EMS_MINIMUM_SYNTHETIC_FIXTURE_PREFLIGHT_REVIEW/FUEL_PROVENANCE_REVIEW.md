# FUEL PROVENANCE REVIEW
## AUDIT OF FUEL INVENTORY & UNCOUPLING FROM T_REQUIRED

### 1. FORENSIC AUDIT OF FUEL PARAMETERS
The proposed minimum synthetic fixture specified:
- **Initial Fuel Volume ($V_{\text{fuel,0}}$)**: $500\text{ L}$
- **Resupply Rate / Schedule**: $0\text{ L/h}$ (No resupply during 24h simulation)
- **Minimum Fuel Floor**: $0\text{ L}$

This audit verified whether $500\text{ L}$ is minimum-sufficient and evaluated its relationship to the sealed $T_{\text{required\_baseline}} = 6\text{h}$ ECD policy.

### 2. UNCOUPLING FROM T_REQUIRED
A critical governance rule established in prior audits is:
> *"Fuel logistics relationship: INDIRECTLY_COUPLED to $T_{\text{required}}$."*

- **Governance Verification**: $T_{\text{required\_baseline}} = 6\text{h}$ represents the required duration for which available station resources (battery energy + diesel fuel + forecast renewables) must be able to sustain protected critical service ($P_{\text{critical}} = 30\text{ kW}$).
- **Fuel Consumption Rationale**:
  - At $30\text{ kW}$ load, diesel fuel consumption is $12.5\text{ L/h}$.
  - To support $30\text{ kW}$ for $6\text{ hours}$ using diesel alone requires $6\text{h} \times 12.5\text{ L/h} = 75\text{ L}$ of usable fuel.
  - The initial fuel reserve of $500\text{ L}$ provides up to $40\text{ hours}$ of continuous generator runtime at $30\text{ kW}$ output ($500 / 12.5 = 40\text{h}$).
- **Conclusion**: $500\text{ L}$ easily satisfies the 6-hour baseline requirement without constraining the ECD calculation. $T_{\text{required}} = 6\text{h}$ is an operational policy horizon, NOT a mathematical calculation of total fuel depletion time.

### 3. MINIMALITY EVALUATION OF 500 L
- **Why 500 L is used**: $500\text{ L}$ is inherited from the prototype station setup (`system/config/fuel.yaml`).
- **Is 500 L uniquely required?**: No. Any initial fuel volume $V_{\text{fuel,0}} \ge 75\text{ L}$ would allow testing 6-hour survival. However, $500\text{ L}$ is useful because it allows testing multihour diesel operation across Scenario 3 (Diesel-Limited Emergency) and Scenario 4 (Both-Resources-Limited Emergency where initial fuel is forced to $< 50\text{ L}$).

### 4. SCIENTIFIC CLAIM FIREWALL
$500\text{ L}$ carries the explicit provenance tag:
`fuel_provenance: REUSED_SYNTHETIC_ENGINEERING_PARAMETER`
`station_identity: NONE`
`empirical_status: NOT_ESTABLISHED`

It MUST NEVER be reported as Nuolja station tank capacity.

### 5. CONCLUSION & RECOMMENDATION
`FUEL_PROVENANCE_STATUS = QUALIFIED`.
Retain initial fuel $V_{\text{fuel,0}} = 500\text{ L}$ for Scenarios 1–3 and reduce to $V_{\text{fuel,0}} = 50\text{ L}$ specifically for Scenario 4 (Both-Resources-Limited Emergency). Maintain strict uncoupling between fuel volume and $T_{\text{required\_baseline}} = 6\text{h}$.
