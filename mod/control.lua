-- Control Bridge: structured RPCs for an LLM-controlled sandbox.
local bridge = {}
local function surface(name)
    local s = game.surfaces[name or "nauvis"]
    assert(s, "unknown surface: " .. tostring(name))
    return s
end
local function player(name)
    local p = game.get_player(name)
    assert(p, "unknown player: " .. tostring(name))
    return p
end
local function entity(id, surface_name)
    local e = (storage.entities or {})[id] or game.get_entity_by_unit_number(id)
    assert(e and e.valid and e.surface == surface(surface_name), "entity not found on surface")
    assert(e.force == game.forces.player, "entity is not owned by player force")
    return e
end
local function describe(e)
    -- Most prototypes cannot be retrieved by game.get_entity_by_unit_number.
    -- Persist references for entities returned by inspect/place so IDs remain usable after save/load.
    if e.unit_number then
        storage.entities = storage.entities or {}
        storage.entities[e.unit_number] = e
    end
    local d = {name=e.name, type=e.type, unit_number=e.unit_number,
        position={x=e.position.x, y=e.position.y}, direction=e.direction,
        force=e.force.name, health=e.health}
    if e.type == "assembling-machine" or e.type == "furnace" then
        local r = e.get_recipe()
        if r then d.recipe = r.name end
    end
    if e.type == "container" or e.type == "logistic-container" then
        d.inventory = e.get_inventory(defines.inventory.chest).get_contents()
    end
    return d
end
function bridge.status()
    local players, surfaces = {}, {}
    for _, p in pairs(game.players) do
        players[#players+1] = {name=p.name, connected=p.connected,
            position={x=p.position.x, y=p.position.y}, surface=p.surface.name}
    end
    for _, s in pairs(game.surfaces) do surfaces[#surfaces+1] = {name=s.name, index=s.index} end
    return {tick=game.tick, speed=game.speed, players=players,
        connected_players=#game.connected_players, surfaces=surfaces, bridge_version="0.2.0"}
end
function bridge.inspect_area(x, y, radius, surface_name, name, limit)
    assert(radius > 0 and radius <= 64 and limit >= 1 and limit <= 200, "invalid query bounds")
    local filter = {area={{x-radius,y-radius},{x+radius,y+radius}}, limit=limit+1}
    if name ~= "" then filter.name = name end
    local entities = surface(surface_name).find_entities_filtered(filter)
    local result = {}
    for i, e in ipairs(entities) do
        if i <= limit then result[#result+1] = describe(e) end
    end
    return {entities=result, truncated=#entities>limit, surface=surface_name}
end
function bridge.place_entity(name, x, y, direction, surface_name)
    assert(prototypes.entity[name], "unknown entity prototype: " .. name)
    local s = surface(surface_name)
    local options = {name=name, position={x=x,y=y}, direction=defines.direction[direction], force="player"}
    assert(s.is_chunk_generated({math.floor(x/32),math.floor(y/32)}), "chunk is not generated")
    assert(s.can_place_entity(options), "cannot place entity at this position")
    options.raise_built = true
    local e = s.create_entity(options)
    assert(e, "entity creation failed")
    return describe(e)
end
function bridge.remove_entity(id, surface_name)
    local e = entity(id, surface_name)
    local d = describe(e)
    assert(e.destroy{raise_destroy=true}, "entity removal failed")
    if storage.entities then storage.entities[id] = nil end
    return {removed=d}
end
function bridge.insert_items(id, item, count, surface_name)
    assert(prototypes.item[item], "unknown item: " .. item)
    assert(count >= 1 and count <= 10000, "invalid item count")
    local e = entity(id, surface_name)
    local inserted = e.insert{name=item,count=count}
    return {unit_number=id, item=item, inserted=inserted}
end
function bridge.set_recipe(id, recipe, surface_name)
    local e = entity(id, surface_name)
    assert(e.type == "assembling-machine", "entity is not an assembling machine")
    if recipe ~= "" then assert(prototypes.recipe[recipe], "unknown recipe: " .. recipe) end
    e.set_recipe(recipe ~= "" and recipe or nil)
    local r = e.get_recipe()
    assert(recipe == "" or (r and r.name == recipe), "recipe was not applied")
    return describe(e)
end
function bridge.give_item(player_name, item_name, count)
    assert(prototypes.item[item_name], "unknown item: " .. item_name)
    assert(count >= 1 and count <= 10000, "invalid item count")
    local p = player(player_name)
    return {player=p.name, item=item_name, inserted=p.insert{name=item_name,count=count}}
end
function bridge.teleport(player_name, x, y, surface_name)
    local p = player(player_name)
    assert(p.teleport({x=x,y=y},surface(surface_name)), "teleport failed")
    return {player=p.name, position={x=p.position.x,y=p.position.y}, surface=p.surface.name}
end
function bridge.print_all(msg)
    game.print(msg)
    return {ok=true}
end
function bridge.save_game(name)
    assert(name:match("^[%w_-]+$"), "invalid save name")
    game.server_save(name)
    return {save_requested=name}
end
remote.add_interface("control-bridge", bridge)
commands.add_command("control-bridge-status", "Print server status", function()
    game.print(helpers.table_to_json(bridge.status()))
end)
