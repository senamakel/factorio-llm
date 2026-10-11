You implement the orchestrator's assignment in your candidate checkout (the
current directory). Only `brain/` and `scripts/test_brain*.py` (plus the legacy
brain tests named in the rules) may change.

1. Read the relevant brain modules and `actuator/actions.py` / `actuator/queries.py`
   (the only way to touch the game; read their docstrings for reach, inventory
   and timing rules).
2. Check facts in `knowledge/prototypes.json` (exact recipes, technologies with
   triggers/prerequisites, entity sizes and speeds) and `knowledge/wiki/*.md`.
3. Make the smallest change that carries out the assignment. Keep the brain
   deterministic and dependency-free.
4. Add or update a unit test in `scripts/test_brain_*.py` that pins the behaviour.
5. Run the gates yourself before replying:
   `.venv/bin/python -m unittest discover -s scripts -p 'test_brain*.py'` is not
   available in worktrees, so use `./factorio brain --help` to confirm the CLI
   imports, then `python3 ../../loops/factorio-brain/gates/green.py` is NOT
   reachable either. Instead run:
   `$(git rev-parse --path-format=absolute --git-common-dir | sed 's#/.git$##')/.venv/bin/python -m unittest scripts.test_brain scripts.test_brain_actions scripts.test_research scripts.test_actuator scripts.test_harness`
   and `... -m harness.honesty .` with the same interpreter.
6. Optional live check (about 4 minutes): `./factorio episode --brain-root . --seed 7 --wall-secs 120 --window-min 1`
   prints the milestones reached and the brain's failures on a throwaway world.
7. Reply to the orchestrator with: files changed, the test you added, gate
   results, and anything you could not do.
