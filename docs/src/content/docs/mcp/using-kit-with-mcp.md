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

1. After installing `kit`, configure your MCP-compatible client by adding this to your settings:

```json
{
  "mcpServers": {
    "kit-mcp": {
      "command": "python3",
      "args": ["-m", "kit.mcp"],
      "env": {
        "KIT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

The MCP client will automatically run that command when it needs code-intelligence from **kit**—no manual server startup required.

## Troubleshooting – "spawn uvx ENOENT" (Claude Desktop / macOS)

On macOS, GUI applications such as **Claude Desktop** inherit a minimal `PATH` from
`launchd` (usually `/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin`).  Any extra
entries you add in *shell* startup files (`~/.zshrc`, `~/.bash_profile`, …) are
ignored, so an executable installed in `~/.cargo/bin` or a custom location will
not be visible.  When Claude tries to launch the server you may therefore see a
log like:

```
spawn uvx ENOENT
```

There are three ways to fix it—pick the one you prefer:

1. **Use an absolute path** (simplest)

   ```jsonc
   {
     "mcpServers": {
       "kit": {
         "command": "/Users/<you>/.cargo/bin/uvx",
         "args": ["kit-mcp"],
         "env": { "KIT_MCP_LOG_LEVEL": "INFO" }
       }
     }
   }
   ```

2. **Symlink `uvx` into a directory already on GUI `PATH`**

   ```bash
   ln -s ~/.cargo/bin/uvx /usr/local/bin/uvx   # may require sudo
   ```

3. **Inject a custom `PATH` via the `env` block**

   ```jsonc
   {
     "command": "uvx",
     "args": ["kit-mcp"],
     "env": {
       "PATH": "/Users/<you>/.cargo/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
       "KIT_MCP_LOG_LEVEL": "INFO"
     }
   }
   ```

After editing the config, **quit Claude Desktop completely and relaunch it** so
it reloads the configuration.  The server log should now show something like

```
[kit] [info] Server started and connected successfully
```

and no further `ENOENT` errors.

If you installed Kit with **uv**, you can wrap the same module invocation like

```jsonc
{
  "command": "uv",
  "args": ["run", "python", "-m", "kit.mcp"]
}
```

This avoids relying on a console-script shim and works regardless of where uv's
virtual environment lives.