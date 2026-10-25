# Page 6 · The forecaster (the sun-guesser), like you are 5

**Job:** for each of the next 24 hours, say how strong the sunlight will be, and how unsure we are.
Name: **N6** (the 6th design we tried that passed every test). It is *frozen*: like a sealed envelope, nobody changed it after testing (its fingerprint, SHA-256, starts b1b54c93…).

## Step 1 · Inputs ready (the 36 clues)
Like a detective: 36 clues, all known before midnight.
- 5 about the sun and the calendar (where is the sun, what day is it) — can be worked out in advance.
- 14 about what the station saw recently (yesterday's light, temperature…).
- 4 about mountains blocking the sun (shading) — a map of the hills built by us.
- 9 from the weather company's forecast (cloud, humidity, wind…).
- 4 mixed clues (e.g. sun height × cloudiness).
The **feature assembler** is the helper that puts the 36 clues into one table: 24 rows (hours) × 36 columns (clues). It refuses to continue if a clue is missing or if any clue contains the real answer.

## Step 2 · The first guess (baseline)
A simple guess from physics ("how bright is a clear sky now, minus clouds") mixed with a time-series model called Chronos-2. This is already decent. The 40 models only learn how to **fix** this guess, so they do not start from zero.

## Step 3 · The 40 models (the "ensemble")
Ensemble = a team. Like asking 40 friends to guess how many sweets are in a jar, then using the average: the silly mistakes cancel.
- **25 additive models.** Each is a little tree of yes/no questions ("is the sun above 20°? is it very cloudy?") that ends in a number: "add 30 or take away 20 from the baseline". Each friend only looks at 78% of the clues, with a different random start (called a seed), so they make different mistakes.
- **15 specialists.** They fix the baseline as a *percentage of a perfectly clear sky* instead of a plain number. They are best when the sun is high.

## Step 4 · Average and blend
Average the 25, average the 15. Then the **blender** decides who to listen to, using how high the sun is:
- Sun below 22° or hidden by a mountain: only the 25.
- Sun between 22° and 32°: slowly give the 15 more say.
- Above 32°: the 15 get 55% say (never more).
Night: the answer is exactly zero.

## Step 5 · "How sure are we?" (uncertainty)
The 40 models disagree a little. If they disagree a lot, we are unsure. We turn that into a safety bound that is right 90% of the time. From this we set the **reserve**: the battery cushion to keep, never below 15 kWh. Unsure day = bigger cushion.

## Step 6 · Output
24 numbers of sunlight (W/m²) + a reserve. Sunlight is turned into panel power: 51 W for each W/m², maximum 60 kW. This goes to the optimizer (Page 7).

## How we know it is fair (the exams)
- Trained only on even-numbered days of 2024.
- Tested on odd-numbered days of 2024 (never seen).
- Then once, on all of 2025, never touched while building ("blind test"). Average mistake there: 36.79 W/m². Physical baseline: 41.77. Successor v2: 38.19. Candidate K: 37.46.
- Two models (F and J) were dropped because they used clues that turned out not to be from before the deadline.
- The only clue set to zero in the simulation changes the error by 0.015%.

## Where are "ensemble" and "assembler"?
Both live **inside the forecaster**. Ensemble = the 40 models. Assembler = the feature assembler (builds the 24×36 table). The blender combines the two groups. The optimizer has none of these; it has its own matrix builder.
