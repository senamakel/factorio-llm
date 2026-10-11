"""The local brain's measurable objective: hold 100 iron plates as Teeny."""
from dataclasses import dataclass
from logic import get_player, inventory_count


@dataclass(frozen=True)
class IronPlateGoal:
    """Require target plates in the selected actor inventory, not in furnace output."""
    player_name: str = "Teeny"
    target: int = 100

    def __post_init__(self):
        if self.target <= 0:
            raise ValueError("target must be positive")

    def evaluate(self, state):
        """Return measured inventory, bounded progress, remaining plates and completion."""
        player = get_player(state, self.player_name)
        plates = inventory_count(player, "iron-plate") if player else 0
        return {"inventory": plates, "target": self.target,
                "progress": min(1.0, plates / self.target),
                "remaining": max(0, self.target - plates),
                "complete": player is not None and plates >= self.target}
