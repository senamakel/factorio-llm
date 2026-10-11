<!-- wiki-cache title="Crafting" url="https://wiki.factorio.com/Crafting" revid="217120" -->
# Crafting

Source: https://wiki.factorio.com/Crafting (revision 217120)

The process of 'crafting' is to produce an end product off of input products using a recipe. The player or a variety of buildings like Assembling machines can craft materials. Smelting is a particular kind of crafting that can only be done by furnaces. Since smelting cannot be done by the player, it is impossible to craft some items directly from raw resources.

In the beginning of the game, it is easy to make everything manually, but as the game advances, manual crafting is less and less efficient of a way to create. Products that require liquids and a few others (such as engine units) cannot be manually crafted. This is to encourage automation. The more advanced or expensive an item is, the more time it may take to craft.

## Achievements
## Manual crafting
Manual crafting is the most basic form of crafting, it is done directly in the player's inventory. To manually craft an object, open the player's inventory with E (X on Nintendo Switch), and select an object to manually craft on the right. Left click for one, right click for five, and shift click to make as many as possible. If the image of the item is grayed out, ensure you have the materials necessary to craft the object. If you lack a resource, it will be shown highlighted in red text if you mouse-over the product. Materials that you don't have but you can craft will be highlighted in orange text, and will be chain-crafted to reach the product you selected. This is an advantage over automatic crafting using machines, which do not automatically create intermediate ingredients.

While manually crafting, there will be icons in the bottom left of the screen, which shows the current crafting operation. When an item is selected for crafting, the resources will be preemptively taken from the player's inventory. If that operation is then canceled, the items will be fully returned to the player.

To cancel a manual crafting operation from the queue at the bottom left of the screen, left click (to cancel one operation), right click (to cancel five operations), or shift-left click to cancel all crafts of that item. This is useful if you accidentally queue the wrong product, or too many of a product. All the materials taken to craft the item will be returned to your inventory. Manual crafting can be canceled at any time, but already-crafted intermediate products will not be uncrafted.

There are many kinds of materials which cannot be manually crafted and must be crafted by a machine:

- Ores can only be smelted in a furnace.
- Any recipe that involves liquids must be processed in a machine.
- Engine units must be crafted in an assembling machine.

If the result of any of these recipes is used as the input to something which can be manually crafted, the player must have that intermediate product in their inventory to craft the item.

## Automated crafting
Automated crafting is done outside of the player's inventory, allowing for multiple products to be produced at once, in synchronous harmony. This is where most crafting should take place.

Key structures in automated crafting are:

| Resource extraction | Resource extraction |
|---|---|
| Burner mining drill | Mines solid resources from surface deposits. |
| Electric mining drill |  |
| Big mining drill |  |
| Offshore pump | Extracts unlimited quantities of water and other fluids(Space Age) from lakes, swamps and oceans. |
| Pumpjack | Extracts crude oil and other fluids(Space Age) from natural deposits. |
| Agricultural tower | Plants seeds and harvests mature plants. |
| Captive biter spawner | Produces biter eggs. |
| Furnaces | Furnaces |
| Stone furnace | Processes raw minerals to their base metal, by smelting. |
| Steel furnace |  |
| Electric furnace |  |
| Foundry | Produces molten metal from lava (with stone as a byproduct) or ore. |
|  | Fabricates items from molten metal. |
| Recycler | Recycles items into their ingredients. |
| Production | Production |
| Assembling machine 1 | Cannot handle fluid ingredients. |
| Assembling machine 2 | Can handle recipes requiring fluid ingredients. |
| Assembling machine 3 |  |
| Electromagnetic plant |  |
| Biochamber |  |
| Oil refinery | Processes crude oil and other fluids. |
| Chemical plant |  |
| Cryogenic plant |  |
| Centrifuge | Process uranium ore into more useful intermediate products. |

## Basic
As an introduction to crafting, let's craft some simple iron plates.

**Task**: create Iron plates.

Steps:
1. Place a Burner mining drill onto an Iron ore resource field. This is a silvery patch that is fairly common.
1. Place a Furnace directly in front of the output (press Alt to show output arrow), so that the miner outputs the ore into the furnace, which can receive on any side.
1. Fill both the miner and the furnace with Fuel, such as coal or logs.
1. Wait. After a few seconds, the first piece of Iron plate is smelted and available for collection. Either collect it manually, or pull it out with an inserter.

This entire process is commonly referred to as 'smelting'. Copper ore must also be smelted.

## Advanced
Crafting of items can be automated. To automatically craft items, place a Assembling machine, and select the recipe. Note that if the recipe is complicated enough, higher tiers of assembling machines may be necessary. Then, place all requested ingredients into the input slots, and the assembling machine should craft the item. Note that unlike manual crafting, each step of the craft requires another assembly machine. For example, crafting a lamp requires a machine to make copper cable, a machine to make iron sticks, a machine to make electronic circuits, etc. *Assembly machines cannot automatically chain-craft like the player.*

To keep up continuous production ingredients must be provided via belts and Inserters. The manufactured items can also be extracted by Inserters and are then available for further usage elsewhere in the factory.

## History
Version 0.15.0:
- Crafting now pauses when the results cannot fit into the player's inventory.

Version 0.13.4:
- Surplus items are used for crafting further items, instead of being dropped into the inventory.

Version 0.13.0:
- Crafting counts are recorded per force.

Version 0.11.15:
- Order of inputs/outputs for fluid in machines is now constant.

Version 0.11.9:
- Inventory now sorts properly when god mode crafting.

Version 0.11.0:
- Event "on_player_crafted_item" is now called for every single finished item.

Version 0.10.3:
- Crafting GUI now supports scrolling.

Version 0.9.4:
- Recipes can now be hidden, so they don't appear in the player crafting screen.

Version 0.9.2:
- Crafting GUI now resizes dynamically to fit the largest size.
- Only play crafting sound when final product is finished.

Version 0.9.0:
- Updated/added sounds for crafting.

Version 0.8.0:
- Unified crafting time, crafting time is now 1:1 with manual crafting.

Version 0.5.0:
- Recipes categorized better.
- Recipes can now cost nothing but time.

Version 0.4.0:
- Wider item selection screen.

Version 0.2.10:
- Tool tip in technology preview now shows total raw.

Version 0.2.9:
- Recipes are categorized.

Version 0.2.8:
- Intermediate items in the crafting queue now show in a different color.
- Canceling crafting now cascades to all ingredients.

Version 0.1.0:
- Introduced

## See also
- Electric system
- Assembling machine
- Furnace
