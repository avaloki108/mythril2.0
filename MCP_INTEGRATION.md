# Mythril MCP Integration Guide

This document provides a comprehensive guide for integrating and using Mythril as an MCP (Model Context Protocol) server.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Available Tools](#available-tools)
5. [Client Configuration](#client-configuration)
6. [Usage Examples](#usage-examples)
7. [Advanced Topics](#advanced-topics)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)

## Overview

Mythril now includes native MCP server support, allowing AI assistants and other MCP-compatible applications to leverage Mythril's security analysis capabilities through a standardized protocol.

### What is MCP?

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It enables:

- **Standardized Integration**: One implementation works with all MCP-compatible clients
- **Tool Discovery**: Clients can query available capabilities
- **Type Safety**: Structured tool definitions with JSON schemas
- **Error Handling**: Standardized error reporting

### Why MCP for Mythril?

- **AI-Powered Analysis**: Let AI assistants help analyze smart contracts
- **Interactive Security Audits**: Conversational interface to security tools
- **Workflow Integration**: Use Mythril within your existing AI-assisted workflows
- **Educational**: Learn about smart contract security through natural language

## Quick Start

### Installation

```bash
# Install Mythril with MCP support
pip install -e .

# Verify installation
mythril-mcp-server --help
```

### Basic Configuration

For **Claude Desktop**, add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mythril": {
      "command": "mythril-mcp-server"
    }
  }
}
```

### First Analysis

After configuration, simply ask your AI assistant:

```
Analyze this smart contract for vulnerabilities:

pragma solidity ^0.8.0;
contract Test {
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
}
```

## Architecture

### System Components

```
┌─────────────────┐
│  MCP Client     │  (Claude Desktop, Cline, etc.)
│  (AI Assistant) │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC over stdio)
         │
┌────────▼────────┐
│  Mythril MCP    │
│  Server         │
└────────┬────────┘
         │
┌────────▼────────┐
│  Mythril Core   │  (Analysis Engine)
│  - Symbolic     │
│    Execution    │
│  - Detectors    │
│  - Disassembler │
└─────────────────┘
```

### Communication Flow

1. **Client Request**: MCP client sends tool call via stdio
2. **Server Processing**: MCP server validates and routes request
3. **Analysis Execution**: Mythril engine performs security analysis
4. **Result Formatting**: Results formatted per MCP protocol
5. **Client Response**: Results sent back to client

### Protocol Transport

The server uses **stdio transport**:
- **stdin**: Receives JSON-RPC requests
- **stdout**: Sends JSON-RPC responses
- **stderr**: Logs diagnostic information

## Available Tools

### 1. analyze_contract

Performs comprehensive security analysis on smart contracts.

**Input Schema:**
```json
{
  "contract_code": "string (optional)",
  "contract_address": "string (optional)",
  "solc_version": "string (optional)",
  "max_depth": "integer (optional, default: 128)",
  "execution_timeout": "integer (optional, default: 86400)",
  "strategy": "string (optional, default: 'dfs')",
  "enable_onchain_data": "boolean (optional, default: false)"
}
```

**Output:** Text report with identified vulnerabilities

**Example:**
```json
{
  "contract_code": "pragma solidity ^0.8.0; ...",
  "max_depth": 256,
  "strategy": "bfs"
}
```

### 2. disassemble_contract

Converts EVM bytecode into human-readable assembly.

**Input Schema:**
```json
{
  "contract_code": "string (optional)",
  "contract_address": "string (optional)"
}
```

**Output:** EVM assembly listing

**Example:**
```json
{
  "contract_code": "0x608060405234801561001057600080fd5b50..."
}
```

### 3. list_detectors

Lists all available security detection modules.

**Input Schema:**
```json
{}
```

**Output:** List of detector modules with descriptions

## Client Configuration

### Claude Desktop

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration:**
```json
{
  "mcpServers": {
    "mythril": {
      "command": "mythril-mcp-server",
      "args": [],
      "env": {
        "MYTHRIL_DIR": "/custom/path"
      }
    }
  }
}
```

### Cline (VS Code Extension)

1. Install Cline extension in VS Code
2. Open Cline settings
3. Add MCP server configuration:

```json
{
  "mcpServers": {
    "mythril": {
      "command": "mythril-mcp-server"
    }
  }
}
```

### Custom MCP Client

For custom integrations:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_mythril():
    server_params = StdioServerParameters(
        command="mythril-mcp-server",
        args=[]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call analyze_contract tool
            result = await session.call_tool(
                "analyze_contract",
                arguments={"contract_code": "..."}
            )
            print(result)
```

