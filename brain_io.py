"""Small RCON adapter: escaped arguments, actor lookup, structured replies."""
import json
from mcp_server.server import lua_string, run


def rpc(body):
    """Run a Lua API adapter; require structured success and propagate game errors."""
    raw = run('/c local ok,v=pcall(function() ' + body +
              ' end); rcon.print(helpers.table_to_json({ok=ok,value=ok and v or nil,error=not ok and tostring(v) or nil}))')
    result = json.loads(raw)
    if not result['ok']:
        raise RuntimeError(result['error'])
    return result.get('value')


def actor_rpc(actor_id, body, args=None):
    """Resolve an unattached character, decode escaped JSON arguments, and call APIs."""
    if not isinstance(actor_id, int) or actor_id <= 0:
        raise ValueError('actor ID must be a positive integer')
    prefix = ('local e=game.get_entity_by_unit_number(' + str(actor_id) + '); '
              'assert(e and e.valid and e.type=="character" and not e.player,"assistant unavailable"); '
              'local s=e.surface; local inv=e.get_inventory(defines.inventory.character_main); ')
    if args is not None:
        prefix += 'local a=helpers.json_to_table(' + lua_string(json.dumps(args, allow_nan=False)) + '); '
    return rpc(prefix + body)
