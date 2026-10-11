-- Inventory-costed assistant actions; movement uses collision-checked small teleports.
local id, a = ...
local actor=game.get_entity_by_unit_number(id)
assert(actor and actor.valid and not actor.player, "assistant missing or controlled by a human")
local s, inv=actor.surface,actor.get_inventory(defines.inventory.character_main)
if a.kind=="wait" then return {ok=true} end
if a.kind=="move" then
    local dx,dy=a.position.x-actor.position.x,a.position.y-actor.position.y
    local distance=math.sqrt(dx*dx+dy*dy)
    local step=math.min(0.75,math.max(0,distance-(a.stop_distance or 1)))
    if step==0 then return {ok=true} end
    local pos={x=actor.position.x+dx/distance*step,y=actor.position.y+dy/distance*step}
    -- Try a short sideways step when trees/buildings obstruct the direct line.
    if not s.can_place_entity{name="character",position=pos,force=actor.force} then
        pos={x=actor.position.x-dy/distance*step,y=actor.position.y+dx/distance*step}
    end
    assert(s.can_place_entity{name="character",position=pos,force=actor.force},"movement blocked")
    return {ok=actor.teleport(pos),position=actor.position}
end
if a.kind=="mine" then
    assert((actor.position.x-a.position.x)^2+(actor.position.y-a.position.y)^2<=2.7^2,"resource out of reach")
    local e=s.find_entities_filtered{name=a.resource,position=a.position,radius=0.1}[1]
    assert(e and e.amount>0,"resource depleted")
    local before=inv.get_item_count(a.resource)
    assert(e.mine{inventory=inv},"mining failed")
    return {ok=true,obtained=inv.get_item_count(a.resource)-before}
end
if a.kind=="craft" then
    assert(a.recipe=="stone-furnace" and a.count==1,"unsupported craft")
    assert(inv.get_item_count("stone")>=5 and inv.can_insert{name="stone-furnace",count=1},"craft inventory unavailable")
    inv.remove{name="stone",count=5}; inv.insert{name="stone-furnace",count=1}
    return {ok=true,crafted=1}
end
assert((actor.position.x-a.position.x)^2+(actor.position.y-a.position.y)^2<=100,"entity out of reach")
if a.kind=="build" then
    assert(a.item=="stone-furnace" and inv.get_item_count(a.item)>0,"building item missing")
    local options={name=a.item,position=a.position,force=actor.force,raise_built=true}
    assert(s.can_place_entity(options),"building site occupied")
    local e=s.create_entity(options); assert(e,"build failed")
    inv.remove{name=a.item,count=1}
    return {ok=true,unit_number=e.unit_number}
end
local e=s.find_entities_filtered{position=a.position,radius=0.1,type="furnace",force=actor.force}[1]
assert(e and e.unit_number==a.unit_number,"furnace missing")
local other=e.get_inventory(defines.inventory[a.inventory]); assert(other,"inventory missing")
local source,destination
if a.kind=="put" then source,destination=inv,other
elseif a.kind=="take" then source,destination=other,inv
else error("unsupported action") end
local count=math.min(a.count,source.get_item_count(a.item))
local inserted=destination.insert{name=a.item,count=count}
source.remove{name=a.item,count=inserted}
return {ok=inserted>0,transferred=inserted}
