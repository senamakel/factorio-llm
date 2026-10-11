"""Read-only world queries. Nothing here changes game state.

Entity fields are chosen by name from ``FIELDS`` so callers never send Lua.
Results are bounded: ``find_entities`` and ``find_tiles`` report ``truncated``
instead of silently returning a prefix.
"""
from actuator.rpc import actor_rpc, rpc

FIELDS = {
    'name': 'f.name', 'type': 'f.type', 'unit_number': 'f.unit_number', 'position': 'f.position',
    'direction': 'DIR[f.direction]', 'force': 'f.force and f.force.name', 'surface': 'f.surface.name',
    'amount': 'f.type=="resource" and f.amount or nil', 'status': 'STATUS[f.status]',
    'energy': 'f.energy', 'health': 'f.health', 'minable': 'f.minable',
    'recipe': '(f.type=="assembling-machine" or f.type=="furnace") and f.get_recipe() and f.get_recipe().name or nil',
    'crafting_progress': '(f.type=="assembling-machine" or f.type=="furnace") and f.crafting_progress or nil',
    'products_finished': '(f.type=="assembling-machine" or f.type=="furnace") and f.products_finished or nil',
    'fluids': 'f.get_fluid_contents and f.get_fluid_contents() or nil',
    'remaining_burning_fuel': 'f.burner and f.burner.remaining_burning_fuel or 0',
    'inventories': 'INVENTORIES(f)',
    'drop_position': '(f.type=="inserter" or f.type=="mining-drill") and f.drop_position or nil',
    'pickup_position': 'f.type=="inserter" and f.pickup_position or nil',
    'drop_target': 'TARGET(f.drop_target)', 'pickup_target': 'f.type=="inserter" and TARGET(f.pickup_target) or nil',
    'belt_contents': 'BELT(f)',
    'bounding_box': 'f.bounding_box',
    'wood_yield': 'WOOD(f)',
}
DEFAULT_FIELDS = ('name', 'type', 'unit_number', 'position', 'direction', 'status')

HELPERS = (
    'local DIR={}; for k,v in pairs(defines.direction) do DIR[v]=k end; '
    'local STATUS={}; for k,v in pairs(defines.entity_status) do STATUS[v]=k end; '
    'local INVNAMES={}; for k,v in pairs(defines.inventory) do INVNAMES[v]=INVNAMES[v] or k end; '
    'local function INVENTORIES(f) local out={}; if not f.get_max_inventory_index then return out end; '
    'for i=1,f.get_max_inventory_index() do local ok,x=pcall(f.get_inventory,i); '
    'if ok and x and #x>0 then out[x.name or INVNAMES[i] or tostring(i)]=x.get_contents() end end; return out end; '
    'local function TARGET(t) return t and {name=t.name,unit_number=t.unit_number,position=t.position} or nil end; '
    'local function BELT(f) if f.type~="transport-belt" and f.type~="underground-belt" and f.type~="splitter" then return nil end; '
    'local out={}; for i=1,f.get_max_transport_line_index() do out[i]=f.get_transport_line(i).get_contents() end; return out end; '
    'local function WOOD(f) if f.type~="tree" then return nil end; local n=0; '
    'for _,p in pairs(f.prototype.mineable_properties.products or {}) do '
    'if p.name=="wood" then n=n+(p.amount or p.amount_min or 1) end end; return n end; ')


def fields_lua(fields):
    """Build a Lua table constructor from allowlisted field names."""
    unknown = [name for name in fields if name not in FIELDS]
    if unknown:
        raise ValueError(f'unknown entity fields: {unknown}; choose from {sorted(FIELDS)}')
    return '{' + ','.join(f'{name}={FIELDS[name]}' for name in fields) + '}'


def actor_state(actor_id):
    """Return the actor's tick, position, inventory, crafting queue, reach and speeds."""
    return actor_rpc(actor_id,
        'local p=e.prototype; return {tick=game.tick,surface=s.name,force=e.force.name,seed=s.map_gen_settings.seed,'
        'position=e.position,health=e.health,inventory=inv.get_contents(),crafting_queue=e.crafting_queue or {},'
        'crafting_queue_size=e.crafting_queue_size,walking=e.walking_state.walking,mining=e.mining_state.mining,'
        'reach_distance=p.reach_distance+e.character_reach_distance_bonus,'
        'build_distance=p.build_distance+e.character_build_distance_bonus,'
        'resource_reach_distance=p.reach_resource_distance+e.character_resource_reach_distance_bonus,'
        'running_speed=e.character_running_speed,mining_speed=p.mining_speed*(1+e.character_mining_speed_modifier),'
        'crafting_speed=1+e.character_crafting_speed_modifier,mining_progress=e.mining_progress,'
        'game_speed=game.speed,tick_paused=game.tick_paused,daytime=s.daytime}')


def find_entities(actor_id, filters, fields=DEFAULT_FIELDS, limit=512):
    """Find entities on the actor's surface with ``find_entities_filtered`` filters.

    ``filters`` accepts name, type, position, radius, area, direction and force,
    where force may be ``"actor"`` for the actor's own force. Returns
    ``{entities, truncated}``; truncated means more than ``limit`` matched.
    """
    allowed = {'name', 'type', 'position', 'radius', 'area', 'force', 'direction', 'ghost_name', 'ghost_type'}
    if set(filters) - allowed:
        raise ValueError(f'unsupported filters: {sorted(set(filters) - allowed)}')
    if not 1 <= limit <= 5000:
        raise ValueError('limit must be 1..5000')
    return actor_rpc(actor_id, HELPERS +
        'local q=a.q; if q.force=="actor" then q.force=e.force end; q.limit=a.limit+1; '
        'local found=s.find_entities_filtered(q); local out={}; '
        'for i,f in ipairs(found) do if i<=a.limit then out[#out+1]=' + fields_lua(fields) + ' end end; '
        'return {entities=out,truncated=#found>a.limit}', {'q': dict(filters), 'limit': limit})


