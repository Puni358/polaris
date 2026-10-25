# Combined Validated Target Control-Flow Architecture

```text
                               ┌─────────────────────────┐
                               │  StationState & Config  │
                               └────────────┬────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │  ECD Evaluation #1      │
                               └────────────┬────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
         operating_mode == NORMAL                        operating_mode == EMERGENCY
                    │                                               │
       ┌────────────▼────────────┐                     ┌────────────▼────────────┐
       │ Option B Native HiGHS   │                     │ Option D Fallback       │
       └────────────┬────────────┘                     └────────────┬────────────┘
                    │                                               │
        ┌───────────┴───────────┐                                   │
        │                       │                                   │
Status == OPTIMAL     Status == INFEASIBLE                          │
        │                       │                                   │
        │             ┌─────────┴─────────┐                         │
        │             │ Check ECD #1 Mode │                         │
        │             └─────────┬─────────┘                         │
        │                       │                                   │
        │            ┌──────────┴──────────┐                        │
        │         NORMAL               EMERGENCY                    │
        │            │                     │                        │
        │            ▼                     └────────────────────────┤
        │     NOT_ESTABLISHED                                       │
        │   (Normal Fallback N/A)                                   │
        │                                                           │
        └───────────────────────┬───────────────────────────────────┘
                                │
                                ▼
                     DispatchPlan (k=0 action)
                                │
                                ▼
                     DigitalTwinSimulator.step()
                                │
                                ▼
                     StationState_{k+1} (SOC_{k+1}, Fuel_{k+1})
```
