# Governance Parameter Firewall

- All physical/reserve parameters (EBR target, terminal target, critical load, fuel rates) are dynamically passed via `config` or `forecast_bundle`.
- Default values are fallback boundaries only and do not promote synthetic fixture values (e.g. 20% SOC, 30 kW) into station facts.

`GOVERNANCE_PARAMETER_FIREWALL = PASS`
