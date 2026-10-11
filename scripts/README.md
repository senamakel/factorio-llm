# Scripts

`factorio.py` manages the local server and client. `mcp_config.py` reads the root
`mcp.json`, resolves checkout-relative paths, exports client configuration, and
registers every configured server. `mcp_entrypoint.py` starts the stdio bridge.

Run `./factorio mcp-config --format json` for portable absolute launch paths,
or `./factorio register` to register both game control and wiki access.
Run `./factorio check` for offline and live checks. The `test_*.py` modules cover
setup, RCON transport, tool encoding, brain decisions and SQLite persistence.
Root `brain/runner.py` runs the assistant through Python observation/action modules with
short Lua API adapters over RCON. No Lua script files are uploaded.
`test_goal_brain/score.py` covers the 100-plate objective and reward components;
`test_brain/execution.py` checks Python movement planning.
`test_brain_live.py` verifies continuous walking, explicit stopping and real mining
on disposable surfaces. Run it with `FACTORIO_LIVE_TESTS=1` and the appropriate
`FACTORIO_CONNECTION_FILE`: `.venv/bin/python -m unittest scripts.test_brain_live`.
