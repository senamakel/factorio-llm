-- Observable whole-world summaries and detailed factory/player state for the local brain.
local S = {}
local copy = require("serialization").copy
local inventory_names = {"chest","fuel","burnt_result","furnace_source","furnace_result",
    "assembling_machine_input","assembling_machine_output","assembling_machine_modules",
    "lab_input","lab_modules","turret_ammo","roboport_robot","roboport_material",
    "car_trunk","car_ammo","cargo_wagon","rocket_silo_input","rocket_silo_output"}
local function optional(object,key)
    local ok, value=pcall(function() return object[key] end)
    if ok then return value end
end
local function contents(inv)
    return inv and inv.valid and inv.get_contents() or {}
end
function S.describe(e)
    local d={name=e.name,type=e.type,unit_number=e.unit_number,position={x=e.position.x,y=e.position.y},
        surface=e.surface.name,force=e.force.name,health=e.health, direction=e.direction, inventories={}}
    if e.unit_number then storage.entities=storage.entities or {}; storage.entities[e.unit_number]=e end
    for _, key in ipairs({"status","energy","active","electric_network_id","temperature","amount","crafting_progress"}) do
        d[key]=optional(e,key)
    end
    if e.type=="furnace" or e.type=="assembling-machine" then
        local recipe=e.get_recipe(); d.recipe=recipe and recipe.name
    end
    for _, name in ipairs(inventory_names) do
        local id=defines.inventory[name]
        if id then
            local ok, inv=pcall(e.get_inventory,id)
            if ok and inv and inv.valid then d.inventories[name]=contents(inv) end
        end
    end
    if e.burner then d.remaining_burning_fuel=e.burner.remaining_burning_fuel end
    local fluidbox=optional(e,"fluidbox")
    if fluidbox then
        d.fluids={}
        for i=1,#fluidbox do local f=fluidbox[i]; if f then d.fluids[#d.fluids+1]=copy(f) end end
    end
    if e.type=="transport-belt" or e.type=="underground-belt" or e.type=="splitter" then
        d.belt_items={}
        for i=1,2 do
            local ok,line=pcall(e.get_transport_line,i)
            if ok and line then d.belt_items[i]=line.get_contents() end
        end
    end
    return d
end
function S.get_players()
    local out={}
    for _,p in pairs(game.players) do
        out[#out+1]={name=p.name,connected=p.connected,force=p.force.name,surface=p.surface.name,
            position={x=p.position.x,y=p.position.y},health=p.character and p.character.health or 0,
            inventory=contents(p.get_main_inventory()),crafting_queue=copy(p.crafting_queue or {}),
            resource_reach_distance=p.resource_reach_distance,reach_distance=p.reach_distance,
            mining_state=copy(p.mining_state),walking_state=copy(p.walking_state),controller_type=p.controller_type}
    end
    return {players=out}
end
function S.get_game_stats()
    return {tick=game.tick,speed=game.speed,tick_paused=game.tick_paused,
        connected_players=#game.connected_players,players=#game.players,finished=game.finished,
        map_settings=copy(game.map_settings),pollution_enabled=game.map_settings.pollution.enabled}
end
function S.get_forces()
    local out={}
    for _,f in pairs(game.forces) do
        local technologies,recipes={},{ }
        for name,t in pairs(f.technologies) do
            technologies[name]={researched=t.researched,enabled=t.enabled,level=t.level}
        end
        for name,r in pairs(f.recipes) do
            recipes[name]={enabled=r.enabled,ingredients=copy(r.ingredients),products=copy(r.products),energy=r.energy}
        end
        out[#out+1]={name=f.name,research=f.current_research and f.current_research.name,
            research_progress=f.research_progress,technologies=technologies,recipes=recipes}
    end
    return {forces=out}
end
function S.get_production_info()
    local out={}
    for _,f in pairs(game.forces) do
        for _,s in pairs(game.surfaces) do
            local items=f.get_item_production_statistics(s)
            local fluids=f.get_fluid_production_statistics(s)
            local kills=f.get_kill_count_statistics(s)
            out[#out+1]={force=f.name,surface=s.name,item_produced=copy(items.input_counts),
                item_consumed=copy(items.output_counts),fluid_produced=copy(fluids.input_counts),
                fluid_consumed=copy(fluids.output_counts),kills=copy(kills.input_counts)}
        end
    end
    return {production=out}
