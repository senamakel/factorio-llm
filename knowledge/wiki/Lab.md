<!-- wiki-cache title="Lab" url="https://wiki.factorio.com/Lab" revid="220199" -->
# Lab

Source: https://wiki.factorio.com/Lab (revision 220199)

## Infobox
- Required technologies: Electronics
- Mining time (to pick up): 0.2
- Prototype type: lab
- Internal (prototype) name: lab
- Category: Production
- Health: 150 (by quality normal/uncommon/rare/epic/legendary: 150 / 195 / 240 / 285 / 375)
- Stack size: 10
- Rocket capacity: 10
- Dimensions: 3×3
- Energy consumption: 60 kW electric
- Research speed: 1 (by quality normal/uncommon/rare/epic/legendary: 1 / 1.3 / 1.6 / 1.9 / 2.5)
- Modules: 2
- Recipe: 2 s; 10 × Electronic circuit + 10 × Iron gear wheel + 4 × Transport belt
- Total raw (per craft): 21.5 s; 15 × Copper plate + 36 × Iron plate
- Boosting technologies: Lab research speed
- Producers: Assembling machine, Player
- Changed by space age mod: yes
- Space age consumers: Biolab

**Labs** are buildings that perform research for technologies by consuming science packs. Use of a lab is required to progress in Factorio.

When productivity modules are used in labs, the productivity bonus is directly calculated and applied each tick so the productivity bar is simply cosmetic. This means that it does not matter that the productivity bar resets when the research is changed, no productivity bonus is lost.

The player can only research one technology at a time, but can use multiple labs for faster results. The speed bonus of labs when lab research speed is researched and modules are present can be calculated using this formula: research_bonus × module_bonus = speed_bonus; the percentage bonuses have to be converted to decimals (e.g. +140% = 2.4) before the formula is used.

Inserters can insert and remove science packs from labs. This allows chaining multiple labs together with inserters, each inserter taking science packs, as needed, from one lab and placing it into the next.

## Production requirements
Calculating the number of science packs needed per second is straightforward:
- `ERS = \left( 1 + \frac{B \left[ r \right] }{100} \right) \times \left( 1 + \frac{M \left[ r \right] }{100} \right) \times BLS`
- `ACT = \frac{T \left[ r \right] }{ERS}`
- `PPS = \frac{N}{ACT}`

Where:
- ***ERS*** is "effective lab research speed"
- ***B[r]*** is the speed bonus from the Lab research speed (research), in percent
- ***M[r]*** is the sum of all module speed effects (speed modules - positive; productivity modules - negative), in percent
- ***BLS*** is the base lab speed, which is adjusted by the quality(Space Age) of the lab
- ***ACT*** is "adjusted cycle time"
- ***T[r]*** is the research cycle time as displayed in the research screen
- ***PPS*** is "packs per second"
- ***N*** is the number of labs available.

Note: while the biolab(Space Age) has twice the speed of a regular lab, it also consumes packs half as fast. As such, the consumption rate of a biolab is the same as the consumption rate of an equal quality regular lab.

Thus, with 10 base quality standard labs, researching Nuclear Power (30 second cycle time) with Lab Research Speed 4 (140% bonus) and no module effects, the calculation is:
- `ERS = 1 + \frac{140}{100} = 2.4`
- `ACT = \frac{30}{2.4} = 12.5 s`
- `PPS = \frac{10}{12.5} = 0.8`

This means 0.8 science packs per second, of each type, would need to be produced to continuously supply the labs.

### Equation simplification
Assuming all labs have the same *B[r]* and *BLS*), the above calculations can be combined into one equation:

- `PPS = \frac{N}{T \left[ r \right] } \times \left( 1 + \frac{B \left[ r \right] }{100} \right) \times \left( 1 + \frac{M \left[ r \right] }{100} \right) \times BLS`

Thus for the numerical example:
- `PPS = 10 \times \left( 1 + \frac{140}{100} \right) \times \frac{1}{30} = \frac{10}{30} \times \left( 1 + 1.4 \right) = \frac{1}{3} \times 2.4 = \frac{2.4}{3} = 0.8` packs per second

If trying to find the amount of labs needed to consume a given amount of packs per second, use the following rearrangement:
- `N = \frac{PPS * T[r]}{\left(1 + \frac{B[r]}{100}\right)\times\left(1 + \frac{M[r]}{100}\right)\times BLS}`

## History
Version 2.1.7:
- Labs can be connected to the circuit network, read contents, read current research cost, read technology level and set current research based on conditions.

Version 0.15.12:
- Lab speed info in the description contains the researched speed bonus as well.

Version 0.12.6:
- The research speed of a lab is now not dependent on its electricity consumption, and can be scripted.

Version 0.12.0:
- Lab research is now continuous; Science packs now have progress bars.

Version 0.9.2:
- Labs are now named after early access backers when built from blueprints.

Version 0.7.2:
- Changed the recipe of Lab to require 4 transport belts, down from 5.

Version 0.7.0:
- Added support for modules to labs.

Version 0.6.0:
- New graphics.
- Labs are dedicated to backers (displayed in entity info).

Version 0.2.7:
- Contents of the Lab is now shown in the entity info.

Version 0.1.0:
- Introduced

## See also
- Electric system
- Crafting
