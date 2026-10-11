"""Plan the next connected steam/lab component from live ingredients."""


def build_steam_power(state, player, experience=None):
    """Plan the next connected steam/lab component from live ingredients."""
    from brain.research_rules.power import build_power
    return build_power(state,player,experience)
