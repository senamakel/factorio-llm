"""The local brain's measurable objective: hold 100 iron plates as Teeny."""
from dataclasses import dataclass
from brain.logic import get_player, inventory_count


@dataclass(frozen=True)
class IronPlateGoal:
    """Require target plates in the selected actor inventory, not in furnace output."""
    player_name: str = "Teeny"
    target: int = 100
    unit: str = 'plates'

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


@dataclass(frozen=True)
class FirstResearchGoal:
    """Require observed Automation completion through the red-science bootstrap."""
    player_name: str = 'Teeny'
    target: int = 10
    unit: str = 'red packs produced'

    def evaluate(self, state):
        """Score unlocks, lab power, science production and actual research progress."""
        from brain.research_rules.power import find_role
        tech=state.get('technologies',{})
        complete=tech.get('automation',{}).get('researched',False)
        lab=find_role(state,'lab')
        milestones=sum(bool(tech.get(name,{}).get('researched')) for name in
                       ('steam-power','electronics','automation-science-pack'))
        progress=milestones*.1 + bool(lab)*.1 + bool(lab and lab.get('energy',0)>0)*.1
        progress+=min(1,state.get('red_produced',0)/self.target)*.1
        progress+=state.get('research_progress',0)*.4 if state.get('current_research')=='automation' else 0
        return {'inventory':state.get('red_produced',0),'target':self.target,
                'progress':1 if complete else min(.99,progress),'complete':complete,
                'remaining':max(0,self.target-state.get('red_produced',0))}
