"""Public high-level actions preserve batch requirements and inventory costs."""
import unittest
import actions
from scripts.test_brain import state


class ActionLibraryTest(unittest.TestCase):
    def test_gathering_actions_request_specific_resource_batches(self):
        s=state(); player=s['players'][0]
        for action,resource,count in ((actions.mine_coal,'coal',4),
                                      (actions.mine_iron_ore,'iron-ore',16),
                                      (actions.mine_stone,'stone',5)):
            plan=action(s,player)['action']
            self.assertEqual(plan['resource'],resource)
            self.assertEqual(plan['count'],count)

    def test_build_furnace_gathers_only_missing_stone(self):
        s=state({'stone':3})
        plan=actions.build_furnace(s,s['players'][0])
        self.assertEqual(plan['action']['resource'],'stone')
        self.assertEqual(plan['action']['count'],2)

    def test_full_production_action_respects_inventory_goal(self):
        self.assertEqual(actions.make_iron_plates(state({'iron-plate':100}),player_name='alice')['phase'],'complete')
        self.assertNotEqual(actions.make_iron_plates(state({'iron-plate':99}),player_name='alice')['phase'],'complete')

    def test_transfer_to_far_furnace_plans_movement_first(self):
        s=state(); furnace={'unit_number':1,'position':{'x':30,'y':0}}
        self.assertEqual(actions.load_iron_ore(s['players'][0],furnace,16)['action']['kind'],'move')
