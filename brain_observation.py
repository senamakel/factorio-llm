"""Python assembles bounded game observations; Lua only reads API fields."""
import math
from brain_io import actor_rpc


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
    for name in ('iron-ore','coal','stone'):
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
        'position=e.position,health=e.health,inventory=inv.get_contents(),'
        'iron_produced=stats.get_input_count("iron-plate"),'
        'mined={stats.get_input_count("iron-ore"),stats.get_input_count("coal"),stats.get_input_count("stone")},'
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
    candidates = [{'x':math.floor(position['x'])+dx,'y':math.floor(position['y'])+dy}
                  for r in range(3,9) for dx,dy in ((r,0),(-r,0),(0,r),(0,-r))
                  if math.hypot(math.floor(position['x'])+dx-position['x'],
                                math.floor(position['y'])+dy-position['y']) <= 10]
    sites = actor_rpc(actor_id,
        'local out={}; for _,pos in ipairs(a) do '
        'if s.can_place_entity{name="stone-furnace",position=pos,force=e.force} then out[#out+1]=pos end end; return out', candidates)
    return {'tick':data['tick'],
            'coverage':{'complete':not furnaces['truncated'] and not enemies['truncated'],
                        'scope':'bounded local resources and enemies; surface furnaces','resource_radii':radii},
            'players':[{'name':name,'surface':surface,'force':data['force'],'position':position,
                        'health':data['health'],'inventory':data['inventory'],'reach_distance':10,
                        'resource_reach_distance':2.7,'crafting_queue':[]}],
            'entities':furnaces['entities'] or [],'enemies':enemies['entities'] or [],
            'world':{'resources':resources},'build_sites':{name:sites or []},
            'iron_produced':data['iron_produced'],'resource_mined':sum(data['mined']),
            'fuel_consumed':sum(data['fuel'])}
