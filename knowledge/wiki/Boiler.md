<!-- wiki-cache title="Boiler" url="https://wiki.factorio.com/Boiler" revid="220197" -->
# Boiler

Source: https://wiki.factorio.com/Boiler (revision 220197)

## Infobox
- Required technologies: Steam power
- Resistance: Explosion: 0/30% / Fire: 0/90% / Impact: 0/30%
- Mining time (to pick up): 0.2
- Prototype type: boiler
- Internal (prototype) name: boiler
- Category: Production
- Health: 200 (by quality normal/uncommon/rare/epic/legendary: 200 / 260 / 320 / 380 / 500)
- Stack size: 50
- Rocket capacity: 50 (1 stack)
- Dimensions: 2×3
- Fluid consumption: 6/s (by quality normal/uncommon/rare/epic/legendary: 6/s / 7.8/s / 9.6/s / 11.4/s / 15/s)
- Energy consumption: 1.8 MW (by quality normal/uncommon/rare/epic/legendary: 1.8 MW / 2.34 MW / 2.88 MW / 3.42 MW / 4.5 MW) burner
- Heat output: 60/s (by quality normal/uncommon/rare/epic/legendary: 60/s / 78/s / 96/s / 114/s / 150/s) steam
- Pollution: 30/m (by quality normal/uncommon/rare/epic/legendary: 30/m / 39/m / 48/m / 57/m / 75/m)
- Fluid storage volume: Input: 200 / Output: 200
- Valid fuel: Wood, Coal, Solid fuel, Rocket fuel, Nuclear fuel
- Recipe: 0.5 s; 4 × Pipe + 1 × Stone furnace
- Total raw (per craft): 3 s; 4 × Iron plate + 5 × Stone
- Producers: Assembling machine, Player
- Changed by space age mod: yes
- Space age consumers: Heating tower

The **boiler** uses fuel to convert water into steam at 165°C suitable for use in a steam engine. It has two water connectors on opposite ends and passes water through to adjacent equipment such as other boilers. The boiler features a single output for the steam it produces. It only consumes fuel as it creates steam. Boilers used in conjunction with offshore pumps and steam engines are a vital part of early power generation.

For each unit of water, 10 units of steam are produced. Inserting one coal (4 MJ) into a boiler then using the resulting steam in a steam engine will supply 4 MJ of energy to an electrical system. It costs 300 kJ to heat 1 unit of water to into 10 steam at 165°C, so one boiler will produce 60 steam per second.

Inserters can insert fuel into boilers. However, using powered inserters to move fuel into a boiler can be problematic should fuel become unavailable: if no power is being produced, then powered inserters fueling a boiler cannot operate. Inserters can also remove fuel from boilers, allowing inserters to move fuel down a chain of boilers.

Using at least one burner inserter, which uses fuel and not electricity, ensures that at least one inserter is available to restart a single boiler. On larger power grids a single burner may not be satisfactory to restart the grid since inserter will spin very slowly due to lack of electrical satisfaction, and won't be able to input coal to one section fast enough before the previous section runs out again, thus never achieving proper uptime or a successful restart.

A single boiler requires a piece of coal roughly every ~2.2... seconds (4/1.8), or 0.45 coal/second. Higher density fuels adjust consumption accordingly (wood is consumed twice as fast, solid fuel 3 times slower, etc). A single full yellow belt of coal (15 coal/second) can supply 60MW of power, feeding ~33.3... boilers.

## History
Version 2.1.7:
- Boilers and heat exchangers can be connected to the circuit network.

Version 2.0.7:
- 1 Water will now produce 10 Steam in boilers/heat exchangers.

Version 0.15.10:
- Steam became a separate resource, boilers now produce steam rather than high temperature water that is displayed as steam
  - This distinction is meaningful for circuit network accounting of steam and the coal liquefaction recipe

Version 0.15.0:
- New graphics.
- Changed boiler dimensions to 3×2.
- 'Steam' is produced on a separate connector rather than heating water passed through.
  - At this time, steam is actually water that is renamed when over 100 degrees.
- Significantly increased energy consumption/production.

Version 0.13.0:
- New fire graphics for boilers.

Version 0.9.2:
- Enabled the inserter to take fuel out of boilers.

Version 0.8.0:
- Flickering light added to furnaces and boilers.

Version 0.6.1:
- Boilers show their fuel inventory in the entity info.

Version 0.5.1:
- Boilers are now fast-replaceable with pipes.
- New boiler graphics.

Version 0.1.0:
- Introduced

## See also
- Electric system
- Fluid system
