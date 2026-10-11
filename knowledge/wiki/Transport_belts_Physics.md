<!-- wiki-cache title="Transport belts/Physics" url="https://wiki.factorio.com/Transport_belts/Physics" revid="217446" -->
# Transport belts/Physics

Source: https://wiki.factorio.com/Transport_belts/Physics (revision 217446)

The belt transport system in Factorio is among the most detailed simulations in the game. Items in chests and other containers are stored simply as summed totals, and items on uninterrupted stretches of belts are moved in aggregate as an optimization, but in the end items on belts are simulated individually, especially when they get picked up or put down by inserters. This leads to some intricate behaviors, in particular when it comes to inserter throughput.

## Belt properties
- **Density**. How many items fit onto a certain length of belt, measured in items per tile per belt lane. This is 4 on a straight belt, regardless of the type of item and type of belt. The item density on belts can be different from what they take up when just dropped on the ground (using the Z key). Density of items can be increased with the use of stack inserters(Space Age), but there are still at most 4 stacks per tile per lane.
- **Speed**. The speed of items on a belt is measured for practical reasons in tiles per second. Note that internally it is measured in positions (1/256 tile) per tick (1/60 sec). More on that below. The speed of a basic transport belt is 1.875 tiles per game-second. Fast transport belt is twice as fast, express transport belt is three times as fast, and turbo transport belt(Space Age) is four times as fast.
- **Throughput**. How many items per second that are moved from one tile to the next. That is density (items per tile) multiplied by speed (tiles per second), e.g. for a basic belt it is 4 * 1.875 = 7.5 items per second, for one belt lane. For both lanes it is doubled, i.e. 15 items per second.
- **Compression**. If there is no empty space between items on the belt it is called *fully compressed*, otherwise its compression is only partial and it does not have optimal throughput. Entities that put items onto belts – inserters, splitters, other belts coming from the side, mining drills, etc - make room for their item by enlarging a small gap until it is exactly big enough for the item. That means belts naturally become fully compressed before items start to back up.
- **Lanes**. Belts have two parallel lanes, and the density and speed of each lane is constant and independent of the other one, regardless of twists and turns. So items in the inner lane of a turn exit it before those in the outer lane, since their speeds are equal and the inner lane is shorter than the outer one.

## Belt speeds
Given the values above we can calculate the speed and throughput of the three types of belts. Measurements confirm these values.

| Belt type | Speed | Speed | Throughput | Throughput | Throughput | Throughput |
|---|---|---|---|---|---|---|
|  | Factor | Tiles/sec | Single lane, items/sec | Single lane, items/min | Both lanes, items/sec | Both lanes, items/min |
| Transport belt | 1 | 1.875 | 7.5 | 450 | 15 | 900 |
| Fast transport belt | 2 | 3.75 | 15 | 900 | 30 | 1800 |
| Express transport belt | 3 | 5.625 | 22.5 | 1350 | 45 | 2700 |
| Turbo transport belt | 4 | 7.5 | 30 | 1800 | 60 | 3600 |

## Items on belts
As mentioned earlier, items take space on belts in terms of density and compression. However, every item on a belt is logically *on* exactly one belt tile at any moment in time.

For example, even though in a screenshot it might look like an item is halfway out from one tile and halfway onto the next, it will be accounted to exactly one of the two tiles:
- If you stop the belt tile the item is on, it stops; else it continues moving - there are no in-between states.
- If you connect the two belt tiles to a circuit network and get them to report statistics about the items they carry, you will see the item being accounted to exactly one of them.
- An inserter can only pick up items that are logically on the tile in front of it, not items butting in from the neighboring tiles.

In this sense it is useful to think of items as points with a certain minimum distance between them, rather than things with an area lying next to each other. For belt calculations and circuit networks involving belts it doesn't really matter where those "center points" are within the graphic of the item, but they appear to be in the middle:

