"""Resolve ingredients and plan native red-science crafting."""


def make_red_science(state, player, count=10, experience=None):
    """Resolve ingredients and plan native red-science crafting."""
    from brain.research_rules.recipes import ensure_item
    return ensure_item(state,player,'automation-science-pack',count,experience)
