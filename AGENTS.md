# AGENTS.md — recursive-factorio

This repository runs a Factorio 2.1 sandbox and exposes live inspection and edits
through a stdlib RCON client, the control-bridge Lua mod, and a stdio MCP server.

## Development workflow

Execute clear requests directly. Preserve unrelated changes. Before new
implementation, fetch the canonical remote, fast-forward the primary checkout's
default branch, then run `worktree <slug>` and work in its reported path. If the
base cannot fast-forward, investigate without resetting. Do not edit main.

Bug fixes require a regression test that fails before the fix and passes after.
Never commit credentials, `.venv/`, or `server/data/`. Do not squash commits or
undo automatic checkpoint commits. Any PR targets the canonical repo and should
be ready for review when complete.

## Commands

- `./factorio setup` — install dependencies and generate private runtime config
- `./factorio start` — start/resume the local world in the background
- `./factorio join` — open the desktop client with matching mods and connect
- `./factorio status` — live status
- `./factorio register` — register this checkout's MCP entrypoint in Codex
- `./factorio mcp-config [--format openhuman|codex|json]` — print client config
- `./factorio mcp` — stdio protocol server; never print diagnostics on stdout
- `./factorio check` — offline tests and read-only live MCP checks
- `./factorio check --edits` — disposable-surface live mutation/save tests
- `./factorio episode [--seed N] [--wall-secs S]` — score a brain on a disposable seeded world
- `./factorio gates` — the RSI loop's gates: honesty check + offline brain tests
- `./factorio memory up|remember|recall|list` — shared hive memory (dedicated CortexDB)
- `./factorio stop` — save and gracefully stop this checkout's server

`setup` detects the Steam installation on macOS; other installations may need
`--binary` and `--read-data`. Runtime paths derive from the checkout. The MCP
entrypoint works regardless of cwd and reads `server/data/connection.json`.
Env overrides: `FACTORIO_HOST`, `FACTORIO_PORT`, `FACTORIO_RCON_PASSWORD`,
`FACTORIO_CONNECTION_FILE`. Settings load at import; reconnect MCP after changes.

## Controlling the live world

1. Call `get_status`; identify the connected player's name, surface and position.
2. Call `inspect_area` around the intended site before making changes. Respect
   existing builds. If results are truncated, reduce radius or filter by name.
3. Prefer typed tools: `place_entity`, `insert_items`, `set_recipe`, `give_item`,
   `teleport`, `remove_entity`, `print_all`, `save_game`. Direction is
   north/east/south/west; names are Factorio prototype names.
4. Use the returned `unit_number` from inspect/place for follow-up entity edits.
   Mod storage retains these references across saves; direct
   `game.get_entity_by_unit_number` does not work for every prototype.
5. Read back the changed area/inventory/recipe. A successful command transport
   is not proof that the requested world change happened.
6. Save after useful work. `save_game` requests a save asynchronously; check the
   file/log if claiming durable completion.

These tools create items/buildings directly, without inventory costs. An
assistant character can be created with raw Lua and labelled via rendering; it
is a visible entity, not a second connected human client or an autonomous loop.
Do not claim to be walking/building autonomously unless that behavior is running.

Raw `rcon_command` takes a full console command, typically `/c ...`. Use
`rcon.print(...)` for tool output and `game.print(...)` for chat. In Factorio 2.1,
JSON conversion is `helpers.table_to_json` / `helpers.json_to_table`. Console Lua
disables achievements. Typed tools encode UTF-8 arguments as fixed-width Lua
byte escapes; retain this encoding and explicit error handling.

## Mods and runtime ownership

The server and desktop client must use exactly matching mod versions and source.
The current mod is `control-bridge_0.2.0`. `join` passes the server's mod directory;
for a normal Steam launch use `./factorio client-mod`, restart the client and sync.
The custom bridge is local, not downloadable from the mod portal.

Do not edit Lua while users are connected: deploy changed mod source with a
coordinated save, server restart and client reload. Python MCP changes only need
an MCP reconnect. Do not stop an unrelated server or reuse an occupied port.
Saves and credentials belong to the current worktree; preserve them when moving
or retiring it. The repository-root `server/config.ini` is only a note; the actual
config is generated at `server/data/config.ini`.

## Verification and layout

`./factorio check` runs `test_mcp_tools`, `test_factorio_setup`, both RCON protocol
scripts, TOML/JSON configuration checks and live MCP. `--edits` tests placement,
collision rejection, inventory read-back, recipe changes, removal and a new save
on a temporary surface. Optional `reload-check` tests saved demo references on a
second server with automatically selected free ports; it requires demo.json.

RSI files: `actuator/` (honest game access), `harness/` (episode servers,
scoring, gates), `knowledge/` (wiki cache, live prototypes), `memory/`
(CortexDB), `loops/factorio-brain/` (tinyrsi loop: manifest, hive, scorer).

Core files: `mcp_server/server.py` (tools), `mod/control.lua` (RPC behavior),
`scripts/factorio.py` (lifecycle), `rcon_client/client.py` (protocol).
Use `.venv/bin/python` for Python commands. Check the full exit code and output;
never treat printed smoke output as proof when the tool result contains an error.

## Code and documentation conventions

- Write docstrings for public modules, classes and functions. Explain inputs,
  outputs, side effects and meaningful failure cases; keep them accurate as code changes.
- Keep each source file below 500 lines of code, excluding comments, docstrings
  and blank lines. Split growing files into focused modules before crossing that limit.
- Prefer small, reusable helper functions and clear module boundaries: observation,
  decisions, execution and persistence should remain independently testable.
- Use descriptive names and a simple directory structure. Avoid catch-all utility
  modules and hidden global state when explicit dependencies work.
- Maintain a README.md in each substantive code folder describing its purpose,
  important files, interfaces, commands and verification. Update the root README
  when behavior or setup changes.
- Keep credentials in private, ignored .env files and runtime history in ignored
  SQLite files. Never copy keys or passwords into logs, examples, source or commits.
- The brain makes local deterministic decisions; no LLM/API call is made at
  runtime. Self-improvement happens offline in the tinyrsi loop
  (`loops/factorio-brain`): a hive edits `brain/` in candidate worktrees, the
  frozen harness scores each candidate on disposable seeded worlds, and only
  candidates that pass the gates and win the paired seed test are promoted to
  `rsi/main`. Never silently rewrite the brain outside that loop.
- The brain reaches the game only through the frozen `actuator` package
  (`actions`, `queries`); `harness/honesty.py` enforces this. Do not add Lua,
  RCON, sockets or subprocesses to `brain/`. `actuator/`, `harness/`,
  `knowledge/` and `loops/` change only by human-reviewed PRs.