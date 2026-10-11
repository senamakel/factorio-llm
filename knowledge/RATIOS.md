# Early-game ratios: red and green science

Every fact cites the cached page in `knowledge/wiki/` it came from, as
`[Page.md]`. Lines marked **derived** are arithmetic on cited facts, with the
working shown. Normal quality, no modules, no research bonuses throughout.
If `knowledge/prototypes.json` exists, it overrides anything here.

Conventions: a machine finishes one craft every `recipe time / crafting speed`
seconds. The cited recipe times are at crafting speed 1. The Crafting and
Player pages give no number for the player's own (hand) crafting speed;
`[Assembling_machine_1.md]` history says only that machine crafting speed "is
relative to manual crafting speed".

## Recipes (time at speed 1; inputs -> outputs)

| Item | Recipe | Source |
|---|---|---|
| Automation science pack | 5 s; 1 copper plate + 1 iron gear wheel -> 1 | [Automation_science_pack.md] |
| Logistic science pack | 6 s; 1 inserter + 1 transport belt -> 1 | [Logistic_science_pack.md] |
| Iron gear wheel | 0.5 s; 2 iron plate -> 1 | [Iron_gear_wheel.md] |
| Inserter | 0.5 s; 1 electronic circuit + 1 iron gear wheel + 1 iron plate -> 1 | [Inserter.md] |
| Transport belt | 0.5 s; 1 iron gear wheel + 1 iron plate -> **2** | [Transport_belt.md] |
| Electronic circuit | 0.5 s; 3 copper cable + 1 iron plate -> 1 | [Electronic_circuit.md] |
| Copper cable | 0.5 s; 1 copper plate -> **2** | [Copper_cable.md] |
| Iron plate | 3.2 s; 1 iron ore -> 1 | [Iron_plate.md] |
| Copper plate | 3.2 s; 1 copper ore -> 1 | [Copper_plate.md] |
| Steel plate | 16 s; 5 iron plate -> 1 | [Steel_plate.md] |
| Stone brick | 3.2 s; 2 stone -> 1 | [Stone_brick.md] |
| Chemical science pack (preview) | 24 s; 3 advanced circuit + 2 engine unit + 1 sulfur -> **2** | [Chemical_science_pack.md] |

Total raw per pack, as stated on the wiki: red = 1 copper plate + 2 iron plate;
green = 1.5 copper plate + 5.5 iron plate [Automation_science_pack.md],
[Logistic_science_pack.md].

Bootstrap buildings (all from their own pages): stone furnace 5 stone;
burner mining drill 3 gear + 3 iron plate + 1 stone furnace; assembling machine 1
3 circuit + 5 gear + 9 iron plate; lab 10 circuit + 10 gear + 4 transport belt;
boiler 4 pipe + 1 stone furnace; steam engine 8 gear + 10 iron plate + 5 pipe;
offshore pump 2 gear + 3 pipe; pipe 1 iron plate; small electric pole
2 copper cable + 1 wood -> 2.

## Machines

| Machine | Speed | Energy | Size | Source |
|---|---|---|---|---|
| Assembling machine 1 | crafting speed 0.5 | 75 kW electric, 2.5 kW drain | 3×3 | [Assembling_machine_1.md] |
| Assembling machine 2 | crafting speed 0.75 | 150 kW electric | 3×3 | [Assembling_machine_2.md] |
| Stone furnace | crafting speed 1 | 90 kW burner | 2×2 | [Stone_furnace.md] |
| Steel furnace | crafting speed 2 | 90 kW burner | 2×2 | [Steel_furnace.md] |
| Burner mining drill | mining speed 0.25; area 2×2 | 150 kW burner | 2×2 | [Burner_mining_drill.md] |
| Electric mining drill | mining speed 0.5; area 5×5 | 90 kW electric | 3×3 | [Electric_mining_drill.md] |
| Lab | research speed 1 | 60 kW electric | 3×3 | [Lab.md] |

Assembling machine 1 cannot use fluid ingredients; assembling machine 2 can
[Crafting.md].

