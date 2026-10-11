"""Python plans native movement; Lua only applies validated game API operations."""
import math
from brain_io import actor_rpc


def walking_instruction(position, target, stop_distance, speed):
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
    return {'direction':direction,'duration':min(2, min(leg, remaining) / speed)}


def execute(actor_id, action):
    """Start a native instruction or apply a costed transfer; caller owns duration/stop."""
    kind = action['kind']
    stop = 'e.walking_state={walking=false}; e.mining_state={mining=false}; '
    if kind == 'wait':
        return actor_rpc(actor_id, stop + 'return {ok=true}')
    if kind == 'move':
        current = actor_rpc(actor_id, 'return {position=e.position,speed=e.character_running_speed*60*game.speed}')
        plan = walking_instruction(current['position'],action['position'],action.get('stop_distance',1),current['speed'])
        result = actor_rpc(actor_id, stop +
                           'e.walking_state={walking=a.duration>0,direction=defines.direction[a.direction]}; return {ok=true}', plan)
        return {**result, **plan}
    if kind == 'mine':
        result = actor_rpc(actor_id, stop +
            'assert((e.position.x-a.position.x)^2+(e.position.y-a.position.y)^2<=2.7^2,"resource out of reach"); '
            'local r=s.find_entities_filtered{name=a.resource,position=a.position,radius=0.1}[1]; '
            'assert(r and r.amount>0,"resource depleted"); e.selected=r; '
            'e.mining_state={mining=true,position=r.position}; return {ok=true}', action)
        return {**result, 'duration':2, 'resource':action['resource']}
    if kind == 'craft':
        if action.get('recipe') != 'stone-furnace' or action.get('count') != 1:
            raise ValueError('unsupported craft')
        return actor_rpc(actor_id, stop +
            'assert(inv.get_item_count("stone")>=5 and inv.can_insert{name="stone-furnace",count=1},"craft inventory unavailable"); '
            'inv.remove{name="stone",count=5}; inv.insert{name="stone-furnace",count=1}; return {ok=true,crafted=1}')
    reach = 'assert((e.position.x-a.position.x)^2+(e.position.y-a.position.y)^2<=100,"entity out of reach"); '
    if kind == 'build':
        if action.get('item') != 'stone-furnace':
            raise ValueError('unsupported building')
        return actor_rpc(actor_id, stop + reach +
            'assert(inv.get_item_count(a.item)>0,"building item missing"); '
            'local o={name=a.item,position=a.position,force=e.force,raise_built=true}; '
            'assert(s.can_place_entity(o),"building site occupied"); '
            'local built=s.create_entity(o); assert(built,"build failed"); '
            'inv.remove{name=a.item,count=1}; return {ok=true,unit_number=built.unit_number}', action)
    inventory = {'furnace_source':'crafter_input','furnace_result':'crafter_output','fuel':'fuel'}
    if kind not in ('put','take') or action.get('inventory') not in inventory:
        raise ValueError('unsupported action or inventory')
    args = {**action, 'inventory_id':inventory[action['inventory']]}
    transfer = ('local source,destination=inv,other; ' if kind == 'put' else 'local source,destination=other,inv; ')
    return actor_rpc(actor_id, stop + reach +
        'local f=s.find_entities_filtered{position=a.position,radius=0.1,type="furnace",force=e.force}[1]; '
        'assert(f and f.unit_number==a.unit_number,"furnace missing"); '
        'local other=f.get_inventory(defines.inventory[a.inventory_id]); ' + transfer +
        'local n=destination.insert{name=a.item,count=math.min(a.count,source.get_item_count(a.item))}; '
        'source.remove{name=a.item,count=n}; return {ok=n>0,transferred=n}', args)
