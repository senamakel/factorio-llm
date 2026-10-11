"""Plan collect iron plates using a measured furnace reference."""


def collect_iron_plates(player, furnace, count):
    """Move within reach if needed, then transfer the requested inventory count."""
    from brain.logic import decision, move_or_act
    if count <= 0:
        raise ValueError("transfer count must be positive")
    action={"kind":"take","player":player["name"],"surface":player["surface"],
            "unit_number":furnace["unit_number"],"position":furnace["position"],
            "inventory":"furnace_result","item":'iron-plate',"count":count}
    return decision("collect","collect iron plates.",
                    move_or_act(player,action,2.7))
