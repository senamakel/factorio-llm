"""Opt-in live regression tests on a disposable surface; no existing builds are touched."""
import os
import time
import unittest
import uuid
from brain import execute, observe, rpc
from brain.logic import entity_item_count
from brain.research_rules.power import steam_layout


@unittest.skipUnless(os.environ.get('FACTORIO_LIVE_TESTS') == '1', 'requires a live Factorio server')
class NativeActionTest(unittest.TestCase):
    def setUp(self):
        self.surface = 'brain-test-' + uuid.uuid4().hex[:10]
        self.actor = rpc('local s=game.create_surface("' + self.surface + '",{width=64,height=64,water=0}); '
                         's.request_to_generate_chunks({0,0},1); s.force_generate_chunk_requests(); '
                         'for _,e in pairs(s.find_entities()) do e.destroy() end; '
                         'local tiles={}; for x=-16,16 do for y=-16,16 do tiles[#tiles+1]={name="grass-1",position={x,y}} end end; '
                         's.set_tiles(tiles); local e=s.create_entity{name="character",position={0,0},force="player"}; return e.unit_number')

    def tearDown(self):
        rpc('game.delete_surface("' + self.surface + '"); return true')

    def position(self):
        return rpc('return game.get_entity_by_unit_number(' + str(self.actor) + ').position')

    def test_move_continues_between_commands_and_stops_at_end(self):
        result=execute(self.actor, {'kind':'move','position':{'x':24,'y':0},'stop_distance':1})
        self.assertGreater(result['duration'],2)
        self.assertEqual(result['confidence'],'high')
        a = self.position()
        time.sleep(0.3)
        b = self.position()
        self.assertGreater(b['x'], a['x'] + 1, 'move must continue in the game without another frame command')
        execute(self.actor, {'kind':'wait'})
        time.sleep(0.1)
        a = self.position()
        time.sleep(0.3)
        b = self.position()
        self.assertAlmostEqual(a['x'], b['x'], delta=0.05)

    def test_native_mining_accumulates_ore_between_commands(self):
        pos = rpc('local e=game.get_entity_by_unit_number(' + str(self.actor) + '); '
                  'local r=e.surface.create_entity{name="iron-ore",position={1,0},amount=100}; return r.position')
        result=execute(self.actor, {'kind':'mine','resource':'iron-ore','position':pos,'count':3})
        self.assertGreater(result['duration'],2)
        time.sleep(2.5)
        count = rpc('return game.get_entity_by_unit_number(' + str(self.actor) +
                    ').get_inventory(defines.inventory.character_main).get_item_count("iron-ore")')
        execute(self.actor, {'kind':'wait'})
        self.assertGreater(count, 0)

    def test_furnace_inputs_and_outputs_can_be_observed_and_transferred(self):
        furnace = rpc('local a=game.get_entity_by_unit_number(' + str(self.actor) + '); '
                      'a.get_inventory(defines.inventory.character_main).insert{name="iron-ore",count=2}; '
                      'local e=a.surface.create_entity{name="stone-furnace",position={4,0},force=a.force}; '
                      'return {unit_number=e.unit_number,position=e.position}')
        execute(self.actor, {'kind':'put',**furnace,'inventory':'furnace_source','item':'iron-ore','count':2})
        s = observe(self.actor, 'Teeny')
        self.assertEqual(entity_item_count(s['entities'][0], 'furnace_source', 'iron-ore'), 2)
        execute(self.actor, {'kind':'take',**furnace,'inventory':'furnace_source','item':'iron-ore','count':2})
        s = observe(self.actor, 'Teeny')
        self.assertEqual(entity_item_count(s['entities'][0], 'furnace_source', 'iron-ore'), 0)

    def test_unattached_character_crafts_with_real_ingredient_costs(self):
        rpc('local e=game.get_entity_by_unit_number('+str(self.actor)+'); '
            'e.get_inventory(defines.inventory.character_main).insert{name="iron-plate",count=2}; return true')
        execute(self.actor,{'kind':'craft','recipe':'iron-gear-wheel','count':1})
        time.sleep(1)
        inv=rpc('local i=game.get_entity_by_unit_number('+str(self.actor)+').get_inventory(defines.inventory.character_main); '
                'return {plates=i.get_item_count("iron-plate"),gears=i.get_item_count("iron-gear-wheel")}')
        self.assertEqual(inv,{'plates':0,'gears':1})

    def test_connected_steam_layout_powers_a_lab(self):
        from mcp_server.server import lua_string
        import json
        rpc('local s=game.surfaces["'+self.surface+'"]; local t={}; '
            'for x=-16,16 do for y=-16,-10 do t[#t+1]={name="water",position={x,y}} end end; s.set_tiles(t); return true')
        layout=steam_layout({'x':-10.5,'y':-8.5},'north')
        payload=lua_string(json.dumps(layout))
        result=rpc('local s=game.surfaces["'+self.surface+'"]; local a=helpers.json_to_table('+payload+'); '
            'local ids={}; for _,p in ipairs(a) do local o={name=p.name,position=p.position,direction=defines.direction[p.direction],force="player"}; '
            'assert(s.can_place_entity(o),"layout blocked: "..p.role); local e=s.create_entity(o); ids[p.role]=e.unit_number; '
            'if p.role=="boiler" then e.insert{name="coal",count=2} end end; return ids')
        time.sleep(2)
        energy=rpc('return game.surfaces["'+self.surface+'"].find_entities_filtered{name="lab"}[1].energy')
        self.assertGreater(energy,0,'lab must receive real steam-engine electricity')
        observed=observe(self.actor,'Teeny')
        self.assertTrue(any(e['name']=='lab' and e['energy']>0 for e in observed['entities']))


if __name__ == '__main__':
    unittest.main()
