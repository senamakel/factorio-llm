<!-- wiki-cache title="Fuel" url="https://wiki.factorio.com/Fuel" revid="220072" -->
# Fuel

Source: https://wiki.factorio.com/Fuel (revision 220072)

**Fuel** can be inserted into burner devices and burned to power them. Different fuels provide different amounts of energy, measured in megajoules (MJ).

## Burnable fuel
The most common fuel type is burner fuel.

This is a list of all items usable as fuel in burner devices:

| Item | Fuel value | Fuel value per raw total | Fuel value / per stack | Fuel Value / per rocket | Vehicle / acceleration | Vehicle / top speed | Train max speed1 |
|---|---|---|---|---|---|---|---|
| Wood | 2 MJ | 2 MJ per wood | 200 MJ | 1 GJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Coal | 4 MJ | 4 MJ per coal | 200 MJ | 2 GJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Solid fuel | 12 MJ | 0.96 MJ per unit of crude oil2, or / 8.7 MJ per coal3 | 600 MJ | 12 GJ | 120% | 105% | 272.2 km/h (~75.6 m/s) |
| Carbon | 2 MJ | 1 MJ per coal | 100 MJ | 2 GJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Rocket fuel | 100 MJ | 0.8 MJ per unit of crude oil2 | 2 GJ | 10 GJ | 180% | 115% | 298.1 km/h (83 m/s) |
| Nuclear fuel | 1.21 GJ | 9.68 MJ per unit of crude oil2, and / 40.89 MJ per uranium ore4 | 1.21 GJ | 12.1 GJ | 250% | 115% | 298.1 km/h (83 m/s) |
| Yumako seed | 4 MJ | 80 kJ per crop4 | 40 MJ | 400 MJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Jellynut seed | 4 MJ | 80 kJ per crop4 | 40 MJ | 400 MJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Tree seed | 100 kJ | 50 kJ per wood | 1 MJ | 10 MJ | 100% | 100% | 259.2 km/h (72 m/s) |
| Yumako | 2 MJ | 2 MJ per crop | 100 MJ | 2 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |
| Jellynut | 10 MJ | 10 MJ per crop | 500 MJ | 10 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |
| Spoilage | 250 kJ | 250 kJ per crop5 | 50 MJ | 500 MJ | 50% | 50% | 129.6 km/h (36 m/s) |
| Yumako mash | 1 MJ | 2 MJ per crop | 100 MJ | 2 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |
| Jelly | 1 MJ | 4 MJ per crop | 100 MJ | 2 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |
| Biter egg | 6 MJ | 6 MJ per egg | 600 MJ | 3 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |
| Pentapod egg | 5 MJ | 5 MJ per egg | 100 MJ | 1 GJ6 | 100% | 100% | 259.2 km/h (72 m/s) |

(1) For the purposes of in-game speed display, the game assumes 1 tile = 1 meter. I.e., a train on basic fuel travels at 72 **tiles** per second at full speed, and so on.

(2) This assumes all crude oil is processed completely into solid fuel using advanced oil processing and heavy oil cracking as intermediate steps, but not light oil cracking. More efficient methods are possible; in practice, the petroleum gas is more likely to be used for something other than solid fuel.

(3) Using coal liquefaction and heavy oil cracking, converting all light oil and petroleum gas into solid fuel. Does not include energy requirements of refining/mining.

(4) This assumes the "cost" is what would have been gained if all seeds were planted and the grown plant was harvested, i.e. 50 yumako or jellynut.

(5) Fuel value per raw for spoilage varies a lot on the item spoiled and if they were made using the biochamber's 50% base productivity. 250 kJ assumes spoilage directly from yumako or jellynut crops.  This is can go as high as about 2.43 MJ per crop using nutrients from bioflux (60 nutrients from 4.16 yumako and 1.66 jellynuts with 3.21 nutrients spent running biochambers).

(6) These products spoil, and thus are usually not suitable fuels to move between planets.

## Other fuel types
These fuels are consumed by specific entities and cannot be placed into standard burners.

| Item | Fuel type | Fuel value | Fuel value / per stack | Consumed by | Consumption rate / (watts) | Consumption rate / (items) |
|---|---|---|---|---|---|---|
| Uranium fuel cell | Nuclear fuel | 8 GJ | 400 GJ | Nuclear reactor | 40 MW | 1 per 200s2 |
| Fusion power cell | Fusion fuel | 40 GJ | 2 TJ | Fusion reactor | 100 MW | 1 per 400s2 |
| Thruster fuel | Fluid1 | 50 kJ |  | Thruster | 0.3 MW - 6.0 MW | 6/s - 120/s2 |
| Thruster oxidizer | Fluid1 | 50 kJ |  | Thruster | 0.3 MW - 6.0 MW | 6/s - 120/s2 |
| Nutrients | Nutrients | 2 MJ | 200 MJ | Biochamber | 500 kW | 1 per 4s |
| Bioflux | Food | 6 MJ | 600 MJ | Captive biter spawner | 100 kW | 1 per 60s |

(1) Thruster fuel and oxidizer have a fuel value but technically do not have a fuel type.  Since they can only be consumed by thrusters which require specific fluids, they are effectively their own fuel types.

2 Most of these fuel consumers increase their fuel consumption rate with quality. However, because the biochamber and captive biter spawner are crafting machines, quality versions of them do not consume fuel faster despite their faster processing speed. They instead become more fuel efficient, producing more output for the same amount of fuel.

## Consumption
The following formula can be used to find how long a fuel will last in a device:
Burn time (s) = Fuel value (MJ) ÷ Energy consumption (MW)

How quality(Space Age) affects burn time depends on the kind of machine in question. Crafting machines do not increase energy consumption with higher quality. As such, crafting machines that run on a fuel, like the stone furnace or biochamber, do not change their burn time with quality.

Inserters like the burner inserter do not increase their energy consumption per-swing, but they do swing faster. As such, higher quality burner inserters can consume more fuel based on this.

The burner mining drill does not get faster with quality, so it does not consume more energy. The car and tank vehicles do not change their energy consumption with quality.

All other entities which use fuel do scale their energy consumption, and thus burn time, with quality. This includes locomotives.

## Trivia
- Though the top speeds given by solid fuel, rocket fuel and nuclear fuel are presented as +5%, +15% and +15% respectively, this seems to only be true for trains. The top speeds for cars and tanks are instead approximately +9.5%, +34% and +58% respectively when these fuels are used.

## History
Version 0.15.0:
- Fuel type affects vehicle acceleration and top speed.

## See also
- Burner devices
  - Burner inserter Burner mining drill Boiler Heating tower Stone furnace Steel furnace Locomotive Car Tank
- Electric system
- Nuclear Ratios
