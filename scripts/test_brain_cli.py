"""Read-only agent commands expose JSON contracts and ownership prevents conflicting runs."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from brain.cli import main
from actuator.controller import ownership


class BrainCliTest(unittest.TestCase):
    def test_action_catalog_is_machine_readable(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):main(['actions'])
        catalog=json.loads(output.getvalue())
        self.assertIn('first_research',catalog)
        self.assertIn('count',catalog['mine_iron_ore']['signature'])

    def test_state_can_be_streamed_as_json(self):
        state={'schema_version':1,'tick':42,'players':[]}
        with patch('brain.observation.observe',return_value=state),contextlib.redirect_stdout(io.StringIO()) as out:
            main(['stream','--actor','14','--count','2','--interval','.1'])
        self.assertEqual([json.loads(line)['tick'] for line in out.getvalue().splitlines()],[42,42])

    def test_invalid_stream_limits_return_an_error(self):
        with patch('brain.observation.observe'),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):main(['stream','--actor','14','--count','0'])

    def test_actor_ownership_rejects_a_second_controller(self):
        with tempfile.TemporaryDirectory() as tmp,patch('actuator.controller.DATA',Path(tmp)):
            with ownership(14,'research'):
                with self.assertRaisesRegex(RuntimeError,'another controller'):
                    with ownership(14,'research'):pass
