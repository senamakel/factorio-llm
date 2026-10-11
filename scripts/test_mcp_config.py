"""Shared manifest integration must preserve the live server launch environment."""
import asyncio
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
