# J2 Reserve Shortfall vs ECD Emergency Authority Signal Separation Audit

## Governance Mandate (Decisions D1 & D3)
1. **Decision D1**: J2 Emergency Reserve semantics are **`HYBRID / MODE-DEPENDENT`**. J2 represents emergency battery reserve shortfall penalty inside normal MPC optimization.
2. **Decision D3**: **ECD is the SOLE EMERGENCY AUTHORITY**. J2 shortfall does **NOT** independently declare emergency.

## Signal Flow Architecture

```mermaid
graph LR
    subgraph Optimization Layer
        J2[J2 Objective Penalty s_J2 > 0]
    end

    subgraph Evaluation Layer
        Telemetry[Battery SOC & Fuel Telemetry] --> ECD[Emergency Condition Detector]
        Auth[Authorized Horizon T_req] --> ECD
        ECD --> EA[EmergencyAssessment]
    end

    subgraph Routing Layer
        EA -- operating_mode == NORMAL --> OptionB[Option B MPC]
        EA -- operating_mode == EMERGENCY --> OptionD[Option D Fallback]
        J2 --> TelemetryLog[Logged as Shortfall Telemetry]
    end
```

## Architectural Guarantee
- If $s_{J2} > 0$ occurs during Option B HiGHS optimization, the system records `reserve_shortfall > 0` in `DispatchPlan`.
- However, the EMS mode router checks `EmergencyAssessment.operating_mode`. As long as $m_{\text{battery}} \ge 0$ and $m_{\text{diesel}} \ge 0$, `operating_mode` remains **`NORMAL`**.
- The system will **NEVER** bypass ECD authority or force `EMERGENCY` mode merely because $s_{J2} > 0$.
