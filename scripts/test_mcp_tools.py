"""Offline checks for Lua encoding, structured failures and bounded queries."""
import json
import unittest
from unittest.mock import patch
from mcp_server import server

class ToolsTest(unittest.TestCase):
    def test_rpc_strings_cannot_escape_lua_literal(self):
        value = 'quote" slash\\ newline\n雪'
        with patch.object(server, 'run', return_value='{"ok":true}') as run:
            server.bridge('print_all', value)
        command = run.call_args.args[0]
        self.assertIn('helpers.json_to_table', command)
        self.assertNotIn('\n', command)
        import re
        literal = command.split('helpers.json_to_table(\"', 1)[1].split('\")', 1)[0]
        decoded = bytes(int(n) for n in re.findall(r'\\([0-9]{3})', literal)).decode('utf-8')
        self.assertEqual(json.loads(decoded), [value])

    def test_lua_errors_are_tool_failures(self):
        with patch.object(server, 'run', return_value='{"error":"unknown entity"}'):
            with self.assertRaisesRegex(ValueError, 'unknown entity'):
                server.bridge('place_entity')

    def test_non_json_response_is_not_reported_as_success(self):
        with patch.object(server, 'run', return_value='Error: missing control-bridge'):
            with self.assertRaisesRegex(ValueError, 'control-bridge'):
                server.bridge('status')

    def test_entity_query_bounds_before_rcon(self):
        with patch.object(server, 'run') as run:
            with self.assertRaises(ValueError):
                server.inspect_area(0, 0, radius=10000)
            run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
