# Mythril MCP Server - Quick Start Guide

Get up and running with Mythril's MCP server in 5 minutes!

## Installation

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/avaloki108/mythril2.0.git
cd mythril2.0

# Install Mythril with MCP support
pip install -e .

# Verify installation
mythril-mcp-server --help
```

## Configuration

### For Claude Desktop

1. **Find your config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add Mythril configuration:**
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

3. **Restart Claude Desktop**

### For Cline (VS Code)

1. Install the Cline extension in VS Code
2. Open Cline settings
3. Add to MCP settings:
   ```json
   {
     "mcpServers": {
       "mythril": {
         "command": "mythril-mcp-server"
       }
     }
   }
   ```
4. Reload VS Code

## Usage

Once configured, you can interact with Mythril through natural language!

### Example 1: Analyze a Contract

```
Analyze this Solidity contract for security vulnerabilities:

pragma solidity ^0.8.0;

contract Example {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
}
```

The AI will use Mythril to analyze the contract and report any vulnerabilities.

### Example 2: Disassemble Bytecode

```
What does this bytecode do?

0x608060405234801561001057600080fd5b50600080546001600160a01b0319163317905560d1806100316000396000f3fe
```

The AI will disassemble it into readable assembly.

### Example 3: List Detectors

```
What security detectors are available in Mythril?
```

The AI will list all available security analysis modules.

## What You Get

✨ **Smart Contract Analysis**
- Detects 20+ types of vulnerabilities
- Reentrancy, integer overflow, unprotected functions, and more
- Works with Solidity source code or EVM bytecode

🔍 **Bytecode Disassembly**
- Convert bytecode to readable assembly
- Understand what contracts really do

📋 **Security Insights**
- Detailed vulnerability reports
- Severity classifications
- Remediation guidance

## Advanced Usage

### Custom Analysis Parameters

```
Analyze this contract with deeper analysis:
- max_depth: 256
- execution_timeout: 3600
- strategy: bfs

[paste contract code]
```

### Analyze On-Chain Contracts

```
Analyze the contract at address 0x1234...5678 on Ethereum mainnet
```

## Troubleshooting

### Server Not Found

If the command isn't found, use the full path:

```bash
# Find the path
which mythril-mcp-server

# Use in config
{
  "command": "/full/path/to/mythril-mcp-server"
}
```

### Analysis Timeout

If analysis is taking too long, try:
- Reduce max_depth (e.g., 64 or 128)
- Increase timeout
- Simplify the contract

### Permission Denied

On Unix systems:
```bash
chmod +x $(which mythril-mcp-server)
```

## Next Steps

- 📖 Read [README-MCP.md](README-MCP.md) for detailed documentation
- 📚 Check [MCP_INTEGRATION.md](MCP_INTEGRATION.md) for comprehensive guide
- 💡 Explore [examples/](examples/) for more configurations
- 🧪 Try the examples in [examples/usage_examples.md](examples/usage_examples.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/avaloki108/mythril2.0/issues)
- **Discord**: Join ConsenSys Discord
- **Docs**: [Mythril Documentation](https://mythril-classic.readthedocs.io/)

## License

MIT License - See [LICENSE](LICENSE) file

---

**Ready to analyze some smart contracts? Start asking your AI assistant! 🚀**
