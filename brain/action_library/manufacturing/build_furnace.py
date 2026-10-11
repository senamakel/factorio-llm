"""Plan obtaining and placing one furnace at an observed clear site."""


def build_furnace(state, player, experience=None):
    """Craft if needed; otherwise choose a site using distance and measured outcomes."""
    from brain.logic import inventory_count, decision, distance, learned_penalty
    from brain.action_library.manufacturing.craft_furnace import craft_furnace
    if player.get("crafting_queue"):
        return decision("crafting","Wait for the queued furnace craft.")
    if not inventory_count(player,"stone-furnace"):
        return craft_furnace(state,player,experience)
    candidates=[{"kind":"build","player":player["name"],"surface":player["surface"],
                 "item":"stone-furnace","position":pos}
                for pos in state.get("build_sites",{}).get(player["name"],[])]
    if not candidates:
        return decision("find_build_site","No observed clear furnace site within reach.")
    action=min(candidates,key=lambda a:distance(a["position"],player["position"])+learned_penalty(a,experience))
    return decision("build_furnace","Place a furnace using one inventory item.",action)
