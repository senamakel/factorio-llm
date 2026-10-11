"""Gate: the candidate's offline brain tests pass (the hive's own tests included).

Uses the frozen ``harness.gates`` from the incumbent to pick the test modules,
and runs them inside the candidate checkout with the shared virtualenv.
"""
import os
import subprocess
import sys

from _checkout import incumbent, python

root = incumbent()
sys.exit(subprocess.run([python(root), '-m', 'harness.gates', '--tests-only', os.environ['RSI_CANDIDATE']],
                        cwd=root, env={**os.environ, 'PYTHONPATH': str(root)}).returncode)
