"""Shared helpers for this loop's step scripts: locate the frozen checkout and its venv.

Steps run from tinyrsi's frozen copy of the loop folder with a minimal
environment. The frozen harness is taken from the incumbent checkout
(``$RSI_INCUMBENT``), which candidates can never change outside ``brain/`` and
tests; the Python interpreter is the primary checkout's ``.venv``.
"""
import os
from pathlib import Path
import subprocess


def incumbent():
    """Return the incumbent checkout path (falls back to the candidate for ``tinyrsi score``)."""
    return Path(os.environ.get('RSI_INCUMBENT') or os.environ['RSI_CANDIDATE']).resolve()


def python(checkout):
    """Return the shared virtualenv interpreter for any worktree of the repository."""
    common = subprocess.run(['git', '-C', str(checkout), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            capture_output=True, text=True, check=True).stdout.strip()
    interpreter = Path(common).parent / '.venv/bin/python'
    if not interpreter.exists():
        raise SystemExit(f'no virtualenv at {interpreter}; run ./factorio setup in the primary checkout')
    return str(interpreter)
