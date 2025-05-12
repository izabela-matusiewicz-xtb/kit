---
title: Using kit with MCP
description: Learn how to use kit with the Model Context Protocol (MCP) for AI-powered code understanding
---

The Model Context Protocol (MCP) provides a unified API for codebase operations, making it easy to integrate kit's capabilities with AI tools and IDEs. This guide will help you set up and use kit with MCP.

Kit provides a MCP server implementation that exposes its code intelligence capabilities through a standardized protocol. When using kit as an MCP server, you gain access to:

- **Code Search**: Perform text-based and semantic code searches
- **Code Analysis**: Extract symbols, find symbol usages, and analyze dependencies
- **Code Summarization**: Create natural language summaries of code
- **File Navigation**: Explore file trees and repository structure


## Setup

1. After installing `kit`, configure your MCP-compatible client by adding a stanza like this to your settings:

Available environment variables for the `env` section:
- `OPENAI_API_KEY`
- `KIT_MCP_LOG_LEVEL`

```json
{
  "mcpServers": {
    "kit-mcp": {
      "command": "python",
      "args": ["-m", "kit.mcp"],
      "env": {
        "KIT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

The `python` executable invoked must be the one where `cased-kit` is installed.
If you see `ModuleNotFoundError: No module named 'kit'`, ensure the Python
interpreter your MCP client is using is the correct one.