"""Static honesty check: the brain may reach the game only through ``actuator``.

The actuator enforces reach, inventory costs and real crafting time, but Python
could bypass it by opening its own RCON socket, spawning a process that does,
or importing the transport directly. This check walks every ``.py`` file under
``brain/`` and rejects those routes. Usage::

    python -m harness.honesty PATH/TO/CHECKOUT

Exit 0 when clean; otherwise prints one violation per line and exits 1.
"""
import ast
from pathlib import Path
import sys

FORBIDDEN_MODULES = {
    'socket', 'ssl', 'socketserver', 'http', 'urllib', 'urllib3', 'requests', 'httpx', 'aiohttp',
    'subprocess', 'multiprocessing', 'asyncio', 'ctypes', 'cffi', 'importlib', 'runpy', 'pty', 'telnetlib',
    'rcon_client', 'mcp', 'mcp_server', 'harness', 'actuator.rpc', 'scripts',
}
FORBIDDEN_CALLS = {'exec', 'eval', 'compile', '__import__', 'breakpoint'}
FORBIDDEN_ATTRS = {('os', 'system'), ('os', 'popen'), ('os', 'fork'), ('os', 'forkpty'), ('os', 'execv'),
                   ('os', 'execve'), ('os', 'execl'), ('os', 'execvp'), ('os', 'spawnl'), ('os', 'spawnv'),
                   ('os', 'posix_spawn'), ('os', 'kill'), ('os', 'killpg')}
FORBIDDEN_TEXT = ('rcon-password', 'connection.json', 'FACTORIO_RCON_PASSWORD')


def _module_blocked(name):
    return any(name == m or name.startswith(m + '.') for m in FORBIDDEN_MODULES)


def violations_in(source, path='<string>'):
    """Return human-readable violations for one Python source string."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f'{path}:{exc.lineno}: syntax error: {exc.msg}']
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [f'{path}:{node.lineno}: imports {a.name}' for a in node.names if _module_blocked(a.name)]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module] + [f'{node.module}.{a.name}' for a in node.names]
            if any(_module_blocked(n) for n in names):
                found.append(f'{path}:{node.lineno}: imports from {node.module}')
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_CALLS:
                found.append(f'{path}:{node.lineno}: calls {func.id}()')
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and \
                    (func.value.id, func.attr) in FORBIDDEN_ATTRS:
                found.append(f'{path}:{node.lineno}: calls {func.value.id}.{func.attr}()')
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            found += [f'{path}:{node.lineno}: mentions {t!r}' for t in FORBIDDEN_TEXT if t in node.value]
    return found


def check(checkout):
    """Scan ``checkout/brain`` and return every violation (empty list when honest)."""
    brain = Path(checkout) / 'brain'
    if not brain.is_dir():
        return [f'{brain}: missing brain package']
    found = []
    for path in sorted(brain.rglob('*.py')):
        found += violations_in(path.read_text(errors='replace'), path.relative_to(checkout))
    return found


def main(argv=None):
    """CLI: print violations, exit 1 if any."""
    argv = sys.argv[1:] if argv is None else argv
    found = check(argv[0] if argv else '.')
    for line in found:
        print(line)
    if found:
        print(f'honesty gate: {len(found)} violation(s); the brain must use only actuator.actions/queries',
              file=sys.stderr)
        return 1
    print('honesty gate: clean')
    return 0


if __name__ == '__main__':
    sys.exit(main())
