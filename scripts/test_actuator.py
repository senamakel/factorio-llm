"""Offline checks for the frozen actuator: argument validation and Lua-table normalisation."""
import unittest
from unittest.mock import patch

from actuator import actions, queries


class ActuatorValidationTest(unittest.TestCase):
    def test_unknown_entity_fields_are_rejected_before_any_game_call(self):
        with patch('actuator.queries.actor_rpc') as rpc:
            with self.assertRaisesRegex(ValueError, 'unknown entity fields'):
                queries.find_entities(1, {'type': 'furnace'}, ('name', 'lua_code'))
        rpc.assert_not_called()

    def test_unsupported_filters_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported filters'):
            queries.find_entities(1, {'type': 'furnace', 'invert': True})

    def test_walk_direction_and_craft_count_are_validated(self):
        with self.assertRaisesRegex(ValueError, 'direction'):
            actions.walk(1, 'up')
        with self.assertRaisesRegex(ValueError, 'count'):
            actions.craft(1, 'iron-gear-wheel', 0)
        with self.assertRaisesRegex(ValueError, 'count'):
            actions.put(1, {'x': 0, 'y': 0}, 'coal', True)

    def test_actor_id_must_be_a_positive_integer(self):
        from actuator.rpc import actor_rpc
        for bad in (0, -1, '3', True):
            with self.assertRaises(ValueError):
                actor_rpc(bad, 'return 1')

    def test_build_enforces_inventory_reach_and_collision_in_lua(self):
        with patch('actuator.actions.actor_rpc', return_value={'ok': True}) as rpc:
            actions.build(7, 'stone-furnace', {'x': 1, 'y': 2}, 'east')
        body, args = rpc.call_args.args[1], rpc.call_args.args[2]
        self.assertIn('inv.get_item_count(a.item)>0', body)
        self.assertIn('site out of build reach', body)
        self.assertIn('s.can_place_entity(o)', body)
        self.assertIn('inv.remove{name=a.item,count=1}', body)
        self.assertEqual(args['direction'], 'east')

    def test_save_names_are_restricted(self):
        with self.assertRaises(ValueError):
            actions.save('x"); game.speed=100; --')


class LuaTableNormalisationTest(unittest.TestCase):
    def test_empty_lua_tables_become_lists(self):
        reply = {'iron-plate': {'enabled': True, 'ingredients': {}, 'products': [{'name': 'iron-plate', 'type': 'item'}],
                                'categories': ['smelting'], 'energy': 3.2}}
        with patch('actuator.queries.actor_rpc', return_value=reply):
            recipe = queries.recipes(1, ['iron-plate'])['iron-plate']
        self.assertEqual(recipe['ingredients'], [])

    def test_empty_inventory_and_entity_lists(self):
        with patch('actuator.queries.actor_rpc', return_value={'inventory': {}, 'crafting_queue': {}, 'tick': 1}):
            state = queries.actor_state(1)
        self.assertEqual((state['inventory'], state['crafting_queue']), ([], []))
        with patch('actuator.queries.actor_rpc', return_value={'entities': {}, 'truncated': False}):
            self.assertEqual(queries.find_entities(1, {'type': 'lab'})['entities'], [])

    def test_technologies_normalise_prerequisites_and_queue(self):
        reply = {'technologies': {'steam-power': {'prerequisites': {}, 'unlocks': ['pipe'], 'ingredients': {}}},
                 'current': None, 'progress': 0, 'queue': {}}
        with patch('actuator.queries.actor_rpc', return_value=reply):
            found = queries.technologies(1, ['steam-power'])
        self.assertEqual(found['technologies']['steam-power']['prerequisites'], [])
        self.assertEqual(found['queue'], [])


if __name__ == '__main__':
    unittest.main()
