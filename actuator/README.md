# actuator

The frozen, honest bridge between the brain and Factorio. `brain/` may only touch
the game through `actuator.actions` and `actuator.queries`; the RSI loop's
honesty gate (`harness/honesty.py`) rejects any other route, and the hive cannot
edit this folder.

| File | Purpose |
| --- | --- |
| `rpc.py` | Persistent RCON transport; the only module that sends Lua. Reads `FACTORIO_CONNECTION_FILE` (default `server/data/connection.json`, else the `mcp.json` manifest). |
| `queries.py` | Read-only queries: actor state, entities (allowlisted fields), tiles, placement checks, production statistics, recipes, technologies, entity/item prototypes. Empty Lua tables come back as lists. |
| `actions.py` | What a character can do: `halt`, `walk`, `mine`, `craft`, `build`, `pickup`, `rotate`, `put`, `take`, `set_recipe`, `research`, `place_ghosts`, `show_status`, `save`. |
| `controller.py` | Exclusive per-actor run ownership (`flock`), status and stop for brain processes. |

Honesty rules enforced in Lua: targets within the character's reach or build
distance; buildings consumed from inventory; items only moved between real
inventories; crafting through the engine queue; no teleport, tech unlock, game
speed change or item creation.

Verification: `.venv/bin/python -m unittest scripts.test_actuator` (offline) and
a live episode, `./factorio episode --seed 1 --wall-secs 120 --window-min 1`.
