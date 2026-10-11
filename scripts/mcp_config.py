"""Load the shared MCP manifest and resolve checkout-relative launch paths."""
import json


def load_servers(root):
    """Return server entries with absolute local paths; invalid JSON raises ValueError."""
    servers = json.loads((root / "mcp.json").read_text())["mcpServers"]
    for server in servers.values():
        if server["command"].startswith("./"):
            server["command"] = str(root / server["command"][2:])
        server["args"] = [str(root / arg[2:]) if arg.startswith("./") else arg
                          for arg in server.get("args", [])]
        server["env"] = {key: str(root / value[2:]) if value.startswith("./") else value
                         for key, value in server.get("env", {}).items()}
    return servers


def print_config(root, format_name):
    """Print all servers as JSON or client TOML, resolving paths against root."""
    servers = load_servers(root)
    if format_name == "json":
        print(json.dumps({"mcpServers": servers}, indent=2))
        return
    for name, server in servers.items():
        if format_name == "codex":
            print(f"[mcp_servers.{name}]")
        else:
            print('[[mcp_client.servers]]')
            print('name = ' + json.dumps(name))
            print('working_dir = ' + json.dumps(str(root)))
        print('command = ' + json.dumps(server['command']))
        print('args = ' + json.dumps(server['args']))
        if server['env']:
            values = ', '.join(f'{key} = {json.dumps(value)}' for key, value in server['env'].items())
            print('env = { ' + values + ' }')
        print()


def register_servers(root):
    """Register manifest entries in Codex; stop and return the first failed exit code."""
    import subprocess
    for name, server in load_servers(root).items():
        command = ['codex', 'mcp', 'add', name]
        for key, value in server['env'].items():
            command.extend(['--env', f'{key}={value}'])
        result = subprocess.run(command + ['--', server['command'], *server['args']])
        if result.returncode:
            return result.returncode
    return 0
