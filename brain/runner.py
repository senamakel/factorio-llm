"""Bounded observation/decision/action/outcome loop with explicit timeout diagnostics."""
import argparse
import json
import signal
import time

from brain.event_store import EventStore
from brain.goal import IronPlateGoal, FirstResearchGoal
from brain.actions import make_iron_plates, first_research
from brain.execution import execute
from actuator.actions import save, show_status
from brain.observation import observe
from brain.score import score_transition
from brain.logic import distance, get_player
from brain.timeouts import deadline, ProgressWatchdog


def interrupt_run(signum, frame):
    """Convert process termination to a catchable interruption so native inputs stop."""
    raise KeyboardInterrupt('brain run interrupted')


def run_brain(actor_id, steps=500, interval=.5, target=100, objective='iron',
              run_timeout=1800, stall_timeout=120, action_timeout=30, observe_timeout=20,
              max_failures=3):
    """Own this actor exclusively while running the bounded objective and persistence loop."""
    from brain.controller import ownership
    with ownership(actor_id,objective):
        return _run_brain(actor_id,steps,interval,target,objective,run_timeout,stall_timeout,
                          action_timeout,observe_timeout,max_failures)


def _run_brain(actor_id, steps=500, interval=.5, target=100, objective='iron',
              run_timeout=1800, stall_timeout=120, action_timeout=30, observe_timeout=20,
              max_failures=3):
    """Run a bounded objective and return measured completion or an explicit stop reason.

    Deadlines include blocking I/O and native action time. Three failed actions or
    stalled meaningful state stop the run. All exit paths attempt a three-second
    native halt; timed-out/interrupted runs also cancel this assistant's handcrafts.
    Server-side factories/research continue naturally. Saves are requested on success.
    """
    if objective not in ('iron','research') or min(steps,interval,run_timeout,stall_timeout,action_timeout,observe_timeout,max_failures)<=0:
        raise ValueError('objective and all run limits must be valid and positive')
    before=None;goal=None;total=0;reason='step_limit';step=0
    with EventStore() as store:
        try:
            with deadline(run_timeout,'overall brain run'):
                with deadline(observe_timeout,'initial observation'):baseline=observe(actor_id,'Teeny')
                tech=baseline.get('technologies',{}).get('automation',{})
                science_cost=tech.get('count',10)*next((i.get('amount',1) for i in tech.get('ingredients',[]) if i['name']=='automation-science-pack'),1)
                goal=FirstResearchGoal(target=science_cost) if objective=='research' else IronPlateGoal(target=target)
                def measured():
                    with deadline(observe_timeout,'world observation'):state=observe(actor_id,goal.player_name)
                    state['resource_drain']=max(0,state['resource_mined']-baseline['resource_mined'])+max(0,state['fuel_consumed']-baseline['fuel_consumed'])
                    return state
                watchdog=ProgressWatchdog(stall_timeout,max_failures)
                before=measured();watchdog.check(before,{'ok':True})
                for step in range(steps):
                    sid=store.snapshot(before)
                    store.log('observation',goal.evaluate(before),before['tick'])
                    plan=(first_research(before,store.experience(),goal.player_name) if objective=='research' else
                          make_iron_plates(before,store.experience(),goal.player_name,goal.target))
                    status=goal.evaluate(before);action=plan['action']
                    detail=f" ({action['count']} {action.get('item',action.get('recipe',''))})" if action.get('count') and action['kind'] not in ('mine','move') else ''
                    show_status(actor_id,f"Teeny: {plan['phase'].replace('_',' ')}{detail} | {status['inventory']}/{goal.target} {goal.unit}")
                    terminal=plan['phase'] in ('complete','danger','blocked')
                    ident=store.decision(sid,plan,applied=not terminal)
                    if terminal:
                        reason=plan['phase']+(': '+plan['reason'] if plan['phase']!='complete' else '')
                        break
                    store.log('action',action,before['tick'])
                    watchdog.note_action(action,before)
                    try:
                        with deadline(action_timeout,'action '+action['kind']):
                            result=execute(actor_id,action)
                            if result.get('duration',0)>0:
                                try:time.sleep(result['duration'])
                                finally:execute(actor_id,{'kind':'wait'})
                    except (RuntimeError,ValueError,OSError) as exc:
                        result={'ok':False,'error':str(exc)}
                    if not result.get('duration'):time.sleep(interval)
                    after=measured()
                    if action['kind']=='move' and result.get('duration',0)>.2:
                        a,b=get_player(before,goal.player_name),get_player(after,goal.player_name)
                        if a and b and distance(a['position'],b['position'])<.2:
                            result.update(ok=False,error='native movement made no measured progress')
                    reward=score_transition(before,after,goal);total+=reward['total']
                    outcome={'result':result,'score':reward,'goal':goal.evaluate(after)}
                    store.outcome(ident,outcome);store.log('outcome',outcome,after['tick'])
                    store.learn(plan['action_key'],result.get('ok',False),reward['total'])
                    print(json.dumps({'step':step,'phase':plan['phase'],**outcome}),flush=True)
                    before=after;watchdog.check(before,result,action)
        except (KeyboardInterrupt,RuntimeError,ValueError,OSError) as exc:
            reason=f'{type(exc).__name__}: {exc}'
            store.log('run_stopped',{'reason':reason,'step':step})
        finally:
            try:
                with deadline(3,'halt native actions'):
                    execute(actor_id,{'kind':'halt','cancel_crafting':reason!='complete'})
            except (RuntimeError,ValueError,OSError) as exc:
                store.log('halt_failed',{'reason':str(exc)})
        summary=({**goal.evaluate(before)} if goal and before else {'complete':False})
        summary.update(score=total,tick=before.get('tick') if before else None,stop_reason=reason)
        store.log('run_summary',summary,summary['tick'])
        if summary['complete']:save('teeny-'+objective+'-complete')
        else:
            try:show_status(actor_id,'Teeny: stopped | '+reason[:90])
            except (RuntimeError,ValueError,OSError):pass
        return summary


def main(argv=None):
    """Parse objective/deadline controls and run the assistant in the main thread."""
    signal.signal(signal.SIGTERM,interrupt_run)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actor',type=int,required=True)
    parser.add_argument('--steps',type=int,default=500)
    parser.add_argument('--interval',type=float,default=.5)
    parser.add_argument('--target',type=int,default=100)
    parser.add_argument('--objective',choices=['iron','research'],default='iron')
    parser.add_argument('--run-timeout',type=float,default=1800)
    parser.add_argument('--stall-timeout',type=float,default=120)
    parser.add_argument('--action-timeout',type=float,default=30)
    parser.add_argument('--observe-timeout',type=float,default=20)
    parser.add_argument('--max-failures',type=int,default=3)
    args=parser.parse_args(argv)
    try:summary=run_brain(args.actor,args.steps,args.interval,args.target,args.objective,
                         args.run_timeout,args.stall_timeout,args.action_timeout,args.observe_timeout,args.max_failures)
    except (ValueError,RuntimeError) as exc:parser.error(str(exc))
    print(json.dumps(summary))
    return 0 if summary['complete'] else 2


if __name__=='__main__':main()
