"""Validate README TOML and all generated MCP client configs without printing secrets."""
import json
from pathlib import Path
import re
import subprocess
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

root = Path(__file__).resolve().parents[1]
readme = (root/'README.md').read_text()
block = re.search(r'```toml\n(.*?)```',readme,re.S).group(1)
example = tomllib.loads(block)['mcp_client']['servers'][0]
assert example['name']=='factorio-control'
assert example['args'][0].endswith('/scripts/mcp_entrypoint.py')
for format_name in ('openhuman','codex','json'):
    raw = subprocess.check_output([sys.executable,str(root/'scripts/factorio.py'),'mcp-config','--format',format_name],text=True)
    if format_name=='json':
        srv=json.loads(raw)['mcpServers']['factorio-control']
    elif format_name=='codex':
        srv=tomllib.loads(raw)['mcp_servers']['factorio-control']
    else:
        srv=tomllib.loads(raw)['mcp_client']['servers'][0]
        assert Path(srv['working_dir'])==root
    assert Path(srv['command']).is_file(), 'venv Python missing'
    assert srv['args']==[str(root/'scripts/mcp_entrypoint.py')]
    assert Path(srv['args'][0]).is_file()
    assert 'password' not in raw.lower()
print('README TOML and generated OpenHuman/Codex/JSON MCP configs: PASS')
