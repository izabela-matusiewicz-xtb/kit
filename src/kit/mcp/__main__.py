from __future__ import annotations

"""Module entry-point for ``python -m kit.mcp``.

This wrapper simply delegates to :pyfunc:`kit.mcp.main.main`. It exists so
that users and MCP clients can start the server without relying on the
``kit-mcp`` console script being on ``$PATH``.
"""

from .main import main

if __name__ == "__main__":
    main() 