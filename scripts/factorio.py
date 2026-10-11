#!/usr/bin/env python3
"""Set up and manage a local Factorio 2.1 sandbox; secrets stay in ignored data."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rcon_client.client import RconClient, RconError
from scripts.mcp_config import print_config, register_servers
from scripts.world_settings import easy_map_settings

DATA = ROOT / 'server/data'
STEAM = Path.home() / 'Library/Application Support/Steam/steamapps/common/Factorio/factorio.app/Contents'


def write_private(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
    path.chmod(0o600)


def connection():
    p = DATA / 'connection.json'
    if not p.exists():
        raise RuntimeError('Run setup first')
    return json.loads(p.read_text())


def install_client_mod(client_mods=None):
    """Install the bridge without changing the user's enabled mod list."""
    mods = Path(client_mods or Path.home()/"Library/Application Support/factorio/mods")
    mods.mkdir(parents=True, exist_ok=True)
    link = mods/"control-bridge_0.2.0"
    if not link.exists() and not link.is_symlink():
        link.symlink_to(ROOT/"mod", target_is_directory=True)
    if link.resolve() != (ROOT/"mod").resolve():
        raise RuntimeError("Client has a different control-bridge_0.2.0; preserve it and resolve the conflict first")


def setup(binary=None, read_data=None, port=27015, game_port=34197):
    binary = Path(binary or os.environ.get('FACTORIO_BINARY') or shutil.which('factorio') or STEAM / 'MacOS/factorio').resolve()
    if not binary.is_file():
        raise RuntimeError('Factorio not found. Pass --binary /path/to/factorio')
    read_data = Path(read_data or os.environ.get('FACTORIO_READ_DATA') or
                     (STEAM / 'data' if binary.parent.name == 'MacOS' else binary.parent.parent.parent / 'data')).resolve()
    if not (read_data / 'base').is_dir():
        raise RuntimeError('Factorio data not found. Pass --read-data /path/to/data')
    version = subprocess.check_output([str(binary), '--version'], text=True)
    if 'Version: 2.1.' not in version:
        raise RuntimeError('This control-bridge mod requires Factorio 2.1.x')
    (DATA / 'saves').mkdir(parents=True, exist_ok=True)
    mods = DATA / 'mods'
    mods.mkdir(exist_ok=True)
    link = mods / 'control-bridge_0.2.0'
    if not link.exists() and not link.is_symlink():
        link.symlink_to(ROOT / 'mod', target_is_directory=True)
    if link.resolve() != (ROOT / 'mod').resolve():
        raise RuntimeError('Existing mod directory points elsewhere')
    mod_list = mods / 'mod-list.json'
    enabled = json.loads(mod_list.read_text()) if mod_list.exists() else {'mods':[]}
    for name in ('base','control-bridge'):
        entry = next((m for m in enabled['mods'] if m['name']==name),None)
        if entry is None:
            enabled['mods'].append({'name':name,'enabled':True})
        else:
            entry['enabled']=True
    write_private(mod_list, enabled)
    (DATA / 'config.ini').write_text(f'[path]\nread-data={read_data}\nwrite-data={DATA}\n')
    write_private(DATA / 'server-settings.json', {
        'name':'LLM Factorio sandbox', 'description':'Local MCP-controlled sandbox',
        'visibility':{'public':False,'lan':False}, 'require_user_verification':False,
        'allow_commands':'true', 'auto_pause':False, 'autosave_interval':5,
        'autosave_slots':3, 'max_players':4,
    })
    password = connection()['password'] if (DATA / 'connection.json').exists() else secrets.token_urlsafe(32)
    write_private(DATA / 'connection.json', {'host':'127.0.0.1','port':port,'password':password,
        'binary':str(binary),'game_port':game_port})
    if binary.parent.name == 'MacOS':
        install_client_mod()
    print(f'Setup ready: {DATA}; game 127.0.0.1:{game_port}, RCON 127.0.0.1:{port}')


def base_command(c):
    return [c['binary'], '--config', str(DATA / 'config.ini'), '--mod-directory', str(DATA / 'mods')]


def owned_pid():
    p = DATA / 'server.pid'
    if not p.exists():
        return None
    pid = int(p.read_text())
    result = subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    if result.returncode == 0 and str(DATA / 'config.ini') in result.stdout:
        return pid
    return None