## Usage Examples

### Example 1: Basic Vulnerability Scan

**User:** "Analyze this contract for security issues"

**AI Response:** Calls `analyze_contract` tool and presents findings in natural language.

### Example 2: Focused Analysis

**User:** "Check this contract specifically for reentrancy vulnerabilities, use a depth of 256"

**AI Response:** Adjusts parameters and provides targeted analysis.

### Example 3: Bytecode Understanding

**User:** "What does this bytecode do? 0x6080604052..."

**AI Response:** Uses `disassemble_contract` to explain the code.

### Example 4: Learning

**User:** "What types of vulnerabilities can Mythril detect?"

**AI Response:** Uses `list_detectors` to enumerate capabilities.

## Advanced Topics

### Custom Analysis Parameters

Control analysis behavior through tool parameters:

```json
{
  "contract_code": "...",
  "max_depth": 256,           // Deeper analysis
  "execution_timeout": 3600,  // 1 hour timeout
  "strategy": "bfs",          // Breadth-first search
  "enable_onchain_data": true // Use blockchain data
}
```

### Performance Tuning

**For Quick Scans:**
- `max_depth`: 64-128
- `execution_timeout`: 300-600

**For Thorough Analysis:**
- `max_depth`: 256-512
- `execution_timeout`: 3600-7200

### Security Considerations

1. **Local Execution**: Server runs locally, no data sent to external services
2. **Blockchain Access**: When `enable_onchain_data` is true, connects to Ethereum nodes
3. **Resource Usage**: Analysis can be CPU-intensive
4. **File Access**: Server reads contract files from local filesystem

### Integration with CI/CD

```yaml
# GitHub Actions example
- name: Security Analysis via MCP
  run: |
    pip install mythril
    echo "$CONTRACT_CODE" | mythril-mcp-server
```

## Troubleshooting

### Server Won't Start

**Problem:** Command not found

**Solution:**
```bash
# Find installation path
which mythril-mcp-server

# Use full path in config
{
  "command": "/home/user/.local/bin/mythril-mcp-server"
}
```

### Analysis Timeout

**Problem:** Analysis takes too long

**Solution:**
- Reduce `max_depth`
- Increase `execution_timeout`
- Simplify contract or analyze specific functions

### Memory Issues

**Problem:** Out of memory during analysis

**Solution:**
- Reduce `max_depth`
- Analyze contracts in smaller pieces
- Increase system memory

### Connection Issues

**Problem:** MCP client can't connect

**Solution:**
1. Verify server starts: `mythril-mcp-server`
2. Check client logs for error messages
3. Verify PATH includes mythril installation
4. Try absolute path to executable

### Missing Dependencies

**Problem:** Module not found errors

**Solution:**
```bash
# Install all dependencies
pip install -e .

# Install specific missing module
pip install py-solc-x
```

## Development

### Running Tests

```bash
# Run MCP server tests
pytest tests/mcp_server_test.py -v

# Test all Mythril functionality
pytest tests/
```

### Modifying the Server

Main files:
- `mythril/mcp_server.py`: Server implementation
- `tests/mcp_server_test.py`: Integration tests
- `examples/`: Configuration examples

### Adding New Tools

1. Define tool in `list_tools()`:
```python
Tool(
    name="new_tool",
    description="...",
    inputSchema={...}
)
```

2. Implement handler in `call_tool()`:
```python
elif name == "new_tool":
    return await new_tool_handler(arguments)
```

3. Add tests:
```python
@pytest.mark.asyncio
async def test_new_tool():
    result = await new_tool_handler({})
    assert result is not None
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check stderr output:
```bash
mythril-mcp-server 2>debug.log
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Mythril Documentation](https://mythril-classic.readthedocs.io/)
- [Example Configurations](examples/)
- [Usage Examples](examples/usage_examples.md)

## Support

- GitHub Issues: Report bugs or request features
- Discord: Join ConsenSys Discord for community support
- Documentation: See README-MCP.md for additional information

## License

MIT License - See LICENSE file for details.
