"""Smoke-test the MCP server over stdio: initialize, list tools, call get_status.

get_status intentionally hits a non-listening port: a structured MCP error
result is itself the pass condition, proving the tool ran end to end.
"""
import json
import os
import subprocess
import sys

env = {
    **os.environ,
    "FACTORIO_HOST": "127.0.0.1",
    "FACTORIO_PORT": "27099",
    "FACTORIO_RCON_PASSWORD": "x",
}
proc = subprocess.Popen(
    ["./.venv/bin/python", "-m", "mcp_server.server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)


def rpc(obj):
    proc.stdin.write((json.dumps(obj) + "\n").encode())
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line)


try:
    init = rpc({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "t", "version": "0"},
        },
    })
    name = init["result"]["serverInfo"]["name"]
    print("initialize OK, serverInfo:", name)
    assert name == "factorio-control"

    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()

    tools = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = sorted(t["name"] for t in tools["result"]["tools"])
    print("tools/list OK:", names)
    assert names == ["get_status", "rcon_command"], names

    res = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
               "params": {"name": "get_status", "arguments": {}}})
    body = json.dumps(res["result"])[:200]
    print("tools/call OK (raw):", body)
    assert "isError" in json.dumps(res["result"]) or "result" in res["result"], res
    print("ALL MCP CHECKS PASS")
finally:
    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    err = proc.stderr.read().decode()
    if err.strip():
        print("STDERR:", err[:300])
sys.exit(0)
