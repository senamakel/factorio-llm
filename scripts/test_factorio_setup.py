"""Setup generates checkout-relative paths and protects connection credentials."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import factorio
from scripts.world_settings import easy_map_settings, RESOURCES

class SetupTest(unittest.TestCase):
    def test_easy_world_disables_enemies_and_has_large_rich_resources(self):
        settings=easy_map_settings()
        self.assertTrue(settings['no_enemies_mode'])
        self.assertTrue(settings['peaceful_mode'])
        self.assertEqual(settings['autoplace_controls']['enemy-base']['size'],0)
        for name in RESOURCES:
            self.assertEqual(settings['autoplace_controls'][name]['size'],6)
            self.assertEqual(settings['autoplace_controls'][name]['richness'],6)
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
