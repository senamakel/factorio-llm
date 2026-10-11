"""Python plans native movement; Lua only applies validated game API operations."""
import math
from brain.io import actor_rpc


def walking_instruction(position, target, stop_distance, speed, confident=False):
    """Choose an eight-direction leg and bounded duration, without crossing the target."""
    dx, dy = target['x'] - position['x'], target['y'] - position['y']
    remaining = max(0, math.hypot(dx, dy) - stop_distance)
    if not remaining:
        return {'direction':'north','duration':0}
    if speed <= 0:
        raise ValueError('game or actor is not moving')
    if abs(dx) > 2 * abs(dy):
        direction, leg = ('east' if dx > 0 else 'west'), abs(dx)
    elif abs(dy) > 2 * abs(dx):
        direction, leg = ('south' if dy > 0 else 'north'), abs(dy)
    else:
        direction = ('south' if dy > 0 else 'north') + ('east' if dx > 0 else 'west')
        leg = min(abs(dx), abs(dy)) * math.sqrt(2)
    return {'direction':direction,'duration':min(8 if confident else 2, min(leg, remaining) / speed)}


def mining_duration(count, mining_time, speed, progress, amount, game_speed, confident):
    """Estimate a batch's wall time from prototype speed/progress; cap uncertain work."""
    if speed <= 0 or game_speed <= 0:
        raise ValueError('game or actor cannot mine')
    cycles = min(max(1,count),amount)
    estimate = max(0,cycles-min(1,max(0,progress))) * mining_time / speed / game_speed
    return min(8 if confident else 2, estimate + .05)


def route_samples(position, plan, speed):
    """Sample a straight leg at half-tile spacing for engine collision checks."""
    vectors={'north':(0,-1),'northeast':(1,-1),'east':(1,0),'southeast':(1,1),
             'south':(0,1),'southwest':(-1,1),'west':(-1,0),'northwest':(-1,-1)}
    dx,dy=vectors[plan['direction']]
    norm=math.hypot(dx,dy)
    distance=plan['duration']*speed
    return [{'x':position['x']+dx/norm*d,'y':position['y']+dy/norm*d}
            for d in [i*.5 for i in range(2,math.ceil(distance*2)+1)]]


