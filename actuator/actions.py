"""Honest actor actions: everything a player character could do, nothing more.

Rules every action enforces:
- the target must be within the actor's reach (``LuaControl.can_reach_entity``
  or ``can_place_entity`` with the character's build distance);
- buildings come out of the actor's inventory and items move between real
  inventories (nothing is created or destroyed by the actuator);
- crafting uses the engine queue with real ingredients and real time;
- walking and mining set native input state; the caller times and stops them.
No action teleports, unlocks technology, changes game speed or creates items.
"""
from actuator.rpc import actor_rpc, rpc

DIRECTIONS = ('north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest')
STOP = 'e.walking_state={walking=false}; e.mining_state={mining=false}; '
FIND = ('local f=s.find_entities_filtered{position=a.position,radius=a.radius or 0.5,force=e.force}; '
        'local t=nil; for _,x in ipairs(f) do if (not a.unit_number or x.unit_number==a.unit_number) '
        'and (not a.name or x.name==a.name) and x.type~="character" then t=x; break end end; '
        'assert(t and t.valid,"target entity missing"); ')
REACH = 'assert(e.can_reach_entity(t),"target out of reach"); '


def _direction(name):
    if name not in DIRECTIONS:
        raise ValueError(f'direction must be one of {DIRECTIONS}')
    return name


def _count(count, upper=100000):
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= upper:
        raise ValueError(f'count must be an integer 1..{upper}')
    return count


def halt(actor_id, cancel_crafting=False):
    """Stop walking and mining; optionally cancel the whole crafting queue (refunding it)."""
    return actor_rpc(actor_id, STOP +
        'if a.cancel then local q=e.crafting_queue or {}; for i=#q,1,-1 do '
        'e.cancel_crafting{index=q[i].index,count=q[i].count} end end; return {ok=true}',
        {'cancel': bool(cancel_crafting)})


def walk(actor_id, direction):
    """Start walking in one of eight directions until ``halt``; returns the position."""
    return actor_rpc(actor_id, 'e.mining_state={mining=false}; '
        'e.walking_state={walking=true,direction=defines.direction[a.d]}; return {ok=true,position=e.position}',
        {'d': _direction(direction)})


def mine(actor_id, position, name):
    """Start mining a resource, tree or rock named ``name`` at ``position`` until ``halt``.

    Raises when the target is missing, depleted or out of resource reach.
    Products land in the actor's inventory as the engine finishes each cycle.
    """
    return actor_rpc(actor_id, STOP +
        'local t=s.find_entities_filtered{name=a.name,position=a.position,radius=0.5}[1]; '
        'assert(t and t.valid,"mining target missing"); assert(t.type=="resource" or t.type=="tree" '
        'or t.type=="simple-entity","only resources, trees and rocks can be mined; use pickup for buildings"); '
        'assert(t.type~="resource" or t.amount>0,"resource depleted"); '
        'assert(e.can_reach_entity(t),"mining target out of reach"); e.selected=t; '
        'e.mining_state={mining=true,position=t.position}; '
        'return {ok=true,target=t.name,position=t.position,mining_time=t.prototype.mineable_properties.mining_time,'
        'amount=t.type=="resource" and t.amount or nil}', {'name': name, 'position': position})


def craft(actor_id, recipe, count):
    """Queue handcrafting with real ingredients; returns the number started and game seconds."""
    return actor_rpc(actor_id,
        'local r=e.force.recipes[a.recipe]; assert(r and r.enabled,"recipe unavailable"); '
        'local n=e.begin_crafting{recipe=a.recipe,count=a.count}; assert(n>0,"craft ingredients unavailable"); '
        'return {ok=true,started=n,game_seconds=n*r.energy/(1+e.character_crafting_speed_modifier)}',
        {'recipe': recipe, 'count': _count(count, 1000)})


def build(actor_id, item, position, direction='north'):
    """Place one ``item`` from inventory at ``position``; collision and build reach are checked.

    Collision uses the surface's script check (the player-style manual check
    rejects valid offshore-pump shorelines); reach is the character's build
    distance to the requested position.

    Returns the new entity's name, unit_number and actual (snapped) position.
    """
    return actor_rpc(actor_id,
        'assert(inv.get_item_count(a.item)>0,"building item missing from inventory"); '
        'local ip=prototypes.item[a.item]; assert(ip and ip.place_result,"item is not placeable"); '
        'local o={name=ip.place_result.name,position=a.position,direction=defines.direction[a.direction]}; '
        'local dx,dy=a.position.x-e.position.x,a.position.y-e.position.y; '
        'local reach=e.prototype.build_distance+e.character_build_distance_bonus; '
        'assert(dx*dx+dy*dy<=reach*reach,"site out of build reach"); '
        'o.force=e.force; assert(s.can_place_entity(o),"site occupied"); o.raise_built=true; '
        'local b=s.create_entity(o); assert(b,"build failed"); inv.remove{name=a.item,count=1}; '
        'return {ok=true,name=b.name,unit_number=b.unit_number,position=b.position}',
        {'item': item, 'position': position, 'direction': _direction(direction)})


