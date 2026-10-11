# AGENTS.md — recursive-factorio

Programmatic control of a Factorio server: stdlib RCON client, the `control-bridge` Lua mod, and an MCP server exposing both over stdio.

## Layout

- `rcon_client/` — stdlib RCON client. CLI: `python -m rcon_client.cli '/c game.print(game.tick)'`
- `mod/` — `control-bridge` mod (Factorio 2.1), exposes `remote.call("control-bridge", ...)` RPCs: `status`, `give_item`, `teleport`, `print_all`
- `mcp_server/` — FastMCP server, tools `rcon_command` and `get_status`
- `docker/` — Dockerfile + compose for containerized MCP server
- `scripts/` — smoke tests (`smoke_mcp.py`, `test_rcon.py`, `test_rcon_adversarial.py`, `check_readme_toml.py`)
- `server/` — Factorio server data (`config.ini` points write-data here)

## Environment

- Python venv: `.venv` (deps: `pip install -r requirements.txt`, only `mcp>=1.0,<2.0`)
- Run MCP server: `.venv/bin/python -m mcp_server.server` (stdio)
- Env vars: `FACTORIO_HOST` (default 127.0.0.1), `FACTORIO_PORT` (default 27015), `FACTORIO_RCON_PASSWORD`
- Server data dir (this checkout): `/Users/enamakel/work/personal/recursive-factorio/server/data`
- Factorio data dir: `/Users/enamakel/Library/Application Support/Steam/steamapps/common/Factorio/factorio.app/Contents/data`

## Conventions

- MCP server reads env at import time; restarting the MCP client is required after config changes.
- RCON commands are sent exactly as typed; `/c ...` executes Lua, `/rcon.print(...)` style quoting matters. The CLI takes one argument, the full command.
- The mod must be installed/symlinked into the Factorio `mods` dir as `control-bridge_0.1.0/` for `get_status` to work.
- Do not commit `.venv/` or `server/data/` (see `.gitignore`).

## Verification

- `./scripts/smoke_mcp.py` — MCP handshake smoke test (needs env vars set)
- `./scripts/test_rcon.py`, `./scripts/test_rcon_adversarial.py` — RCON client tests
