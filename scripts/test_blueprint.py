"""Exact factory balances, machine sizing, blueprint validation and persistence."""
from fractions import Fraction
import unittest
from brain.blueprint_solver import solve
from brain.blueprint import Blueprint, create, design
import tempfile
from pathlib import Path


def recipes():
    return {'iron-plate':{'category':'smelting','energy':3.2,'ingredients':[{'name':'iron-ore','amount':1}],
                         'products':[{'name':'iron-plate','amount':1}]},
            'copper-plate':{'category':'smelting','energy':3.2,'ingredients':[{'name':'copper-ore','amount':1}],
                           'products':[{'name':'copper-plate','amount':1}]},
            'iron-gear-wheel':{'energy':.5,'ingredients':[{'name':'iron-plate','amount':2}],
                               'products':[{'name':'iron-gear-wheel','amount':1}]},
            'automation-science-pack':{'energy':5,'ingredients':[{'name':'iron-gear-wheel','amount':1},{'name':'copper-plate','amount':1}],
                                      'products':[{'name':'automation-science-pack','amount':1}]}}


def machines():
    return [{'name':'stone-furnace','speed':1,'categories':['smelting'],'width':2,'height':2,
             'power_w':90000,'fuel_item':'coal','fuel_value_j':4000000},
            {'name':'assembling-machine-1','speed':.5,'categories':['crafting'],'width':3,'height':3,'power_w':75000}]


class SolverTest(unittest.TestCase):
    def test_red_science_balances_ore_fuel_and_machine_speed(self):
        plan=solve({'automation-science-pack':'.1'},recipes(),machines())
        self.assertEqual(Fraction(plan['raw_inputs']['iron-ore']),Fraction(1,5))
        self.assertEqual(Fraction(plan['raw_inputs']['copper-ore']),Fraction(1,10))
        self.assertEqual(Fraction(plan['raw_inputs']['coal']),Fraction(27,1250))
        self.assertEqual(Fraction(plan['electric_watts']),82500)
        self.assertEqual(sum(r['machines'] for r in plan['recipes']),4)

    def test_joint_outputs_satisfy_both_targets_without_double_counting(self):
        data={'split':{'energy':1,'ingredients':[{'name':'ore','amount':1}],
                       'products':[{'name':'a','amount':1},{'name':'b','amount':2}]}}
        plan=solve({'a':1,'b':2},data,[{'name':'assembler','speed':1,'categories':['crafting']}])
        self.assertEqual(plan['raw_inputs'],{'ore':'1'})

    def test_alternative_recipe_uses_the_lower_input_cost(self):
        data={'expensive':{'energy':1,'ingredients':[{'name':'ore','amount':3}],'products':[{'name':'a','amount':1}]},
              'cheap':{'energy':1,'ingredients':[{'name':'ore','amount':1}],'products':[{'name':'a','amount':1}]}}
        plan=solve({'a':1},data,[{'name':'assembler','speed':1,'categories':['crafting']}])
        self.assertEqual([r['recipe'] for r in plan['recipes']],['cheap'])

    def test_missing_raw_supply_is_infeasible(self):
        with self.assertRaisesRegex(ValueError,'infeasible'):
            solve({'automation-science-pack':1},recipes(),machines(),raw_inputs=[])


class BlueprintTest(unittest.TestCase):
    def test_designed_cells_are_nonoverlapping_and_expose_supply_requirements(self):
        bp=design({'automation-science-pack':'.1'},recipes(),machines())
        self.assertTrue(bp.validate())
        self.assertFalse(bp.analysis['automatic_material_routing'])
        self.assertTrue(bp.analysis['ports'])

    def test_save_and_exchange_string_preserve_entity_recipes(self):
        bp=design({'automation-science-pack':'.1'},recipes(),machines())
        with tempfile.TemporaryDirectory() as tmp:
            path=bp.save(Path(tmp)/'factory.json')
            loaded=Blueprint.load(path)
        self.assertEqual(loaded.understand(),bp.understand())
        imported=Blueprint.from_factorio_string(bp.factorio_string())
        self.assertEqual(imported.understand()['recipes'],bp.understand()['recipes'])

    def test_overlapping_entities_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlap'):
            create('collision',[{'name':'iron-chest','position':{'x':0,'y':0}},
                                {'name':'iron-chest','position':{'x':0,'y':0}}])

    def test_existing_factory_requires_explicit_adoption(self):
        bp=create('one chest',[{'name':'iron-chest','position':{'x':0,'y':0}}])
        state={'entities':[{'name':'iron-chest','position':{'x':0,'y':0},'force':'player','surface':'nauvis','unit_number':1}]}
        player={'name':'Teeny','surface':'nauvis','force':'player'}
        self.assertEqual(bp.next_action(state,player)['phase'],'blocked')
        self.assertIsNone(bp.next_action(state,player,allow_existing=True))
