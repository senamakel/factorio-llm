"""Recipe dependencies, trigger gates, research progress and machine interactions."""
import unittest
from brain.research_rules.recipes import ensure_item
from brain.research_rules.bootstrap import first_research
from brain.research_rules.smelting import transfer
from scripts.test_brain import state


class ResearchRulesTest(unittest.TestCase):
    def test_two_product_recipe_does_not_double_material_requirements(self):
        s=state({'copper-plate':1})
        s['recipes']={'copper-cable':{'enabled':True,'ingredients':[{'name':'copper-plate','amount':1}],
                                    'products':[{'name':'copper-cable','amount':2}]}}
        plan=ensure_item(s,s['players'][0],'copper-cable',2)
        self.assertEqual(plan['action'],{'kind':'craft','player':'alice','recipe':'copper-cable','count':1})

    def test_locked_recipes_are_not_bypassed(self):
        s=state(); s['recipes']={'lab':{'enabled':False}}
        self.assertEqual(ensure_item(s,s['players'][0],'lab',1)['phase'],'blocked')

    def test_trigger_research_requires_real_production_before_power_build(self):
        s=state({'iron-plate':100})
        s['technologies']={'steam-power':{'researched':False}}
        s['iron_produced']=0
        self.assertNotEqual(first_research(s,player_name='alice')['phase'],'plan_power')

    def test_automation_completion_is_observed_not_fabricated(self):
        s=state(); s['technologies']={'automation':{'researched':True}}
        self.assertEqual(first_research(s,player_name='alice')['phase'],'complete')

    def test_machine_transfer_requires_close_approach(self):
        s=state(); e={'name':'stone-furnace','unit_number':1,'position':{'x':8,'y':0}}
        self.assertEqual(transfer(s['players'][0],e,'fuel','coal',8)['kind'],'move')
