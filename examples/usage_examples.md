# Mythril MCP Server Usage Examples

This guide shows practical examples of using the Mythril MCP server with different clients.

## Example 1: Analyze a Smart Contract

Once you've configured an MCP client (like Claude Desktop or Cline), you can analyze smart contracts using natural language:

### Prompt to Client:
```
Please analyze this Solidity smart contract for security vulnerabilities:

pragma solidity ^0.8.0;

contract SimpleVulnerable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
}
```

### What Happens:
1. The MCP client sends a `call_tool` request to Mythril MCP server
2. The server invokes the `analyze_contract` tool
3. Mythril performs symbolic execution to find vulnerabilities
4. Results are returned to the client, which presents them to you

### Expected Output:
The analysis will identify the unprotected selfdestruct vulnerability (SWC-106).

## Example 2: Disassemble Bytecode

### Prompt to Client:
```
Can you disassemble this EVM bytecode?

0x608060405234801561001057600080fd5b50600080546001600160a01b0319163317905560d1806100316000396000f3fe
```

### What Happens:
The MCP server uses the `disassemble_contract` tool to convert the bytecode into human-readable assembly instructions.

## Example 3: List Available Detectors

### Prompt to Client:
```
What security detectors are available in Mythril?
```

### What Happens:
The MCP server calls `list_detectors` and returns information about all available security analysis modules.

## Example 4: Advanced Analysis with Parameters

### Prompt to Client:
```
Analyze this contract with increased depth for more thorough checking:

[paste contract code]

Use max_depth of 256 and execution_timeout of 7200 seconds.
```

### What Happens:
The MCP client passes additional parameters to the `analyze_contract` tool, allowing for more thorough analysis.

## Example 5: Analyze an On-Chain Contract

### Prompt to Client:
```
Analyze the smart contract at address 0x1234567890123456789012345678901234567890 
on Ethereum mainnet, including its onchain storage data.
```

### What Happens:
The MCP server fetches the contract from the blockchain and analyzes it with `enable_onchain_data` set to true.

## Testing Without a Client

You can test the MCP server manually using a simple Python script:

```python
import json
import subprocess

def test_mythril2_mcp():
    # Start the MCP server
    proc = subprocess.Popen(
        ["mythril2-mcp-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize request
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    proc.stdin.write(json.dumps(init_msg) + "\n")
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    print(json.loads(response))

if __name__ == "__main__":
    test_mythril2_mcp()
```

## Common Use Cases

### Security Audit Workflow
1. **Initial Scan**: "Analyze this contract for vulnerabilities"
2. **Deep Dive**: "Run a more thorough analysis with max_depth=256"
3. **Specific Issues**: "Check for reentrancy vulnerabilities specifically"

### Development Workflow
1. **Quick Check**: Analyze during development to catch issues early
2. **Pre-commit**: Use as part of your git pre-commit hooks
3. **CI/CD**: Integrate into continuous integration pipelines

### Learning and Research
1. **Understand Bytecode**: "Disassemble this bytecode to understand what it does"
2. **Compare Patterns**: Analyze similar contracts to identify patterns
3. **Detector Exploration**: "What detectors would catch this type of vulnerability?"

## Tips for Best Results

1. **Provide Context**: Include compiler version and any relevant information
2. **Be Specific**: If looking for specific vulnerability types, mention them
3. **Iterate**: Start with default settings, then adjust timeouts/depth as needed
4. **Review Results**: Always review the analysis results carefully

## Troubleshooting

### Analysis Takes Too Long
Try reducing `max_depth` or `execution_timeout`:
```
Analyze with max_depth=64 and timeout of 600 seconds
```

### Missing Dependencies
If you get errors about missing Solidity compiler:
```bash
pip install py-solc-x
```

### Connection Issues
Check that the MCP server is properly configured in your client's settings and that the `mythril2-mcp-server` command is in your PATH.
