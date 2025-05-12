---
title: Using kit with MCP
description: Learn how to use kit with the Model Context Protocol (MCP) for AI-powered code understanding
---

# Using kit with MCP

The Model Context Protocol (MCP) provides a unified API for codebase operations, making it easy to integrate kit's capabilities with AI tools and IDEs. This guide will help you set up and use kit with MCP.

## Overview

Kit provides a MCP server implementation that exposes its code intelligence capabilities through a standardized protocol. This allows any MCP-compatible tool to leverage kit's advanced code understanding features.

When using kit as an MCP server, you gain access to:

- **Code Search**: Perform text-based and semantic code searches
- **Code Analysis**: Extract symbols, find symbol usages, and analyze dependencies
- **Code Summarization**: Create natural language summaries of code
- **File Navigation**: Explore file trees and repository structure


## Setup

1. Install kit with MCP support:

```bash
pip install cased-kit
```

This will make `kit-mcp` available to you.

2. Configure your MCP-compatible client by adding this to your settings:

```json
{
  "mcpServers": {
    "kit-mcp": {
      "command": "kit-mcp",
      "env": {
        "KIT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```
