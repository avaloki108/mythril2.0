# Mythril MCP Server

This directory contains the MCP (Model Context Protocol) server implementation for Mythril, allowing clients to interact with Mythril's security analysis capabilities through the standardized MCP protocol.

## What is MCP?

MCP (Model Context Protocol) is an open protocol that standardizes how applications provide context to LLMs. It allows AI assistants and other clients to access tools and resources through a uniform interface.

## Installation

1. Install Mythril with MCP support:

```bash
pip install -e .
```

This will install all dependencies including the `mcp` package and make the `mythril-mcp-server` command available.

## Running the Server

The MCP server runs locally and communicates via stdio (standard input/output). To start the server:

```bash
mythril-mcp-server
```

The server will start and listen for MCP protocol messages on stdin, responding on stdout.

## Configuration for MCP Clients

To use the Mythril MCP server with MCP-compatible clients (like Claude Desktop, Cline, etc.), add it to your MCP client configuration.

### Example: Claude Desktop Configuration

Add this to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mythril": {
      "command": "mythril-mcp-server",
      "args": []
    }
  }
}
```

### Example: Cline Configuration

In VS Code with Cline extension, add to your MCP settings:

```json
{
  "mythril": {
    "command": "mythril-mcp-server"
  }
}
```

## Available Tools

The Mythril MCP server exposes the following tools:

### 1. analyze_contract

Analyzes a Solidity smart contract for security vulnerabilities.

**Parameters:**
- `contract_code` (string, optional): Solidity source code or bytecode to analyze
- `contract_address` (string, optional): Blockchain address to analyze (alternative to contract_code)
- `solc_version` (string, optional): Solidity compiler version (e.g., '0.8.0')
- `max_depth` (integer, optional): Maximum recursion depth for symbolic execution (default: 128)
- `execution_timeout` (integer, optional): Execution timeout in seconds (default: 86400)
- `strategy` (string, optional): Search strategy: 'dfs' or 'bfs' (default: 'dfs')
- `enable_onchain_data` (boolean, optional): Enable fetching onchain storage data (default: false)

**Example:**
```json
{
  "contract_code": "pragma solidity ^0.8.0; contract Test { ... }"
}
```

### 2. disassemble_contract

Disassembles EVM bytecode into readable assembly instructions.

**Parameters:**
- `contract_code` (string, optional): Solidity source code or bytecode to disassemble
- `contract_address` (string, optional): Blockchain address to disassemble

**Example:**
```json
{
  "contract_code": "0x6060604052..."
}
```

### 3. list_detectors

Lists all available security detection modules in Mythril.

**Parameters:** None

## Usage Examples

Once configured with an MCP client, you can use natural language to interact with Mythril:

- "Analyze this smart contract for security vulnerabilities: [paste contract code]"
- "Disassemble this bytecode: 0x6060604052..."
- "What security detectors are available in Mythril?"

## Architecture

The MCP server:
1. Listens for JSON-RPC requests on stdin
2. Processes requests using Mythril's core analysis engine
3. Returns results via stdout in MCP protocol format
4. Logs diagnostic information to stderr

## Troubleshooting

### Server doesn't start

Make sure you've installed the package:
```bash
pip install -e .
```

### MCP client can't connect

Verify that:
1. The `mythril-mcp-server` command is in your PATH
2. Your MCP client configuration uses the correct command
3. Check stderr output for error messages

### Analysis fails

Common issues:
- Missing Solidity compiler: Install with `pip install py-solc-x`
- Invalid contract code: Ensure the code is valid Solidity or bytecode
- Timeout issues: Increase `execution_timeout` parameter

## Development

To modify the MCP server:

1. Edit `/home/runner/work/mythril2.0/mythril2.0/mythril/mcp_server.py`
2. Test your changes:
   ```bash
   python -m mythril.mcp_server
   ```

## Protocol Compliance

This server implements MCP protocol version 1.0 and supports:
- Tool listing and invocation
- Stdio transport
- Standard error handling

## Security Considerations

- The MCP server runs locally on your machine
- It has access to your local filesystem for reading contract files
- When `enable_onchain_data` is true, it will connect to Ethereum nodes
- All communication happens via local stdio (no network exposure)

## Contributing

Contributions are welcome! Please see the main [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
