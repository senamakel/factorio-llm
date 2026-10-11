<!-- wiki-cache title="Pipe" url="https://wiki.factorio.com/Pipe" revid="220211" -->
# Pipe

Source: https://wiki.factorio.com/Pipe (revision 220211)

## Infobox
- Required technologies: Steam power
- Resistance: Fire: 0/80% / Impact: 0/30%
- Mining time (to pick up): 0.1
- Recipe: 0.5 s; 1 × Iron plate
- Prototype type: pipe
- Internal (prototype) name: pipe
- Category: Logistics
- Health: 100 (by quality normal/uncommon/rare/epic/legendary: 100 / 130 / 160 / 190 / 250)
- Stack size: 100
- Dimensions: 1×1
- Fluid storage volume: 100
- Producers: Assembling machine, Player
- Consumers: Artillery wagon, Boiler, Chemical plant, Engine unit, Flamethrower turret, Fluid wagon, Heat exchanger, Offshore pump, Oil refinery, Pipe to ground, Pump, Pumpjack, Rocket silo, Steam engine, Steam turbine
- Changed by space age mod: yes
- Space age producers: Assembling machine, Foundry, Player
- Rocket capacity: 200 (2 stacks)

The **pipe** is the most basic method of distribution of fluids. It is commonly used to provide water from offshore pumps to boilers and steam to steam engines for power generation, and later on, crude oil and oil products. Unlike transport belts, players and enemies can't walk over them.

Comprehensive information on fluid distribution can be found on the fluid system page.

Attempting to build a pipe that would potentially mix two liquids will fail, as the pipe won't be placed. Undesired fluid can be flushed from the pipe system by opening the pipe GUI and clicking the trash button next to the fluid. Fluids that are flushed from pipes are deleted permanently.

## Alternative recipes
| Process | Input | Output | Made in | Required technology |
|---|---|---|---|---|
| Casting pipe Casting pipe | 1 × Time + 10 × Molten iron | 1 × Pipe | Foundry | Foundry (research) |

## Gallery
## History
Version 2.1.7:
- Pipes and pipes to ground can be connected to the circuit network.
- Added circuit network reads for pipeline contents and fluid temperature to pipes, pipes to ground, and storage tanks.
- Added an interface setting to disable visualization of fluid pipelines when holding a fluid-related entity.
- Added a checkbox and a hotkey (unbound by default) to visualize fluid pipelines that an entity is a member of.
- Fluid pipeline visualization when holding a fluid-related entity will only show in alt mode.
- Removed automatic fluid pipeline visualization on entity hover. Use the pipe GUI or the configurable hotkey to persistently visualize specific pipelines instead.

Version 2.0.7:
- Reworked the fluid system flow logic. (https://factorio.com/blog/post/fff-416)
  - Contiguous sections of pipes and storage tanks are merged into segments.
  - Each segment contains a single fluid, and throughput is proportional to how full a segment is.

Version 0.15.0:
- Increased stack size from 50 to 100.

Version 0.13.0:
- Underground pipes and belts are placed at max connecting distance apart when built by dragging.

Version 0.11.6:
- The Oil refinery and chemical plant are disconnected from pipes if the recipe is reset.

Version 0.10.1:
- Added new icons

Version 0.10.0:
- Unused pipe connections are passive and do not connect to pipes.

Version 0.9.1:
- Pipes now refresh their connection to storage tanks when rotated.
- Small quantities of fluid can be pushed/destroyed by larger quantities in pipes.

Version 0.9.0:
- New graphics.
- All terminating pipes now have visuals.
- Pipes now show fluid inside when ALT mode is enabled.
- Optimized bounding boxes.

Version 0.5.1:
- The boiler is now fast-replaceable with pipes, and vice versa.
- New graphics.

Version 0.2.0:
- Visualization of connection to a pipe to ground.

Version 0.1.0:
- Introduced

## See also
- Pump
- Pipe to ground
- Fluid system
