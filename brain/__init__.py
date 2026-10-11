"""Deterministic Factorio brain: observations, actions, goals, rules and persistence."""
def __getattr__(name):
    """Lazily expose runtime helpers so pure planning imports need no live connection."""
    from importlib import import_module
    modules={'execute':'execution','observe':'observation'}
    if name not in modules:raise AttributeError(name)
    return getattr(import_module('brain.'+modules[name]),name)
