"""Python assembles bounded game observations; Lua only reads API fields."""
import math
from brain.io import actor_rpc


def read_entities(actor_id, filters, fields, limit=512):
    """Read a bounded list of entity fields and report truncation explicitly."""
    return actor_rpc(actor_id,
        'a.force=a.force=="actor" and e.force or a.force; local found=s.find_entities_filtered(a); '
        'local out={}; for i,f in ipairs(found) do if i<=a.limit-1 then '
        'out[#out+1]={' + fields + '} end end; return {entities=out,truncated=#found>=a.limit}',
        {**filters, 'limit':limit+1})


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
                                   'name=f.name,position=f.position,amount=f.amount')
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


def observe(actor_id, name):
    """Assemble actor state, nearby resources/threats and all bounded surface furnaces."""
    data = actor_rpc(actor_id,
        'local stats=e.force.get_item_production_statistics(s); return {tick=game.tick,surface=s.name,force=e.force.name,'
        'position=e.position,health=e.health,inventory=inv.get_contents(),crafting_queue=e.crafting_queue or {},seed=s.map_gen_settings.seed,'
        'iron_produced=stats.get_input_count("iron-plate"),'
        'copper_produced=stats.get_input_count("copper-plate"),red_produced=stats.get_input_count("automation-science-pack"),'
        'mined={stats.get_input_count("iron-ore"),stats.get_input_count("copper-ore"),stats.get_input_count("coal"),stats.get_input_count("stone")},'
        'fuel={stats.get_output_count("coal"),stats.get_output_count("wood"),stats.get_output_count("solid-fuel")}}')
    position, surface = data['position'], data['surface']
    resources, radii = resource_targets(actor_id, position)
    for resource in resources:
        resource['surface'] = surface
    furnaces = read_entities(actor_id, {'type':'furnace','force':'actor'},
        'name=f.name,type=f.type,unit_number=f.unit_number,surface=s.name,force=f.force.name,position=f.position,'
        'remaining_burning_fuel=f.burner and f.burner.remaining_burning_fuel or 0,'
        'inventories={fuel=f.get_inventory(defines.inventory.fuel).get_contents(),'
        'furnace_source=f.get_inventory(defines.inventory.crafter_input).get_contents(),'
        'furnace_result=f.get_inventory(defines.inventory.crafter_output).get_contents()}')
    enemies = read_entities(actor_id, {'force':'enemy','position':position,'radius':32},
                            'type=f.type,surface=s.name,position=f.position')
    trees = read_entities(actor_id, {'type':'tree','position':position,'radius':128},
                          'name=f.name,position=f.position',64)
    machines=read_entities(actor_id,{'name':['offshore-pump','pipe','boiler','steam-engine','small-electric-pole','lab'],'force':'actor'},
        'name=f.name,type=f.type,unit_number=f.unit_number,position=f.position,surface=s.name,force=f.force.name,'
        'energy=f.energy,status=f.status,fluids=(function() local out={} for i=1,#f.fluidbox do out[#out+1]=f.fluidbox[i] end return out end)(),'
        'inventories={fuel=f.get_fuel_inventory() and f.get_fuel_inventory().get_contents() or {},'
        'lab_input=f.type=="lab" and f.get_inventory(defines.inventory.lab_input).get_contents() or {}}')
    progression=actor_rpc(actor_id,
        'local recipes,tech={},{}; for _,n in ipairs(a.recipes) do local r=e.force.recipes[n]; '
        'if r then recipes[n]={enabled=r.enabled,ingredients=r.ingredients,products=r.products,energy=r.energy} end end; '
        'for _,n in ipairs(a.technologies) do local t=e.force.technologies[n]; '
        'tech[n]={researched=t.researched,enabled=t.enabled,count=t.research_unit_count,energy=t.research_unit_energy} end; '
        'return {recipes=recipes,technologies=tech,current=e.force.current_research and e.force.current_research.name,progress=e.force.research_progress}',
        {'recipes':['stone-furnace','iron-gear-wheel','copper-cable','electronic-circuit','transport-belt','lab',
                    'automation-science-pack','pipe','boiler','offshore-pump','steam-engine','small-electric-pole'],
         'technologies':['steam-power','electronics','automation-science-pack','automation']})
    candidates = [{'x':math.floor(position['x'])+dx,'y':math.floor(position['y'])+dy}
                  for r in range(3,9) for dx,dy in ((r,0),(-r,0),(0,r),(0,-r))
                  if math.hypot(math.floor(position['x'])+dx-position['x'],
                                math.floor(position['y'])+dy-position['y']) <= 10]
    sites = actor_rpc(actor_id,
        'local out={}; for _,pos in ipairs(a) do '
        'if s.can_place_entity{name="stone-furnace",position=pos,force=e.force} then out[#out+1]=pos end end; return out', candidates)
    return {'tick':data['tick'],
            'coverage':{'complete':not furnaces['truncated'] and not enemies['truncated'] and not machines['truncated'],
                        'scope':'bounded local resources and enemies; surface furnaces','resource_radii':radii},
            'players':[{'name':name,'surface':surface,'force':data['force'],'position':position,
                        'health':data['health'],'inventory':data['inventory'],'reach_distance':10,
                        'resource_reach_distance':2.7,'crafting_queue':data['crafting_queue'] or []}],
            'entities':(furnaces['entities'] or [])+(machines['entities'] or []),'enemies':enemies['entities'] or [],
            'trees':trees['entities'] or [],'recipes':progression['recipes'],'technologies':progression['technologies'],
            'current_research':progression.get('current'),'research_progress':progression['progress'],
            'power_layout':load_layout(data['seed'],surface),
            'world':{'resources':resources},'build_sites':{name:sites or []},
            'iron_produced':data['iron_produced'],'copper_produced':data['copper_produced'],'red_produced':data['red_produced'],'resource_mined':sum(data['mined']),
            'fuel_consumed':sum(data['fuel'])}


def load_layout(seed, surface):
    """Read the optional persisted layout only when it belongs to this map/surface."""
    from brain.research_rules.power import LAYOUT_FILE
    import json
    if not LAYOUT_FILE.exists():
        return {}
    record=json.loads(LAYOUT_FILE.read_text())
    return record if record['seed']==seed and record['surface']==surface else {}
