"""Factorio tools over stdio MCP. Settings are loaded at process startup."""
import json
import math
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from rcon_client.client import RconClient

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(os.environ.get('FACTORIO_CONNECTION_FILE', ROOT / 'server/data/connection.json'))
settings = json.loads(CONFIG.read_text()) if CONFIG.exists() else {}
HOST = os.environ.get('FACTORIO_HOST', settings.get('host', '127.0.0.1'))
PORT = int(os.environ.get('FACTORIO_PORT', settings.get('port', 27015)))
PASSWORD = os.environ.get('FACTORIO_RCON_PASSWORD', settings.get('password', ''))

mcp = FastMCP('factorio-control', instructions=(
    'Control a live Factorio sandbox. Start with get_status and inspect_area. '
    'Use prototype names (iron-chest, transport-belt, assembling-machine-1). '
    'Inspect after each change to confirm the result; save_game after useful work. '
    'Coordinates use tiles; direction is north/east/south/west. '
    'Typed tools return JSON. rcon_command accepts arbitrary Lua via /c; '
    'use rcon.print for output. Changes are immediate and do not consume player items.'
))


def run(cmd: str) -> str:
    if not PASSWORD:
        raise ValueError('RCON password missing. Run scripts/factorio.py setup first.')
    with RconClient(HOST, PORT, PASSWORD) as c:
        return c.command(cmd)


def lua_string(value: str) -> str:
    """Encode bytes with fixed-width Lua escapes, including UTF-8 and newlines."""
    return '"' + ''.join('\\%03d' % b for b in value.encode('utf-8')) + '"'


def bridge(method: str, *args) -> dict:
    payload = lua_string(json.dumps(list(args), ensure_ascii=False, allow_nan=False))
    cmd = ('/c local a=helpers.json_to_table(' + payload + '); '
           'local ok,v=pcall(remote.call,"control-bridge",' + lua_string(method) + ',table.unpack(a)); '
           'if not ok then v={error=tostring(v)} end; rcon.print(helpers.table_to_json(v))')
    response = run(cmd)
    try:
        result = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError('Invalid control-bridge response: ' + response[:500]) from exc
    if not isinstance(result, dict):
        raise ValueError('Expected a JSON object from control-bridge')
    if 'error' in result:
        raise ValueError(result['error'])
    # Factorio serializes empty Lua arrays as JSON objects.
    for key in ('players', 'surfaces', 'entities'):
        if result.get(key) == {}:
            result[key] = []
    for entity in result.get('entities', []) + ([result] if 'unit_number' in result else []):
        if entity.get('inventory') == {}:
            entity['inventory'] = []
    return result


@mcp.tool()
def rcon_command(command: str) -> str:
    """Run a console command or /c Lua. Use rcon.print(...) to return output."""
    return run(command)


@mcp.tool()
def get_status() -> dict:
    """Get tick, speed, players with positions, surfaces, and bridge version."""
    return bridge('status')


@mcp.tool()
def inspect_area(x: float, y: float, radius: float = 16, surface: str = 'nauvis',
                 name: str = '', limit: int = 100) -> dict:
    """List nearby entities, unit numbers, positions, recipes and inventories. Radius <=64, limit <=200."""
    if not all(math.isfinite(v) for v in (x, y, radius)) or not 0 < radius <= 64 or not 1 <= limit <= 200:
        raise ValueError('Use finite coordinates, radius 0..64, and limit 1..200')
    return bridge('inspect_area', x, y, radius, surface, name, limit)


@mcp.tool()
def place_entity(name: str, x: float, y: float, direction: str = 'north',
                 surface: str = 'nauvis') -> dict:
    """Build an entity immediately for the player force. Fails if the location is occupied."""
    if direction not in ('north', 'east', 'south', 'west'):
        raise ValueError('direction must be north/east/south/west')
    return bridge('place_entity', name, x, y, direction, surface)


@mcp.tool()
def remove_entity(unit_number: int, surface: str = 'nauvis') -> dict:
    """Destroy one player-owned entity by its unit number from inspect_area."""
    return bridge('remove_entity', unit_number, surface)


@mcp.tool()
def insert_items(unit_number: int, item: str, count: int, surface: str = 'nauvis') -> dict:
    """Insert items into an entity (chest/machine/furnace); returns the actual inserted count."""
    if not 1 <= count <= 10000:
        raise ValueError('count must be 1..10000')
    return bridge('insert_items', unit_number, item, count, surface)


@mcp.tool()
def set_recipe(unit_number: int, recipe: str, surface: str = 'nauvis') -> dict:
    """Set an assembling machine recipe by unit number. Use an empty recipe to clear it."""
    return bridge('set_recipe', unit_number, recipe, surface)


@mcp.tool()
def give_item(player_name: str, item_name: str, count: int = 100) -> dict:
    """Give items to an existing player. Player names are listed by get_status."""
    if not 1 <= count <= 10000:
        raise ValueError('count must be 1..10000')
    return bridge('give_item', player_name, item_name, count)


@mcp.tool()
def teleport(player_name: str, x: float, y: float, surface: str = 'nauvis') -> dict:
    """Teleport an existing player to a surface and tile position."""
    return bridge('teleport', player_name, x, y, surface)


@mcp.tool()
def print_all(message: str) -> dict:
    """Display a chat message to everyone in the game."""
    return bridge('print_all', message)


@mcp.tool()
def save_game(name: str = 'llm-save') -> dict:
    """Request a server save under server/data/saves. Saving finishes asynchronously."""
    if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in name):
        raise ValueError('save name must contain only letters, digits, hyphens and underscores')
    return bridge('save_game', name)


if __name__ == '__main__':
    mcp.run()
