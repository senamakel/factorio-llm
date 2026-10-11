"""Enrich bootstrap rules with attributed infobox facts fetched through the wiki MCP."""
import asyncio
import json
import os
from pathlib import Path
import re
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.mcp_config import load_servers

TITLES = ['Steam power (research)', 'Electronics (research)',
          'Automation science pack (research)', 'Automation (research)',
          'Automation science pack', 'Lab', 'Boiler', 'Steam engine',
          'Offshore pump', 'Small electric pole']


async def enrich():
    """Fetch wiki infoboxes over MCP and store compact facts with source revisions."""
    config = load_servers(ROOT)['factorio-wiki']
    entries = []
    async with stdio_client(StdioServerParameters(command=config['command'], args=config['args'],
                            env={**os.environ, **config['env']})) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for title in TITLES:
                result = await asyncio.wait_for(session.call_tool('get-page', {'title':'Infobox:' + title, 'metadata':True}),20)
                if result.isError:
                    raise RuntimeError('Wiki MCP failed for ' + title)
                text = '\n'.join(c.text for c in result.content if c.type == 'text')
                fields = dict(re.findall(r'^\|\s*([\w-]+)\s*=\s*(.*)$', text, re.M))
                entries.append({'title':title,
                                'url':re.search(r'^URL: (.+)$', text, re.M).group(1),
                                'revision':int(re.search(r'Latest revision ID: (\d+)', text).group(1)),
                                'facts':{k:v for k,v in fields.items() if k in (
                                    'technology-trigger','recipe','total-raw','cost','cost-multiplier',
                                    'energy','power-output','required-technologies')}})
    path = ROOT/'brain/knowledge/red_science.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({'source':'Factorio Wiki via factorio-wiki MCP',
                               'runtime_rule':'Live recipes and technology state override wiki assumptions.',
                               'entries':entries}, indent=2) + '\n')
    print(f'Enriched {len(entries)} entries: {path}')


if __name__ == '__main__':
    asyncio.run(asyncio.wait_for(enrich(),180))
