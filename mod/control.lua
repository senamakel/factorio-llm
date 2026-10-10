-- Control Bridge: exposes remote.call("control-bridge", ...) helpers.
-- Usage from RCON: /c remote.call("control-bridge", "give_item", "player", "iron-plate", 100)

local bridge = {}

function bridge.status()
    return {
        tick = game.tick,
        players = #game.players,
    }
end

function bridge.give_item(player_name, item_name, count)
    local player = game.players[player_name] or game.player
    if not player then return "no player" end
    local inserted = player.insert { name = item_name, count = count or 10 }
    return string.format("inserted %d %s for %s", inserted, item_name, player.name)
end

function bridge.teleport(player_name, x, y)
    local player = game.players[player_name] or game.player
    if not player then return "no player" end
    player.teleport({ x = tonumber(x), y = tonumber(y) })
    return string.format("teleported %s to %d,%d", player.name, x, y)
end

function bridge.print_all(msg)
    game.print(msg)
    return "ok"
end

remote.add_interface("control-bridge", bridge)

-- Console command: /control-bridge-status
commands.add_command("control-bridge-status", "Print server status via control bridge", function()
    local s = bridge.status()
    game.print(string.format("tick=%d players=%d", s.tick, s.players))
end)
