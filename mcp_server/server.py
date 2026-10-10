"""Factorio Control MCP server.

Exposes tools:
  - rcon_command: run any console command on the Factorio server
  - get_status:   call the control-bridge mod's status() RPC

Env vars: FACTORIO_HOST, FACTORIO_PORT, FACTORIO_RCON_PASSWORD
"""
import asyncio
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from rcon_client.client import RconClient

HOST = os.environ.get("FACTORIO_HOST", "127.0.0.1")
PORT = int(os.environ.get("FACTORIO_PORT", "27015"))
PASSWORD = os.environ.get("FACTORIO_RCON_PASSWORD", "")

server = Server("factorio-control")


def run(cmd: str) -> str:
    with RconClient(HOST, PORT, PASSWORD) as c:
        return c.command(cmd)


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="rcon_command",
            description="Run a Factorio console command via RCON (e.g. '/c game.print(1+1)').",
            inputSchema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        ),
        Tool(
            name="get_status",
            description="Query server status via the control-bridge mod (tick, player count).",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name, arguments):
    if name == "rcon_command":
        result = await asyncio.to_thread(run, arguments["command"])
    elif name == "get_status":
        result = await asyncio.to_thread(
            run, '/c rcon.print(game.table_to_json(remote.call("control-bridge", "status")))'
        )
    else:
        raise ValueError(f"unknown tool {name}")
    return [TextContent(type="text", text=result)]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
