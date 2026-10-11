"""Plan the complete steam/electronics/red-science/Automation bootstrap."""


def first_research(state, experience=None, player_name='Teeny'):
    """Return the next inventory-backed action toward powered red-science research."""
    from research_rules.bootstrap import first_research as plan
    return plan(state,experience,player_name)
