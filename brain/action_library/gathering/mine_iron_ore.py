"""Plan gathering a batch of iron-ore."""


def mine_iron_ore(state, player=None, experience=None, count=16):
    """Select a resource tile, move into reach, then mine the requested batch."""
    from brain.logic import get_player, mining_decision, decision
    if count <= 0:
        raise ValueError("batch count must be positive")
    player = player or get_player(state)
    if player is None:
        return decision("wait_for_player", "No actor available.")
    return mining_decision(state, player, "iron-ore", experience, count)
