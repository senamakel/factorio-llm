"""Pure local decisions for the first recursive-factorio objective: ore → iron plates.

No network or game mutations here. Each decision consumes the world projection and
persistent outcome scores; brain.py handles observation, execution and feedback.
"""
import math


def item_count(items,name):
    if isinstance(items,dict):
        return items.get(name,0)
    return sum(i.get('count',0) for i in items or [] if i.get('name')==name)


def inventory_count(player,name):
    return item_count(player.get('inventory',[]),name)


def entity_item_count(entity,inventory,name):
    return item_count(entity.get('inventories',{}).get(inventory,[]),name)


def distance(a,b):
    return math.hypot(a['x']-b['x'],a['y']-b['y'])


def get_player(state,name=''):
    players=state.get('players',[])
    if name:
        return next((p for p in players if p['name']==name),None)
    return next((p for p in players if p.get('connected')), players[0] if players else None)


def own_entities(state,player,entity_type=None):
    return [e for e in state.get('entities',[]) if e.get('surface')==player['surface'] and
            e.get('force')==player.get('force','player') and (not entity_type or e.get('type')==entity_type)]


def nearby_enemies(state,player,radius=24):
    return [e for e in state.get('enemies',[]) if e.get('surface')==player['surface'] and
            e.get('type') in ('unit','turret','unit-spawner') and distance(e['position'],player['position'])<radius]


def action_key(action):
    pos=action.get('position',{})
    return ':'.join(map(str,(action['kind'],action.get('player',''),action.get('surface',''),
        action.get('resource',action.get('item',action.get('recipe',''))),
        action.get('unit_number',''),pos.get('x',''),pos.get('y',''))))


def learned_penalty(action,experience):
    score=(experience or {}).get(action_key(action),{})
    attempts=score.get('attempts',0)
    # Failed sites/targets become less attractive; successful evidence can reduce the penalty.
    return (score.get('failures',0)/max(1,attempts))*40 - score.get('mean_reward',0)*2


def select_resource(state,player,name,experience=None):
    choices=[r for r in state.get('world',{}).get('resources',[]) if r['name']==name and
             r['surface']==player['surface'] and r.get('amount',0)>0]
    def score(resource):
        action={'kind':'mine','player':player['name'],'surface':player['surface'],
                'resource':name,'position':resource['position']}
        return distance(resource['position'],player['position'])+learned_penalty(action,experience)
    return min(choices,key=score) if choices else None


def decision(phase,reason,action=None,**extra):
    action=action or {'kind':'wait'}
    return {'policy_version':1,'phase':phase,'reason':reason,'action':action,
            'action_key':action_key(action),**extra}


def move_or_act(player,action,reach):
    if distance(player['position'],action['position'])>reach:
        return {'kind':'move','player':player['name'],'surface':player['surface'],
                'position':action['position'],'stop_distance':max(0.5,reach-0.5)}
    return action


def mining_decision(state,player,resource,experience):
    target=select_resource(state,player,resource,experience)
    if not target:
        return decision('explore',f'No {resource} target is known on this surface; explore and observe again.')
    action={'kind':'mine','player':player['name'],'surface':player['surface'],
            'resource':resource,'position':target['position']}
    return decision('mine_'+resource,f'Gather {resource} for the iron-smelting chain.',
        move_or_act(player,action,player.get('resource_reach_distance',2.7)))


