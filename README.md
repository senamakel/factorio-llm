# factorio-control

Programmatic control of a Factorio server: RCON client, Lua mod helpers, and an MCP server exposing them as tools.

## Layout
- `rcon_client/` - stdlib RCON client + CLI (`python -m rcon_client.cli '/c game.print(game.tick)')`
- `mod/` - `control-bridge` mod exposing `remote.call("control-bridge", ...)` RPCs
- `mcp_server/` - MCP server with `rcon_command` and `get_status` tools
- `docker/` - Dockerfile + compose to run the MCP server as a container
- `scripts/` - helper launch scripts

## Server setup
Enable RCON by launching Factorio with:

    factorio --start-server your-save.zip \
        --rcon-port 27015 --rcon-password YOURPASSWORD \
        --mod-directory ../mods

## Install the mod
Copy or symlink `mod/` into your Factorio `mods` directory as `control-bridge_0.1.0/`.

## Run the MCP server

    pip install -r requirements.txt
    export FACTORIO_HOST=127.0.0.1 FACTORIO_PORT=27015 FACTORIO_RCON_PASSWORD=...
    python -m mcp_server.server

Or with Docker (from `docker/`):

    docker compose up --build

The MCP server speaks stdio, so point your MCP client (e.g. this machine's agent) at the container's process or run it natively for simplest wiring.
