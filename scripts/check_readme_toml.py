"""Validate the README's TOML snippet parses and its paths exist."""
import json
import os
import re

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
readme = open(os.path.join(repo, "README.md")).read()
block = re.search(r"```toml\n(.*?)```", readme, re.S).group(1)
try:
    import tomllib
except ImportError:
    import tomli as tomllib

cfg = tomllib.loads(block)
srv = cfg["mcp_client"]["servers"][0]
print("name:", srv["name"])
print("command exists:", os.path.isfile(srv["command"]), "->", srv["command"])
print("args:", srv["args"])
print("working_dir exists:", os.path.isdir(srv["working_dir"]))
print("env keys:", sorted(srv["env"]))
assert os.path.isfile(srv["command"]), "venv python missing"
assert os.path.isdir(srv["working_dir"])
assert srv["args"] == ["-m", "mcp_server.server"]
assert sorted(srv["env"]) == ["FACTORIO_HOST", "FACTORIO_PORT", "FACTORIO_RCON_PASSWORD"]
print("TOML SNIPPET VALID")
