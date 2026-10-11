# recursive-factorio

Run a local Factorio world and let an LLM inspect and change it through MCP.
The headless server keeps the simulation running; you can join in the desktop game
and watch the LLM build, edit inventories, change recipes, or teleport players.

Requires Python 3.10+ and an installed **Factorio 2.1.x**. On macOS, setup finds the
Steam installation automatically. Factorio itself is not downloaded by this repo.

## Start playing

```sh
./factorio setup
./factorio start
./factorio join
```

`setup` creates `.venv`, a private RCON password, the mod installation, and configs
under `server/data/`. `start` creates a peaceful map on first use and loads the
newest save thereafter. The server runs in the background on `127.0.0.1:34197`;
RCON listens on `127.0.0.1:27015`. It keeps simulating when nobody is connected.

`join` launches the desktop client with the same mods as the server. If you open
Factorio through Steam instead, run `./factorio client-mod`, restart the client,
connect via **Multiplayer → Connect to address → 127.0.0.1:34197**, and accept
**Sync mods**. The custom bridge is installed locally because it is not on the
mod portal. Space Age built-in mods may also be active; use the server's mod list.

For another installation or ports:

```sh
./factorio setup --binary /path/to/factorio --read-data /path/to/data \
  --port 27016 --game-port 34198
```

Setup detects the Steam installation on macOS and typical `bin/x64/factorio`
layouts elsewhere. `FACTORIO_BINARY` and `FACTORIO_READ_DATA` are also supported.
On other systems, pass `./factorio client-mod --client-mods /path/to/client/mods`
if using a separately launched client. Avoid launching a second desktop client
while one is already open.

## Connect an LLM

For Codex:

```sh
./factorio register
```

