"""Python navigation planning stays bounded and does not overshoot axis changes."""
import unittest
from brain_actions import walking_instruction


class WalkingPlanTest(unittest.TestCase):
    def test_confident_clear_leg_runs_longer_than_two_seconds(self):
        plan=walking_instruction({'x':0,'y':0},{'x':100,'y':0},2,9,confident=True)
        self.assertEqual(plan['duration'],8)

    def test_mining_duration_estimates_only_the_requested_batch(self):
        from brain_actions import mining_duration
        self.assertAlmostEqual(mining_duration(3,1,.5,0,100,1,True),6.05)
        self.assertEqual(mining_duration(16,1,.5,0,100,1,False),2)

    def test_long_moves_choose_cardinal_direction_and_bounded_duration(self):
        plan=walking_instruction({'x':0,'y':0},{'x':100,'y':10},2,9)
        self.assertEqual(plan, {'direction':'east','duration':2})

    def test_diagonal_leg_stops_when_shorter_axis_is_aligned(self):
        plan=walking_instruction({'x':0,'y':0},{'x':-6,'y':4},1,9)
        self.assertEqual(plan['direction'],'southwest')
        self.assertAlmostEqual(plan['duration'],4*2**0.5/9)

    def test_already_in_reach_does_not_start_walking(self):
        self.assertEqual(walking_instruction({'x':0,'y':0},{'x':1,'y':0},2,9)['duration'],0)

    def test_paused_game_cannot_produce_a_timed_movement(self):
        with self.assertRaises(ValueError):
            walking_instruction({'x':0,'y':0},{'x':10,'y':0},2,0)
