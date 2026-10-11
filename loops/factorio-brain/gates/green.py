"""Gate: the candidate's offline brain tests pass (the hive's own tests included).

Runs every ``scripts/test_brain*.py`` plus the fixed brain, actuator and harness
suites inside the candidate checkout with the shared virtualenv.
"""
import os
from pathlib import Path
import subprocess
import sys

from _checkout import python

candidate = Path(os.environ['RSI_CANDIDATE'])
modules = sorted(f'scripts.{p.stem}' for p in (candidate / 'scripts').glob('test_brain*.py') if p.stem != 'test_brain_live')
modules += ['scripts.test_actions', 'scripts.test_goal_score', 'scripts.test_research', 'scripts.test_navigation',
            'scripts.test_blueprint', 'scripts.test_timeouts', 'scripts.test_tree_search', 'scripts.test_actuator',
            'scripts.test_harness']
modules = [m for m in modules if (candidate / (m.replace('.', '/') + '.py')).exists()]
sys.exit(subprocess.run([python(candidate), '-m', 'unittest', *modules], cwd=candidate,
                        env={**os.environ, 'PYTHONPATH': str(candidate)}).returncode)
