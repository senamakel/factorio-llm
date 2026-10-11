"""Offline checks for the frozen episode harness: ladder, score, failures, staging and honesty."""
import json
from pathlib import Path
import tempfile
import unittest

from harness import honesty, milestones as ladder
from harness.episode import failures, stage, tinyrsi_result

NOTHING = {'researched': [], 'entity_counts': {}, 'assembler_products': 0}


class LadderTest(unittest.TestCase):
    def test_empty_world_reaches_nothing_and_scores_zero(self):
        reached = ladder.reached(NOTHING, {})
        self.assertFalse(any(reached.values()))
        self.assertEqual(ladder.score({}, reached), 0)
        self.assertEqual(ladder.next_goal(reached)[0], 'G1')

    def test_rates_are_capped_and_milestones_add_five_each(self):
        world = {'researched': ['automation', 'logistic-science-pack', 'automation-2'],
                 'entity_counts': {'electric-mining-drill': 4}, 'assembler_products': 50}
        rates = {ladder.RED: 150, ladder.GREEN: 120, 'iron-ore': 300, 'iron-plate': 200}
        reached = ladder.reached(world, rates)
        self.assertTrue(all(reached.values()))
        self.assertEqual(ladder.score(rates, reached), 100 + 100 + 5 * len(ladder.LADDER))
        self.assertIsNone(ladder.next_goal(reached))

    def test_handcraft_free_red_production_is_needed_for_g3(self):
        world = {**NOTHING, 'researched': ['automation'], 'assembler_products': 3}
        reached = ladder.reached(world, {ladder.RED: 0})
        self.assertTrue(reached['G1'] and reached['G2'])
        self.assertFalse(reached['G3'])

    def test_window_rates_per_minute_never_negative(self):
        rates = ladder.window_rates({'a': 10, 'b': 5}, {'a': 40, 'b': 5}, 2)
        self.assertEqual(rates, {'a': 15, 'b': 0})
        with self.assertRaises(ValueError):
            ladder.window_rates({}, {}, 0)


class FailureSummaryTest(unittest.TestCase):
    def test_errors_ok_false_and_stop_reason_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, err = Path(tmp) / 'o.jsonl', Path(tmp) / 'e.txt'
            rows = [{'phase': 'build_x', 'result': {'ok': False, 'error': 'site occupied'}}] * 2 + [
                {'phase': 'start_research', 'result': {'ok': False}}, {'phase': 'mine', 'result': {'ok': True}},
                {'stop_reason': 'TimeoutError: stopped after 3 consecutive action failures'}]
            out.write_text('\n'.join(json.dumps(r) for r in rows) + '\nnot json\n')
            err.write_text('Traceback...\nValueError: boom\n')
            lines = failures(out, err)
        self.assertIn('2x build_x: site occupied', lines)
        self.assertIn('1x start_research: returned ok=false', lines)
        self.assertTrue(any(line.startswith('stop reason: TimeoutError') for line in lines))
        self.assertTrue(any('ValueError: boom' in line for line in lines))


class ResultShapeTest(unittest.TestCase):
    def test_tinyrsi_result_has_numeric_metrics_and_status_first(self):
        detail = {'score': 15.0, 'red_spm': 2.5, 'green_spm': 0, 'milestones': 2, 'reached': ['G1', 'G2'],
                  'next_goal': ('G3', 'Red packs produced by machines'), 'rates_per_min': {ladder.RED: 2.5},
                  'game_minutes_played': 30.0, 'researched': ['automation'], 'entity_counts': {'lab': 1},
                  'seed': 2, 'failures': ['3x build_pipe: site occupied']}
        result = tinyrsi_result(detail)
        self.assertEqual(result['score'], 15.0)
        for name, value in result['metrics'].items():
            self.assertIsInstance(value, (int, float), name)
        self.assertEqual(result['failures'][0]['type'], 'status')
        self.assertIn("next goal ('G3'", result['failures'][0]['text'])
        self.assertEqual(result['failures'][1], {'id': 'seed2-0', 'type': 'episode', 'text': '3x build_pipe: site occupied'})


class StageTest(unittest.TestCase):
    def test_candidate_brain_runs_beside_this_checkouts_frozen_actuator(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / 'candidate'
            (candidate / 'brain').mkdir(parents=True)
            (candidate / 'brain/__init__.py').write_text('MARK = "candidate"\n')
            (candidate / 'actuator').mkdir()
            (candidate / 'actuator/__init__.py').write_text('TAMPERED = True\n')
            repo = stage(candidate, Path(tmp) / 'episode')
            self.assertEqual((repo / 'brain/__init__.py').read_text(), 'MARK = "candidate"\n')
            self.assertNotIn('TAMPERED', (repo / 'actuator/__init__.py').read_text())
            self.assertTrue((repo / 'rcon_client/client.py').exists())


class HonestyTest(unittest.TestCase):
    def test_bypass_routes_are_rejected(self):
        bad = ('import socket\nfrom rcon_client.client import RconClient\nimport subprocess as sp\n'
               'from actuator.rpc import rpc\nimport importlib\nexec("1")\nimport os\nos.system("x")\n'
               'P = "server/data/connection.json"\n')
        found = honesty.violations_in(bad, 'brain/x.py')
        for needle in ('socket', 'rcon_client', 'subprocess', 'actuator.rpc', 'importlib', 'exec()', 'os.system',
                       'connection.json'):
            self.assertTrue(any(needle in f for f in found), (needle, found))

    def test_actuator_actions_and_queries_are_allowed(self):
        good = 'from actuator import actions, queries\nimport actuator.queries\nimport json, math, os\nos.path.join("a")\n'
        self.assertEqual(honesty.violations_in(good, 'brain/y.py'), [])

    def test_current_brain_is_honest(self):
        self.assertEqual(honesty.check(Path(__file__).resolve().parents[1]), [])


if __name__ == '__main__':
    unittest.main()
