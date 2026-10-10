"""Live MCP session test: initialize, list tools, call both tools against a running server.

Env: FACTORIO_HOST / FACTORIO_PORT / FACTORIO_RCON_PASSWORD must point at a live server.
"""
import json
import os
import subprocess
import sys

proc = subprocess.Popen(
    ["./.venv/bin/python", "-m", "mcp_server.server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=os.environ.copy(),
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)


def rpc(obj):
    proc.stdin.write((json.dumps(obj) + "\n").encode())
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


try:
    rpc({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "t", "version": "0"},
        },
    })
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()

    r = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
             "params": {"name": "get_status", "arguments": {}}})
    print("get_status LIVE:", json.dumps(r["result"]["content"]))

    r2 = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
              "params": {"name": "rcon_command",
                         "arguments": {"command": "/c rcon.print('mcp round trip ok')"}}})
    print("rcon_command LIVE:", json.dumps(r2["result"]["content"]))
finally:
    proc.stdin.close()
    proc.wait(timeout=5)
    err = proc.stderr.read().decode()
    if err.strip():
        print("STDERR:", err[:200])
sys.exit(0)
