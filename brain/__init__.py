"""Deterministic Factorio brain: observations, actions, goals, rules and persistence."""
def __getattr__(name):
    """Lazily expose runtime helpers so pure planning imports need no live connection."""
    if name=='execute':
        from brain.execution import execute
        return execute
    if name=='observe':
        from brain.observation import observe
        return observe
    raise AttributeError(name)
