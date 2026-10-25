# Runner Selection Control Flow

```text
PolarisLocalRunner.__init__(optimizer_type=...)
    ├── optimizer_type == "rule_based" ──────> LocalRuleBasedEnergyOptimizer()
    ├── optimizer_type in ("highs_native", "gap19_highs_native") ─> GAP19HighsNativeOptimizer()
    └── default / "milp" / unknown ─────────> LocalMILPEnergyOptimizer()
```

- `DEFAULT_SELECTION = LocalMILPEnergyOptimizer`
- `MILP_SELECTION = LocalMILPEnergyOptimizer`
- `RULE_BASED_SELECTION = LocalRuleBasedEnergyOptimizer`
- `HIGHs_NATIVE_SELECTION = GAP19HighsNativeOptimizer`
- `ALIAS_SELECTION = GAP19HighsNativeOptimizer`
- `UNKNOWN_SELECTION = LocalMILPEnergyOptimizer` (Falls back to default)
