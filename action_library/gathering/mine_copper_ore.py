"""Plan gathering copper ore for electronics and red science."""


def mine_copper_ore(state, player, experience=None, count=16):
    """Move to a measured copper tile and mine a bounded native batch."""
    from logic import mining_decision
    return mining_decision(state,player,'copper-ore',experience,count)
