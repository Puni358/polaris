# Production vs Synthetic Claim Firewall

## ABSOLUTE FIREWALL PRINCIPLE
A successful synthetic integration test of ECD $\to$ Option D **MUST NOT** be interpreted as evidence of real-station operational readiness.

## Explicit Claim Classification

### Legitimate Synthetic Assertions (ALLOWED):
- "The EMS Policy Router correctly invokes ECD and transitions between NORMAL and EMERGENCY modes."
- "Option D fallback solver correctly enforces critical-load prioritization on synthetic fixtures."
- "ECD fail-closed logic successfully intercepts invalid telemetry and returns UNKNOWN_INVALID."
- "Option B native HiGHS solver remains 100% protected and unmodified during NORMAL mode operation."

### Prohibited Real-Station Claims (FORBIDDEN):
- PROHIBITED: Claiming Nuolja battery capacity ($200	ext{ kWh}$) is validated for production.
- PROHIBITED: Claiming Nuolja critical load ($30	ext{ kW}$) is validated for production.
- PROHIBITED: Claiming Nuolja generator fuel curve ($5	ext{L/h} + 0.25	ext{L/kWh}$) is validated for production.
- PROHIBITED: Claiming Nuolja emergency resupply interval ($6	ext{h}$) is validated for production.
- PROHIBITED: Claiming POLARIS is ready for live physical station deployment.

---

## Verdict
`PRODUCTION_DEPLOYMENT = NOT_ESTABLISHED`. The firewall is strict, explicit, and unyielding.
