# Scripts

`factorio.py` manages the local server and client. `mcp_config.py` reads the root
`mcp.json`, resolves checkout-relative paths, exports client configuration, and
registers every configured server. `mcp_entrypoint.py` starts the stdio bridge.

Run `./factorio mcp-config --format json` for portable absolute launch paths,
or `./factorio register` to register both game control and wiki access.
Run `./factorio check` for offline and live checks. The `test_*.py` modules cover
setup, RCON transport, tool encoding, brain decisions and SQLite persistence.
