"""Plan the next step of the complete ore-to-plates production chain."""


def make_iron_plates(state, experience=None, player_name="Teeny", target=100):
    """Mine, craft, build, fuel, smelt and collect until target plates are held."""
    from brain.logic import brain_think
    return brain_think(state, experience, player_name, target)
