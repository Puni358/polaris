# Combined Corrected Control Flow Diagram

```text
                State_k
                   │
                   ▼
               Forecast_k
                   │
                   ▼
                ECD #1
                   │
          ┌────────┴────────┐
          │                 │
       NORMAL           EMERGENCY
          │                 │
          ▼                 ▼
      Option B           Option D
          │                 │
     ┌────┴─────┐           │
     │          │           │
  OPTIMAL   INFEASIBLE      │
     │          │           │
     ▼          ▼           │
 Dispatch    unresolved     │
   Plan      operational    │
     │         action       │
     │                      │
     └──────────┬───────────┘
                │
                ▼
      First Action Only (k=0)
                │
                ▼
      DigitalTwinSimulator.step()
      (Advances SOC_next & Fuel_next)
                │
                ▼
            State_{k+1}
```
