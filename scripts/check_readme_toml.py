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
        servers=json.loads(raw)['mcpServers']
    elif format_name=='codex':
        servers=tomllib.loads(raw)['mcp_servers']
    else:
        servers={s['name']:s for s in tomllib.loads(raw)['mcp_client']['servers']}
    assert set(servers)==set(json.loads((root/'mcp.json').read_text())['mcpServers'])
    srv=servers['factorio-control']
    if format_name=='openhuman':
        assert Path(srv['working_dir'])==root
    wiki=servers['factorio-wiki']
    assert wiki['command']=='npx'
    assert wiki['env']['CONFIG']==str(root/'mediawiki.json')
    assert wiki['env']['MCP_TRANSPORT']=='stdio'
    assert Path(srv['command']).is_file(), 'venv Python missing'
    assert srv['args']==[str(root/'scripts/mcp_entrypoint.py')]
    assert Path(srv['args'][0]).is_file()
    assert 'password' not in raw.lower()
print('README TOML and generated OpenHuman/Codex/JSON MCP configs: PASS')