def execute(actor_id, action):
    """Start a native instruction or apply a costed transfer; caller owns duration/stop."""
    kind = action['kind']
    stop = 'e.walking_state={walking=false}; e.mining_state={mining=false}; '
    if kind == 'halt':
        return actor_rpc(actor_id,stop+
            'if a.cancel_crafting then local q=e.crafting_queue or {}; '
            'for i=#q,1,-1 do e.cancel_crafting{index=i,count=q[i].count} end end; return {ok=true}',action)
    if kind == 'wait':
        result=actor_rpc(actor_id, stop + 'return {ok=true}')
        return {**result,'duration':min(8,max(0,action.get('duration',0)))}
    if kind == 'plan_power':
        from brain.research_rules.power import discover_layout
        return discover_layout(actor_id)
    if kind == 'research':
        return actor_rpc(actor_id,
            'assert(not e.force.current_research or e.force.current_research.name==a.technology,"another research is active"); '
            'local ok=e.force.add_research(a.technology); return {ok=ok}',action)
    if kind == 'set_recipe':
        return actor_rpc(actor_id,
            'local f=s.find_entities_filtered{name=a.entity_name,position=a.position,radius=.1,force=e.force}[1]; '
            'assert(f and f.unit_number==a.unit_number,"blueprint machine missing"); '
            'assert(e.force.recipes[a.recipe] and e.force.recipes[a.recipe].enabled,"recipe unavailable"); '
            'f.set_recipe(a.recipe); return {ok=f.get_recipe() and f.get_recipe().name==a.recipe}',action)
    if kind == 'move':
        current = actor_rpc(actor_id, 'return {position=e.position,speed=e.character_running_speed*60*game.speed}')
        candidate = walking_instruction(current['position'],action['position'],action.get('stop_distance',1),current['speed'],True)
        samples = route_samples(current['position'],candidate,current['speed'])
        checks = actor_rpc(actor_id,
            'local clear={}; for _,pos in ipairs(a.points) do clear[#clear+1]=s.can_place_entity{name="character",position=pos,force=e.force} end; '
            'return {clear=clear,enemies=s.count_entities_filtered{force="enemy",position=e.position,radius=a.radius}}',
            {'points':samples,'radius':candidate['duration']*current['speed']+24})
        confident = bool(samples) and all(checks['clear']) and checks['enemies']==0
        target=action['position']; stop_distance=action.get('stop_distance',1)
        if samples and not all(checks['clear']):
            from brain.navigation import waypoint
            target=waypoint(actor_id,current['position'],target,stop_distance)
            stop_distance=0
            confident=checks['enemies']==0
        plan = walking_instruction(current['position'],target,stop_distance,current['speed'],confident)
        result = actor_rpc(actor_id, stop +
                           'e.walking_state={walking=a.duration>0,direction=defines.direction[a.direction]}; return {ok=true}', plan)
        return {**result, **plan, 'confidence':'high' if confident else 'low'}
    if kind in ('mine','mine_tree'):
        timing = actor_rpc(actor_id,
            'local r=s.find_entities_filtered{name=a.resource,position=a.position,radius=0.1}[1]; assert(r,"resource missing"); '
            'return {mining_time=r.prototype.mineable_properties.mining_time,amount=a.kind=="mine_tree" and 1 or r.amount,'
            'speed=e.prototype.mining_speed*(1+e.character_mining_speed_modifier),progress=e.mining_progress,'
            'game_speed=game.speed,enemies=s.count_entities_filtered{force="enemy",position=e.position,radius=32},health=e.health}',action)
        confident = timing['enemies']==0 and timing['health']>=75
        duration = mining_duration(action.get('count',1),timing['mining_time'],timing['speed'],
                                   timing['progress'],timing['amount'],timing['game_speed'],confident)
        result = actor_rpc(actor_id, stop +
            'assert((e.position.x-a.position.x)^2+(e.position.y-a.position.y)^2<=2.7^2,"resource out of reach"); '
            'local r=s.find_entities_filtered{name=a.resource,position=a.position,radius=0.1}[1]; '
            'assert(r and (a.kind=="mine_tree" or r.amount>0),"resource depleted"); e.selected=r; '
            'e.mining_state={mining=true,position=r.position}; return {ok=true}', action)
        return {**result, 'duration':duration, 'resource':action['resource'], 'confidence':'high' if confident else 'low'}
    if kind == 'craft':
        if not isinstance(action.get('count'),int) or not 1<=action['count']<=100:
            raise ValueError('craft count must be 1..100')
        result=actor_rpc(actor_id,stop+
            'local r=e.force.recipes[a.recipe]; assert(r and r.enabled,"recipe unavailable"); '
            'local n=e.begin_crafting{recipe=a.recipe,count=a.count}; assert(n>0,"craft ingredients unavailable"); '
            'return {ok=true,started=n,seconds=n*r.energy/(1+e.character_crafting_speed_modifier)/game.speed}',action)
        return {**result,'duration':min(8,result['seconds']+.05)}
    reach = 'assert((e.position.x-a.position.x)^2+(e.position.y-a.position.y)^2<=100,"entity out of reach"); '
    if kind == 'build':
        if action.get('item') not in ('stone-furnace','offshore-pump','pipe','boiler','steam-engine','lab','small-electric-pole',
                                    'assembling-machine-1','inserter','iron-chest','transport-belt'):
            raise ValueError('unsupported building')
        return actor_rpc(actor_id, stop + reach +
            'assert(inv.get_item_count(a.item)>0,"building item missing"); '
            'local o={name=a.item,position=a.position,direction=defines.direction[a.direction or "north"],force=e.force,raise_built=true}; '
            'assert(s.can_place_entity(o),"building site occupied"); '
            'local built=s.create_entity(o); assert(built,"build failed"); '
            'inv.remove{name=a.item,count=1}; return {ok=true,unit_number=built.unit_number}', action)
    inventory = {'furnace_source':'crafter_input','furnace_result':'crafter_output','fuel':'fuel','lab_input':'lab_input'}
    if kind not in ('put','take') or action.get('inventory') not in inventory:
        raise ValueError('unsupported action or inventory')
    current=actor_rpc(actor_id,'return e.position')
    facing=walking_instruction(current,action['position'],0,9)['direction']
    args = {**action, 'inventory_id':inventory[action['inventory']],'facing':facing}
    transfer = ('local source,destination=inv,other; ' if kind == 'put' else 'local source,destination=other,inv; ')
    result=actor_rpc(actor_id, stop + reach +
        'local f=s.find_entities_filtered{position=a.position,radius=0.1,name=a.entity_name or {"stone-furnace","steel-furnace"},force=e.force}[1]; '
        'assert(f and f.unit_number==a.unit_number,"furnace missing"); '
        'e.selected=f; e.direction=defines.direction[a.facing]; '
        'local other=f.get_inventory(defines.inventory[a.inventory_id]); ' + transfer +
        'local count=math.min(a.count,source.get_item_count(a.item)); assert(count>0,"transfer source is empty"); '
        'local n=destination.insert{name=a.item,count=count}; if n==0 then '
        'return {ok=false,transferred=0,error="destination full or incompatible; existing contents preserved"} end; '
        'source.remove{name=a.item,count=n}; return {ok=true,transferred=n}', args)
    return {**result,'duration':min(1.2,.3+.03*result['transferred'])}
