"""Disposable, seeded Factorio headless servers for scored brain episodes.

An episode server never touches the live sandbox: it gets its own write-data
directory, a fresh map created from a fixed seed, a base-game-only mod list and
free loopback ports. The live install (binary and read-data) is located through
the primary checkout's ``server/data/connection.json`` and ``config.ini``.
"""
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import time

from rcon_client.client import RconClient, RconError
from scripts.world_settings import easy_map_settings

ROOT = Path(__file__).resolve().parents[1]
MOD_SOURCE = ROOT / 'mod'


def free_port(kind=socket.SOCK_STREAM):
    """Return a loopback port that is currently free for the given socket kind."""
    with socket.socket(socket.AF_INET, kind) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def install_paths(live_data):
    """Read the Factorio binary and read-data paths from a configured live sandbox.

    Raises RuntimeError when the sandbox has not been set up, because an episode
    cannot guess where Factorio is installed.
    """
    live_data = Path(live_data)
    connection = live_data / 'connection.json'
    config = live_data / 'config.ini'
    if not connection.exists() or not config.exists():
        raise RuntimeError(f'No configured Factorio sandbox at {live_data}; run ./factorio setup')
    binary = json.loads(connection.read_text())['binary']
    read_data = next((line.split('=', 1)[1].strip() for line in config.read_text().splitlines()
                      if line.replace(' ', '').startswith('read-data=')), None)
    if not read_data:
        raise RuntimeError(f'{config} has no read-data path')
    return binary, read_data


def prepare(workdir, seed, live_data):
    """Write config, mods, settings and a new seeded map into an empty episode directory.

    Returns the connection record (host, ports, password, binary). Map creation
    failures raise RuntimeError pointing at the episode's server log.
    """
    workdir = Path(workdir).resolve()
    binary, read_data = install_paths(live_data)
    (workdir / 'saves').mkdir(parents=True, exist_ok=True)
    mods = workdir / 'mods'
    mods.mkdir(exist_ok=True)
    link = mods / 'control-bridge_0.2.0'
    if not link.exists():
        link.symlink_to(MOD_SOURCE, target_is_directory=True)
    disabled = ('elevated-rails', 'quality', 'recycler', 'space-age')
    (mods / 'mod-list.json').write_text(json.dumps({'mods': [
        {'name': 'base', 'enabled': True}, {'name': 'control-bridge', 'enabled': True},
        *({'name': name, 'enabled': False} for name in disabled)]}, indent=2))
    (workdir / 'config.ini').write_text(f'[path]\nread-data={read_data}\nwrite-data={workdir}\n')
    (workdir / 'server-settings.json').write_text(json.dumps({
        'name': f'episode seed {seed}', 'description': 'disposable brain episode', 'visibility': {'public': False, 'lan': False},
        'require_user_verification': False, 'allow_commands': 'true', 'auto_pause': False,
        'autosave_interval': 0, 'max_players': 2}, indent=2))
    (workdir / 'map-gen-settings.json').write_text(json.dumps({**easy_map_settings(), 'seed': seed}, indent=2))
    connection = {'host': '127.0.0.1', 'port': free_port(), 'game_port': free_port(socket.SOCK_DGRAM),
                  'password': secrets.token_urlsafe(24), 'binary': binary}
    fd = os.open(workdir / 'connection.json', os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(connection, handle, indent=2)
    with (workdir / 'server.log').open('a') as log:
        created = subprocess.run(base_command(connection, workdir) + [
            '--create', str(workdir / 'saves/episode.zip'),
            '--map-gen-settings', str(workdir / 'map-gen-settings.json')], stdout=log, stderr=log)
    if created.returncode:
        raise RuntimeError(f'Episode map creation failed; see {workdir / "server.log"}')
    return connection


def base_command(connection, workdir):
    """Return the binary invocation with this episode's config and mod directory."""
    return [connection['binary'], '--config', str(Path(workdir) / 'config.ini'),
            '--mod-directory', str(Path(workdir) / 'mods')]


class EpisodeServer:
    """Context manager that runs one disposable headless server and always stops it.

    ``rcon(command)`` sends a raw console command over a persistent connection.
    The process is interrupted (SIGINT, then SIGKILL) on exit, even after errors.
    """

    def __init__(self, workdir, seed, live_data, ready_timeout=90):
        self.workdir, self.seed, self.live_data = Path(workdir).resolve(), seed, live_data
        self.ready_timeout = ready_timeout
        self.proc = self.client = self.connection = None

    def __enter__(self):
        self.connection = prepare(self.workdir, self.seed, self.live_data)
        c = self.connection
        log = (self.workdir / 'server.log').open('a')
        self.proc = subprocess.Popen(base_command(c, self.workdir) + [
            '--start-server', str(self.workdir / 'saves/episode.zip'),
            '--bind', f"127.0.0.1:{c['game_port']}", '--rcon-bind', f"127.0.0.1:{c['port']}",
            '--rcon-password', c['password'], '--server-settings', str(self.workdir / 'server-settings.json')],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        log.close()
        deadline = time.monotonic() + self.ready_timeout
        try:
            while time.monotonic() < deadline:
                if self.proc.poll() is not None:
                    raise RuntimeError(f'Episode server exited; see {self.workdir / "server.log"}')
                try:
                    if self.rcon('/c rcon.print(game.tick)').strip().isdigit():
                        return self
                except (OSError, RconError):
                    self.close_client()
                time.sleep(.5)
            raise RuntimeError(f'Episode server not ready in {self.ready_timeout}s')
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def rcon(self, command):
        """Send one console command, reconnecting once if the connection dropped."""
        for attempt in (0, 1):
            try:
                if self.client is None:
                    c = self.connection
                    self.client = RconClient(c['host'], c['port'], c['password'], timeout=10)
                    self.client.connect()
                return self.client.command(command)
            except (OSError, RconError):
                self.close_client()
                if attempt:
                    raise

    def lua(self, body):
        """Run a Lua body returning a table and decode its JSON reply."""
        raw = self.rcon('/c local ok,v=pcall(function() ' + body + ' end); '
                        'rcon.print(helpers.table_to_json({ok=ok,value=ok and v or nil,error=not ok and tostring(v) or nil}))')
        reply = json.loads(raw)
        if not reply['ok']:
            raise RuntimeError(reply['error'])
        return reply.get('value')

    def close_client(self):
        """Drop the RCON connection without raising."""
        if self.client is not None:
            try:
                self.client.close()
            except (OSError, RconError):
                pass
        self.client = None

    def __exit__(self, *exc):
        self.close_client()
        if self.proc and self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGINT)
            try:
                self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=10)
        return False
