---
title: Using kit with MCP
description: Learn how to use kit with the Model Context Protocol (MCP) for AI-powered code understanding
---

# Using kit with MCP

The Model Context Protocol (MCP) provides a unified API for codebase operations, making it easy to integrate kit's capabilities with AI tools and IDEs. This guide will help you set up and use kit with MCP.

## Overview

MCP enables AI tools to understand and interact with your codebase through a local server. It provides several key capabilities:

- **Code Summaries**: Generate natural language summaries of files, functions, and classes
- **Symbol Information**: Extract and track functions, classes, and other code constructs
- **Code Search**: Find specific code patterns or text across your codebase
- **File Navigation**: Explore and understand your codebase structure

## Setup

1. Configure your IDE (Cursor or Windsurf) by adding this to your settings:

```json
{
  "mcpServers": {
    "kit": {
      "command": "/path/to/your/venv/bin/kit-mcp",
      "args": []
    }
  }
}
```

Replace `/path/to/your/venv/bin/kit-mcp` with the actual path to your kit-mcp executable. For example, if you're using a virtual environment in your project directory:

```json
{
  "mcpServers": {
    "kit": {
      "command": "/Users/username/project/.venv/bin/kit-mcp",
      "args": []
    }
  }
}
```




## Requirements

- Python 3.9 or higher
- MCP version 1.8.0 or higher
- An OpenAI API key (for code summarization features)

## Next Steps

- Learn about [Code Summaries](/docs/features/code-summaries)
- Explore [Symbol Extraction](/docs/features/symbol-extraction)
- Check out [Dependency Analysis](/docs/features/dependency-analysis)