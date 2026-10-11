"""Plan crafting a stone furnace, gathering missing stone first."""


def craft_furnace(state, player, experience=None):
    """Gather five stone or craft one furnace with the actor's real inventory."""
    from logic import inventory_count, decision
    from action_library.gathering.mine_stone import mine_stone
    missing=5-inventory_count(player,"stone")
    if missing>0:
        return mine_stone(state,player,experience,missing)
    return decision("craft_furnace","Craft a stone furnace from five stone.",
                    {"kind":"craft","player":player["name"],"recipe":"stone-furnace","count":1})