def brain_think(state,experience=None,player_name='',target_plates=16):
    """Choose one bounded action from the comprehensive observable state, without LLM calls.

    The initial policy protects the selected player, mines iron, acquires fuel and
    a furnace, supplies it and collects plates. Learned failure/reward scores change
    resource and build-site selection. Unsupported or incomplete observations cause
    waiting rather than fabricated knowledge. Other factories and surfaces remain
    available in state for future policies; this policy edits only the iron chain.
    """
    if not state.get('coverage',{}).get('complete'):
        return decision('observe','World collection is incomplete; retry observation before acting.')
    player=get_player(state,player_name)
    if not player:
        return decision('wait_for_player','No selected player exists in this world.')
    if player.get('health',250)<=0:
        return decision('respawn','The selected player needs a character before mining.')
    if nearby_enemies(state,player) or player.get('health',250)<75:
        return decision('danger','Enemies or low health make mining unsafe; stop and reassess.')
    plates=inventory_count(player,'iron-plate')
    if plates>=target_plates:
        return decision('complete',f'Iron goal reached: {plates}/{target_plates} plates.',progress=plates)
    furnaces=sorted(own_entities(state,player,'furnace'),key=lambda e:distance(e['position'],player['position']))
    # Collect completed output before gathering more material.
    for furnace in furnaces:
        output=entity_item_count(furnace,'furnace_result','iron-plate')
        if output:
            action={'kind':'take','player':player['name'],'surface':player['surface'],
                    'unit_number':furnace['unit_number'],'position':furnace['position'],
                    'inventory':'furnace_result','item':'iron-plate','count':min(output,target_plates-plates)}
            return decision('collect','Collect the furnace\'s completed iron plates.',
                            move_or_act(player,action,player.get('reach_distance',10)))
    ore=inventory_count(player,'iron-ore')
    batch=min(16,max(1,target_plates-plates))
    loaded=sum(entity_item_count(f,'furnace_source','iron-ore') for f in furnaces)
    if ore<batch and loaded==0:
        return mining_decision(state,player,'iron-ore',experience)
    fuel_name=next((name for name in ('coal','wood','solid-fuel') if inventory_count(player,name)>0),None)
    fueled=[f for f in furnaces if any(entity_item_count(f,'fuel',n)>0 for n in ('coal','wood','solid-fuel'))
            or f.get('remaining_burning_fuel',0)>0]
    if not fuel_name and not fueled:
        return mining_decision(state,player,'coal',experience)
    if not furnaces:
        if player.get('crafting_queue'):
            return decision('crafting','Wait for the queued furnace craft to finish.')
        if inventory_count(player,'stone-furnace')==0:
            if inventory_count(player,'stone')<5:
                return mining_decision(state,player,'stone',experience)
            return decision('craft_furnace','Craft a stone furnace from five stone.',
                            {'kind':'craft','player':player['name'],'recipe':'stone-furnace','count':1})
        sites=state.get('build_sites',{}).get(player['name'],[])
        actions=[{'kind':'build','player':player['name'],'surface':player['surface'],
                  'item':'stone-furnace','position':site} for site in sites]
        if not actions:
            return decision('find_build_site','No collision-free furnace site is within reach.')
        action=min(actions,key=lambda a:distance(a['position'],player['position'])+learned_penalty(a,experience))
        return decision('build_furnace','Place the furnace using one item from the player inventory.',action)
    furnace=furnaces[0]
    base={'player':player['name'],'surface':player['surface'],'unit_number':furnace['unit_number'],
          'position':furnace['position']}
    if furnace not in fueled:
        if fuel_name:
            action={'kind':'put',**base,'inventory':'fuel','item':fuel_name,'count':min(4,inventory_count(player,fuel_name))}
            return decision('fuel_furnace','Transfer fuel from the player into the furnace.',
                            move_or_act(player,action,player.get('reach_distance',10)))
    if ore and entity_item_count(furnace,'furnace_source','iron-ore')<batch:
        action={'kind':'put',**base,'inventory':'furnace_source','item':'iron-ore','count':min(ore,batch)}
        return decision('load_furnace','Transfer iron ore into the furnace.',
                        move_or_act(player,action,player.get('reach_distance',10)))
    return decision('smelting','The furnace is processing ore; wait and inspect output.',progress=plates)


def progress_metrics(state,player_name=''):
    player=get_player(state,player_name)
    if not player:
        return {'iron_ore':0,'iron_plate':0,'health':0}
    return {'iron_ore':inventory_count(player,'iron-ore'),'iron_plate':inventory_count(player,'iron-plate'),
            'health':player.get('health',0),'position':player['position']}


def action_reward(before,after,action):
    """Reward measured material progress, penalize damage; moving is rewarded by distance gained."""
    player=action.get('player','')
    a,b=progress_metrics(before,player),progress_metrics(after,player)
    reward=5*(b['iron_plate']-a['iron_plate'])+0.2*(b['iron_ore']-a['iron_ore'])
    reward+=min(0,b['health']-a['health'])/10
    if action['kind']=='move' and a.get('position') and b.get('position'):
        reward+=distance(a['position'],action['position'])-distance(b['position'],action['position'])
    return reward
