# The whole story (matched to the website pages)

## The problem (say this first, on Page 1)
Imagine a small house on a snowy mountain, very far north (Nuolja, 68°N). It has solar panels, a wind machine, a big battery (like a giant phone battery) and a diesel generator (a noisy machine that burns fuel).
For many weeks in winter the sun never comes up. Then the house needs the generator. Diesel is dirty, costly to carry up a mountain, and can run out.
**Goal: use as little diesel as possible, and never switch off the lights or heating that matter.**

## Our idea in one line
**Guess how sunny tomorrow will be. Plan the next 24 hours. Do only the first hour. Look at what really happened. Plan again.**

## Page 1 · SYSTEM  (the picture of the whole house)
- The live station shows sun, wind, battery and generator moving through a real year of real weather. Press Play.
- Real: sunshine, temperature, humidity, snow (measured at the station).
- Made up by a formula, the same for every test: wind and how much power the house uses. Say this out loud; it is honest.
- Five protections (chips): lights for important things, comfort, battery cushion, fuel last, don't waste sun.

## Page 5 · PIPELINE  (how the information travels)
Think of a relay race. Each runner hands a baton to the next.
1. **Collect clues** about tomorrow (36 clues, see Page 6).
2. **Firewall check**: no clue may come from the future. Like an exam where nobody may peek at the answers. The check passes before anything runs.
3. **Forecaster** turns clues into "how much sun each hour tomorrow".
4. **Optimizer** turns that into a plan for the battery and generator.
5. **House does hour 1**, we measure what really happened, and the loop starts again.
Two clocks: the forecast is made **once a day at midnight (00:00 UTC)**, the plan is re-made **every hour**.
Why midnight? The weather company (MET Norway) publishes its forecast about 20:15 the evening before. We wait and use it at 00:00. So nothing is from the future.

## Page 6 · FORECASTER  (the part that guesses the sun)
See file 02. Short version: 40 small helper models each give a guess, we average them, and the disagreement between them tells us how careful to be.

## Page 7 · OPTIMIZER  (the part that plans)
See file 03. Short version: it must obey five rules in order of importance, and it answers a 432-question puzzle every hour.

## Page 2 · INSPECTOR  (watch one hour of thinking)
Pick any day (the "featured days" menu has the interesting ones, e.g. 7 July when the forecast was wrong and still nothing was lost). You see the plan the optimizer made and WHY it did or did not charge or start the generator, e.g. "sun is strong in the next 3 hours, so no need to run the generator".

## Page 3 · DECISION MAP  (was each decision right?)
For every hour of the year we re-ran the plan with the OPPOSITE diesel choice (generator on instead of off, or off instead of on). If the opposite would have lost power or emptied the battery, that hour is marked important (green/red). It shows the choices were not lucky guesses.

## Page 4 · PROOF  (the numbers)
Same weather, same wind, same demand for every test.
- Simple controller (no planning): 38,405 litres.
- POLARIS: 26,890 litres. That is **30% less**, and **0 kWh of power lost**.
- Remove the battery cushion: some power is lost (2.5 kWh in the year). So the cushion matters.
- Five different forecasters, same planner: all about 26,860 to 26,990 litres (file 05 explains why this is normal).
- CO₂: 2.68 kg per litre of diesel, so about 31 tonnes less.
- We do not quote money; fuel prices on a mountain vary too much.

## The honest weak points (say them before a judge does)
1. It is a simulation on one real year, not a field test.
2. Wind and demand are formulas.
3. POLARIS does not win every single day, but it is among the lowest and loses no power.
4. The generator starts 1.3× more often and the battery cycles 3.2× more; we did not put a price on wear.
5. A better forecast does not change fuel much; it keeps the battery safer (file 05).
