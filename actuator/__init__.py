"""Frozen, honest bridge from the brain to the game.

The brain may only touch Factorio through this package. ``queries`` reads the
world; ``actions`` performs what a player character could do (walk, mine,
craft, build from inventory, move items, set recipes, queue research). The
hive cannot edit this package, and a gate rejects brains that bypass it.
"""
from actuator import actions, queries

__all__ = ['actions', 'queries']
