"""Setup generates checkout-relative paths and protects connection credentials."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import factorio

class SetupTest(unittest.TestCase):
    def test_setup_uses_current_checkout_and_keeps_password_on_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "mod").mkdir()
            binary = root / 'factorio'; binary.touch()
            read = root / 'data'; (read / 'base').mkdir(parents=True)
            with patch.object(factorio,'ROOT',root), patch.object(factorio,'DATA',root/'server/data'), patch.object(factorio.subprocess,'check_output',return_value='Version: 2.1.21'):
                factorio.setup(binary,read)
                config = root/'server/data/connection.json'
                pw = json.loads(config.read_text())['password']
                factorio.setup(binary,read)
                self.assertEqual(json.loads(config.read_text())['password'],pw)
                self.assertEqual(config.stat().st_mode & 0o777,0o600)
                ini = (root/'server/data/config.ini').read_text()
                self.assertIn(f'write-data={root}/server/data',ini)
                self.assertNotIn('OpenHuman/projects',ini)

if __name__ == '__main__':
    unittest.main()
