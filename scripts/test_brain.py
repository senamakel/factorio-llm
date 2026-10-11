"""Behavioral checks for the local iron-start policy and durable event ingestion."""
import json
from pathlib import Path
import tempfile
import unittest
from brain.logic import brain_think
from brain.event_store import EventStore


def state(items=None, entities=None, enemies=None):
    return {'tick':100,'coverage':{'complete':True},
            'players':[{'name':'alice','surface':'nauvis','force':'player','position':{'x':0,'y':0},
                        'health':250,'inventory':[{'name':k,'count':v} for k,v in (items or {}).items()],
                        'resource_reach_distance':2.7,'reach_distance':10,'crafting_queue':[]}],
            'entities':entities or [], 'enemies':enemies or [],
            'world':{'resources':[{'name':'iron-ore','surface':'nauvis','position':{'x':1,'y':0},'amount':1000},
                                  {'name':'coal','surface':'nauvis','position':{'x':1,'y':1},'amount':1000},
                                  {'name':'stone','surface':'nauvis','position':{'x':2,'y':1},'amount':1000}]},
            'build_sites':{'alice':[{'x':3,'y':0},{'x':-3,'y':0}]}}

class PolicyTest(unittest.TestCase):
    def test_first_step_is_mining_iron(self):
        d=brain_think(state(),player_name='alice')
        self.assertEqual(d['action']['kind'],'mine')
        self.assertEqual(d['action']['resource'],'iron-ore')

    def test_ore_then_fuel_then_furnace(self):
        self.assertEqual(brain_think(state({'iron-ore':16}),player_name='alice')['action']['resource'],'coal')
        self.assertEqual(brain_think(state({'iron-ore':16,'coal':4}),player_name='alice')['action']['resource'],'stone')
        self.assertEqual(brain_think(state({'iron-ore':16,'coal':4,'stone':5}),player_name='alice')['action']['kind'],'craft')
        self.assertEqual(brain_think(state({'iron-ore':16,'coal':4,'stone-furnace':1}),player_name='alice')['action']['kind'],'build')

    def test_furnace_gets_real_inventory_fuel_and_ore(self):
        furnace={'name':'stone-furnace','type':'furnace','unit_number':1,'surface':'nauvis',
                 'force':'player','position':{'x':3,'y':0},'inventories':{}}
        s=state({'iron-ore':16,'coal':4},[furnace])
        self.assertEqual(brain_think(s,player_name='alice')['action']['item'],'coal')
        furnace['inventories']['fuel']=[{'name':'coal','count':4}]
        self.assertEqual(brain_think(s,player_name='alice')['action']['item'],'iron-ore')

    def test_collects_plates_and_does_not_steal_from_other_forces(self):
        furnace={'name':'stone-furnace','type':'furnace','unit_number':1,'surface':'nauvis',
                 'force':'player','position':{'x':3,'y':0},
                 'inventories':{'furnace_result':[{'name':'iron-plate','count':5}]}}
        d=brain_think(state(entities=[furnace]),player_name='alice')
        self.assertEqual(d['action']['kind'],'take')
        furnace['force']='enemy'
        self.assertNotEqual(brain_think(state(entities=[furnace]),player_name='alice')['action']['kind'],'take')

    def test_threats_and_incomplete_state_stop_actions(self):
        s=state(enemies=[{'surface':'nauvis','position':{'x':2,'y':0},'type':'unit'}])
        self.assertEqual(brain_think(s,player_name='alice')['phase'],'danger')
        s['coverage']['complete']=False
        self.assertEqual(brain_think(s,player_name='alice')['phase'],'observe')

    def test_failure_feedback_changes_next_build_site(self):
        s=state({'iron-ore':16,'coal':4,'stone-furnace':1})
        first=brain_think(s,player_name='alice')
        experience={first['action_key']:{'attempts':3,'failures':3,'mean_reward':-1}}
        second=brain_think(s,experience=experience,player_name='alice')
        self.assertNotEqual(first['action']['position'],second['action']['position'])

class StoreTest(unittest.TestCase):
    def test_partial_event_line_and_restart_are_imported_exactly_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp); journal=path/'events.jsonl'; db=path/'brain.sqlite3'
            journal.write_text('{"tick":1,"kind":"mined","data":{}}\n{"tick":2')
            with EventStore(db) as store:
                self.assertEqual(store.ingest(journal),1)
            with journal.open('a') as out:
                out.write(',"kind":"smelted","data":{}}\n')
            with EventStore(db) as store:
                self.assertEqual(store.ingest(journal),1)
                self.assertEqual(store.ingest(journal),0)
                self.assertEqual(store.count('events'),2)

    def test_snapshot_roundtrip_and_learned_failure_survive_reopening(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'brain.sqlite3'
            with EventStore(db) as store:
                sid=store.snapshot(state())
                store.learn('build:3:0',False,-1)
            with EventStore(db) as store:
                self.assertEqual(store.load_snapshot(sid),state())
                self.assertEqual(store.experience()['build:3:0']['failures'],1)

    def test_secrets_are_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            with EventStore(Path(tmp)/'brain.sqlite3',secrets=('private-test-token',)) as store:
                store.log('error',{'password':'hidden','message':'private-test-token'})
                row=store.conn.execute('SELECT payload_json FROM events').fetchone()[0]
                self.assertNotIn('private-test-token',row)
                self.assertNotIn('hidden',row)

if __name__=='__main__':
    unittest.main()
