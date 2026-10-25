# End-of-Horizon & Conceptual Cases Analysis (Cases B, C, D)

## 1. Trace of Conceptual Case B: Current Time = 23:00

### 1.1 Context & Forecast State at 23:00
Suppose current observation time is $t_{\text{now}} = \text{"2024-01-01T23:00:00Z"}$ (11:00 PM).
`ForecastEngine.predict()` generates a 24-hour `ForecastBundle` for $[t_{\text{now}} + 1\text{h}, \dots, t_{\text{now}} + 24\text{h}]$:
- Timestamps span `"2024-01-02T00:00:00Z"` (midnight) through `"2024-01-02T23:00:00Z"` (11:00 PM tomorrow).

### 1.2 Executed Step ($k=0$) Lookahead Analysis
For the executed control decision ($k=0$, interval 23:00 to 00:00):
- The 6-hour EBR lookahead window covers hours 00:00 through 06:00 of tomorrow (Jan 2).
- The 24-hour forecast bundle contains all 24 hours of Jan 2.
- Hours 00:00 through 06:00 of Jan 2 are **the first 6 hours of the new forecast bundle**!
- **Verdict for Case B**: The controller possesses 100% complete critical-load information for the 6-hour EBR of the executed step. **No information beyond the 24-hour forecast bundle is required.**

---

## 2. Trace of Conceptual Case C: End of the 24h Decision Horizon ($k=23$)

### 2.1 Context & Problem Statement
Inside the 24-hour optimization plan solved at $t_0 = \text{00:00}$, consider decision timestep $k = 23$ (hour 24, interval 23:00 to 00:00 of the plan).
The 6-hour EBR lookahead window for step $k=23$ extends to $t_0 + 29\text{h}$ (hours 24..29 from origin $t_0$).
Indices $m \in [24, 28]$ are absent from the static 24-hour forecast bundle generated at $t_0$.

### 2.2 Rolling MPC Resolution Mechanics
- **Does the controller execute step $k=23$ from the $t_0$ solve?** `NO. NEVER.`
- The runner executes ONLY step $k=0$ and immediately advances time.
- When physical reality reaches 23:00 (23 hours later), the MPC controller has performed **23 rolling re-forecast and re-optimization cycles**!
- At 23:00, the controller invokes `ForecastEngine.predict()` and receives a **fresh 24-hour forecast bundle** covering 00:00 to 23:00 of the NEXT day!
- The decision for interval 23:00 to 00:00 is made using **step 0 of the 23:00 solve**, which has 100% complete forecast data for 00:00..06:00!
- **Verdict for Case C**: Rolling MPC itself completely resolves the missing tail information. The unexecuted tail $k=23$ of the $t_0$ plan is coupled to Terminal Reserve ($E_{\text{term,target}}$), ensuring state viability without requiring extra forecast hours.

---

## 3. Trace of Conceptual Case D: Next MPC Cycle After Executing One Hour

### 3.1 Context & State Transition
After executing step 0 ($t_0 \to t_1 = t_0 + 1\text{h}$):
1. `current_state.timestamp` is updated to $t_1 = \text{"2024-01-01T01:00:00Z"}$.
2. `current_state.battery_energy_wh` is updated to $E_{\text{bat}}[1]$ based on step 0 physical charge/discharge.
3. `runtime_context` is updated with observed load and solar at $t_1$.

### 3.2 Second MPC Cycle Solve ($t_1$)
1. `ForecastEngine.predict()` is invoked with $t_1 = \text{"2024-01-01T01:00:00Z"}$.
2. A new 24-hour `ForecastBundle` is generated for $t_1 + 1\text{h} \dots t_1 + 24\text{h}$ (`02:00` today to `01:00` tomorrow).
3. The new executed control step ($k=0$ of cycle 1) covers interval 01:00 to 02:00.
4. Its 6-hour EBR lookahead window spans 02:00 to 07:00.
5. Hours 02:00 to 07:00 are the first 6 hours of the new forecast bundle!
- **Verdict for Case D**: The 6-hour EBR lookahead window is **AGAIN FULLY EVALUABLE with 100% complete evidentiary data**.

---

## 4. Summary Matrix of Conceptual Cases

| Case | Origin $t_0$ | Executed Control Interval | 6h EBR Window | Available in 24h Bundle? | Extra Forecast Hours Required? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case A** | `18:00` | `18:00 - 19:00` | `19:00 - 00:00` | **YES (Complete)** | **0 Hours** |
| **Case B** | `23:00` | `23:00 - 00:00` | `00:00 - 06:00` | **YES (Complete)** | **0 Hours** |
| **Case C** | `00:00` (Plan $k=23$) | *Not Executed* (Replaced by MPC) | `24:00 - 29:00` | Coupled to Terminal Reserve | **0 Hours** |
| **Case D** | `01:00` (Cycle 1) | `01:00 - 02:00` | `02:00 - 07:00` | **YES (Complete)** | **0 Hours** |
