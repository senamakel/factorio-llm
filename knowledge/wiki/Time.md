<!-- wiki-cache title="Time" url="https://wiki.factorio.com/Time" revid="209863" -->
# Time

Source: https://wiki.factorio.com/Time (revision 209863)

The concept of **Time** in Factorio is used for many different implements, most notably crafting time and game time.

## Crafting time and speed
When hovering over an item recipe, the player may see a clock symbol and a number. This is the amount of time needed to craft the item in seconds at crafting speed 1. The player always crafts at speed 1 while assembling machines have different crafting speeds. Modules may also affect crafting time, either speeding it up or slowing it down for some other benefit. The player, when handcrafting, crafts with a multiplier of 1, so items that claim to take 10 seconds to craft will take 10 seconds, but an assembling machine 1 with a multiplier of 0.5 will take 20 seconds. It is important to take this into consideration when creating setups with proper ratios.

## Ticks
The base unit of all time inside Factorio. When running at game speed 1, there should always be 60 ticks in every real-time second leading to the figure of 60 updates per second, short UPS. This means that 1 tick should ideally always take 1/60th of a real-time second (0.01667 seconds). However, it is possible to change the game speed using mods or console commands, so it is possible that ticks don't take 0.01667 real-time seconds. Furthermore, game speed will automatically slow down when the computer that is running the game is unable to do all needed calculations in the wanted 0.01667 real-time seconds. The "show-fps" debug option allows to see the current UPS which can be used to estimate how long a tick currently takes.

## Seconds
As stated above, there should always be 60 ticks in every second, so 1 in-game second equals 60 in-game ticks. The 60 to 1 ratio is also applied when the game runs at lower speeds, so an in-game second can take longer than a real-time second.

## Days
An in-game day on Nauvis lasts 25200 ticks or 7 in-game minutes.

The light varies throughout the day in a cycle consisting of 4 phases:

| Phase Name | Internal name | Behaviour | Time of day at start | Time of day at end | Duration (in ticks) | Duration (in seconds) |
|---|---|---|---|---|---|---|
| day | dawn | fully light | 0.75 | 0.25 | 12600 | 210 |
| sunset | dusk | darkening | 0.25 | 0.45 | 5040 | 84 |
| night | evening | fully dark | 0.45 | 0.55 | 2520 | 42 |
| sunrise | morning | lightening | 0.55 | 0.75 | 5040 | 84 |

   ------------- day -------><----- sunset ----->< night -><----- sunrise ----><-------- day ------------

 % 0    5    10   15   20   25   30   35   40   45   50   55   60   65   70   75   80   85   90   95  100
   |----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|

During sunset, the light level decreases linearly from fully light to fully dark. During sunrise, it increases linearly from dark to light. This linear slope does not necessarily apply to the values returned by LuaSurface.darkness. During night time, players will passively activate their flashlights (or headlights if in a vehicle), and placed lamps will turn on automatically if powered.

Note: The actual time between phases can vary +/- a tick due to rounding errors.