end
function S.get_factory_entities()
    local out={}
    for _,s in pairs(game.surfaces) do
        for _,f in pairs(game.forces) do
            if f.name~="neutral" and f.name~="enemy" then
                for _,e in pairs(s.find_entities_filtered{force=f}) do out[#out+1]=S.describe(e) end
            end
        end
    end
    return {entities=out}
end
function S.get_enemy_info()
    local out, evolution={},{ }
    for _,s in pairs(game.surfaces) do
        evolution[s.name]=game.forces.enemy.get_evolution_factor(s)
        for _,e in pairs(s.find_entities_filtered{force="enemy"}) do
            out[#out+1]={name=e.name,type=e.type,force="enemy",surface=s.name,position={x=e.position.x,y=e.position.y},health=e.health}
        end
    end
    return {enemies=out,evolution=evolution}
end
function S.get_world_info(player_name)
    local surfaces,resources={},{}
    local focus=player_name and game.get_player(player_name)
    for _,s in pairs(game.surfaces) do
        local chunks,patches={},{ }
        local center=focus and focus.surface==s and focus.position or {x=0,y=0}
        for c in s.get_chunks() do chunks[#chunks+1]={x=c.x,y=c.y} end
        for _,e in pairs(s.find_entities_filtered{type="resource"}) do
            local cx,cy=math.floor(e.position.x/32),math.floor(e.position.y/32)
            local key=e.name..":"..cx..":"..cy
            local p=patches[key]
            local dist=(e.position.x-center.x)^2+(e.position.y-center.y)^2
            if not p then
                p={name=e.name,surface=s.name,chunk={x=cx,y=cy},amount=0,count=0,position={x=e.position.x,y=e.position.y},distance=dist}
                patches[key]=p
            end
            p.amount=p.amount+e.amount; p.count=p.count+1
            if dist<p.distance then p.distance=dist; p.position={x=e.position.x,y=e.position.y} end
        end
        for _,p in pairs(patches) do p.distance=nil; resources[#resources+1]=p end
        surfaces[#surfaces+1]={name=s.name,index=s.index,daytime=s.daytime,peaceful=s.peaceful_mode,
            pollution=s.get_total_pollution(),chunks=chunks,tree_count=s.count_entities_filtered{type="tree"},
            water_tiles=s.count_tiles_filtered{collision_mask="water_tile"},map_gen_settings=copy(s.map_gen_settings)}
    end
    return {world={surfaces=surfaces,resources=resources}}
end
function S.get_build_sites(player_name)
    local p=game.get_player(player_name)
    if not p or not p.character then return {sites={}} end
    local sites={}
    for r=3,8 do
        for _,delta in ipairs({{r,0},{-r,0},{0,r},{0,-r},{r,r},{-r,-r}}) do
            local pos={x=math.floor(p.position.x)+delta[1],y=math.floor(p.position.y)+delta[2]}
            if p.surface.can_place_entity{name="stone-furnace",position=pos,force=p.force} and
                (pos.x-p.position.x)^2+(pos.y-p.position.y)^2<=p.reach_distance^2 then
                sites[#sites+1]=pos
            end
        end
    end
    return {sites=sites}
end
function S.get_chunk_info(surface_name,x,y)
    local s=game.surfaces[surface_name]; assert(s,"unknown surface")
    local area={{x*32,y*32},{x*32+32,y*32+32}}
    local entities,tiles={},{ }
    for _,e in pairs(s.find_entities_filtered{area=area}) do entities[#entities+1]=S.describe(e) end
    for _,t in pairs(s.find_tiles_filtered{area=area}) do tiles[#tiles+1]={name=t.name,position={x=t.position.x,y=t.position.y}} end
    return {entities=entities,tiles=tiles,surface=surface_name,chunk={x=x,y=y}}
end
return S
