"""Opt-in live regression tests on a disposable surface; no existing builds are touched."""
import os
import time
import unittest
import uuid
from brain import execute, rpc


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
        execute(self.actor, {'kind':'move','position':{'x':12,'y':0},'stop_distance':1})
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
        execute(self.actor, {'kind':'mine','resource':'iron-ore','position':pos})
        time.sleep(2.5)
        count = rpc('return game.get_entity_by_unit_number(' + str(self.actor) +
                    ').get_inventory(defines.inventory.character_main).get_item_count("iron-ore")')
        execute(self.actor, {'kind':'wait'})
        self.assertGreater(count, 0)


if __name__ == '__main__':
    unittest.main()
