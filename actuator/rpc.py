"""Persistent RCON transport for the actuator; the only module that sends Lua.

Connection settings come from ``FACTORIO_CONNECTION_FILE`` (default: the
checkout's ``server/data/connection.json``) and the ``FACTORIO_HOST`` /
``FACTORIO_PORT`` / ``FACTORIO_RCON_PASSWORD`` overrides, read on first use.
Every call wraps its Lua body in ``pcall`` and returns decoded JSON, raising
``RuntimeError`` with the game's message when the body fails.
"""
import json
import os
import re
from pathlib import Path
import threading

from rcon_client.client import RconClient, RconError

ROOT = Path(__file__).resolve().parents[1]
_lock = threading.Lock()
_client = None


def settings():
    """Return host, port and password for the configured server."""
    path = Path(os.environ.get('FACTORIO_CONNECTION_FILE', ROOT / 'server/data/connection.json'))
    record = json.loads(path.read_text()) if path.exists() else {}
    password = os.environ.get('FACTORIO_RCON_PASSWORD', record.get('password', ''))
    if not password:
        raise RuntimeError(f'RCON password missing; no connection file at {path}')
    return (os.environ.get('FACTORIO_HOST', record.get('host', '127.0.0.1')),
            int(os.environ.get('FACTORIO_PORT', record.get('port', 27015))), password)


def lua_string(value):
    """Encode text as a Lua string literal of fixed-width byte escapes (UTF-8 safe)."""
    return '"' + ''.join('\\%03d' % b for b in value.encode('utf-8')) + '"'


def _command(text):
    """Send one console command over the shared connection, reconnecting once."""
    global _client
    with _lock:
        for attempt in (0, 1):
            try:
                if _client is None:
                    host, port, password = settings()
                    _client = RconClient(host, port, password, timeout=10)
                    _client.connect()
                return _client.command(text)
            except (OSError, RconError) as exc:
                try:
                    if _client is not None:
                        _client.close()
                except (OSError, RconError):
                    pass
                _client = None
                if attempt:
                    raise RuntimeError(f'RCON transport error: {exc}') from exc


def rpc(body, args=None):
    """Run a Lua body (which may read ``a`` = decoded args) and return its value."""
    prefix = ''
    if args is not None:
        prefix = 'local a=helpers.json_to_table(' + lua_string(json.dumps(args, allow_nan=False)) + '); '
    raw = _command('/c local ok,v=pcall(function() ' + prefix + body + ' end); '
                   'rcon.print(helpers.table_to_json({ok=ok,value=ok and v or nil,'
                   'error=not ok and tostring(v) or nil}))')
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'unexpected console reply: {raw[:200]!r}') from exc
    if not result['ok']:
        raise RuntimeError(re.sub(r'^\[string "[^"]*"\]:\d+: ', '', result['error'] or 'unknown game error'))
    return result.get('value')


ACTOR = ('local e=game.get_entity_by_unit_number({id}); '
         'assert(e and e.valid and e.type=="character" and not e.player,"assistant unavailable"); '
         'local s=e.surface; local inv=e.get_inventory(defines.inventory.character_main); ')


def actor_rpc(actor_id, body, args=None):
    """Run a Lua body with ``e`` (the actor character), ``s`` (surface) and ``inv`` bound."""
    if not isinstance(actor_id, int) or isinstance(actor_id, bool) or actor_id <= 0:
        raise ValueError('actor ID must be a positive integer')
    return rpc(ACTOR.format(id=actor_id) + body, args)