def pickup(actor_id, position, unit_number=None, name=None):
    """Mine one of the actor's own buildings back into inventory, with its contents."""
    return actor_rpc(actor_id, STOP + FIND + REACH +
        'local n=t.name; local ok=e.mine_entity(t,false); assert(ok,"pickup failed (inventory full?)"); '
        'return {ok=true,name=n}', {'position': position, 'unit_number': unit_number, 'name': name})


def rotate(actor_id, position, unit_number=None, reverse=False):
    """Rotate one of the actor's buildings in reach; returns the new direction."""
    return actor_rpc(actor_id, FIND + REACH +
        'assert(t.rotatable,"entity cannot rotate"); t.rotate{reverse=a.reverse}; '
        'local d; for k,v in pairs(defines.direction) do if v==t.direction then d=k end end; return {ok=true,direction=d}',
        {'position': position, 'unit_number': unit_number, 'reverse': bool(reverse)})


def put(actor_id, position, item, count, inventory=None, unit_number=None):
    """Move up to ``count`` of ``item`` from the actor into a building in reach.

    With ``inventory`` (a ``defines.inventory`` name such as ``fuel``,
    ``crafter_input``, ``chest`` or ``lab_input``) the items go into that
    inventory; without it the engine routes them like a ctrl-click insert.
    Returns the amount actually moved; a full destination moves nothing.
    """
    return actor_rpc(actor_id, FIND + REACH +
        'local have=inv.get_item_count(a.item); local want=math.min(a.count,have); assert(want>0,"item not in inventory"); '
        'local n; if a.inventory then local d=defines.inventory[a.inventory]; assert(d,"unknown inventory"); '
        'local x=t.get_inventory(d); assert(x,"entity has no such inventory"); n=x.insert{name=a.item,count=want} '
        'else n=t.insert{name=a.item,count=want} end; '
        'if n>0 then inv.remove{name=a.item,count=n} end; return {ok=n>0,transferred=n}',
        {'position': position, 'item': item, 'count': _count(count), 'inventory': inventory, 'unit_number': unit_number})


def take(actor_id, position, item, count, inventory, unit_number=None):
    """Move up to ``count`` of ``item`` out of a named building inventory into the actor."""
    return actor_rpc(actor_id, FIND + REACH +
        'local d=defines.inventory[a.inventory]; assert(d,"unknown inventory"); local x=t.get_inventory(d); '
        'assert(x,"entity has no such inventory"); local want=math.min(a.count,x.get_item_count(a.item)); '
        'assert(want>0,"source is empty"); local n=inv.insert{name=a.item,count=want}; '
        'if n>0 then x.remove{name=a.item,count=n} end; return {ok=n>0,transferred=n}',
        {'position': position, 'item': item, 'count': _count(count), 'inventory': inventory, 'unit_number': unit_number})


def set_recipe(actor_id, position, recipe, unit_number=None):
    """Set an assembler's recipe; items it ejects go back to the actor's inventory."""
    return actor_rpc(actor_id, FIND + REACH +
        'assert(t.type=="assembling-machine","not an assembling machine"); '
        'if a.recipe then local r=e.force.recipes[a.recipe]; assert(r and r.enabled,"recipe unavailable") end; '
        'local back=t.set_recipe(a.recipe); for _,it in pairs(back or {}) do '
        'local n=inv.insert(it); assert(n==it.count,"no room for returned ingredients") end; '
        'return {ok=(t.get_recipe() and t.get_recipe().name)==a.recipe}',
        {'position': position, 'recipe': recipe, 'unit_number': unit_number})


def research(actor_id, technology):
    """Queue a technology for research (labs still need real science packs)."""
    return actor_rpc(actor_id,
        'local t=e.force.technologies[a.t]; assert(t,"unknown technology"); assert(not t.researched,"already researched"); '
        'local ok=e.force.add_research(a.t); return {ok=ok,current=e.force.current_research and e.force.current_research.name}',
        {'t': technology})


def place_ghosts(actor_id, rows):
    """Mark planned buildings as ghosts (visual only; ghosts build nothing without robots)."""
    return actor_rpc(actor_id,
        'local out={}; for _,p in ipairs(a) do local o={name="entity-ghost",inner_name=p.name,position=p.position,'
        'direction=defines.direction[p.direction or "north"],force=e.force}; '
        'local g=s.create_entity(o); assert(g,"ghost creation failed"); if p.recipe then g.set_recipe(p.recipe) end; '
        'out[#out+1]={name=g.ghost_name,position=g.position} end; return out', list(rows))


def show_status(actor_id, text):
    """Draw or update a status label above the actor."""
    return actor_rpc(actor_id,
        'if storage.teeny_label and storage.teeny_label.valid then storage.teeny_label.text=a.text '
        'else storage.teeny_label=rendering.draw_text{text=a.text,surface=s,target=e,'
        'color={r=0.1,g=0.8,b=1},alignment="center",target_offset={0,-3.5}} end; return true', {'text': str(text)[:200]})


def save(name):
    """Request an asynchronous server save under ``name``."""
    if not name.replace('-', '').replace('_', '').isalnum():
        raise ValueError('save name must be alphanumeric with - or _')
    return rpc('game.server_save(a.n); return true', {'n': name})
