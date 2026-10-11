<!-- wiki-cache title="Technologies" url="https://wiki.factorio.com/Technologies" revid="219704" -->
# Technologies

Source: https://wiki.factorio.com/Technologies (revision 219704)

**Technologies** are series of research projects that provide various enhancements. Some technologies unlock new items or recipes, while others provide bonuses.

Most technologies can be researched in labs by consuming science packs of various types. For example, the Logistics technology can be unlocked by placing 20 automation science packs into labs while the technology is selected for research.  Besides, some technologies will automatically unlock after meeting specific conditions, without consumption of any science packs.

## Infinite technologies
While most technologies in Factorio are either one-off or have a finite, relatively small number of levels available, a few are "infinite", meaning the player can research as many levels as they can afford. All of them unlock bonuses to existing technologies, never new structures or abilities. The per-level bonuses are constant for a particular infinite technologies and, like finite research bonuses, are additive within a single technology. They are subject to diminishing returns; thus, the per-level and per-science pack contributions from very high levels of infinite technologies will eventually provide only marginal improvements.

All base game infinite technologies levels require space science packs, and are also the only technologies that do. As such, they are late-game technologies intended primarily for players who wish to continue playing and expand their factory past the nominal victory condition of launching a rocket.

Infinite technologies are identified in-game by a small ∞ infinity symbol shown in the top right corner of the research technology's card in the research screen.

Most infinite technologies are continuations of ordinary multi-level technologies; the "infinite" mechanic becomes effective once the player reaches the card initially labeled with N - ∞ in the research tree.  In the base game, only the two artillery-related technologies (artillery shell range and shooting speed) are infinite-only; for these, 1 - ∞ is shown before any levels in them are researched. In either case, once the first infinite level is researched, the card label switches to the one discussed above.

### Pricing formulas
The price of all infinite technologies is generated in a mathematical progression; for the majority of technologies, the progression is geometric, mostly in powers of 2. Two technologies - mining productivity and follower robot count - use an arithmetic progression instead.

The table below summarizes for all infinite researches their first infinite level, the cost of the first few infinite levels, the cost formula and the per-level bonus.

We denote by N the current level of the research, by F the final non-infinite level of the research (hence F+1 is the first "infinite" level) and by P[N] the price of the research at level N.

| Technology | Category | Bonus | Science Packs | F+1 | P[N] | P[F+1] | P[F+2] | P[F+3] | P[F+4] | P[F+5] | ... |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mining productivity (research) Mining productivity | Productivity | +10% Mining productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Utility science pack Space science pack | 4 | 2,500 × (N - F) | 2,500 | 5,000 | 7,500 | 10,000 | 12,500 | +2500 |
| Physical projectile damage (research) Physical projectile damage | Weapon Damage | +40% Bullet damage / +70% Gun turret damage / +40% Shotgun shell damage / +100% Cannon shell damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | 2,000 | 4,000 | 8,000 | 16,000 | ×2 |
| Stronger explosives (research) Stronger explosives | +50% Rocket damage / +20% Grenade damage / +20% Land mine damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | 2,000 | 4,000 | 8,000 | 16,000 | ×2 |  |
| Refined flammables (research) Refined flammables | +20% Fire damage / +20% Flamethrower turret damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | 2,000 | 4,000 | 8,000 | 16,000 | ×2 |  |
| Energy weapons damage (research) Energy weapons damage | +70% Laser damage / +70% Electric damage / +30% Beam damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | 2,000 | 4,000 | 8,000 | 16,000 | ×2 |  |
| Artillery shell range (research) Artillery shell range | Non-Damage / Weapon Bonus | +30% Artillery shell range | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 1 | 1,000 × 2^N | 2,000 | 4,000 | 8,000 | 16,000 | 32,000 | ×2 |
| Artillery shell shooting speed (research) Artillery shell shooting speed | +100% Artillery shell shooting speed | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 1 | 1,000 + 1,000 × 3^(N - 1) | 2,000 | 4,000 | 10,000 | 28,000 | 82,000 | ×3 then - 2,000 |  |
| Follower robot count (research) Follower robot count | +25 Maximum following robots | Automation science pack Logistic science pack Chemical science pack Military science pack Production science pack Utility science pack Space science pack | 5 | 1,000 × (N - F) | 1,000 | 2,000 | 3,000 | 4,000 | 5,000 | +1,000 |  |
| Worker robot speed (research) Worker robot speed | Other | +65% Worker robot speed | Automation science pack Logistic science pack Chemical science pack Production science pack Utility science pack Space science pack | 6 | 1,000 × 2^(N - F - 1) | 1,000 | 2,000 | 4,000 | 8,000 | 16,000 | ×2 |

