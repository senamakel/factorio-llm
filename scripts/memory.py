#!/usr/bin/env python3
"""Shared hive memory in a dedicated CortexDB: start it, remember, recall and list.

Usage (through ``./factorio memory``)::

    up                                  start CortexDB (docker compose), create the key once
    down                                stop it (data is kept)
    remember KIND TEXT [--tag T ...]    append one memory; KIND is lesson|failure|idea|result|goal
    recall QUERY [--kind KIND] [--limit N]
    list [--kind KIND] [--limit N]      newest first

Everything lives under the scope prefix ``app:factorio/kind:<KIND>``. The key and
URL are stored in the primary checkout's ignored ``server/data/memory.json``, so
every worktree (including tinyrsi candidates) shares one memory. Output is JSON;
failures print ``{"error": ...}`` to stderr and exit 1. Enrichment and
embeddings call OpenRouter with ``OPENROUTER_API_KEY`` (one cheap model), so
keep writes short and few.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.episode import default_live_data  # noqa: E402

KINDS = ('lesson', 'failure', 'idea', 'result', 'goal')
PREFIX = 'app:factorio'
COMPOSE = ROOT / 'memory/docker-compose.yml'


def config_path():
    """Return the shared private memory config path in the primary checkout's data dir."""
    return Path(default_live_data()) / 'memory.json'


def load_config():
    """Read ``{url, key}``; raise RuntimeError when memory was never started."""
    path = config_path()
    if not path.exists():
        raise RuntimeError('hive memory is not set up; run ./factorio memory up')
    return json.loads(path.read_text())


def scope(kind):
    """Scope path for one kind of memory."""
    if kind not in KINDS:
        raise ValueError(f'kind must be one of {KINDS}')
    return f'{PREFIX}/kind:{kind}'


def request(method, path, body=None, timeout=60):
    """Call the CortexDB v1 API with the operator key and decode JSON."""
    cfg = load_config()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(cfg['url'] + path, data=data, method=method,
                                 headers={'Authorization': f"Bearer {cfg['key']}", 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'CortexDB {method} {path} -> {exc.code}: {exc.read()[:300]!r}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f'CortexDB unreachable ({exc.reason}); run ./factorio memory up') from exc
    return json.loads(raw) if raw else {}


def up(port=3142):
    """Start the compose project, generating the operator key once; wait until ready."""
    path = config_path()
    cfg = json.loads(path.read_text()) if path.exists() else {
        'url': f'http://127.0.0.1:{port}', 'key': 'ctx_local_' + secrets.token_hex(24)}
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(cfg, handle, indent=2)
    data = Path(default_live_data()) / 'cortexdb'
    data.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'CORTEX_API_KEY': cfg['key'], 'FACTORIO_MEMORY_DATA': str(data),
           'FACTORIO_MEMORY_PORT': cfg['url'].rsplit(':', 1)[1]}
    subprocess.run(['docker', 'compose', '-f', str(COMPOSE), 'up', '-d', '--wait'], env=env, check=True)
    return {'url': cfg['url'], 'ready': request('GET', '/v1/admin/ready')}


def down():
    """Stop the compose project; the data directory is kept."""
    subprocess.run(['docker', 'compose', '-f', str(COMPOSE), 'down'],
                   env={**os.environ, 'CORTEX_API_KEY': 'unused', 'FACTORIO_MEMORY_DATA': '/tmp'}, check=True)
    return {'stopped': True}


def remember(kind, text, tags=()):
    """Append one memory event; returns its ``event_id``."""
    text = text.strip()
    if not text or len(text) > 4000:
        raise ValueError('memory text must be 1..4000 characters')
    body = {'scope': scope(kind), 'modality': 'observation',
            'idempotency_key': f'rf-{time.time_ns()}-{secrets.token_hex(4)}',
            'content': {'kind': 'message', 'role': 'user', 'text': text},
            'context': {'labels': [f'kind:{kind}', *(f'tag:{t}' for t in tags)],
                        'observed_at': time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime())}}
    return request('POST', '/v1/experience?wait=indexed', body)


def _texts(items, limit):
    """Deduplicate events (the engine returns copies) into ``[{text, labels, at}]``."""
    seen, out = set(), []
    for item in items or []:
        text = (item.get('content') or {}).get('text') or item.get('text')
        if not text or text in seen:
            continue
        seen.add(text)
        context = item.get('context') or {}
        out.append({'text': text, 'labels': context.get('labels', []), 'at': context.get('observed_at')})
        if len(out) >= limit:
            break
    return out


def recall(query, kind=None, limit=8):
    """Return the memories most relevant to ``query`` (one kind, or all kinds)."""
    kinds = [kind] if kind else list(KINDS)
    found = []
    for k in kinds:
        try:
            pack = request('POST', '/v1/recall', {'scope': scope(k), 'query': query,
                                                  'budgets': {'per_layer_limits': {'events': limit * 2}}})
        except RuntimeError as exc:
            if '404' in str(exc):
                continue
            raise
        found += [{**m, 'kind': k} for m in _texts((pack.get('layers') or {}).get('events'), limit)]
    return found[:limit * len(kinds)] if kind is None else found[:limit]


def listing(kind=None, limit=20):
    """List the newest memories of one kind, or of every kind."""
    out = []
    for k in [kind] if kind else KINDS:
        try:
            page = request('GET', f'/v1/events?scope={scope(k)}&limit={min(200, limit * 2)}')
        except RuntimeError as exc:
            if '404' in str(exc):
                continue
            raise
        out += [{**m, 'kind': k} for m in _texts(page.get('items'), limit)]
    return out


def main(argv=None):
    """Parse the subcommand, print JSON, return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('up').add_argument('--port', type=int, default=3142)
    sub.add_parser('down')
    p = sub.add_parser('remember')
    p.add_argument('kind', choices=KINDS)
    p.add_argument('text')
    p.add_argument('--tag', action='append', default=[])
    p = sub.add_parser('recall')
    p.add_argument('query')
    p.add_argument('--kind', choices=KINDS)
    p.add_argument('--limit', type=int, default=8)
    p = sub.add_parser('list')
    p.add_argument('--kind', choices=KINDS)
    p.add_argument('--limit', type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.command == 'up':
            result = up(args.port)
        elif args.command == 'down':
            result = down()
        elif args.command == 'remember':
            result = remember(args.kind, args.text, args.tag)
        elif args.command == 'recall':
            result = recall(args.query, args.kind, args.limit)
        else:
            result = listing(args.kind, args.limit)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
