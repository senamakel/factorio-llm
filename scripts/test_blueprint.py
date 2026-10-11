"""Exact factory balances, machine sizing, blueprint validation and persistence."""
from fractions import Fraction
import unittest
from brain.blueprint_solver import solve


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
