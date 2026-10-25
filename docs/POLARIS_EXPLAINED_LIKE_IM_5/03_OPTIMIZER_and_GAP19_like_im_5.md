# Page 7 · The optimizer and "GAP 19", like you are 5

## Why "GAP 19"?
When we wrote down what the energy system must do, we listed open questions and numbered them "gaps". Question number 19 was: **"how do we make the computer obey the rules in order of importance?"** The optimizer is our answer to question 19, so it carries the number. (Not on the website any more; say it only if asked.)
Kid version: "Gap 19 is just the 19th question on our to-do list, and this is the answer."

## What the optimizer is
A planner. Each hour it gets: sun for 24 hours, wind, how much the house will use, the cushion to keep, and the battery level right now. It returns: for each of the 24 hours, how much solar, wind, battery and diesel to use.

## The puzzle size
18 choices per hour × 24 hours = **432 unknowns**. 96 of them are on/off switches (is the generator on? is the battery charging?). It must obey **336 rules** (energy in = energy out, the battery is 20% to 95% full of 200 kWh, the generator is off or between 10 and 100 kW…). Because of the on/off switches this kind of puzzle is called MILP. The free solver that solves it is **HiGHS**.

## The five priorities (the part to say to judges)
Think of packing a school bag: first the things you must have, last the nice extras. We settle each one completely before touching the next, and once settled it can never be made worse.
1. **J1 · critical load**: the important power (15 kW, always) is never cut.
2. **J1b · comfort load**: everything else the house uses stays on.
3. **J2 · battery cushion**: keep enough energy in the battery for a bad cloudy night, and end the day roughly where you began.
4. **J3 · diesel**: now use the least fuel possible (5 L per hour running + 0.25 L per kWh + 2 L per start).
5. **J4 · wasted sun/wind**: waste as little as possible.
"Why not one big score?" A single score can trade a little darkness for a lot of fuel. Strict order cannot. (Grown-up word: lexicographic.)

## The loop (feedback)
Plan 24 hours → do only hour 1 → measure the real battery → plan again. Hour 12 of a plan is less trustworthy than hour 1, so we only trust hour 1. If the forecast was wrong, the real battery shows it, and the next plan corrects itself. This is error-correcting (negative) feedback; the optimizer does not "learn", it re-plans.

## Why diesel is used sensibly
The generator wastes 5 L just by running, so it is best run hard in short blocks, not idle. The planner knows this and groups its running.