#### Space Age
The table below summarizes all the infinite technologies in Space Age. Some are unique to Space Age, while some have their price and/or effect changed from the base game.

Due to the introduction of tesla weapons, the energy weapons damage technology is split into laser weapons damage and electric weapons damage.

| Technology | Category | Bonus | Science Packs | F+1 | P[N] | P[F+1] | ... |
|---|---|---|---|---|---|---|---|
| Mining productivity (research) Mining productivity | Productivity | +10% Mining productivity | Automation science pack Logistic science pack Chemical science pack Production science pack | 3 | 1,000 × (N - F) | 1,000 | +1,000 |
| Research productivity (research) Research productivity (Space Age) | +10% Lab research productivity | Automation science pack Logistic science pack Military science pack Chemical science pack Production science pack Utility science pack Space science pack Metallurgic science pack Electromagnetic science pack Agricultural science pack Cryogenic science pack Promethium science pack | 1 | 1,000 × 1.2^N | 1,200 | ×1.2 |  |
| Steel plate productivity (research) Steel plate productivity (Space Age) | Recipe Productivity / (no effect beyond level 30) | +10% Steel plate productivity / +10% Casting steel productivity | Automation science pack Logistic science pack Chemical science pack Production science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |
| Low density structure productivity (research) Low density structure productivity (Space Age) | +10% Low density structure productivity / +10% Casting low density structure productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Metallurgic science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |  |
| Scrap recycling productivity (research) Scrap recycling productivity (Space Age) | +10% Scrap recycling productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Electromagnetic science pack | 1 | 500 × 1.5^N | 750 | ×1.5 |  |
| Processing unit productivity (research) Processing unit productivity (Space Age) | +10% Processing unit productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Electromagnetic science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |  |
| Plastic bar productivity (research) Plastic bar productivity (Space Age) | +10% Plastic bar productivity / +10% Bioplastic productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Agricultural science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |  |
| Rocket fuel productivity (research) Rocket fuel productivity (Space Age) | +10% Rocket fuel productivity / +10% Rocket fuel from jelly productivity / +10% Ammonia rocket fuel productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Agricultural science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |  |
| Asteroid productivity (research) Asteroid productivity (Space Age) | +10% Carbonic asteroid crushing productivity / +10% Oxide asteroid crushing productivity / +10% Metallic asteroid crushing productivity / +10% Advanced carbonic asteroid productivity / +10% Advanced oxide asteroid crushing productivity / +10% Advanced metallic asteroid crushing productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Utility science pack Space science pack Agricultural science pack | 1 | 1,000 × 1.5^N | 1,500 | ×1.5 |  |
| Rocket part productivity (research) Rocket part productivity (Space Age) | +10% Rocket part productivity | Automation science pack Logistic science pack Chemical science pack Production science pack Cryogenic science pack | 1 | 2,000 × 1.5^N | 3,000 | ×1.5 |  |
| Physical projectile damage (research) Physical projectile damage | Weapon Damage | +20% Bullet damage / +20% Gun turret damage / +40% Shotgun shell damage / +100% Cannon shell damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | ×2 |
| Laser weapons damage (research) Laser weapons damage (Space Age) | +70% Laser damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | ×2 |  |
| Artillery shell damage (research) Artillery shell damage (Space Age) | +10% Artillery shell damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Metallurgic science pack | 1 | 1,000 × 2^(N - 1) | 1,000 | ×2 |  |
| Stronger explosives (research) Stronger explosives | +50% Rocket damage / +20% Grenade damage / +20% Land mine damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Agricultural science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | ×2 |  |
| Refined flammables (research) Refined flammables | +20% Fire damage / +20% Flamethrower turret damage | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Agricultural science pack | 7 | 1,000 × 2^(N - F - 1) | 1,000 | ×2 |  |
| Electric weapons damage (research) Electric weapons damage (Space Age) | +70% Tesla damage / +70% Electric damage / +30% Beam damage | Automation science pack Logistic science pack Military science pack Chemical science pack Utility science pack Space science pack Electromagnetic science pack | 4 | 1,000 × 2^(N - F) | 2,000 | ×2 |  |
| Railgun damage (research) Railgun damage (Space Age) | +40% Railgun damage | Automation science pack Logistic science pack Military science pack Chemical science pack Utility science pack Space science pack Metallurgic science pack Agricultural science pack | 1 | 1,000 × 2^(N - 1) | 1,000 | ×2 |  |
| Artillery shell range (research) Artillery shell range | Non-Damage / Weapon Bonus | +30% Artillery shell range | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Metallurgic science pack | 1 | 1,000 × 2^(N - 1) | 1,000 | ×2 |
| Artillery shell shooting speed (research) Artillery shell shooting speed | +100% Artillery shell shooting speed | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Metallurgic science pack | 1 | 1,000 × 2^(N - 1) | 1,000 | ×2 |  |
| Railgun shooting speed (research) Railgun shooting speed (Space Age) | +15% Railgun shooting speed | Automation science pack Logistic science pack Chemical science pack Military science pack Utility science pack Space science pack Electromagnetic science pack Cryogenic science pack | 1 | 1,000 × 2^(N - 1) | 1,000 | ×2 |  |
| Follower robot count (research) Follower robot count | +25 Maximum following robots | Automation science pack Logistic science pack Chemical science pack Military science pack Production science pack Utility science pack Space science pack | 5 | 1,000 × (N - F) | 1,000 | +1,000 |  |
| Worker robot speed (research) Worker robot speed | Other | +65% Worker robot speed | Automation science pack Logistic science pack Chemical science pack Production science pack Utility science pack Space science pack Electromagnetic science pack | 7 | 1,000 × 2^(N - F) | 2,000 | ×2 |
| Health (research) Health (Space Age) | +50 Character health | Military science pack Utility science pack Agricultural science pack | 1 | 50 × 2^N | 100 | ×2 |  |

