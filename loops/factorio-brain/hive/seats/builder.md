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
5. Run the gates yourself before replying: `./factorio gates` (honesty check +
   every offline brain test, exactly what the loop runs). Fix until it passes.
6. Optional live check (about 4 minutes): `./factorio episode --brain-root . --seed 7 --wall-secs 120 --window-min 1`
   prints the milestones reached and the brain's failures on a throwaway world.
7. Reply to the orchestrator with: files changed, the test you added, gate
   results, and anything you could not do.