All project MCP servers live in `mcp.json`: `factorio-control` for the live game
and `factorio-wiki` for read-only access to https://wiki.factorio.com/ through
[ProfessionalWiki's MediaWiki MCP server](https://github.com/ProfessionalWiki/mediawiki-mcp-server).
The wiki server uses `mediawiki.json` and requires Node.js 22.12+ and `npx`.
The first launch downloads the pinned npm package; no wiki credentials are needed.
Manifest paths are relative to the repository root. For clients launched elsewhere,
use the exported configuration, which resolves local paths to absolute paths.
The control entry currently points at the running sandbox's private connection
file in `worktrees/factorio-mcp-setup`; its world and credentials stay there.

This registers every server from `mcp.json` in your user-level Codex config.
Start a new Codex session
(or reconnect MCP) so it loads the tools. `./factorio mcp-config --format codex`
prints the TOML for a project-scoped config instead. Configuration follows the
[official MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

For OpenHuman, run `./factorio mcp-config` and copy the generated TOML into the
user config, or add the same command and args in **Connections → MCP → Add server**.
The generated configuration has this shape; use the generated paths:

```toml
[[mcp_client.servers]]
name = "factorio-control"
command = "/absolute/path/to/repo/.venv/bin/python"
args = ["/absolute/path/to/repo/scripts/mcp_entrypoint.py"]
working_dir = "/absolute/path/to/repo"
```

For a client using JSON `mcpServers` configuration, run
`./factorio mcp-config --format json`. No API key is needed by the bridge: the LLM
runs in your MCP client, using its existing provider configuration.

The stdio entrypoint works from any working directory and reads the private
`server/data/connection.json` automatically. For an external server, override
`FACTORIO_HOST`, `FACTORIO_PORT`, and `FACTORIO_RCON_PASSWORD`, or point
`FACTORIO_CONNECTION_FILE` to another connection JSON. Settings load at startup;
reconnect the MCP client after changing them. `./factorio mcp` is also a stdio
entrypoint; it waits for protocol messages and does not present an interactive UI.

Try: **“Inspect the area around me and build a small iron smelting line.”**
Or: **“Put 100 iron plates in that chest, then verify its inventory and save.”**

## Local assistant brain

New worlds use an easy sandbox preset: no naturally spawning enemies, peaceful
mode, 600% resource patch size/richness and 300% frequency. This preset is independent
of expansion mods; it does not change an existing world's enabled mod list.
The local server runs headless in the background; the separate desktop client
connects to it to show and play the world.

All assistant logic and rules live in `brain/`. `brain/goal.py` defines iron and
first-research objectives. Add `--objective research` to the command below for
the real steam/electronics/red-science/Automation chain. Refresh attributed wiki
facts with `.venv/bin/python -m brain.enrichment`.
`brain/actions.py` exports high-level plans such as `mine_coal`, `mine_iron_ore`,
`build_furnace`, and `make_iron_plates`. Each action lives in its own file under
`brain/action_library/`, grouped into gathering, movement, manufacturing and inventory.
Python owns the behavior: `brain/observation.py` assembles observations and selects
resource candidates; `brain/execution.py` plans movement directions and durations;
`brain/logic.py` chooses tasks; `brain/runner.py` runs and times them. `brain/io.py` sends short
Lua API adapters to read state or apply an instruction. It does not upload Lua
files, install a new mod, or run policy/scoring logic inside Factorio.
`brain/score.py` rewards measured inventory gains, goal progress and plates produced
per game second. It penalizes depleted resources, consumed fuel, elapsed game
time, nearby enemies and damage. Production/fuel counters currently cover the
actor's force on its surface, so another factory can contribute to those scores.
Resource reads are bounded and local, with adaptive query radii recorded in each
observation; unknown distant resources are not treated as observed.

Run `.venv/bin/python -m brain --actor UNIT_NUMBER --steps 1200 --target 100`
using the inspected unit number of an unattached assistant character. Supply
`FACTORIO_CONNECTION_FILE` if the running server belongs to another checkout.
The loop stops at completion, danger, or its step limit and records observations,
decisions, actions, outcomes and learning in ignored `server/data/brain.sqlite3`.
Walking and mining use continuous native engine instructions with adaptive durations.
Clear, enemy-free walking legs and safe mining batches can last up to eight seconds;
uncertain actions are capped at two seconds. Python estimates travel time from
current movement speed and mining time from prototype speed, progress and batch
count. Routes are sampled for collision checks before using longer legs.
Actions stop on interruption. Handcrafting uses the native queue and real costs;
close machine transfers are paced and batched. Smelting runs in the
actual game furnace. The loop does not restart or modify the running mod.

## Tools

| Tool | What it does |
| --- | --- |
| `get_status` | Tick, speed, players, positions, surfaces, bridge version |
| `inspect_area` | Nearby entities, stable IDs, recipes, chest inventories |
| `place_entity` | Build an entity by prototype name, coordinates and direction |
| `remove_entity` | Destroy a player-owned entity by inspected ID |
| `insert_items` | Add items to a chest or machine and report actual inserted count |
| `set_recipe` | Change an assembler recipe |
| `give_item` | Give items to a named player |
| `teleport` | Move a named player to coordinates on a surface |
| `print_all` | Display an in-game chat message |
| `save_game` | Request a save; completion is asynchronous |
| `rcon_command` | Raw console commands and `/c` Lua for advanced operations |

This is a sandbox: building and item tools create things without consuming your
inventory. Lua console commands disable achievements. World changes happen
immediately. `inspect_area` is bounded to radius 64 and 200 entities; narrow the
query if `truncated` is true. Inspect/place records entity references in mod
storage so IDs can be used for subsequent edits and survive save/load.

For advanced Lua, Factorio 2.1 uses `helpers.table_to_json`, as documented in
[LuaHelpers](https://lua-api.factorio.com/latest/classes/LuaHelpers.html).
Use `rcon.print(...)` to return output; `game.print(...)` goes to in-game chat.
Entity lookup has prototype restrictions in
[LuaGameScript](https://lua-api.factorio.com/latest/classes/LuaGameScript.html#get_entity_by_unit_number),
which is why the bridge retains references to entities it inspects or creates.

## Operate and verify

```sh
./factorio status
./factorio check          # offline tests + read-only live MCP handshake/tool checks
./factorio check --edits  # build/inventory/recipe/remove tests on a disposable surface
./factorio stop          # save as llm-save and gracefully stop the managed server
./factorio start         # resume the newest save
```

Live checks require the server to be running. `--edits` cleans up its temporary
surface and verifies an actual new save ZIP. Errors fail the check. The optional
`./factorio reload-check` validates the current demo chest from
`server/data/demo.json` in a second isolated server; it never stops the live game.
It is intended for the local demonstration and requires its `llm-save.zip`.

Saves: `server/data/saves/`. Server log: `server/data/server.log`.
Client log when launched with `join`: `server/data/client.log`.
`stop` only signals the PID whose command references this checkout's config.
Occupied ports cause startup to fail without stopping other processes.

Keep `.venv/` and `server/data/` out of Git. Back up saves before deleting a
worktree: both runtime data and registered MCP paths belong to that checkout.

## Layout

- `factorio` — single command for setup, server/client lifecycle and verification
- `scripts/factorio.py` — config generation and background process management
- `scripts/mcp_entrypoint.py` — MCP entrypoint independent of the working directory
- `mcp_server/` — FastMCP stdio tools (MCP SDK 1.x)
- `mod/` — `control-bridge` 0.2.0 for Factorio 2.1
- `rcon_client/` — stdlib RCON protocol client and CLI
- `scripts/` — offline tests and live MCP/save verification
- `docker/` — optional containerized MCP bridge to an existing Factorio server

Docker does not run Factorio. Supply RCON credentials and use stdio attachment
(e.g. `docker compose -f docker/docker-compose.yml run --rm -T factorio-mcp`)
from a client that can launch that command. The host's Factorio must expose RCON
to the container; the default local launcher deliberately binds it to loopback.
