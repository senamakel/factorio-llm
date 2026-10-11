#!/usr/bin/env python3
"""Verify demo entity references after reloading a copy of the save, without stopping the live server."""
import json
from pathlib import Path
import signal
import socket
import subprocess
import time
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rcon_client.client import RconClient, RconError

def main():
    data = ROOT/'server/data'
    c = json.loads((data/'connection.json').read_text())
    demo = json.loads((data/'demo.json').read_text())
    verify = data/'reload-check'
    (verify/'saves').mkdir(parents=True,exist_ok=True)
    config = (data/'config.ini').read_text().replace(f'write-data={data}',f'write-data={verify}')
    (verify/'config.ini').write_text(config)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        rcon_port = sock.getsockname()[1]
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1',0))
        game_port = sock.getsockname()[1]
    with (verify/'server.log').open('a') as log:
        proc = subprocess.Popen([c['binary'],'--config',str(verify/'config.ini'),
            '--mod-directory',str(data/'mods'),'--start-server',str(data/'saves/llm-save.zip'),
            '--bind',f'127.0.0.1:{game_port}','--rcon-bind',f'127.0.0.1:{rcon_port}',
            '--rcon-password',c['password'],'--server-settings',str(data/'server-settings.json')],
            stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    try:
        deadline = time.monotonic()+30
        while time.monotonic()<deadline:
            if proc.poll() is not None:
                raise RuntimeError('Reload server exited; inspect server/data/reload-check/server.log')
            try:
                with RconClient(port=rcon_port,password=c['password']) as client:
                    status=json.loads(client.command('/c rcon.print(helpers.table_to_json(remote.call("control-bridge","status")))'))
                    assert status['bridge_version']=='0.2.0'
                    uid=demo['chest']['unit_number']
                    result=json.loads(client.command(f'/c rcon.print(helpers.table_to_json(remote.call("control-bridge","insert_items",{uid},"iron-plate",1,"nauvis")))'))
                    assert result['inserted']==1,result
                    pos=demo['chest']['position']
                    area=json.loads(client.command(f'/c rcon.print(helpers.table_to_json(remote.call("control-bridge","inspect_area",{pos["x"]},{pos["y"]},1,"nauvis","iron-chest",10)))'))
                    chest=next(e for e in area['entities'] if e['unit_number']==uid)
                    assert any(i['name']=='iron-plate' and i['count']==101 for i in chest['inventory']),chest
                    print('Reloaded save: existing chest ID resolved, insert and inventory read-back PASS')
                    return
            except (OSError,RconError,json.JSONDecodeError):
                time.sleep(0.25)
        raise RuntimeError('Reload verification timed out')
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=15)

if __name__=='__main__':
    main()
