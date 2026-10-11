<!-- wiki-cache title="Player" url="https://wiki.factorio.com/Player" revid="218270" -->
# Player

Source: https://wiki.factorio.com/Player (revision 218270)

## Infobox
- Health: 250
- Category: Logistics
- Map icon:
- Mining speed: 0.5
- Storage size: 80 (Default) / 90 (Modular armor) / 100 (Power armor) / 110 (Power armor MK2) / +10 (Toolbelt (research))
- Prototype type: character
- Internal (prototype) name: character
- Dimensions: 1×1

Factorio is played from the angled top down perspective of the *player*.

The *physical representation* (or the **Engineer**) of the player is the *character*, who is always at the center of view. In multiplayer, player characters will appear in different colors. Color can be set manually with the /color command, see Console. These colors transfer to any entered car or tank, depending on which player is driving them. These colors also transfer to gun turrets, laser turrets or gates, depending on who they were placed by.

The character is **part of the player** and represents the physical existence of the player in the game-world. In technical terms: A character is just one property of the player, and it is the only that can be controlled at a time.

The character's maximum health is 250 (without energy shields), increased by 50 for each level of the health research(Space Age). The player's health can naturally, slowly regenerate a few seconds after taking damage, at 6 hit points per second. The character's main inventory has 80 slots (without bonuses from power armor, toolbelt research, toolbelt equipment(Space Age), or logistic trash slots). Similar to the stationary radar, the character constantly reveals an area of 5×5 chunks, centered on the chunk the character occupies.

## Distinction between player and character
Technically the player is only the "player-view". The player is unlike the *character* (the little person that runs around on the ground). The character is part of the player, but the player is not just the character.

You can for example play in god-mode (such as in the sandbox game mode). In that mode you don't have a character, only a player.

In other words, 'player' is a term that encompasses both the internal code that defines a player, and the entity in game that interacts with machines/rocks/trees, which is the *character*. While this distinction is important for modding and understanding the game's core, the terms can be used interchangeably for most conversations. For the purpose of this article, "player" will be used.

## World interaction
The player has six primary ways of interacting with the world:

1. Crafting items personally from resources using the craft menu (Default open key: E)
1. Placing entities or tiles by selecting them from the inventory or quickbar (Default: lmb)
  1. Opening contextual menus for entities like assembly machines or chests, using the same button
  1. Removing an entity from the world, returning it to your inventory (Default: **Hold** rmb)
1. Harvesting resources from a resource entity (Default: **Hold** RMB)
1. Picking up non-placed items from the ground and placing them in your inventory (Default: Hold/press F)
1. Firing weapons at enemies (Default: Press or hold space depending on weapon)
1. Passively with a flashlight that automatically turns on during the night time (which transfers to headlights if the player is in a vehicle.)

*For more key-bindings, see Controls*

Note: The player can do that only if their character has the abilities for this. For example: They cannot fire a weapon, if they have no weapon slots.

## Death
When a player character is killed it leaves behind a corpse that contains all items that were located in the player's inventory, quickbar, trash slots, and equipment slots. 10 seconds after being killed, the character respawns at the center of the world or at a pre-determined spawn point which can be set via the map editor. The character corpse sprite changes based on the type of armor.

Mining a corpse will attempt to pick up its inventory, and emptying its inventory will destroy the corpse. If it contains armor, the first armor picked up will be automatically equipped if the player is not already wearing armor. However, beware that the armor is not given priority to pick up. If the corpse has a lot of other stuff in it, simply mining the corpse is likely to pick up only as much as will fit in the player's naked inventory and fail to pick up the armor. To ensure the armor is equipped, first open the corpse's inventory, find the armor and pick it up, then pick up everything else.

## Quickbar and shortcut bar
The quickbar is a user interface component for creating links to items that are always visible at the bottom of the screen. Once created they can be quickly selected at any time without needing to open the inventory. It shows between one and four bars from a set of ten available, each containing 10 slots. Clicking any filled slot will place the chosen item in the player's hand if available in the inventory.

The shortcut bar is a group of icons for accessing regularly used features such as obtaining blueprints and deconstruction planners with a simple mouse click. It is always visible at the bottom of the screen, appearing to the right of the quickbar. The icons can be hidden, and their order can be changed.

To the left most side of the screen are the player's equipped weapons and armor, along with the types of ammo being used for each weapon. The player can switch between weapons at any time.

## Gallery
## Trivia
- The character's base speed moves 8.9 tiles per second. Providing that each tile is one meter, the engineer runs 32 km/h, or half the speed of a behemoth biter.
- (Space Age) Quality players have higher health, but there is no way to get higher quality players in the game.

## History
Version 2.0.7:
- Character corpses no longer despawn.

Version 0.18.13:
- The character GUI now has a new look.
  - Personal logistics has been moved to a separate tab. Logistic requests and auto trash have been merged into one panel.
  - Using quick inventory transfers in the player inventory of the character gui will transfer the items either to weapons and armor slots or to trash slots depending on the selected tab, regardless of item type.
- Personal logistics are now unlocked by a single research. This unlocks personal logistic requests and auto trash (unlimited count), plus 30 character trash slots.

Version 0.17.0:
- Increased player reach from 6 to 10.

Version 0.13.14:
- Surplus items from crafting are again available for crafting other items. For example, crafting two green circuits will no longer result in two extra copper wires in the player's inventory. This only applies to items that are automatically crafted as a prerequisite; items the player has explicitly requested to craft will not be used to satisfy the dependencies of any further orders.

Version 0.13.0:
- Armors have inventory size bonuses (10 for modular armor, 20 for power armor, 30 for power armor mk2).

Version 0.12.1:
- Changed fast inventory transfer from the main player inventory so ctrl+clicking empty slots doesn't move items to the logistic trash slots.

Version 0.12.0:
- New muzzle flash graphics.

Version 0.11.4:
- Improved player running animation.

Version 0.11.0:
- New player animation, depends on armor

Version 0.10.9:
- Mining a chest now fails instead of spilling items onto the ground.

Version 0.9.0:
- Player gets a separate warning icon when a building is destroyed.
- Recipe gui contains recipes not craftable by player (however, their tooltip shows machines where they can be crafted).

Version 0.8.0:
- Player now starts with 1 burner mining drill and one stone furnace in the freeplay.
- The player can repair structures using repair packs.

Version 0.7.0:
- Player moves slower while shooting.

Version 0.6.0:
- Added the ability for the player to request items directly from logistic robots.

Version 0.5.0:
- Player picks all items in range when picking items on the ground, instead of 1 per tick
- Shooting particles added

Version 0.4.0:
- Player slides around corners

Version 0.2.8:
- Player no longer collides with Underground belt.
- Added auto-targeting for guns.

Version 0.2.1:
- Added warning message when the player tries to build in an invalid position.

Version 0.2.0:
- Screen reddens when taking damage
- Character animations added

Version 0.1.0:
- Introduced

## See also
- Armor
- Weapons
