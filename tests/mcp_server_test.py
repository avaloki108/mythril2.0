#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration tests for Mythril MCP server."""

import pytest


def test_mcp_server_import():
    """Test that the MCP server module can be imported."""
    try:
        import mythril.mcp_server
        assert hasattr(mythril.mcp_server, 'app')
        assert hasattr(mythril.mcp_server, 'main')
    except ImportError as e:
        pytest.fail(f"Failed to import MCP server: {e}")


def test_mcp_server_tools():
    """Test that the MCP server defines expected tools."""
    import mythril.mcp_server
    
    # The server should have decorated functions for tools
    assert hasattr(mythril.mcp_server.app, 'list_tools')
    assert hasattr(mythril.mcp_server.app, 'call_tool')


def test_create_default_args():
    """Test default argument creation."""
    from mythril.mcp_server import create_default_args
    
    args = create_default_args()
    
    # Check essential attributes
    assert hasattr(args, 'execution_timeout')
    assert hasattr(args, 'max_depth')
    assert hasattr(args, 'no_onchain_data')
    assert args.execution_timeout > 0
    assert args.max_depth > 0


@pytest.mark.asyncio
async def test_list_tools_function():
    """Test the list_tools function returns expected tools."""
    from mythril.mcp_server import list_tools
    
    tools = await list_tools()
    
    # Should return a list of Tool objects
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # Check for expected tools
    tool_names = [tool.name for tool in tools]
    assert "analyze_contract" in tool_names
    assert "disassemble_contract" in tool_names
    assert "list_detectors" in tool_names


@pytest.mark.asyncio
async def test_list_detectors_tool():
    """Test the list_detectors tool."""
    from mythril.mcp_server import list_detectors_tool
    
    result = await list_detectors_tool({})
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert hasattr(result[0], 'type')
    assert result[0].type == "text"
