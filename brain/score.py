"""Explainable measured rewards for inventory, production, progress and costs."""
from brain.goal import IronPlateGoal
from brain.logic import get_player, inventory_count, nearby_enemies


def metrics(state, goal):
    """Read actor holdings and cumulative production/resource counters from observations."""
    player = get_player(state, goal.player_name)
    return {"plates": inventory_count(player, "iron-plate") if player else 0,
            "health": player.get("health", 0) if player else 0,
            "enemies": len(nearby_enemies(state, player)) if player else 0,
            "produced": state.get("iron_produced", 0),
            "drain": state.get("resource_drain", 0),
            "tick": state.get("tick", 0)}


def score_transition(before, after, goal=None):
    """Return component rewards and total; use game time and cumulative counter deltas.

    Throughput is plates produced per game second. Inventory and progress rewards
    use signed changes, so losing plates reverses their reward. Drain includes mined
    ore/stone and consumed fuel; productive conversions still earn a net reward.
    Counter resets earn no throughput/drain delta. No elapsed ticks means no rate.
    """
    goal = goal or IronPlateGoal()
    a, b = metrics(before, goal), metrics(after, goal)
    seconds = max(0, b["tick"] - a["tick"]) / 60
    produced = max(0, b["produced"] - a["produced"])
    parts = {"throughput": produced / seconds if seconds else 0,
             "inventory": 5 * (b["plates"] - a["plates"]),
             "progress": 100 * (goal.evaluate(after)["progress"] - goal.evaluate(before)["progress"]),
             "resource_drain": -0.1 * max(0, b["drain"] - a["drain"]),
             "time": -0.02 * seconds,
             "enemies": -b["enemies"] * seconds,
             "damage": min(0, b["health"] - a["health"]) / 10}
    return {"components": parts, "total": sum(parts.values()), "seconds": seconds}
