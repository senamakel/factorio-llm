"""Score a candidate brain: one honest episode on a disposable seeded world per seed.

Runs the frozen ``harness.episode`` from the incumbent checkout against
``$RSI_CANDIDATE``'s ``brain/`` for ``$RSI_SEED``; it writes ``$RSI_OUT/result.json``
(score = capped red/min + capped green/min + 5 per ladder milestone, measured
while the actor is halted) and prints METRIC/DIAG lines. Afterwards the outcome
is appended to the hive's shared memory (best effort; a memory outage never
fails scoring).
"""
import json
import os
from pathlib import Path
import subprocess
import sys

from _checkout import incumbent, python

root = incumbent()
py = python(root)
env = {**os.environ, 'PYTHONPATH': str(root)}
done = subprocess.run([py, '-m', 'harness.episode', '--brain-root', os.environ['RSI_CANDIDATE'],
                       '--seed', os.environ.get('RSI_SEED', '1'), '--out', os.environ['RSI_OUT']], cwd=root, env=env)
if done.returncode:
    sys.exit(done.returncode)
result = json.loads((Path(os.environ['RSI_OUT']) / 'result.json').read_text())
m = result['metrics']
summary = (f"Episode {os.environ.get('RSI_LABEL', '?')} epoch {os.environ.get('RSI_EPOCH', '?')} seed {m['seed']}: "
           f"score {result['score']:.1f}, red {m['red_spm']}/min, green {m['green_spm']}/min, reached {m['reached']}, "
           f"next {m['next_goal']}. Top failures: {[f['text'] for f in result['failures'][:3]]}")
subprocess.run([py, 'scripts/memory.py', 'remember', 'result', summary[:3900], '--tag', f"seed{m['seed']}"],
               cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
