<!-- wiki-cache title="Research" url="https://wiki.factorio.com/Research" revid="217102" -->
# Research

Source: https://wiki.factorio.com/Research (revision 217102)

**Research** is used to unlock technologies, offering new recipes and bonuses. Research is performed by labs consuming different types of science packs.

## Mechanics
In singleplayer games, only one technology can be researched at a time. The same is true for every force (team of players) in a multiplayer game. In multiplayer games with multiple forces, each force has its own technology tree and research status, so different forces can research independently in PvP games.

The technology to be researched is selected from the technology screen, opened by pressing T (ZL - on Nintendo Switch). The currently active research can be changed at any time from the technology screen; if another research is in progress, that progress will be saved. Multiple technologies can be partially researched like this at any one time.

Research progress for a technology is divided into *units*. Each unit has a time and a science pack cost. When research is in progress, labs with the required amount of science packs for one unit will consume the amount and contribute towards research progress.

The time *T* it will take to research a particular technology is given by:

- T = (T[0] × P) ÷ (L × S) seconds,

where:
- ***T[0]*** is the time cost per unit (as shown in Research screen)
- ***P*** is the price of the research, in units (as shown in Research screen)
- ***L*** is the number of labs used
- ***S*** is lab speed, which is given by:
  - (1 + B[r]) × (1 + M[r]), where
  - ***B[r]*** is the total research speed modifier from lab research speed research, expressed as a decimal (% value divided by 100); and
  - ***M[r]*** is the sum of all module effects (Speed modules with + sign, Productivity modules with - sign), expressed as a decimal

*Note that *P* represents the research price **in units**, not in individual science packs summed across all their types. For example, a research that costs 100 automation science packs and 100 logistic science packs, grouped into 100 units of 1 each of automation and logistic science packs, would have a *P* of 100, *not* 200.*

Unlike most bonus effects, the lab research speed bonus gained from research is *multiplicative* with module speed effects, not additive. However, different module effects (Speed vs. Productivity, beacon vs. in-lab) are additive with each other.

### Automation
Crafting science packs by hand is not feasible, mainly because of the amount of resources and time needed to craft them. Some science packs also require ingredients that cannot be handcrafted, such as oil products. Science pack production automation is the primary incentive for factory development throughout the game.

The insertion of science packs into labs may be automated using inserters and transport belts, as shown to the right, or using robots and the logistic network.

Note that inserters can take science packs from labs and hand them to other labs, making a lab chain a feasible solution. Other options include using 3 belts (before space science packs are needed), or a sushi belt.

### Research queue
The research queue allows players to automatically research more technologies after research finishes. The research queue is enabled for new games.

Once the research queue is enabled, a technology can be added to the queue by pressing the "Start Research" button when it is selected. Double-clicking (Double-pressing Y or A on Nintendo Switch) or using shift lmb (ZR A on Nintendo Switch) on any research in the tree or the list on the left will also add it to the queue. This is particularly useful to queue prerequisites without focusing them in the technology tree.

Technologies in the queue are displayed in the upper left corner of the interface. If a technology is added to the queue, the technologies that depend on it may become available to be added to the queue as well and those technologies are displayed in orange. For example adding the logistics and logistic science pack technologies to the queue allows the technology logistics 2 to be queued. The player can reorder the queue at any time.

To remove a technology from the queue, the technology's image must be hovered in the queue display in the upper left corner and the red button that appears must be pressed.

## Achievements
- Completing infinite technologies of any level is not required for **Tech maniac**. All non-infinite levels of technologies that have infinite continuations are still required.

## History
Version 2.0.7:
- Now displays the player's SPM (science per minute) in a graph.

Version 1.1.92:
- Added a notification when a technology is researched.
- Added /enable-research-queue console command to enable the research queue without disabling achievements.
- The research queue is enabled by default for new games.

Version 0.17.0:
- Research UI overhauled.
- Research Queue added.

Version 0.15.0:
- Research system overhauled
  - There are now 7 science pack types instead of 4, research prices have been changed to compensate.
  - Top-tier science pack is no longer obtained by destroying alien nests, but by launching rockets with satellites.
  - "Infinite research" mechanic introduced.

Version 0.2.0:
- Introduced

## See also
- Technologies
- Science pack
