"""Plan fuel furnace using a measured furnace reference."""


def fuel_furnace(player, furnace, count, item="coal"):
    """Move within reach if needed, then transfer the requested inventory count."""
    from logic import decision, move_or_act
    if count <= 0:
        raise ValueError("transfer count must be positive")
    action={"kind":"put","player":player["name"],"surface":player["surface"],
            "unit_number":furnace["unit_number"],"position":furnace["position"],
            "inventory":"fuel","item":item,"count":count}
    return decision("fuel_furnace","fuel furnace.",
                    move_or_act(player,action,player.get("reach_distance",10)))
