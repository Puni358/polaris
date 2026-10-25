# Emergency → Normal Return Boundary Design

## Governance & Runtime Status
- **`EMERGENCY_RETURN_POLICY = NOT_ESTABLISHED`**
- **`EMERGENCY_RETURN_RUNTIME = NOT_IMPLEMENTED`**

## Entry Boundary Design
In future code, if a governed return policy is established, it will enter at the `EMSControlRouter` evaluation boundary:

```text
Assess ECD Margins (m_b, m_d)
   ↓
If m_b >= 0 AND m_d >= 0:
   Check Governed Return Policy (e.g., hysteresis / cooldown if specified by governance)
   ├── Authorized: Route to NORMAL (Option B)
   └── Not Authorized / In Cooldown: Maintain EMERGENCY (Option D)
```

No hysteresis, cooldown, or debounce values are invented by this design.
