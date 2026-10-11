"""Agent-friendly JSON inspection, planning, bounded streaming and run commands."""
import argparse
import inspect
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def configure_runtime():
    """Use explicit connection overrides or the shared manifest before importing RCON settings."""
    if not os.environ.get('FACTORIO_CONNECTION_FILE') and not (ROOT/'server/data/connection.json').exists():
        from scripts.mcp_config import load_servers
        for key,value in load_servers(ROOT)['factorio-control'].get('env',{}).items():os.environ.setdefault(key,value)


def default_actor():
    """Read the private current assistant reference; require explicit selection if absent."""
    path=ROOT/'server/data/teeny-actor.json'
    return json.loads(path.read_text())['unit_number'] if path.exists() else None


def episode(argv):
    """Scored-episode entrypoint called by the frozen harness: play until the wall budget ends.

    Contract: ``python -m brain episode --actor ID --wall-secs N``. The harness
    sends SIGTERM when time is up, then measures what the factory produces on
    its own. Print one JSON object per step on stdout (``phase``, ``result``
    with ``error`` on failure) and a final object with ``stop_reason``; the
    harness feeds those errors back to the hive. Exit code is informational.
    """
    parser=argparse.ArgumentParser(prog='brain episode')
    parser.add_argument('--actor',type=int,required=True)
    parser.add_argument('--wall-secs',type=float,required=True)
    args=parser.parse_args(argv)
    from brain.runner import main as run
    return run(['--actor',str(args.actor),'--objective','research','--steps','100000',
                '--run-timeout',str(max(1,args.wall_secs-5))])


def main(argv=None):
    """Run JSON-first commands; only run mutates the game, inspection/planning are read-only."""
    argv=list(sys.argv[1:] if argv is None else argv)
    configure_runtime()
    if argv and argv[0].startswith('-') and argv[0] not in ('--help','-h'):
        from brain.runner import main as run
        return run(argv)
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('state','think','stream'):
        p=sub.add_parser(name);p.add_argument('--actor',type=int,default=default_actor())
        if name=='state':p.add_argument('--output');p.add_argument('--store',action='store_true')
        if name=='think':p.add_argument('--objective',choices=['iron','research'],default='research')
        if name=='stream':p.add_argument('--count',type=int,default=10);p.add_argument('--interval',type=float,default=2)
    p=sub.add_parser('run');p.add_argument('options',nargs=argparse.REMAINDER)
    p=sub.add_parser('history');p.add_argument('--limit',type=int,default=20)
    sub.add_parser('actions')
    sub.add_parser('status');sub.add_parser('stop')
    p=sub.add_parser('blueprint');p.add_argument('path')
    p=sub.add_parser('episode');p.add_argument('options',nargs=argparse.REMAINDER)
    if argv and argv[0]=='episode':
        return episode(argv[1:])
    if argv and argv[0]=='run':
        from brain.runner import main as run
        options=argv[1:]
        if '--actor' not in options:
            actor=default_actor()
            if actor is None:parser.error('create/select an assistant before running')
            options=['--actor',str(actor),*options]
        return run(options)
    args=parser.parse_args(argv)
    try:
        if args.command in ('status','stop'):
            from brain.controller import status,stop
            print(json.dumps(stop() if args.command=='stop' else status(),indent=2));return
        if args.command=='actions':
            from brain import actions
            print(json.dumps({name:{'signature':str(inspect.signature(getattr(actions,name))),
                                  'doc':inspect.getdoc(getattr(actions,name))} for name in actions.__all__},indent=2));return
        if args.command=='history':
            if not 1<=args.limit<=1000:parser.error('history limit must be 1..1000')
            from brain.event_store import EventStore
            with EventStore() as store:print(json.dumps(store.recent_events(args.limit),indent=2))
            return
        if args.command=='blueprint':
            from brain.blueprint import Blueprint
            print(json.dumps(Blueprint.load(args.path).understand(),indent=2));return
        if args.actor is None:parser.error('use --actor or create the private current assistant reference')
        from brain.observation import observe
        from brain.timeouts import deadline
        def snapshot():
            with deadline(20,'CLI state observation'):return observe(args.actor,'Teeny')
        if args.command=='think':
            from brain.actions import first_research,make_iron_plates
            state=snapshot()
            plan=first_research(state) if args.objective=='research' else make_iron_plates(state)
            print(json.dumps(plan,indent=2));return
        if args.command=='stream':
            if not 1<=args.count<=1000 or not .1<=args.interval<=60:parser.error('stream count/interval exceed bounds')
            with deadline(1800,'state stream'):
                for i in range(args.count):
                    print(json.dumps(snapshot()),flush=True)
                    if i+1<args.count:time.sleep(args.interval)
            return
        state=snapshot()
        if args.store:
            from brain.event_store import EventStore
            with EventStore() as store:state['snapshot_id']=store.snapshot(state)
        raw=json.dumps(state,indent=2)
        if args.output:
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(raw+'\n')
            print(json.dumps({'output':str(path),'tick':state['tick'],'snapshot_id':state.get('snapshot_id')}))
        else:print(raw)
    except (ValueError,RuntimeError,OSError) as exc:
        print(json.dumps({'error':str(exc),'operation':args.command}),file=sys.stderr)
        return 1
