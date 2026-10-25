# Dictionary: every word, kid language first, grown-up meaning second

## A. The place and the machines
- **Nuolja** · the mountain station in Sweden, 68°N (above the Arctic circle). Our real weather data comes from here.
- **Polar night** · weeks when the sun never rises.
- **PV / solar panels** · panels that turn light into electricity. We say 51 W of panel power per 1 W/m² of sunlight, up to 60 kW.
- **Wind turbine** · wind machine. In our test the wind is a formula, same for everyone.
- **Battery** · 200 kWh. We keep it between 20% and 95%. Charging/discharging loses 8% (efficiency η = 0.92).
- **Diesel generator** · loud fuel machine. Off, or between 10 and 100 kW. Burns 5 L/h just for running + 0.25 L per kWh + 2 L per start.
- **Load / demand** · how much power the house uses. In our test it follows a formula.
- **Critical load** · must-never-fail power: 15 kW.
- **Non-critical load** · comfort power above 15 kW.
- **Load not served / unmet load** · power the house wanted but did not get. Our target is 0.
- **Curtailment** · throwing away free sun/wind because the battery is full.

## B. Units
- **W** watt, how strong. **kW** = 1,000 W. **kWh** = how much energy over time (a 1 kW heater for 1 hour). **Wh** = 1/1000 of kWh.
- **W/m²** · how bright the sunlight is on one square metre. Midday summer sun is about 800+, a dark day is near 0.
- **L** litre of diesel. **CO₂** 2.68 kg per litre burned.
- **SOC** (state of charge) · how full the battery is, in %.
- **UTC** · world clock time, used so nobody confuses time zones.

## C. Forecaster words
- **Forecaster** · the part that guesses tomorrow's sunlight, hour by hour.
- **N6** · name of our final forecaster (6th design).
- **Feature / clue / input** · one thing we tell the forecaster (like "yesterday's brightness").
- **36 inputs** · 5 sun/calendar, 14 station memory, 4 mountain shading, 9 weather-company forecast, 4 combined.
- **Causal** · only uses things known before the deadline. No peeking at the future.
- **Leakage** · accidentally peeking at the answer. We have a check that blocks it. (Models F and J were withheld because of this.)
- **Firewall** (Page 5) · the check at the door that blocks future information.
- **MET Norway / MEPS** · the Norwegian weather service and its forecast model. The 18:00 UTC run is published about 20:15 and used at 00:00.
- **Clear-sky light** · how bright it would be if there were no clouds at all (from sun position).
- **Solar elevation** · how high the sun is above the horizon, in degrees.
- **Terrain shading** · mountains hiding the sun. Our own 4-clue mountain model.
- **GHI** · global horizontal irradiance, i.e. total sunlight on flat ground (the W/m²).
- **Chronos-2** · a ready-made AI that predicts time series (a number that changes over time). It is part of the first guess.
- **Baseline** · the first guess (physics + Chronos-2). The 40 models correct it.
- **Decision tree** · a flow-chart of yes/no questions ending in a number.
- **Gradient boosting (HGB)** · lots of small trees added one after another, each fixing the last one's mistakes.
- **Additive model** · predicts "add or subtract this many W/m²".
- **Clearness-ratio specialist** · predicts the fix as a percentage of clear-sky light. Better in high sun.
- **Ensemble** · a team of models. Here: 25 + 15 = 40.
- **Seed** · the starting random number; different seeds give different, independent friends (seeds 100–124 and 500–514).
- **Bagging** · each model looks at only part of the clues so their mistakes differ; the average is steadier.
- **Max features 0.78 / 0.8** · each model looks at 78% (or 80%) of the clues.
- **Depth 4** · each tree asks at most 4 questions in a row.
- **Leaf** · the end of a tree, holding a number. "Min leaf 25" = at least 25 examples must agree before making a rule.
- **L2 penalty** · a brake that stops the model from getting too excited about small patterns.
- **Absolute-error loss** · scoring by how far off, so a few crazy hours don't ruin learning.
- **Feature assembler** · the helper that builds the 24 × 36 table and checks it.
- **Blender** · the helper that mixes the 25-average and the 15-average by sun height (ramp 22°→32°, max 55%).
- **Night zeroing** · below the horizon the answer is 0.
- **Uncertainty / spread** · how much the 40 models disagree.
- **Conformal bound (Q̂ = 1.859)** · a margin factor measured on past data so the range is right about 90% of the time.
- **Scale** · std of the 40 + 0.10 × terrain clear-sky + 5. The size of our doubt.
- **Reserve** · the battery cushion that doubt asks for; at least 15 kWh.
- **Train / test / blind** · train on even days of 2024, test on odd days of 2024, blind = 2025 used once.
- **MAE** · average size of the mistake (W/m²). N6 blind: 36.79.
- **Frozen model / SHA-256** · locked file with a fingerprint so nobody can say we changed it.
- **Candidates K, N1, Successor v2, F, J** · other designs tried. K, N1, v2 pass tests; F, J withheld (not causal); N1 on hold (gain not significant on blind year).
- **Midnight snapshot** · the one forecast made at 00:00 UTC; hourly slices of it feed the optimizer.
- **OD-02 alignment** · we shift the forecast by one hour so "hour 1" means the next hour. The last step is filled with a clear-sky rule (decision pending).

## D. Optimizer words
- **Optimizer / GAP19** · the planner (see file 03).
- **GAP 19** · the 19th numbered open question in our specification ("how to make the solver obey priorities in order"); the optimizer is the answer.
- **HiGHS** · the free maths solver that does the work.
- **MILP** · mixed-integer linear program: a puzzle with straight-line rules and some yes/no choices.
- **Binary variable** · a yes/no switch (generator on?). 96 of them.
- **Variable / unknown** · a number the solver must choose. 432.
- **Constraint** · a rule that must hold. 336.
- **Objective** · what we want to make small.
- **Lexicographic** · strict order like a dictionary: settle the first letter before the second. Kid word: "most important first, never undone".
- **J1, J1b, J2, J3, J4** · critical load missed, comfort load missed, reserve shortfall, litres of diesel, wasted sun/wind. In that order.
- **Horizon (24 h)** · how far ahead it plans.
- **Rolling horizon** · plan 24, do 1, plan again.
- **Terminal / end-of-horizon rule** · end the 24 hours with about the battery you started with (10 kWh deadband = allowed wiggle).
- **EBR** · the cushion (reserve) number used in the plan.
- **Feedback loop** · measure, compare, correct. Ours is error-correcting (negative) feedback, not "positive".
- **Matrix builder** · the optimizer's own helper that writes the 336 rules in table form. Not related to the forecaster's assembler.
- **Reactive controller** · simple controller with no plan: reacts to the battery only. 38,405 L.
- **What-if re-solve** · re-run an hour with the opposite diesel choice to test it (Page 3).
- **Stakes** · what would be lost with the opposite choice: critical / reserve / costly / near-tie / better.
- **Featured days** · hand-picked interesting days (Page 2).

## E. Website words
- **REAL DATA / SIMULATED tags** · tells you if a number was measured or made by formula.
- **Provenance** · where a number came from.
