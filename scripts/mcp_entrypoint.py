#!/usr/bin/env python
"""Standalone MCP entrypoint: makes mcp_server importable regardless of cwd."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from mcp_server.server import mcp
mcp.run()
