"""Python assembles bounded game observations from the read-only actuator queries."""
import math
from actuator import queries


def read_entities(actor_id, filters, fields, limit=512):
    """Read a bounded list of allowlisted entity fields and report truncation explicitly."""
    return queries.find_entities(actor_id, filters, fields, limit)


def resource_targets(actor_id, position):
    """Find nearby ore/fuel/stone, reducing radius when a query is truncated.

    Python groups candidates by resource/chunk and keeps the nearest tile in each.
    The bounded search starts at 256 tiles and reports its chosen radius per item.
    """
    targets, radii = [], {}
    for name in ('iron-ore','copper-ore','coal','stone'):
        radius, empty_radius, crowded_radius = 256, 0, 256
        for attempt in range(20):
            result = read_entities(actor_id, {'name':name,'type':'resource','position':position,'radius':radius},
                                   ('name','position','amount'))
            if not result['truncated'] and (result['entities'] or attempt == 0):
                break
            if result['truncated']:
                crowded_radius = radius
            else:
                empty_radius = radius
            radius = (empty_radius + crowded_radius) / 2
        else:
            raise RuntimeError('could not bound a nonempty resource query')
        if result['truncated']:
            raise RuntimeError('resource query remains truncated')
        radii[name] = radius
        nearest = {}
        for resource in result['entities'] or []:
            pos = resource['position']
            key = (math.floor(pos['x']/32), math.floor(pos['y']/32))
            distance = math.hypot(pos['x']-position['x'], pos['y']-position['y'])
            if key not in nearest or distance < nearest[key][0]:
                nearest[key] = (distance, resource)
        targets.extend(r for _, r in nearest.values())
    return targets, radii


def tree_targets(actor_id, position):
    """Find nearby harvestable trees using complete bounded results, never a truncated prefix."""
    radius,empty,crowded=128,0,128
    fields=('name','position','minable','wood_yield')
    for attempt in range(20):
        result=read_entities(actor_id,{'type':'tree','position':position,'radius':radius},fields,128)
        if not result['truncated'] and (result['entities'] or attempt==0):
            return [t for t in result['entities'] or [] if t.get('minable') and t.get('wood_yield',0)>0]
        if result['truncated']:crowded=radius
        else:empty=radius
        radius=(empty+crowded)/2
    raise RuntimeError('tree search could not obtain complete bounded candidates')


MACHINES = ('offshore-pump','pipe','boiler','steam-engine','small-electric-pole','lab',
            'assembling-machine-1','inserter','iron-chest','transport-belt')
RECIPES = ('stone-furnace','iron-gear-wheel','copper-cable','electronic-circuit','transport-belt','lab',
           'automation-science-pack','pipe','boiler','offshore-pump','steam-engine','small-electric-pole',
           'assembling-machine-1','inserter','iron-chest','iron-plate','copper-plate')
TECHNOLOGIES = ('steam-power','electronics','automation-science-pack','automation')
MACHINE_FIELDS = ('name','type','unit_number','position','surface','force','energy','status','fluids',
                  'remaining_burning_fuel','recipe','inventories')


def observe(actor_id, name):
    """Assemble actor state, nearby resources/threats and all bounded surface furnaces."""
    data = queries.actor_state(actor_id)
    stats = queries.production(actor_id, ('iron-plate','copper-plate','automation-science-pack','iron-ore',
                                          'copper-ore','coal','stone','wood','solid-fuel'))['items']
    position, surface = data['position'], data['surface']
    resources, radii = resource_targets(actor_id, position)
    for resource in resources:
        resource['surface'] = surface
    furnaces = read_entities(actor_id, {'type':'furnace','force':'actor'}, MACHINE_FIELDS)
    for furnace in furnaces['entities'] or []:
        inventories = furnace.get('inventories') or {}
        furnace['inventories'] = {'fuel':inventories.get('fuel',[]),'furnace_source':inventories.get('crafter_input',[]),
                                  'furnace_result':inventories.get('crafter_output',[])}
    enemies = read_entities(actor_id, {'force':'enemy','position':position,'radius':32}, ('type','surface','position'))
    trees = tree_targets(actor_id,position)
    machines = read_entities(actor_id, {'name':list(MACHINES),'force':'actor'}, MACHINE_FIELDS)
    for machine in machines['entities'] or []:
        inventories = machine.get('inventories') or {}
        machine['inventories'] = {'fuel':inventories.get('fuel',[]),'chest':inventories.get('chest',[]),
                                  'lab_input':inventories.get('lab_input',[])}
    progression = queries.technologies(actor_id, TECHNOLOGIES)
    recipes = queries.recipes(actor_id, RECIPES)
    for recipe in recipes.values():
        recipe['categories'] = {name: True for name in recipe['categories']}
    fuel = queries.item_facts(actor_id, ('coal','wood','solid-fuel'))
    candidates = [{'x':math.floor(position['x'])+dx,'y':math.floor(position['y'])+dy}
                  for r in range(3,9) for dx,dy in ((r,0),(-r,0),(0,r),(0,-r))
                  if math.hypot(math.floor(position['x'])+dx-position['x'],
                                math.floor(position['y'])+dy-position['y']) <= 10]
    clear = queries.can_place(actor_id, [{'name':'stone-furnace','position':p} for p in candidates])
    sites = [p for p, ok in zip(candidates, clear) if ok]
    game_status = {'speed':data['game_speed'],'tick_paused':data['tick_paused'],'connected_players':0}
    return {'schema_version':1,'tick':data['tick'],'game_status':game_status,
            'surface_info':{'name':surface,'seed':data['seed'],'daytime':data['daytime'],'peaceful':None,'no_enemies':None},
            'coverage':{'complete':not furnaces['truncated'] and not enemies['truncated'] and not machines['truncated'],
                        'scope':'bounded local resources and enemies; surface furnaces','resource_radii':radii},
            'players':[{'name':name,'surface':surface,'force':data['force'],'position':position,
                        'health':data['health'],'inventory':data['inventory'],'reach_distance':data['reach_distance'],
                        'resource_reach_distance':data['resource_reach_distance'],'crafting_queue':data['crafting_queue'] or []}],
            'entities':(furnaces['entities'] or [])+(machines['entities'] or []),'enemies':enemies['entities'] or [],
            'trees':trees,'recipes':recipes,'technologies':progression['technologies'],
            'current_research':progression.get('current'),'research_progress':progression['progress'],
            'fuel_values':{k:v['fuel_value'] for k,v in fuel.items()},
            'power_layout':load_layout(data['seed'],surface),
            'world':{'resources':resources},'build_sites':{name:sites},
            'iron_produced':stats['iron-plate']['produced'],'copper_produced':stats['copper-plate']['produced'],
            'red_produced':stats['automation-science-pack']['produced'],
            'resource_mined':sum(stats[k]['produced'] for k in ('iron-ore','copper-ore','coal','stone')),
            'fuel_consumed':sum(stats[k]['consumed'] for k in ('coal','wood','solid-fuel'))}


def load_layout(seed, surface):
    """Read the optional persisted layout only when it belongs to this map/surface."""
    from brain.research_rules.power import LAYOUT_FILE
    import json
    if not LAYOUT_FILE.exists():
        return {}
    record=json.loads(LAYOUT_FILE.read_text())
    return record if record['seed']==seed and record['surface']==surface else {}
