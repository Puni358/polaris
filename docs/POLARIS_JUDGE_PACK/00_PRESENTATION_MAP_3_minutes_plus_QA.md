# POLARIS — presentation map: 3 minutes + 2 minutes of questions

**One sentence to remember:** *A polar station burns diesel because the sun disappears for weeks. POLARIS predicts the sun, plans 24 hours ahead in strict priority order, and cuts diesel by 30% with zero load lost.*

Open the website on **tab 1**, press **Play** on the live station (it starts on a spring morning), and keep the keyboard ← → for tabs 6 and 7.

## The 3-minute script (180 seconds)

| Time | Tab | Say this | Show this |
|---|---|---|---|
| 0:00 – 0:20 | **1 · SYSTEM** | "Nuolja station, 68°N. For weeks there is no sun, so the generator runs. Real measured weather drives this replay of the whole year." | Live station playing: sun, battery, diesel, real temperature. Mention REAL DATA tags. |
| 0:20 – 0:50 | **1 · SYSTEM** (flow diagram) | "Every hour: forecast the sun, plan 24 hours, carry out the first hour, measure, plan again. Diesel is the last resort." | The flow diagram and the five protection chips (lights, comfort, cushion, fuel, sun). |
| 0:50 – 1:25 | **6 · FORECASTER** | "36 clues: real station history, the weather forecast issued before we use it, a mountain-shading model we built. 40 models vote: 25 additive, 15 specialists. Their disagreement tells us how big a battery cushion to keep." | Press → through the chapters; click a dot; show the blender graph. |
| 1:25 – 1:45 | **5 · PIPELINE** (chapter 1) | "Nothing from the future: every input is known before 00:00 UTC. The audit passes before data flows." | The firewall strip, AUDIT PASS. |
| 1:45 – 2:10 | **7 · OPTIMIZER** | "Five priorities solved in order and locked: critical load, comfort load, battery reserve, fuel, wasted sun. Only the first hour is carried out; the real battery level restarts the plan — an error-correcting loop." | Run all in order; the plan-vs-reality day chart. |
| 2:10 – 2:40 | **4 · PROOF** | "Same weather, demand and wind for every run. Basic controller 38,405 litres. POLARIS 26,890 litres: 30% less, zero load lost. Without the safety cushion, power is lost. 31 tonnes of CO₂ not emitted." | The fuel bars and the load-not-served card. |
| 2:40 – 2:55 | **2 · INSPECTOR** | "Pick any day. On 7 July the forecast missed badly — and still no diesel, no load lost." | Featured day 7 Jul, the thinking cards. |
| 2:55 – 3:00 | — | "Real weather, every number traceable, every script in the judge pack." | Close. |

**Backup tab:** **3 · DECISION MAP** — use it if asked "how do you know the decisions were right?": every hour was re-run with the opposite diesel choice; green days = that choice would have lost load or reserve.

## The 2-minute Q&A: short, honest answers

| Question | Answer |
|---|---|
| Is wind and demand real? | No. Wind and demand are simulation formulas, identical for every scenario. Sunshine, temperature, humidity and snow are real measurements from the Nuolja station. |
| Is any input from the future? | No. The 36 inputs are: calendar and sun position (calculable in advance), the station's own readings before the forecast time, the MET Norway 18:00 UTC weather run (published about 20:15, used at 00:00), and a static terrain profile. The code rejects any column containing the real outcome, and an independent audit checked it. |
| Can it run offline? | Almost. Only the daily weather file must be downloaded; once stored the forecaster needs no internet. A simple on-site fallback exists (prototype). |
| Is the forecast refreshed every hour? | The forecast is made once a day at 00:00 UTC. The optimizer re-plans every hour from the measured battery level. |
| Why is the forecast shifted by one hour? | Hour-1 of the plan covers [t0, t0+1h], so a forecast stamped t0 would lag one hour. The one leftover step is filled by the clear-sky-ratio rule (owner decision pending); only hour 1 is ever executed. |
| Why 30% and not more? | We re-ran every scenario on identical inputs. The saving against the basic controller is 38,405 → 26,890 litres. |
| Does POLARIS win every day? | No. On 7 Feb Scenario 3 used less diesel. Over the year POLARIS is among the lowest-diesel options with zero load lost. |
| What does the safety cushion do? | Without it (Scenario 4) 2.5 kWh of load was lost over the year; with it, none. |
| What does it cost you? | The generator starts 1.3× as often (548 vs 435) and the battery cycles 3.2× as often. Savings already include battery losses; ageing is not priced. |
| What is GAP 19? | The 19th open design question we numbered in the specification: "how do we make the solver obey the priorities in order?" The optimizer is the answer, so it carries the number. The optimizer answers it using HiGHS in lexicographic mode. |
| What are J1, J1b, J2, J3, J4? | Critical load not served, non-critical load not served, battery reserve shortfall, litres of diesel, wasted renewable energy, solved in that strict order. |
| Is it positive feedback? | It is error-correcting (negative) feedback: measure, compare with the plan, plan again from the measured state. The optimizer does not retrain. |
| Where is the ensemble / assembler? | Both are inside the forecaster. The ensemble is the 40 models (25 + 15). The feature assembler builds the 24×36 input table; the blender combines the two groups using the sun's height. |
| Why is N1 on hold? | It beat Candidate K on the 2024 odd test, but on the blind 2025 test its gain (0.19 W/m²) was not statistically significant. N6 passed all four gates. |
| Why not show models F and J? | Their inputs were later found not to be causal, so we withheld them. |
| Every model saves about the same diesel. Why? | The 30% comes from the planner, not the forecaster. Any decent forecast lets the planner see when the sun returns; all five forecasters land within 0.5% (26,859 to 26,992 L, zero load lost) and the hourly re-plan corrects small errors. N6's benefit is safety: battery never below 22.5% against 20.5% for the physical baseline. We do not claim N6 saves more fuel. |
| Do other forecasters change diesel? | Barely (within 0.5%). N6 is the most accurate (36.79 W/m² blind error against 37.46 for K, 38.19 for Successor v2, 41.77 for the physical baseline) and keeps the largest battery margin. |
| What is the weak point? | It is a simulation on one year of real weather, not a field test; demand and wind are simulated; the forecast refreshes daily. One of N6's 36 inputs is set to zero in the simulation; we measured the effect at 0.015% of forecast error. |
| Do you claim a money saving? | No. Delivered fuel at a polar station varies too much. We quote litres and CO₂ (2.68 kg per litre). |
| Where are the scripts? | `POLARIS_JUDGE_PACK/` — open `00_START_HERE_where_to_find_everything.md`. |
