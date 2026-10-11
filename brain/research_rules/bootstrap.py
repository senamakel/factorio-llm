"""Wiki-enriched early unlocks, red-science production and first lab research."""
from brain.logic import decision, get_player, inventory_count, nearby_enemies, entity_item_count
from brain.research_rules.recipes import ensure_item
from brain.research_rules.smelting import ensure_plates, transfer
from brain.research_rules.power import build_power, find_role


def first_research(state, experience=None, player_name='Teeny'):
    """Plan through real production triggers and ten red packs to Automation research."""
    if not state.get('coverage',{}).get('complete'):
        return decision('observe','Incomplete observation; do not act.')
    player=get_player(state,player_name)
    if not player:
        return decision('wait_for_player','Selected assistant is unavailable.')
    if player.get('health',0)<75 or nearby_enemies(state,player):
        return decision('danger','Stop for low health or nearby enemies.')
    tech=state.get('technologies',{})
    if tech.get('automation',{}).get('researched'):
        return decision('complete','Automation researched; red science has powered the lab.')
    for name,item,total,key in [('steam-power','iron-plate',50,'iron_produced'),
                                ('electronics','copper-plate',10,'copper_produced')]:
        if not tech.get(name,{}).get('researched'):
            missing=max(1,total-state.get(key,0))
            return ensure_plates(state,player,item,inventory_count(player,item)+missing,experience)
    construction=build_power(state,player,experience)
    if construction:
        return construction
    boiler=find_role(state,'boiler')
    if entity_item_count(boiler,'fuel','coal')<4:
        needed=ensure_item(state,player,'coal',8,experience)
        if needed:
            return needed
        return decision('fuel_boiler','Load enough coal to keep the lab powered.',transfer(player,boiler,'fuel','coal',8))
    lab=find_role(state,'lab')
    if lab.get('energy',0)<=0:
        return decision('check_power','Wait for real steam generation and lab electricity.',{'kind':'wait','duration':2})
    if state.get('current_research') not in (None,'automation'):
        return decision('research_busy','Preserve the other active research.')
    if not state.get('current_research'):
        return decision('start_research','Start Automation using real lab consumption.',{'kind':'research','technology':'automation'})
    # Count already-produced packs so consumed science is not crafted again.
    remaining=max(0,10-state.get('red_produced',0))
    if remaining:
        needed=ensure_item(state,player,'automation-science-pack',remaining,experience)
        if needed:
            return needed
    packs=inventory_count(player,'automation-science-pack')
    if packs:
        return decision('load_science','Supply the powered lab with red science.',transfer(player,lab,'lab_input','automation-science-pack',packs))
    return decision('researching','Observe actual Automation progress.',{'kind':'wait','duration':8})
