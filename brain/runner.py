"""Bounded local assistant loop: observe, decide, execute, score and persist.

The assistant is an unattached character. Walking and mining use sustained native
engine instructions; crafting/building use inventory-costed script actions.
No LLM or mod restart is needed.
"""
import argparse
import json
from pathlib import Path
import signal
import time

from brain.event_store import EventStore
from brain.goal import IronPlateGoal, FirstResearchGoal
from brain.actions import make_iron_plates, first_research
from brain.execution import execute
from brain.io import rpc, show_status
from brain.observation import observe
from brain.score import score_transition

ROOT = Path(__file__).resolve().parents[1]


def interrupt_run(signum, frame):
    """Convert process termination into an exception so active native inputs stop."""
    raise KeyboardInterrupt('brain run interrupted')


def run_brain(actor_id, steps=500, interval=0.5, target=100, objective='iron'):
    """Run at most steps actions, record each outcome, and stop on completion or danger."""
    baseline = observe(actor_id, 'Teeny')
    tech=baseline.get('technologies',{}).get('automation',{})
    science_cost=tech.get('count',10)*next((i.get('amount',1) for i in tech.get('ingredients',[]) if i['name']=='automation-science-pack'),1)
    goal = FirstResearchGoal(target=science_cost) if objective=='research' else IronPlateGoal(target=target)
    total = 0
    def measured():
        state = observe(actor_id, goal.player_name)
        state['resource_drain'] = max(0, state['resource_mined'] - baseline['resource_mined']) + max(0, state['fuel_consumed'] - baseline['fuel_consumed'])
        return state
    with EventStore() as store:
        before = measured()
        for step in range(steps):
            sid = store.snapshot(before)
            store.log('observation', goal.evaluate(before), before['tick'])
            decision = (first_research(before,store.experience(),goal.player_name) if objective=='research' else
                        make_iron_plates(before, store.experience(), goal.player_name, goal.target))
            status = goal.evaluate(before)
            action=decision['action']
            detail=f" ({action['count']} {action.get('item',action.get('recipe',''))})" if action.get('count') and action['kind'] not in ('mine','move') else ''
            show_status(actor_id, f"Teeny: {decision['phase'].replace('_',' ')}{detail} | {status['inventory']}/{goal.target} {goal.unit}")
            ident = store.decision(sid, decision, applied=decision['phase'] not in ('complete','danger'))
            if decision['phase'] in ('complete', 'danger','blocked'):
                break
            store.log('action', decision['action'], before['tick'])
            try:
                result = execute(actor_id, decision['action'])
                if result.get('duration', 0) > 0:
                    try:
                        time.sleep(result['duration'])
                    finally:
                        execute(actor_id, {'kind':'wait'})
            except (RuntimeError, ValueError) as exc:
                result = {'ok':False,'error':str(exc)}
            if not result.get('duration'):
                time.sleep(interval)
            after = measured()
            reward = score_transition(before, after, goal)
            total += reward['total']
            outcome = {'result':result,'score':reward,'goal':goal.evaluate(after)}
            store.outcome(ident, outcome)
            store.log('outcome', outcome, after['tick'])
            store.learn(decision['action_key'], result.get('ok',False), reward['total'])
            print(json.dumps({'step':step,'phase':decision['phase'],**outcome}), flush=True)
            before = after
        summary = {**goal.evaluate(before),'score':total,'tick':before['tick']}
        store.log('run_summary', summary, before['tick'])
        if summary['complete']:
            rpc('game.server_save("teeny-'+objective+'-complete"); return true')
        return summary


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, interrupt_run)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actor',type=int,required=True)
    parser.add_argument('--steps',type=int,default=500)
    parser.add_argument('--interval',type=float,default=0.5)
    parser.add_argument('--target',type=int,default=100)
    parser.add_argument('--objective',choices=['iron','research'],default='iron')
    args = parser.parse_args()
    if args.steps <= 0 or args.interval <= 0:
        parser.error('steps and interval must be positive')
    print(json.dumps(run_brain(args.actor,args.steps,args.interval,args.target,args.objective)))
