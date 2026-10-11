# Action library

Each public action lives in its own file. Import actions from `brain.actions`.
Planners return decisions and bounded primitive instructions; `brain/execution.py`
executes them. Planning has no game side effects. Gathering actions carry batch
counts so the executor can estimate native mining duration.

Verify with `.venv/bin/python -m unittest scripts.test_actions scripts.test_brain`.