### Cumulative cost
As the price of most infinite technologies (specifically, those based on geometric progressions) increases very steeply, it may be a good idea for players to set realistic target levels for each of the infinite technologies they wish to pursue, and make their factory plans accordingly. To that end, the following properties of cumulative infinite research prices may be useful:

1. For infinite technologies whose underlying equation is a powers-of-two geometric series, the cumulative price of the first N - F infinite levels (skipping the first F level, so counting "infinite" levels only) is 2 × P[N] - P[F+1]; i.e., twice the price of the final researched level, less the price of the first "infinite" level.
  - As *N* increases, this is approximated well by 2 × P[N] = P[N+1], so the cumulative cost of researching to level N is about as much as researching level N+1.
  - If one decides a level M which one considers the "highest feasible" with their current science pack production capacity, expanding said capacity by a factor of X will allow about log[2](X) additional levels to be researched before the next level takes longer to research with the expanded capacity than level M + 1 would have taken with the pre-expansion production capacity.
  - For example, if one expands production capacity by a factor of 10, they will be able to research at least floor(log[2](10)) = 3 and at most ceiling(log[2](10)) = 4 additional levels in a given technology before the exponential increase in price negates the speed benefits of their ×10 capacity expansion.
1. The cumulative price of the first N - F levels of infinite technologies whose underlying equation is an arithmetic series is (N - F) × (P[N] + P[F + 1]) ÷ 2; i.e, N - F times the mean of the prices of the first and last "infinite" level. For the Follower robot count (research), an additional 900 × (N-F) need to be added.
  - Expanding production capacity by a factor of X, as above, will in this case allow an additional N × (X - 1) levels to be researched before the benefit of the expansion is wiped out (i.e., research progress speed drops to or below what it was pre-expansion).
1. The cumulative price of the first ***N*** levels of **artillery shell shooting speed**, the sole infinite technology whose underlying equation is a powers-of-three geometric series (equation type (2)) is 1.5 × P[N] - 0.5 × P[1]; i.e., 1.5 times the price of the final researched level, less half the price of the first level.

Note that these prices reflect **research units**, which will not be equal to science packs if productivity modules are used in labs. (In that case, the science pack requirement will be lower.)

### Infinite research limits
Follower robot count is limited by the rate at which capsules can be thrown out. 2 destroyer capsules can be thrown out per second, creating 10 robots per second. With a lifetime of 120s, this allows a theoretical maximum of 1200 robots to be deployed at once. This maximum is reached at level 50 and researching past that level will have no practical effect on the maximum number of deployed robots.

