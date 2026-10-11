"""Plan ore, fuel and real copper-plate output batches."""


def smelt_copper_plates(state, player, target=10, experience=None):
    """Plan ore, fuel and real copper-plate output batches."""
    from brain.research_rules.smelting import ensure_plates
    return ensure_plates(state,player,'copper-plate',target,experience)
