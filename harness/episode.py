"""Run one scored brain episode on a disposable, seeded headless world.

Usage::

    python -m harness.episode --brain-root PATH --seed 1 [--out DIR]
        [--wall-secs 1200] [--game-speed 4] [--window-min 5]

Steps: copy the candidate's ``brain/`` next to the frozen ``actuator/``,
``rcon_client/`` and ``knowledge/`` from this checkout; start a fresh seeded
server; spawn the actor; run ``python -m brain episode --actor ID`` for the wall
budget; stop it; halt the actor; let the world run for the automation window;
read milestones and rates back from the world. Writes ``result.json``
(``score``, ``metrics``, ``failures``) and prints ``METRIC``/``DIAG`` lines in
the tinyrsi scorer format. The live sandbox is never touched.
"""
import argparse
import collections
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import milestones as ladder  # noqa: E402
from harness.server import EpisodeServer  # noqa: E402

TRACKED = (ladder.RED, ladder.GREEN, 'iron-ore', 'copper-ore', 'coal', 'stone', 'iron-plate', 'copper-plate',
           'iron-gear-wheel', 'copper-cable', 'electronic-circuit', 'inserter', 'transport-belt')
FROZEN = ('actuator', 'rcon_client', 'knowledge')
TICKS_PER_MINUTE = 3600


def stage(brain_root, workdir):
    """Assemble the episode checkout: candidate ``brain/`` plus this checkout's frozen packages."""
    repo = Path(workdir) / 'repo'
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    shutil.copytree(Path(brain_root) / 'brain', repo / 'brain', ignore=ignore)
    for name in FROZEN:
        if (ROOT / name).exists():
            shutil.copytree(ROOT / name, repo / name, ignore=ignore)
    (repo / 'server/data').mkdir(parents=True)
    return repo


def spawn_actor(server, speed):
    """Create the unattached character at a free spot near spawn and set game speed."""
    return server.lua(
        f'game.speed={float(speed)}; local s=game.surfaces[1]; '
        'local p=s.find_non_colliding_position("character",{0,0},64,0.5); assert(p,"no free spawn"); '
        'local e=s.create_entity{name="character",position=p,force="player"}; '
        'return {unit_number=e.unit_number,position=e.position}')


def sample(server):
    """Read the tick and cumulative production of tracked items."""
    return server.lua('local st=game.forces.player.get_item_production_statistics(game.surfaces[1]); '
                      'local out={}; for _,n in ipairs({' + ','.join(f'"{n}"' for n in TRACKED) + '}) do '
                      'out[n]=st.get_input_count(n) end; return {tick=game.tick,produced=out}')


def halt_actor(server, actor):
    """Stop walking/mining and cancel handcrafting so only machines produce afterwards."""
    return server.lua(f'local e=game.get_entity_by_unit_number({actor}); if not (e and e.valid) then return false end; '
                      'e.walking_state={walking=false}; e.mining_state={mining=false}; '
                      'local q=e.crafting_queue or {}; for i=#q,1,-1 do e.cancel_crafting{index=q[i].index,count=q[i].count} end; '
                      'return true')


def world_facts(server):
    """Read researched technologies, entity counts and assembler output from the world."""
    return server.lua(
        'local f=game.forces.player; local r={}; for n,t in pairs(f.technologies) do if t.researched then r[#r+1]=n end end; '
        'local counts,made={},0; for _,e in pairs(game.surfaces[1].find_entities_filtered{force=f}) do '
        'counts[e.name]=(counts[e.name] or 0)+1; if e.type=="assembling-machine" then made=made+e.products_finished end end; '
        'return {researched=r,entity_counts=counts,assembler_products=made}')


def wait_ticks(server, ticks, speed):
    """Block until the game advances ``ticks``; raise if the server stalls."""
    target = sample(server)['tick'] + ticks
    deadline = time.monotonic() + ticks / 60 / max(speed, .1) * 3 + 60
    while time.monotonic() < deadline:
        current = sample(server)
        if current['tick'] >= target:
            return current
        time.sleep(1)
    raise RuntimeError('server did not advance through the automation window')


def stop_brain(proc):
    """SIGTERM the brain (it halts and cancels its own actions), then SIGKILL if needed."""
    if proc.poll() is not None:
        return proc.returncode
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        return proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        return proc.wait(timeout=10)


def failures(stdout_path, stderr_path, limit=8):
    """Summarise the brain's most frequent action errors and its final stop reason."""
    errors, stop = collections.Counter(), None
    for line in Path(stdout_path).read_text(errors='replace').splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        result = row.get('result') if isinstance(row, dict) else None
        if isinstance(result, dict) and result.get('error'):
            errors[f"{row.get('phase', '?')}: {result['error']}"[:200]] += 1
        if isinstance(row, dict) and 'stop_reason' in row:
            stop = row['stop_reason']
    out = [f'{count}x {text}' for text, count in errors.most_common(limit)]
    if stop:
        out.append(f'stop reason: {stop}'[:300])
    tail = [line for line in Path(stderr_path).read_text(errors='replace').splitlines() if line.strip()][-5:]
    out += [f'stderr: {line}'[:300] for line in tail]
    return out