#### Space Age
All recipes have a maximum productivity of 300%. This was primarily done to prevent infinite resource exploits involving the recycler(Space Age) and its 25% return of input items. This cap puts a hard limit on the effectiveness of most infinite productivity researches. It can be researched past level 30, but it will have no practical effect.

Note that miners are not crafting machines that execute recipes, nor are labs. As such, mining productivity (research) and research productivity (research)(Space Age) have no limit.

The railgun turret's shooting speed is limited by its animation, which means it can't shoot faster than 0.845 times per second (once per 71 ticks). This shooting speed is reached at level 10 and researching past that level will have no practical effect on the railgun turret, however it **will** continue to increase the shooting speed of the hand-held railgun.

### Infinite research breakpoints
While infinite research technologies can be leveled forever, there are certain breakpoints that provide a notable benefit by reaching a practical cap or greatly conserving resources. These may be important factory goals. The costs in the below table are the number of each science pack required - e.g., processing unit productivity 13 requires 581k of each relevant type of science.

#### Productivity
| Technology | Interesting breakpoints |
|---|---|
| Processing unit productivity (research) Processing unit productivity (Space Age) | **Level 13**: Electromagnetic plants filled with legendary productivity module 3s reach the 300% productivity cap. (Cost = 581k) **Level 25**: Electromagnetic plants reach the 300% productivity cap with no modules. (Cost = 75.7M) |
| Low density structure productivity (research) Low density structure productivity (Space Age) Steel plate productivity (research) Steel plate productivity (Space Age) | **Level 15**: Foundries filled with legendary productivity module 3s reach the 300% productivity cap. (Cost = 1.31M) **Level 25**: Foundries reach the 300% productivity cap with no modules. (Cost = 75.7M) |
| Plastic bar productivity (research) Plastic bar productivity (Space Age) Rocket fuel productivity (research) Rocket fuel productivity (Space Age) | **Level 10**: Cryogenic plants filled with legendary productivity module 3s reach the 300% productivity cap. (Cost = 170k) **Level 15**: Biochambers filled with legendary productivity module 3s reach the 300% productivity cap. (Cost = 1.31M) **Level 25**: Biochambers reach the 300% productivity cap with no modules. (Cost = 75.7M) **Level 30**: All buildings reach the 300% productivity cap with no modules. (Cost = 575M) |
| Rocket part productivity (research) Rocket part productivity (Space Age) | **Level 20**: Rocket silos filled with legendary productivity module 3s reach the 300% productivity cap. (Cost = 19.9M) **Level 30**: Rocket silos reach the 300% productivity cap with no modules. (Cost = 1.15B) |
| Mining productivity (research) Mining productivity | (Space Age) **Level 50**: Big mining drills mining scrap saturate one side of a turbo belt. (Cost = 1.18M) (Space Age) **Level 110**: Big mining drills saturate an entire turbo belt with scrap, or one side of a turbo belt with normal ores. (Cost = 5.89M) (Space Age) **Level 230**: Big mining drills saturate an entire turbo belt with normal ores. (Cost = 26.1M) (Space Age) **Level 590**: Big mining drills saturate one side of a turbo belt with tungsten ore. (Cost = 173M) (Space Age) **Level 1190**: Big mining drills saturate an entire turbo belt with tungsten ore. (Cost = 706M) |

#### Combat
| Technology | Interesting breakpoints |
|---|---|
| Physical projectile damage (research) Physical projectile damage | **Level 1**: Gun turrets loaded with firearm magazines kill basic biters in 3 shots instead of 4; greatly conserves iron plates. (Cost = 100) |
| Stronger explosives (research) Stronger explosives | **Level 2:** Grenades destroy trees in one hit. (Cost = 300) (Space Age) **Level 7:** Rockets (yellow) destroy medium asteroids in one hit; greatly conserves rockets. (Cost = 3.1k) (Space Age) **Level 12:** Rockets (yellow) destroy large asteroids in two hits; greatly conserves rockets. (Cost = 65.1k) (Space Age) **Level 16:** Explosive rockets (red) destroy large asteroids in two hits with direct damage; greatly conserves rockets. (Cost = 1.03M) |
| Laser weapons damage (research) Laser weapons damage (Space Age) | **Level 11:** Laser turrets destroy small asteroids in one damage cycle. (Cost = 33.1k) |
| Railgun damage (research) Railgun damage (Space Age) | **Level 2**: Railgun turrets destroy all asteroid sizes in one shot; conserves ammo. (Cost = 3k) |
| Railgun shooting speed (research) Railgun shooting speed (Space Age) | **Level 10**: Railgun turrets reach their effective maximum speed (this cap does not apply to the hand-held railgun). (Cost = 1.02M) |
| Artillery shell damage (research) Artillery shell damage (Space Age) | **Level 9:** Artillery shells defeat Nauvis spawners and Behemoth worms in one hit; conserves shells. (Cost = 3.58M) |
| Refined flammables (research) Refined flammables | **Level 9:** Flamethrower turrets require 90% less crude oil to destroy Behemoth Biters; greatly conserves fuel. (Cost = 9.1k) **Level 16:** Flamethrower turrets require 95% less crude oil to destroy Behemoth Biters; greatly conserves fuel. (Cost = 1.03M) |

