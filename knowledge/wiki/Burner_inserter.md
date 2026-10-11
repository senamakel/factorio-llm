<!-- wiki-cache title="Burner inserter" url="https://wiki.factorio.com/Burner_inserter" revid="220204" -->
# Burner inserter

Source: https://wiki.factorio.com/Burner_inserter (revision 220204)

## Infobox
- Resistance: Fire: 0/90%
- Mining time (to pick up): 0.1
- Prototype type: inserter
- Internal (prototype) name: burner-inserter
- Category: Logistics
- Health: 100 (by quality normal/uncommon/rare/epic/legendary: 100 / 130 / 160 / 190 / 250)
- Rocket capacity: 50
- Stack size: 50
- Dimensions: 1×1
- Energy consumption: 144 (by quality normal/uncommon/rare/epic/legendary: 144 / 187 / 230 / 274 / 360) kW burner
- Rotation speed: 281°/s (by quality normal/uncommon/rare/epic/legendary: 281°/s / 365°/s / 449°/s / 534°/s / 702°/s)
- Valid fuel: Wood, Coal, Solid fuel, Rocket fuel, Nuclear fuel
- Recipe: 0.5 s; 1 × Iron gear wheel + 1 × Iron plate
- Total raw (per craft): 1 s; 3 × Iron plate
- Boosting technologies: Inserter capacity bonus
- Producers: Assembling machine, Player

The **burner inserter** is the most basic and slowest type of inserters. It is powered by burning fuel, compared to the more advanced inserters which are powered by electricity. It will add fuel to its own supply if it picks any up, which makes it useful for filling boilers with coal. This has the advantage that it will continue working even if the power fails, as opposed to electrically-powered inserters which will be unable to function. It consumes no fuel while idle, though it consumes vastly more energy than most other inserters when active.

Even though it doesn't use electricity, a burner inserter can be connected to and controlled by the logistic and the circuit network.

Burner inserters, like all inserters, do not directly produce any pollution in their operation. However, burner inserters can still indirectly contribute to pollution by consuming fuel, which costs pollution to gather.

## Fuel consumption
A burner inserter consumes no power while idle and does not continuously consume the maximum amount of power when working. Burner inserters spawn with an internal energy buffer of 500 kJ, represented as 25% the value of a piece of wood fuel (which is 2MJ). Aside from not having drain, all its other power characteristics are identical to the rest of the inserters. It simply pulls its joules from its fuel rather than the power grid.

Burner inserters consume around 69.4 kJ per item transfer. That means the inserter can spin just below ~29 times from a single piece of wood (2 MJ). That makes ~58 for coal, and ~173 for solid fuel. With a maximum speed of ~0.79 per second, or inversely ~1.27 seconds per spin, it can run full speed for ~218 seconds before needing refueling using solid fuel. For more detailed information on inserter power characteristics, see inserters.

Burners also have a behavior known as "leeching" where they will pull fuel from their input and commandeer it for their own use. This leeching behavior is not exactly quantified, but it is triggered whenever the internal fuel inventory reaches zero, and performing the action also consumes fuel since motion is never free.

## History
Version 2.1.7:
- Inserters can be flipped to make blueprint flipping reliable.

Version 2.0.7:
- All inserters now have filter option.
- Energy consumption increased from 94.2 kW to 144 kW.
- Burner inserters now reliably pick up items off of fast transport belts and express transport belts.

Version 0.13.2:
- Inserters connected to the circuit network now have the option to only read hand contents.

Version 0.13.0:
- Inserters can now send the item held in hand to the circuit network.
- Inserters are able to squeeze things *slightly* better to belts.
- All types of inserters can be controlled by the circuit and logistic network, once the respective network is researched.

Version 0.12.16:
- Improved burner inserter's fuel searching logic; it will now search both transport belt lines for fuel

Version 0.12.11:
- Burner inserter now grabs fuel for itself even if the target doesn't need it

Version 0.12.2:
- Inserters will never take more than the max stack size of an item.
- Inserters and logistic robots no longer extract from enemy chests
- Inserters now correctly pick up items from splitters

Version 0.12.1:
- Burner inserters start with enough energy to pick up 1 item and fuel themselves.

Version 0.12.0:
- Inserters can now extract from roboports and beacons.
- Inserters now take items from right behind them, not from the center of the pickup target entity.

Version 0.10.0:
- New icon
- New sounds

Version 0.9.2:
- Inserters can have arbitrary pickup and insert positions.

Version 0.9.0:
- Inserter code optimisation, inserters that have nothing to do will sleep.

Version 0.8.0:
- Improved inserter's ability to pull from train wagons.

Version 0.7.1:
- Fast inserter now has the same speed as the smart inserter.

Version 0.5.0:
- Inserter can now pick up up to 5 items when researched.

Version 0.4.0:
- Smaller inserter bounding box

Version 0.3.0:
- New Inserter graphics

Version 0.2.1:
- The item in the hand of the inserter is returned to the player when mined.

Version 0.2.0:
- Show direction of inserter

Version 0.1.0:
- Introduced

## See also
- Inserters
