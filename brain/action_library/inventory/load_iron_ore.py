"""Plan load iron ore using a measured furnace reference."""


def load_iron_ore(player, furnace, count):
    """Move within reach if needed, then transfer the requested inventory count."""
    from brain.logic import decision, move_or_act
    if count <= 0:
        raise ValueError("transfer count must be positive")
    action={"kind":"put","player":player["name"],"surface":player["surface"],
            "unit_number":furnace["unit_number"],"position":furnace["position"],
            "inventory":"furnace_source","item":'iron-ore',"count":count}
    return decision("load_furnace","load iron ore.",
                    move_or_act(player,action,2.7))
