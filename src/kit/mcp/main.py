"""Console-script entry point for the Kit MCP server."""

from __future__ import annotations

import logging
import sys
import asyncio

from .server import serve


def main() -> None:  # noqa: D401
    """Launch the Kit MCP server."""
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:  # pragma: no cover
        logging.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 