def command(c, cmd):
    with RconClient(c['host'], c['port'], c['password']) as rcon:
        return rcon.command(cmd)


def start():
    c = connection()
    if owned_pid():
        print('Server already running')
        return
    for port, kind in ((c['port'],socket.SOCK_STREAM),(c['game_port'],socket.SOCK_DGRAM)):
        with socket.socket(socket.AF_INET,kind) as sock:
            if kind == socket.SOCK_STREAM:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('127.0.0.1',port))
            except OSError as exc:
                raise RuntimeError(f'Port {port} is occupied; no existing server was stopped') from exc
    log_path = DATA / 'server.log'
    if not list((DATA / 'saves').glob('*.zip')):
        write_private(DATA / 'map-gen-settings.json', easy_map_settings())
        with log_path.open('a') as log:
            result = subprocess.run(base_command(c) + ['--create',str(DATA / 'saves/sandbox.zip'),
                '--map-gen-settings',str(DATA / 'map-gen-settings.json')],stdout=log,stderr=log)
        if result.returncode:
            raise RuntimeError(f'Map creation failed; see {log_path}')
    with log_path.open('a') as log:
        proc = subprocess.Popen(base_command(c) + ['--start-server-load-latest',
            '--bind',f"127.0.0.1:{c['game_port']}", '--rcon-bind',f"127.0.0.1:{c['port']}",
            '--rcon-password',c['password'], '--server-settings',str(DATA / 'server-settings.json')],
            stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
    (DATA / 'server.pid').write_text(str(proc.pid))
    deadline = time.monotonic()+60
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f'Server exited; see {log_path}')
        try:
            response = command(c, '/c rcon.print(helpers.table_to_json(remote.call("control-bridge","status")))')
            status = json.loads(response)
            if status.get('bridge_version') == '0.2.0':
                print(f"Server ready (PID {proc.pid}); join 127.0.0.1:{c['game_port']}")
                return
        except (OSError,ValueError,RconError):
            pass
        time.sleep(0.5)
    os.kill(proc.pid,signal.SIGINT)
    raise RuntimeError(f'Server not ready within 60 seconds; see {log_path}')


def stop():
    pid = owned_pid()
    if not pid:
        print('No managed server running')
        return
    c = connection()
    command(c, '/server-save llm-save')
    os.kill(pid,signal.SIGINT)
    deadline = time.monotonic()+30
    while time.monotonic() < deadline:
        if not owned_pid():
            (DATA / 'server.pid').unlink(missing_ok=True)
            print('Server saved and stopped')
            return
        time.sleep(0.25)
    raise RuntimeError('Server is still shutting down; inspect server/data/server.log')


def mcp_config(format_name):
    """Print every server from mcp.json in the requested client format."""
    print_config(ROOT, format_name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['setup','start','stop','status','join','register','mcp-config','client-mod'])
    parser.add_argument('--binary')
    parser.add_argument('--read-data')
    parser.add_argument('--port',type=int,default=27015)
    parser.add_argument('--game-port',type=int,default=34197)
    parser.add_argument('--format',choices=['openhuman','codex','json'],default='openhuman')
    parser.add_argument('--client-mods',help='Client mods directory for client-mod')
    args = parser.parse_args()
    try:
        if args.action == 'setup':
            setup(args.binary,args.read_data,args.port,args.game_port)
        elif args.action == 'start':
            start()
        elif args.action == 'stop':
            stop()
        elif args.action == 'status':
            print(command(connection(),'/c rcon.print(helpers.table_to_json(remote.call("control-bridge","status")))'))
        elif args.action == 'register':
            return register_servers(ROOT)
        elif args.action == 'mcp-config':
            mcp_config(args.format)
        elif args.action == 'client-mod':
            install_client_mod(args.client_mods)
            print('Client mod installed. Restart the client, connect, and accept mod sync.')
        else:
            c = connection()
            # The desktop client uses its normal user data, separate from the server.
            subprocess.Popen([c['binary'],'--mod-directory',str(DATA/'mods'),'--mp-connect',f"127.0.0.1:{c['game_port']}"], stdin=subprocess.DEVNULL, stdout=(DATA/'client.log').open('a'), stderr=subprocess.STDOUT, start_new_session=True)
    except (OSError,ValueError,RuntimeError,RconError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
