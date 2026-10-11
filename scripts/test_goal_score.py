"""Goal and reward behavior using measured inventory and cumulative counters."""
from copy import deepcopy
import unittest
from goal import IronPlateGoal
from score import score_transition
from scripts.test_brain import state


class GoalScoreTest(unittest.TestCase):
    def setUp(self):
        self.goal = IronPlateGoal('alice')

    def test_only_actor_inventory_completes_goal(self):
        self.assertFalse(self.goal.evaluate(state({'iron-plate':99}))['complete'])
        self.assertTrue(self.goal.evaluate(state({'iron-plate':100}))['complete'])
        self.assertFalse(IronPlateGoal('missing').evaluate(state({'iron-plate':100}))['complete'])

    def test_production_inventory_and_progress_are_rewarded(self):
        before = state()
        after = state({'iron-plate':10})
        after.update(tick=160, iron_produced=10, resource_drain=12)
        parts = score_transition(before, after, self.goal)['components']
        self.assertEqual(parts['throughput'], 10)
        self.assertEqual(parts['inventory'], 50)
        self.assertEqual(parts['progress'], 10)
        self.assertAlmostEqual(parts['resource_drain'], -1.2)

    def test_idle_time_resource_drain_and_enemies_cost_reward(self):
        before = state()
        after = deepcopy(before)
        after.update(tick=160, resource_drain=5)
        after['enemies']=[{'surface':'nauvis','type':'unit','position':{'x':1,'y':1}}]
        parts = score_transition(before, after, self.goal)['components']
        self.assertEqual(parts['time'], -0.02)
        self.assertEqual(parts['resource_drain'], -0.5)
        self.assertEqual(parts['enemies'], -1)
        self.assertLess(score_transition(before, after, self.goal)['total'], 0)

    def test_losing_inventory_and_health_is_penalized(self):
        before = state({'iron-plate':10})
        after = state({'iron-plate':5})
        after['players'][0]['health']=200
        parts = score_transition(before, after, self.goal)['components']
        self.assertLess(parts['inventory'],0)
        self.assertLess(parts['progress'],0)
        self.assertEqual(parts['damage'],-5)

    def test_zero_time_and_reset_counters_do_not_fabricate_throughput(self):
        before = state(); before['iron_produced']=50; before['resource_drain']=20
        after = state(); after['iron_produced']=0; after['resource_drain']=0
        parts = score_transition(before, after, self.goal)['components']
        self.assertEqual(parts['throughput'],0)
        self.assertEqual(parts['resource_drain'],0)


if __name__ == '__main__':
    unittest.main()