### Furnace and drill rates

- Stone furnace: 0.3125 iron/copper plate/s, 0.3125 stone brick/s, 0.0625 steel/s;
  coal 0.0225/s. Steel furnace: 0.625 plate/s, 0.125 steel/s, coal 0.0225/s
  [Stone_furnace.md] (Output table).
- Iron, copper, coal and stone have mining time 1. Burner drill gives 0.25/s,
  electric drill 0.5/s [Mining.md] (table), [Electric_mining_drill.md].
  Burner drill: "about 7 items per single unit of coal" [Burner_mining_drill.md].
- Player mining speed 0.5 [Player.md].
- **derived:** a yellow belt of plates (15/s) needs 15 / 0.3125 = 48 stone furnaces
  or 24 steel furnaces. One stone furnace eats 0.3125 ore/s, which is 1.25 burner
  drills or 0.625 electric drills.

## Logistics throughput

- Transport belt: 15 items/s across both lanes, 7.5 items/s per lane, 1.875
  tiles/s [Transport_belts_Physics.md], [Transport_belt.md]. Underground belt and
  splitter: 15 items/s [Underground_belt.md], [Splitter.md]. Maximum underground
  distance is 4 tiles [Underground_belt.md].
- Inserters, items/s at no capacity bonus (2.0.26 measurements, [Inserters.md]):

| Inserter | Chest→chest | Chest→empty yellow belt | Belt→chest (yellow, items moving)* | Energy | Source |
|---|---|---|---|---|---|
| Burner inserter | 0.79 | 0.78 | 0.60 | 144 kW burner | [Inserters.md], [Burner_inserter.md] |
| Inserter | 0.86 | 0.85 | 0.94 | 15.1 kW, 400 W drain | [Inserters.md], [Inserter.md] |
| Long-handed inserter | 1.25 | 1.2 | 1.18 | 21.4 kW, 400 W drain | [Inserters.md], [Long-handed_inserter.md] |
| Fast inserter | 2.5 | 2.5 | 2.50 | 59.3 kW, 500 W drain | [Inserters.md], [Fast_inserter.md] |

  \*The belt→chest numbers on the page are labelled as 1.1 experimental data.
- Inserters stop topping up a machine once it holds the ingredients for about
  2 crafts (more for fast recipes), and stop fuelling a boiler/furnace/burner
  inserter at 5 fuel items [Inserters.md] (Insertion limits).
- Burner inserters pick up fuel for themselves [Burner_inserter.md].

## Power

- Offshore pump: 1200 water/s, no power needed [Offshore_pump.md].
- Boiler: burns 1.8 MW of fuel; 6 water/s -> 60 steam/s at 165 °C
  [Boiler.md].
- Steam engine: 900 kW; 30 steam/s [Steam_engine.md].
- Ratio 1 offshore pump : 200 boilers : 400 steam engines; 1 boiler : 2 engines
  [Power_production.md], [Steam_engine.md].
- Fuel value: coal 4 MJ, wood 2 MJ [Fuel.md], [Coal.md], [Wood.md].
- 20 MW needs 5 coal/s [Tutorial_Applied_power_math.md].
- **derived:** one boiler at full load burns 1.8 MW / 4 MJ = 0.45 coal/s.
- Poles: small, wire reach 7.5, supply area 5×5; medium, reach 9, supply 7×7
  [Small_electric_pole.md], [Medium_electric_pole.md].

## Research and tech gates (Factorio 2.x)

- The first techs are **trigger technologies**. They need no science packs:
  Steam power (craft 50 iron plate), Electronics (craft 10 copper plate),
  Automation science pack (craft 1 lab, requires Electronics + Steam power)
  [Technologies.md] (Trigger technologies),
  [Steam_power_research.md], [Electronics_research.md],
  [Automation_science_pack_research.md].
- Electronics unlocks copper cable, electronic circuit, inserter, lab and small
  electric pole. Steam power unlocks boiler, offshore pump, pipe,
  pipe-to-ground and steam engine [Electronics_research.md],
  [Steam_power_research.md].

