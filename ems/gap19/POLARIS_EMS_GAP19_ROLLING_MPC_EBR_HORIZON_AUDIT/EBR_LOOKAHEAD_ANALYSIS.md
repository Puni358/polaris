# EBR 6-Hour Lookahead vs Decision Horizon Mathematical Analysis

## 1. Problem Statement & Mathematical Indexing

Let $t_0$ be the forecast origin timestamp at the start of an MPC cycle.
Let the decision / optimization horizon be $H = 24$ timesteps, indexed $k \in \{0, 1, 2, \dots, 23\}$, corresponding to timestamps $t_0 + 1\text{h}, t_0 + 2\text{h}, \dots, t_0 + 24\text{h}$.
Let the governed Emergency Battery Reserve (EBR) lookahead duration be $T_{\text{REQUIRED}} = 6\text{ hours}$ ($N_{\text{req}} = 6$ timesteps).

For any decision timestep $k \in \{0, 1, \dots, 23\}$, the forward 6-hour critical load lookahead window is:
$$W(k) = \{m \in \mathbb{Z} \mid k \le m \le k + N_{\text{req}} - 1\} = \{k, k+1, k+2, k+3, k+4, k+5\}$$

---

## 2. Evaluation of Forecast Availability Across Plan Timesteps

A 24-hour `ForecastBundle` provides forecast data for timesteps $m \in \{0, 1, \dots, 23\}$.

### Timestep Breakdown inside a Single 24-Hour Optimization Plan

| Decision Step $k$ | Lookahead Window $W(k)$ | Required Forecast Range | Available in 24h Bundle? | Missing Forecast Steps |
| :---: | :---: | :---: | :---: | :---: |
| **$k = 0$ (EXECUTED)** | $[0, 5]$ | $t_0+1\text{h} \dots t_0+6\text{h}$ | **YES (100% COMPLETE)** | **0 hours** |
| **$k = 1$** | $[1, 6]$ | $t_0+2\text{h} \dots t_0+7\text{h}$ | **YES (100% COMPLETE)** | **0 hours** |
| **$k = 17$** | $[17, 22]$ | $t_0+18\text{h} \dots t_0+23\text{h}$ | **YES (100% COMPLETE)** | **0 hours** |
| **$k = 18$** | $[18, 23]$ | $t_0+19\text{h} \dots t_0+24\text{h}$ | **YES (100% COMPLETE)** | **0 hours** |
| **$k = 19$** | $[19, 24]$ | $t_0+20\text{h} \dots t_0+25\text{h}$ | NO (Truncated at 23) | **1 hour** ($m=24$) |
| **$k = 20$** | $[20, 25]$ | $t_0+21\text{h} \dots t_0+26\text{h}$ | NO (Truncated at 23) | **2 hours** ($m=24, 25$) |
| **$k = 21$** | $[21, 26]$ | $t_0+22\text{h} \dots t_0+27\text{h}$ | NO (Truncated at 23) | **3 hours** ($m=24..26$) |
| **$k = 22$** | $[22, 27]$ | $t_0+23\text{h} \dots t_0+28\text{h}$ | NO (Truncated at 23) | **4 hours** ($m=24..27$) |
| **$k = 23$** | $[23, 28]$ | $t_0+24\text{h} \dots t_0+29\text{h}$ | NO (Truncated at 23) | **5 hours** ($m=24..28$) |

---

## 3. Answers to Specific Questions 9 & 10

### Question 9: At the final six hours of a 24-hour decision horizon, does the controller actually have the future critical-load information needed to calculate the complete six-hour EBR?
- **Answer**:
  - **For the EXECUTED control step ($k=0$)**: `YES`. The controller has 100% complete forecast data covering all 6 hours of lookahead.
  - **For unexecuted plan steps at the horizon edge ($k \in [19, 23]$)**: `NO`. Within a single static 24-hour forecast bundle, indices $m \in [24, 28]$ (corresponding to hours 25 through 29 from $t_0$) are missing.

### Question 10: If not, exactly how many additional forecast hours are required?
- **Answer**:
  - If the optimizer is required to evaluate an explicit, un-truncated 6-hour EBR lookahead for **every single timestep $k \in [0, 23]$ inside a static 24-hour decision plan**, then exactly **5 additional forecast hours** are required (total forecast information horizon = $23 + 5 + 1 = 29$ hours, or rounded to 30 hours).
  - **HOWEVER**, under **rolling MPC with Terminal Reserve coupling**:
    Because the controller re-forecasts every 1 hour and commits ONLY step $k=0$, timesteps $k \in [19, 23]$ inside the plan are never executed. Coupling horizon edge $k \in [19, 23]$ to Terminal Reserve ($E_{\text{term,target}}$) or Tail Persistence satisfies optimization stability with **ZERO additional forecast hours** ($H_{\text{forecast}} = 24\text{ hours}$ is sufficient).

---

## 4. Analytical Conclusion

```text
EXECUTED_STEP_EBR_COVERAGE = 100% (COMPLETE)
UNEXECUTED_TAIL_MISSING_HOURS = 5 HOURS (AT k=23)
RESOLUTION_VIA_ROLLING_MPC = FULLY VALID
ADDITIONAL_FORECAST_HOURS_REQUIRED = 0 HOURS (WITH TERMINAL COUPLING)
```
