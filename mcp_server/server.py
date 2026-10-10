"""Factorio Control MCP server (FastMCP, mcp 1.x).

Tools:
  - rcon_command: run any console command on the Factorio server
  - get_status:   call the control-bridge mod's status() RPC

Env vars: FACTORIO_HOST, FACTORIO_PORT, FACTORIO_RCON_PASSWORD
"""
import os

from mcp.server.fastmcp import FastMCP

from rcon_client.client import RconClient

HOST = os.environ.get("FACTORIO_HOST", "127.0.0.1")
PORT = int(os.environ.get("FACTORIO_PORT", "27015"))
PASSWORD = os.environ.get("FACTORIO_RCON_PASSWORD", "")

mcp = FastMCP("factorio-control")


def run(cmd: str) -> str:
    with RconClient(HOST, PORT, PASSWORD) as c:
        return c.command(cmd)


@mcp.tool()
def rcon_command(command: str) -> str:
    """Run a Factorio console command via RCON, e.g. '/c game.print(1+1)'."""
    return run(command)


@mcp.tool()
def get_status() -> str:
    """Query server status via the control-bridge mod (tick, player count)."""
    return run('/c rcon.print(game.table_to_json(remote.call("control-bridge", "status")))')


if __name__ == "__main__":
    mcp.run()
