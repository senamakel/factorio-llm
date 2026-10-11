# Recursive Factorio: climb the production ladder

You improve `brain/`, a deterministic Python program that plays Factorio 2.1 as
one honest character (walk, mine, craft, build from inventory) through the
frozen `actuator` package. Each candidate is scored on three fresh seeded
worlds: the brain plays for 10 wall-minutes at game speed 4, then the actor is
halted and only the factory it built keeps running for 5 game-minutes.

Score = min(red packs/min, 100) + min(green packs/min, 100) + 5 per milestone.
Goal of this campaign: **100 red + 100 green science packs per minute** (G12).

| Step | Milestone |
| --- | --- |
| G1 | Automation researched |
| G2 | An assembling machine has crafted something |
| G3 | Red packs produced by machines (actor halted) |
| G4 | Ore mined and iron plates smelted by machines (actor halted) |
| G5 / G6 / G7 | 10 / 30 / 100 red packs per minute |
| G8 | Logistic science pack researched and an electric mining drill built |
| G9 | Green packs produced by machines |
| G10 / G11 | 10 / 30 green packs per minute (G11 also needs Automation 2) |
| G12 | 100 red + 100 green packs per minute |

## Where we are

{{incumbent}}

## Recent failures from the scored episodes

{{failures}}

## What has been tried

{{history}}

## Ideas

{{ideas}}

## Your task

Orchestrator: read the metrics (`next_goal`, `reached`, rates) and the failures,
recall the hive's memory, and pick the ONE change most likely to reach the next
milestone or raise packs/min. Facts live in `knowledge/prototypes.json`,
`knowledge/RATIOS.md` and `knowledge/wiki/`. Have builder implement it with a
test, have critic check it, and make sure `./factorio gates` passes. Small,
verified steps up the ladder beat big rewrites.