## Trigger technologies
The technologies listed below are researched by the player performing certain actions (usually mining or crafting a specific item) instead of by using science packs in labs.

### Nauvis
| Technology | Research trigger |
|---|---|
| Steam power (research) Steam power | Craft 50 iron plate |
| Electronics (research) Electronics | Craft 10 copper plate |
| Automation science pack (research) Automation science pack | Craft a lab |
| Steel axe (research) Steel axe | Craft 50 steel plate |
| Oil processing (research) Oil processing | Mine crude oil |
| Uranium processing (research) Uranium processing | Mine uranium ore |
| Biter egg handling (research) Biter egg handling (Space Age) | Capture a biter/spitter spawner |

### Space (Space Age)
| Technology | Research trigger |
|---|---|
| Space platform (research) Space platform (Space Age) | Launch a space platform starter pack |
| Space science pack (research) Space science pack (Space Age) | Craft an asteroid collector |

### Fulgora (Space Age)
| Technology | Research trigger |
|---|---|
| Recycling (research) Recycling (Space Age) | Mine Fulgoran vault ruin |
| Holmium processing (research) Holmium processing (Space Age) | Craft holmium ore |
| Electromagnetic plant (research) Electromagnetic plant (Space Age) | Craft 50 holmium plate |
| Electromagnetic science pack (research) Electromagnetic science pack (Space Age) | Craft supercapacitor |

### Gleba (Space Age)
| Technology | Research trigger |
|---|---|
| Jellynut (research) Jellynut (Space Age) | Mine jellystem |
| Yumako (research) Yumako (Space Age) | Mine yumako tree |
| Heating tower (research) Heating tower (Space Age) | Mine copper stromatolite |
| Agriculture (research) Agriculture (Space Age) | Mine iron stromatolite |
| Biochamber (research) Biochamber (Space Age) | Craft 10 nutrients |
| Artificial soil (research) Artificial soil (Space Age) | Craft 500 nutrients |
| Bioflux (research) Bioflux (Space Age) | Craft biochamber |
| Bacteria cultivation (research) Bacteria cultivation (Space Age) | Craft bioflux |
| Bioflux processing (research) Bioflux processing (Space Age) | Craft 25 bioflux |
| Agricultural science pack (research) Agricultural science pack (Space Age) | Craft 100 bioflux |

### Vulcanus (Space Age)
| Technology | Research trigger |
|---|---|
| Tungsten carbide (research) Tungsten carbide (Space Age) | Mine big volcanic rock |
| Calcite processing (research) Calcite processing (Space Age) | Mine calcite |
| Foundry (research) Foundry (Space Age) | Craft tungsten carbide |
| Big mining drill (research) Big mining drill (Space Age) | Craft a foundry |
| Tungsten steel (research) Tungsten steel (Space Age) | Craft a big mining drill |
| Metallurgic science pack (research) Metallurgic science pack (Space Age) | Craft tungsten plate |

### Aquilo (Space Age)
| Technology | Research trigger |
|---|---|
| Lithium processing (research) Lithium processing (Space Age) | Mine big lithium ice formation |
| Cryogenic plant (research) Cryogenic plant (Space Age) | Craft lithium plate |
| Cryogenic science pack (research) Cryogenic science pack (Space Age) | Craft cryogenic plant |

## Achievements
- Completing infinite technologies of any level is not required for **Tech maniac**. All non-infinite levels of technologies that have infinite continuations are still required.

## History
Version 2.0.7:
- Introduced trigger technologies (https://www.factorio.com/blog/post/fff-376)

## See also
- Research
- Science pack
