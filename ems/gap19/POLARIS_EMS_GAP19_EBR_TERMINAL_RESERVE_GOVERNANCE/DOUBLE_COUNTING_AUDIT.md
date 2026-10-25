# Double-Counting & Overlap Audit

This audit identifies potential overlaps between reserve mechanisms that human governance must resolve to prevent conflicting optimization penalties.

## Identified Overlap Areas

1. **EBR vs. Battery Technical Minimum SOC:**
   - Technical minimum SOC (e.g. 20%) protects battery hardware health.
   - If EBR is defined as an additional 20% SOC floor, the effective usable range is reduced to 40%–95%, locking 40% of battery capacity from normal cycling.

2. **EBR vs. Terminal Reserve:**
   - If $s_{\text{EBR}}[23]$ penalizes reserve shortfall at $t = 23\text{h}$, and $s_{\text{terminal}}$ separately penalizes reserve shortfall at $t = 23\text{h}$, the terminal timestep suffers double objective penalization.

3. **EBR vs. $T_{\text{REQUIRED}} = 6\text{h}$ vs. ECD Assessment:**
   - If ECD already evaluates whether battery energy covers $T_{\text{REQUIRED}} = 6\text{h}$, and Option B separately enforces a 6-hour energy reserve in normal mode, the system may force premature diesel generation before an actual emergency exists.

```text
DOUBLE_COUNTING_RESOLUTION = GOVERNANCE_DECISION_REQUIRED
T_REQUIRED_RELATIONSHIP = GOVERNANCE_DECISION_REQUIRED
```
