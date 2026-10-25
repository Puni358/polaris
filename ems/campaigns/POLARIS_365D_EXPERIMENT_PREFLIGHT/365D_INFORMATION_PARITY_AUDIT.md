# 365D CONTROL VS TREATMENT INFORMATION PARITY AUDIT

## Information Symmetry Checklist

| Input / Capability | POLARIS Treatment Arm | Baseline Control Arm | Asymmetry Status |
| :--- | :--- | :--- | :--- |
| **Environmental Trajectory** | H1.0 Canonical Fixture | H1.0 Canonical Fixture | **IDENTICAL** |
| **Station Load Trajectory** | H1.0 Canonical Fixture | H1.0 Canonical Fixture | **IDENTICAL** |
| **Initial Battery SOC** | 50.0% (100.0 kWh) | 50.0% (100.0 kWh) | **IDENTICAL** |
| **Initial Diesel Fuel** | Cumulative accounting | Cumulative accounting | **IDENTICAL** |
| **Physical Asset Limits** | 50kW Bat, 100kW Diesel, 60kW PV | 50kW Bat, 100kW Diesel, 60kW PV | **IDENTICAL** |
| **State-Transition Rules** | Digital Twin Discrete Step | Digital Twin Discrete Step | **IDENTICAL** |
| **Fuel Consumption Model** | $5.0\text{ L/h} + 0.25\text{ L/kWh}$ | $5.0\text{ L/h} + 0.25\text{ L/kWh}$ | **IDENTICAL** |
| **Future Ground Truth Access** | Prohibited (Static audit verified) | Prohibited (Static audit verified) | **IDENTICAL** |
| **Control Decision Execution** | First-action-only ($k=0$) committed | First-action-only ($k=0$) committed | **IDENTICAL** |

## Audit Verdict
Static audit confirms 100% information symmetry between treatment and control arms in Mode 1 (Same-Forecast). Runtime truth-firewall compliance will be measured during execution.
