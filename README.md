# factorio-control

Programmatic control of a Factorio server: RCON client, Lua mod helpers, and an MCP server exposing them as tools.

Repo: https://github.com/senamakel/factorio-llm

## Layout
- `rcon_client/` - stdlib RCON client + CLI (`python -m rcon_client.cli '/c game.print(game.tick)')`
- `mod/` - `control-bridge` mod exposing `remote.call("control-bridge", ...)` RPCs
- `mcp_server/` - MCP server with `rcon_command` and `get_status` tools
- `docker/` - Dockerfile + compose to run the MCP server as a container
- `scripts/` - helper launch scripts and tests

## OpenHuman MCP registration
Connections -> MCP -> Add server (or a `[[mcp_client.servers]]` entry in the user config):

```toml
[[mcp_client.servers]]
name = "factorio-control"
command = "/Users/enamakel/work/personal/recursive-factorio/.venv/bin/python"
args = ["-m", "mcp_server.server"]
working_dir = "/Users/enamakel/work/personal/recursive-factorio"

[mcp_client.servers.env]
FACTORIO_HOST = "127.0.0.1"
FACTORIO_PORT = "27015"
FACTORIO_RCON_PASSWORD = "<your rcon password>"
```

## Server setup
Enable RCON by launching Factorio with:

    factorio --start-server your-save.zip \
        --rcon-port 27015 --rcon-password YOURPASSWORD \
        --mod-directory ../mods

## Install the mod
Copy or symlink `mod/` into your Factorio `mods` directory as `control-bridge_0.1.0/`.

## Run the MCP server directly

    pip install -r requirements.txt
    export FACTORIO_HOST=127.0.0.1 FACTORIO_PORT=27015 FACTORIO_RCON_PASSWORD=...
    python -m mcp_server.server

Or with Docker (from `docker/`; needs DOCKER_BUILDKIT=0 on some hosts):

    docker compose up --build

The MCP server speaks stdio, so point your MCP client at the command above.