def default_live_data():
    """Find the configured sandbox: this checkout's ``server/data``, else the primary checkout's."""
    local = ROOT / 'server/data'
    if (local / 'connection.json').exists():
        return local
    common = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True)
    return Path(common.stdout.strip()).parent / 'server/data' if common.returncode == 0 else local


def run(brain_root, seed, out, wall_secs, speed, window_min, live_data):
    """Play and measure one episode; returns the result dict written to ``out/result.json``."""
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    world_dir = out / 'world'
    if world_dir.exists():
        shutil.rmtree(world_dir)
    repo = stage(brain_root, out)
    with EpisodeServer(world_dir, seed, live_data) as server:
        actor = spawn_actor(server, speed)
        (repo / 'server/data/teeny-actor.json').write_text(json.dumps(actor))
        env = {**os.environ, 'FACTORIO_CONNECTION_FILE': str(world_dir / 'connection.json'), 'PYTHONPATH': str(repo)}
        stdout, stderr = out / 'brain.jsonl', out / 'brain.err'
        started = sample(server)
        with stdout.open('w') as so, stderr.open('w') as se:
            proc = subprocess.Popen([sys.executable, '-m', 'brain', 'episode', '--actor', str(actor['unit_number']),
                                     '--wall-secs', str(wall_secs)], cwd=repo, env=env, stdout=so, stderr=se,
                                    stdin=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + wall_secs
            while time.monotonic() < deadline and proc.poll() is None:
                time.sleep(2)
            exit_code = stop_brain(proc)
        halted = halt_actor(server, actor['unit_number'])
        before = sample(server)
        after = wait_ticks(server, window_min * TICKS_PER_MINUTE, speed)
        rates = ladder.window_rates(before['produced'], after['produced'], (after['tick'] - before['tick']) / TICKS_PER_MINUTE)
        world = world_facts(server)
        server.rcon('/c game.server_save("episode-end")')
        time.sleep(2)
    reached = ladder.reached(world, rates)
    result = {
        'score': ladder.score(rates, reached),
        'metrics': {
            'red_spm': round(rates.get(ladder.RED, 0), 2), 'green_spm': round(rates.get(ladder.GREEN, 0), 2),
            'milestones': sum(reached.values()), 'reached': [k for k, v in reached.items() if v],
            'next_goal': ladder.next_goal(reached), 'rates_per_min': {k: round(v, 2) for k, v in rates.items()},
            'game_minutes_played': round((before['tick'] - started['tick']) / TICKS_PER_MINUTE, 1),
            'produced_while_playing': before['produced'], 'researched': sorted(world['researched']),
            'entity_counts': world['entity_counts'], 'brain_exit': exit_code, 'actor_halted': halted,
            'seed': seed, 'wall_secs': wall_secs, 'game_speed': speed,
        },
        'failures': failures(stdout, stderr),
    }
    (out / 'result.json').write_text(json.dumps(result, indent=2))
    return result


def main(argv=None):
    """Parse options (env defaults: EPISODE_WALL_SECS, EPISODE_GAME_SPEED, EPISODE_WINDOW_MIN)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--brain-root', default=os.environ.get('RSI_CANDIDATE', str(ROOT)))
    parser.add_argument('--seed', type=int, default=int(os.environ.get('RSI_SEED', '1')))
    parser.add_argument('--out', default=os.environ.get('RSI_OUT'))
    parser.add_argument('--wall-secs', type=float, default=float(os.environ.get('EPISODE_WALL_SECS', '1200')))
    parser.add_argument('--game-speed', type=float, default=float(os.environ.get('EPISODE_GAME_SPEED', '4')))
    parser.add_argument('--window-min', type=float, default=float(os.environ.get('EPISODE_WINDOW_MIN', '5')))
    parser.add_argument('--live-data', default=os.environ.get('FACTORIO_EPISODE_LIVE_DATA') or str(default_live_data()))
    args = parser.parse_args(argv)
    out = args.out or str(Path(args.live_data) / 'episodes' / f'{time.strftime("%Y%m%d-%H%M%S")}-seed{args.seed}')
    result = run(args.brain_root, args.seed, out, args.wall_secs, args.game_speed, args.window_min, args.live_data)
    m = result['metrics']
    print(f"DIAG seed {m['seed']}: {m['game_minutes_played']} game-min played, reached {m['reached']}, next {m['next_goal']}")
    print(f"DIAG rates/min in automation window: {m['rates_per_min']}")
    for line in result['failures']:
        print(f'DIAG failure: {line}')
    print(f"METRIC red_spm={m['red_spm']}")
    print(f"METRIC green_spm={m['green_spm']}")
    print(f"METRIC milestones={m['milestones']}")
    print(f"METRIC score={result['score']}")
    print(f'DIAG result: {Path(out) / "result.json"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