def count_entities(actor_id, filters):
    """Count entities matching ``find_entities`` filters without listing them."""
    return actor_rpc(actor_id, 'local q=a; if q.force=="actor" then q.force=e.force end; '
                     'return s.count_entities_filtered(q)', dict(filters))


def find_tiles(actor_id, names, position, radius, limit=8192):
    """Return positions of named tiles (e.g. water) near a position, flagged if truncated."""
    return actor_rpc(actor_id,
        'local t=s.find_tiles_filtered{name=a.names,position=a.position,radius=a.radius,limit=a.limit+1}; '
        'local out={}; for i,x in ipairs(t) do if i<=a.limit then out[#out+1]=x.position end end; '
        'return {tiles=out,truncated=#t>a.limit}',
        {'names': list(names), 'position': position, 'radius': radius, 'limit': limit})


def can_place(actor_id, rows):
    """Check placement of ``[{name, position, direction?}]``; returns a list of booleans."""
    if not rows:
        return []
    return actor_rpc(actor_id,
        'local out={}; for _,p in ipairs(a) do out[#out+1]=s.can_place_entity{name=p.name,position=p.position,'
        'direction=defines.direction[p.direction or "north"],force=e.force} end; return out', list(rows))


def production(actor_id, items):
    """Return cumulative force production/consumption counts per item on this surface."""
    return actor_rpc(actor_id,
        'local st=e.force.get_item_production_statistics(s); local out={}; '
        'for _,n in ipairs(a) do out[n]={produced=st.get_input_count(n),consumed=st.get_output_count(n)} end; '
        'return {tick=game.tick,items=out}', list(items))


def recipes(actor_id, names=None):
    """Return recipe facts (enabled, ingredients, products, energy, category) for names or all."""
    return actor_rpc(actor_id,
        'local out={}; local function add(r) out[r.name]={enabled=r.enabled,ingredients=r.ingredients,'
        'products=r.products,energy=r.energy,category=r.category,hidden=r.hidden} end; '
        'if a.names then for _,n in ipairs(a.names) do local r=e.force.recipes[n]; if r then add(r) end end '
        'else for _,r in pairs(e.force.recipes) do if not r.hidden then add(r) end end end; return out',
        {'names': list(names) if names else None})


def technologies(actor_id, names=None):
    """Return technology state, cost, trigger and prerequisites, plus current research."""
    return actor_rpc(actor_id,
        'local out={}; local function add(t) local pre={}; for k,_ in pairs(t.prerequisites) do pre[#pre+1]=k end; '
        'local eff={}; for _,x in pairs(t.prototype.effects or {}) do if x.type=="unlock-recipe" then eff[#eff+1]=x.recipe end end; '
        'out[t.name]={researched=t.researched,enabled=t.enabled,count=t.research_unit_count,'
        'unit_seconds=t.research_unit_energy/60,ingredients=t.research_unit_ingredients,'
        'trigger=t.prototype.research_trigger,prerequisites=pre,unlocks=eff} end; '
        'if a.names then for _,n in ipairs(a.names) do local t=e.force.technologies[n]; if t then add(t) end end '
        'else for _,t in pairs(e.force.technologies) do add(t) end end; '
        'local cur=e.force.current_research; return {technologies=out,current=cur and cur.name,'
        'progress=e.force.research_progress,queue=(function() local q={}; '
        'for _,t in pairs(e.force.research_queue or {}) do q[#q+1]=t.name end; return q end)()}',
        {'names': list(names) if names else None})


def entity_prototypes(actor_id, names):
    """Return size, crafting/mining speed, power use, categories and placement facts per entity."""
    return actor_rpc(actor_id,
        'local out={}; for _,n in ipairs(a) do local p=prototypes.entity[n]; assert(p,"unknown entity "..n); '
        'local box=p.collision_box; out[n]={type=p.type,width=math.ceil(box.right_bottom.x-box.left_top.x),'
        'height=math.ceil(box.right_bottom.y-box.left_top.y),crafting_speed=p.get_crafting_speed and p.get_crafting_speed("normal") or nil,'
        'crafting_categories=p.crafting_categories,mining_speed=p.mining_speed,'
        'energy_w=p.get_max_energy_usage and p.get_max_energy_usage("normal")*60 or nil,'
        'burner=p.burner_prototype~=nil,electric=p.electric_energy_source_prototype~=nil,'
        'inserter_rotation_speed=p.get_inserter_rotation_speed and p.get_inserter_rotation_speed("normal") or nil,'
        'belt_speed=p.belt_speed,mining_drill_radius=p.mining_drill_radius,supply_area_distance=p.get_supply_area_distance and p.get_supply_area_distance("normal") or nil,'
        'max_wire_distance=p.get_max_wire_distance and p.get_max_wire_distance("normal") or nil} end; return out', list(names))


def item_facts(actor_id, names):
    """Return stack size, fuel value and the entity each item places."""
    return actor_rpc(actor_id,
        'local out={}; for _,n in ipairs(a) do local p=prototypes.item[n]; assert(p,"unknown item "..n); '
        'out[n]={stack_size=p.stack_size,fuel_value=p.fuel_value,fuel_category=p.fuel_category,'
        'place_result=p.place_result and p.place_result.name or nil} end; return out', list(names))


def tick():
    """Return the current game tick and speed (no actor needed)."""
    return rpc('return {tick=game.tick,speed=game.speed,paused=game.tick_paused}')
