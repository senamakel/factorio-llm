"""Shared manifest integration must preserve the live server launch environment."""
import asyncio
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from scripts.mcp_config import load_servers
from scripts import smoke_mcp


class ManifestTest(unittest.TestCase):
    def test_smoke_launches_control_with_manifest_environment(self):
        with patch.object(smoke_mcp, 'stdio_client', side_effect=RuntimeError('captured')) as launch:
            with self.assertRaisesRegex(RuntimeError, 'captured'):
                asyncio.run(smoke_mcp.smoke(False))
        expected = load_servers(smoke_mcp.ROOT)['factorio-control']
        params = launch.call_args.args[0]
        self.assertEqual(params.command, expected['command'])
        self.assertEqual(params.args, expected['args'])
        self.assertEqual(params.env, expected['env'])


class WorktreeVenvTest(unittest.TestCase):
    def test_worktree_without_venv_uses_the_primary_checkouts_interpreter(self):
        with tempfile.TemporaryDirectory() as tmp:
            primary = Path(tmp) / 'primary'
            primary.mkdir()
            subprocess.run(['git', 'init', '-q', str(primary)], check=True)
            (primary / 'mcp.json').write_text(json.dumps({'mcpServers': {'factorio-control': {
                'command': './.venv/bin/python', 'args': ['./scripts/mcp_entrypoint.py']}}}))
            subprocess.run(['git', '-C', str(primary), 'add', 'mcp.json'], check=True)
            subprocess.run(['git', '-C', str(primary), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'x'],
                           check=True)
            interpreter = primary / '.venv/bin/python'
            interpreter.parent.mkdir(parents=True)
            interpreter.write_text('')
            worktree = Path(tmp) / 'wt'
            subprocess.run(['git', '-C', str(primary), 'worktree', 'add', '-q', str(worktree)], check=True)
            command = load_servers(worktree)['factorio-control']['command']
        self.assertEqual(Path(command).resolve(), interpreter.resolve())