In the image above the belts have been started at 1 tick offsets, then all the top row tiles have been stopped at once, causing the front-most stopped items to poke out by varying amounts. The items on the leftmost belt are almost halfway into the next tile, which means their center points are the closest to the edge of the upper stopped tile.

Below is a schematic example showing some items moving over two straight fast transport belt tiles and what their read signals would be at each tick. Their center points are marked with *. (The space between belt tile 1 and 2 is only for visualisation - in the game there are no such gaps between tiles.)

```
Tick  Belt tile 1                      Belt tile 2                       Read belt tile 1  Read belt tile 2
      |------------------------------| |------------------------------|    Pulse   Hold      Pulse   Hold
  0         <---*-->  <---*--> <---*-- ><---*-->            <---*-->         0       3         0       2
  1           <---*-->  <---*--> <---* --><---*-->            <---*-->       0       3         0       2
  2             <---*-->  <---*--> <-- -*--><---*-->            <---*--      0       2         1       3
  3               <---*-->  <---*--> < ---*--><---*-->            <---*      0       2         0       3
  4   ->            <---*-->  <---*-->  <---*--><---*-->            <--      0       2         0       2
  5   *-->            <---*-->  <---*- -> <---*--><---*-->            <      1       3         0       2
  6   --*-->            <---*-->  <--- *--> <---*--><---*-->                 0       2         1       3
  7   <---*-->            <---*-->  <- --*--> <---*--><---*-->               0       2         0       3
  8     <---*-->            <---*-->   <---*--> <---*--><---*-->             0       2         0       3
```

## Belt positions and lengths
Careful measurement shows that the outer lane of a turn is exactly 1.15234375 times longer than a straight belt, or 295/256 in fractional format. That means each straight belt tile has 256 *positions* an item can be in, even though measuring the position with that precision can only be done indirectly. This has since been confirmed by the devs.

Here are the speeds and lengths of the various types of belt tiles in terms of these positions:

| Belt | Belt | Item Speed (Positions per Tick) |
|---|---|---|
| Transport belt | Transport belt | 8 |
| Fast transport belt | Fast transport belt | 16 |
| Express transport belt | Express transport belt | 24 |
| Turbo transport belt | Turbo transport belt | 32 |

| Measurement | Measurement | Length (Positions) |
|---|---|---|
| Distance between items on a saturated belt (of any speed) | Distance between items on a saturated belt (of any speed) | 64 |
| Length of one lane of a straight belt | Length of one lane of a straight belt | 256 |
| Length of inner lane of a belt turn | Length of inner lane of a belt turn | 106 |
| Length of outer lane of a belt turn | Length of outer lane of a belt turn | 295 |
| Length of one lane of an underground belt | Length of one lane of an underground belt | 256 |
| Length of one lane of a splitter's input | Length of one lane of a splitter's input | 128–179† |
| Length of one lane of a splitter's output | Length of one lane of a splitter's output | 128 |
| Distance travelled by an item sideloaded late on a straight belt / or an underground exit |  | 68 |
| Distance travelled by an item sideloaded early on a straight belt / or an underground entrance |  | 188 |

† Splitters have 128 normal positions, plus an invisible internal buffer of 51 positions that is used to align items before merging them with another transport line. Items in the buffer can "teleport" to the appropriate output lane at any time, including immediately, so the buffer may appear to be anywhere from 0 to 51 positions long depending on the exact circumstances.

For example, given the figures above, we can deduce the speed of a basic belt:

8 (positions per tick) / 256 (positions per straight belt tile) * 60 (ticks per second) = 1.875 tiles per second

Its throughput per belt lane is:

8 (positions per tick) / 64 (positions per item) * 60 (ticks per second) = 7.5 items per second

## See also
- Belt transport system
- FFF #287: Just bugs again
- FFF #276: Belt item spacing & Script rendering
- FFF #231: Belt compression & Crash log uploading
- FFF #176: Belts optimization for 0.15
- Accurate belt segment measurements (discusses 0.17)
- About belt numbers, from boskid
