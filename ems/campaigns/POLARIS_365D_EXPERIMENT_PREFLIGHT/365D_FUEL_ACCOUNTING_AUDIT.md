# 365D DIESEL FUEL ACCOUNTING & MODEL AUDIT

## Fuel Consumption Equation
$$F_{\text{step}} = \left( 5.0 \cdot \mathbb{I}(P_{\text{diesel}} > 0) + 0.00025 \cdot P_{\text{diesel}} \right) \cdot 1.0\text{ h}$$

## Scenario Accounting Rules
- **Scenario Fuel-1 (Primary)**: Cumulative fuel integrated continuously over all 8,784 steps without tank depletion clipping or logistics halts.
- **Scenario Fuel-2 (Secondary Sensitivity)**: Synthetic finite tank with frozen refill parameters (`GOVERNANCE/PARAMETER BLOCKED`).
- **Scenario Fuel-3 (Physical Logistics)**: `NOT_ESTABLISHED`.