| Tech | Units × (time; packs per unit) | Unlocks | Source |
|---|---|---|---|
| Automation | 10 × (10 s; 1 red) | assembling machine 1, long-handed inserter | [Automation_research.md] |
| Electric mining drill | 25 × (10 s; 1 red) | electric mining drill | [Electric_mining_drill_research.md] |
| Logistics | 20 × (15 s; 1 red) | underground belt, splitter | [Logistics_research.md] |
| Fast inserter | 30 × (15 s; 1 red) | fast inserter | [Fast_inserter_research.md] |
| Steel processing | 50 × (5 s; 1 red) | steel plate, steel chest | [Steel_processing_research.md] |
| Logistic science pack | 75 × (5 s; 1 red) | logistic science pack | [Logistic_science_pack_research.md] |
| Automation 2 | 40 × (15 s; 1 red + 1 green) | assembling machine 2 | [Automation_2_research.md] |
| Advanced material processing | 75 × (30 s; 1 red + 1 green) | steel furnace | [Advanced_material_processing_research.md] |
| Electric energy distribution 1 | 120 × (30 s; 1 red + 1 green) | medium/big pole, iron stick | [Electric_energy_distribution_1_research.md] |
| Logistics 2 | 200 × (30 s; 1 red + 1 green) | fast belt/underground/splitter | [Logistics_2_research.md] |

- Research consumption: packs/s per pack type = labs × (lab speed) / (unit
  time) [Lab.md] (Production requirements). **derived:** a stream of 100 packs/min
  (1.667/s) on 15 s-per-unit research needs 1.667 × 15 = 25 labs; on 30 s units,
  50 labs.

## Worked target: 100 red + 100 green per minute (derived)

100/min = 1.667/s of each pack. Machine counts = demand / per-machine rate,
using the recipe and speed facts above.

| Product | Demand /s | Per AM1 /s (speed 0.5) | AM1 | Per AM2 /s (0.75) | AM2 |
|---|---|---|---|---|---|
| Automation science pack | 1.667 | 0.1 | 16.7 | 0.15 | 11.1 |
| Logistic science pack | 1.667 | 0.0833 | 20 | 0.125 | 13.3 |
| Inserter (for green) | 1.667 | 1 | 1.7 | 1.5 | 1.1 |
| Transport belt (for green) | 1.667 | 2 | 0.83 | 3 | 0.56 |
| Electronic circuit (for inserters) | 1.667 | 1 | 1.7 | 1.5 | 1.1 |
| Copper cable (3 per circuit) | 5 | 2 | 2.5 | 3 | 1.7 |
| Iron gear wheel (1 red + 1 inserter + 0.5 belt) | 4.167 | 1 | 4.2 | 1.5 | 2.8 |

- Plates: iron = 1.667 × (2 + 5.5) = 12.5/s; copper = 1.667 × (1 + 1.5) =
  4.167/s. That is 40 stone furnaces for iron and 13.3 for copper (0.3125/s each),
  or 20 and 6.7 steel furnaces.
- Ore: 25 electric drills on iron and 8.3 on copper (0.5/s each), or 50 and 16.7
  burner drills.
- Furnace coal: 53.3 stone furnaces × 0.0225 = 1.2 coal/s.
- Electricity: assemblers at full load, about 50 AM1 × 75 kW = 3.75 MW, plus
  34 electric drills × 90 kW = 3.06 MW, plus labs at 60 kW each and inserters at
  15.1 kW each. A 7–9 MW total needs 8–10 steam engines, 4–5 boilers, 1 offshore pump
  and about 2 coal/s for boilers. This is a rough sizing; measure the real grid in game.
- Iron plates (12.5/s) fit one yellow belt (15/s); copper fits on one lane (7.5/s).

## Not found in the cached pages

- Player hand-crafting speed as a number (the cached pages give none).
- Character reach distance in 2.x: [Player.md] history says only "Increased
  player reach from 6 to 10", with no version shown.
- Inserter belt-pickup rates measured on 2.x; the cached ones are labelled 1.1.
