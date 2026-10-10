"""Smoke-test: start the MCP server, send an initialize request, print the reply."""
import os
import subprocess
import sys

env = {
    **os.environ,
    "FACTORIO_HOST": "127.0.0.1",
    "FACTORIO_PORT": "27015",
    "FACTORIO_RCON_PASSWORD": "x",
}
proc = subprocess.Popen(
    ["./.venv/bin/python", "-m", "mcp_server.server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
)
init = (
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":'
    '{"protocolVersion":"2024-11-05","capabilities":{},'
    '"clientInfo":{"name":"t","version":"0"}}}\n'
)
try:
    out, err = proc.communicate(init.encode(), timeout=10)
except subprocess.TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()
    print("TIMEOUT (server stayed alive; no response?)")
print("STDOUT:", out.decode()[:600])
print("STDERR:", err.decode()[:400])
sys.exit(0)
