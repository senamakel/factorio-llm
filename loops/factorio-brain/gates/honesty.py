"""Gate: the candidate brain may reach the game only through the frozen actuator."""
import os
import subprocess
import sys

from _checkout import incumbent, python

root = incumbent()
sys.exit(subprocess.run([python(root), '-m', 'harness.gates', '--honesty-only', os.environ['RSI_CANDIDATE']], cwd=root,
                        env={**os.environ, 'PYTHONPATH': str(root)}).returncode)
