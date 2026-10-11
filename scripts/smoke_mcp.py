#!/usr/bin/env python3
"""Verify live stdio MCP. --edits tests changes on a temporary surface, then removes it."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
import time
import uuid

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mcp_config import load_servers

ROOT = Path(__file__).resolve().parents[1]

async def smoke(edits):
    server = load_servers(ROOT)['factorio-control']
    params = StdioServerParameters(command=server['command'],args=server['args'],env=server['env'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            listing = await session.list_tools()
            names = {t.name for t in listing.tools}
            required = {'get_status','inspect_area','place_entity','remove_entity','insert_items','set_recipe',
                        'give_item','teleport','print_all','save_game','rcon_command'}
            assert required <= names, f'Missing tools: {required-names}'
            async def call(tool_name, **args):
                response = await session.call_tool(tool_name,args)
                assert not response.isError, f'{tool_name}: {response.content}'
                text = '\n'.join(c.text for c in response.content if c.type=='text')
                return text if tool_name == 'rcon_command' else json.loads(text)
            status = await call('get_status')
            assert status['bridge_version'] == '0.2.0', status
            assert await call('rcon_command',command='/c rcon.print("mcp round trip ok")') == 'mcp round trip ok\n'
            print(f'MCP handshake and {len(names)} tool schemas: PASS; tick={status["tick"]}')
            if not edits:
                return
            surface = 'mcp-smoke-'+uuid.uuid4().hex[:12]
            await call('rcon_command',command='/c local s=game.create_surface("'+surface+'", {width=64,height=64,water=0}); s.request_to_generate_chunks({0,0},1); s.force_generate_chunk_requests(); for _,e in pairs(s.find_entities()) do e.destroy() end; local t={}; for x=-10,10 do for y=-10,10 do t[#t+1]={name="grass-1",position={x,y}} end end; s.set_tiles(t); rcon.print("created")')
            try:
                chest = await call('place_entity',name='iron-chest',x=0.5,y=0.5,surface=surface)
                inserted = await call('insert_items',unit_number=chest['unit_number'],item='iron-plate',count=37,surface=surface)
                assert inserted['inserted']==37, inserted
                area = await call('inspect_area',x=0,y=0,radius=4,surface=surface,name='iron-chest')
                found = area['entities'][0]
                assert found['unit_number']==chest['unit_number'], area
                assert any(i['name']=='iron-plate' and i['count']==37 for i in found['inventory']), found
                failed = await session.call_tool('place_entity',{'name':'iron-chest','x':0.5,'y':0.5,'surface':surface})
                assert failed.isError, 'Occupied placement was reported as success'
                machine = await call('place_entity',name='assembling-machine-1',x=5,y=5,surface=surface)
                recipe = await call('set_recipe',unit_number=machine['unit_number'],recipe='iron-gear-wheel',surface=surface)
                assert recipe['recipe']=='iron-gear-wheel', recipe
                await call('remove_entity',unit_number=chest['unit_number'],surface=surface)
                empty = await call('inspect_area',x=0,y=0,radius=2,surface=surface,name='iron-chest')
                assert not empty['entities'], empty
                await call('print_all',message='MCP verified: build, inventory, recipe, inspect, remove. "Unicode: 雪"')
                print('Live placement, collision failure, inventory read-back, recipe and removal: PASS')
            finally:
                await call('rcon_command',command='/c game.delete_surface("'+surface+'"); rcon.print("removed test surface")')
            requested_at = time.time()
            saved = await call('save_game',name='mcp-verified')
            assert saved['save_requested']=='mcp-verified', saved
            save = ROOT/'server/data/saves/mcp-verified.zip'
            for _ in range(100):
                if save.exists() and save.stat().st_size > 0 and save.stat().st_mtime >= requested_at:
                    import zipfile
                    try:
                        with zipfile.ZipFile(save) as z:
                            assert z.testzip() is None
                        print('Save completed and ZIP verified: PASS')
                        break
                    except zipfile.BadZipFile:
                        pass
                await asyncio.sleep(0.1)
            else:
                raise AssertionError('Requested save did not finish')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edits',action='store_true')
    args = parser.parse_args()
    asyncio.run(asyncio.wait_for(smoke(args.edits),timeout=60))
