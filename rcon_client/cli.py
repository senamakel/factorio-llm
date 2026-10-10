"""CLI: python -m rcon_client.cli '<command>'"""
import argparse
import json
import os
import sys

from .client import RconClient


def config_from_env_or_args(host, port, password):
    return (
        host or os.environ.get("FACTORIO_HOST", "127.0.0.1"),
        int(port or os.environ.get("FACTORIO_PORT", 27015)),
        password or os.environ.get("FACTORIO_RCON_PASSWORD", ""),
    )


def main(argv=None):
    p = argparse.ArgumentParser(description="Send a command to a Factorio server via RCON")
    p.add_argument("command", help="e.g. '/c game.print(game.tick)'")
    p.add_argument("--host")
    p.add_argument("--port")
    p.add_argument("--password")
    args = p.parse_args(argv)
    host, port, password = config_from_env_or_args(args.host, args.port, args.password)
    try:
        with RconClient(host, port, password) as c:
            print(c.command(args.command))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
