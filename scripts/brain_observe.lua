-- RCON-loaded observation for a labelled assistant; no running mod source changes.
local name, id = ...
local actor = game.get_entity_by_unit_number(id)
assert(actor and actor.valid and actor.type == "character", "assistant character missing")
local s, force = actor.surface, actor.force
local function items(inv) return inv and inv.get_contents() or {} end
local player = {name=name,surface=s.name,force=force.name,position=actor.position,
    health=actor.health,inventory=items(actor.get_inventory(defines.inventory.character_main)),
    reach_distance=10,resource_reach_distance=2.7,crafting_queue={}}
local resources, entities, enemies, sites = {}, {}, {}, {}
local nearest = {}
local drain = 0
for _,e in pairs(s.find_entities_filtered{type="resource"}) do
    drain = drain + e.amount
    local key = e.name..":"..math.floor(e.position.x/32)..":"..math.floor(e.position.y/32)
    local d = (e.position.x-actor.position.x)^2+(e.position.y-actor.position.y)^2
    if not nearest[key] or d < nearest[key].distance then
        nearest[key]={name=e.name,surface=s.name,position=e.position,amount=e.amount,distance=d}
    end
end
for _,r in pairs(nearest) do resources[#resources+1]=r end
for _,e in pairs(s.find_entities_filtered{type="furnace",force=force}) do
    entities[#entities+1]={name=e.name,type=e.type,unit_number=e.unit_number,
        surface=s.name,force=force.name,position=e.position,
        remaining_burning_fuel=e.burner and e.burner.remaining_burning_fuel or 0,
        inventories={fuel=items(e.get_inventory(defines.inventory.fuel)),
            furnace_source=items(e.get_inventory(defines.inventory.furnace_source)),
            furnace_result=items(e.get_inventory(defines.inventory.furnace_result))}}
end
for _,e in pairs(s.find_entities_filtered{force="enemy",position=actor.position,radius=32}) do
    enemies[#enemies+1]={type=e.type,surface=s.name,position=e.position}
end
for r=3,8 do
    for _,delta in ipairs({{r,0},{-r,0},{0,r},{0,-r}}) do
        local pos={x=math.floor(actor.position.x)+delta[1],y=math.floor(actor.position.y)+delta[2]}
        if s.can_place_entity{name="stone-furnace",position=pos,force=force} then sites[#sites+1]=pos end
    end
end
local stats=force.get_item_production_statistics(s)
local consumed=stats.output_counts
return {tick=game.tick,coverage={complete=true,scope="assistant surface resources/furnaces; enemies within 32 tiles"},
    players={player},entities=entities,enemies=enemies,world={resources=resources},
    build_sites={[name]=sites},iron_produced=stats.get_input_count("iron-plate"),
    resource_remaining=drain, fuel_consumed=(consumed.coal or 0)+(consumed.wood or 0)+(consumed["solid-fuel"] or 0)}
