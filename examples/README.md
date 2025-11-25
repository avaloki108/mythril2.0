# Mythril MCP Server Configuration Examples

This directory contains example configuration files for popular MCP clients.

## Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Copy the contents from `claude_desktop_config.json` and merge it into your configuration file.

3. Restart Claude Desktop.

## Cline (VS Code Extension)

1. Open VS Code with the Cline extension installed.

2. Go to Cline settings (Settings → Extensions → Cline).

3. In the "MCP Settings" section, add the configuration from `cline_mcp_settings.json`.

4. Reload VS Code or restart Cline.

## Generic MCP Client

For any MCP-compatible client, you can use the following basic configuration:

```json
{
  "command": "mythril-mcp-server",
  "args": []
}
```

## Testing the Connection

Once configured, you can test the Mythril MCP server by asking your AI assistant:

- "What tools does Mythril provide?"
- "Can you analyze this smart contract for vulnerabilities?"
- "List the available security detectors in Mythril"

## Environment Variables

If you need to customize the Mythril environment, you can add environment variables:

```json
{
  "mcpServers": {
    "mythril": {
      "command": "mythril-mcp-server",
      "args": [],
      "env": {
        "MYTHRIL_DIR": "/path/to/custom/mythril/dir",
        "SOLC_VERSION": "0.8.0"
      }
    }
  }
}
```

## Troubleshooting

### Server Not Found

If the client can't find `mythril-mcp-server`, specify the full path:

```json
{
  "command": "/usr/local/bin/mythril-mcp-server"
}
```

To find the path, run:
```bash
which mythril-mcp-server
```

### Permission Issues

On Unix-like systems, ensure the script is executable:
```bash
chmod +x $(which mythril-mcp-server)
```

### Check Server Logs

MCP servers log to stderr. Check your MCP client's log directory for error messages.

## Advanced Configuration

### Custom Analysis Timeout

While the MCP server uses default timeouts, you can request different values through tool parameters:

```json
{
  "contract_code": "...",
  "execution_timeout": 3600,
  "max_depth": 256
}
```

### Enable Onchain Data

To analyze contracts with onchain storage data, set `enable_onchain_data` to true:

```json
{
  "contract_address": "0x...",
  "enable_onchain_data": true
}
```

Note: This requires a valid Ethereum node connection (Infura, Alchemy, etc.).
