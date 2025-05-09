"""Main entry point for the kit MCP server."""
import sys
import logging
from .server import serve

def main():
    """Run the kit MCP server."""
    try:
        import asyncio
        asyncio.run(serve())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 