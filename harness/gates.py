"""Run the loop's acceptance gates on a checkout: honesty, then the offline brain tests.

Usage: ``python -m harness.gates [CHECKOUT] [--tests-only | --honesty-only]``
(``./factorio gates`` runs both on the current checkout). The test set is every
``scripts/test_brain*.py`` except the opt-in live suite, plus the fixed brain,
actuator and harness suites. Exit code 0 means the gates would pass.
"""
import argparse
from pathlib import Path
import subprocess
import sys

from harness import honesty

FIXED = ('test_actions', 'test_goal_score', 'test_research', 'test_navigation', 'test_blueprint',
         'test_timeouts', 'test_tree_search', 'test_actuator', 'test_harness')


def test_modules(checkout):
    """Return the unittest module names the green gate runs for ``checkout``."""
    scripts = Path(checkout) / 'scripts'
    names = sorted(p.stem for p in scripts.glob('test_brain*.py') if p.stem != 'test_brain_live')
    names += [n for n in FIXED if (scripts / f'{n}.py').exists()]
    return [f'scripts.{n}' for n in names]


def run_tests(checkout):
    """Run the green-gate unit tests inside ``checkout``; return the exit code."""
    return subprocess.run([sys.executable, '-m', 'unittest', *test_modules(checkout)], cwd=checkout,
                          env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(checkout), 'HOME': str(Path.home())}).returncode


def main(argv=None):
    """CLI: run the selected gates and exit non-zero on the first failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', nargs='?', default='.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tests-only', action='store_true')
    group.add_argument('--honesty-only', action='store_true')
    args = parser.parse_args(argv)
    checkout = Path(args.checkout).resolve()
    if not args.tests_only and honesty.main([str(checkout)]):
        return 1
    if not args.honesty_only:
        return run_tests(checkout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
