#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP Server for Mythril - Security analysis tool for Ethereum smart contracts.

This module implements an MCP (Model Context Protocol) server that exposes
Mythril's security analysis capabilities to MCP clients.
"""

import json
import logging
import sys
from argparse import Namespace
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from mythril.analysis.report import Report
from mythril.exceptions import CriticalError, DetectorNotFoundError
from mythril.mythril import MythrilAnalyzer, MythrilConfig, MythrilDisassembler

log = logging.getLogger(__name__)

# Initialize MCP server
app = Server("mythril-mcp-server")


def create_default_args() -> Namespace:
    """Create default arguments for Mythril analysis."""
    args = Namespace()
    
    # Analysis arguments
    args.execution_timeout = 86400
    args.create_timeout = 10
    args.max_depth = 128
    args.solver_timeout = 10000
    args.loop_bound = 3
    args.transaction_sequences = []
    args.modules = []
    args.custom_modules_directory = None
    args.pruning_factor = None
    args.solver_log = None
    args.parallel_solving = False
    args.unconstrained_storage = False
    args.call_depth_limit = 3
    args.disable_iprof = True
    args.disable_coverage_strategy = False
    args.disable_mutation_pruner = False
    args.enable_summaries = False
    args.enable_state_merging = False
    args.disable_dependency_pruning = False
    args.no_onchain_data = True
    
    # RPC arguments
    args.rpc = None
    args.rpctls = False
    args.infura_id = None
    
    # Output arguments
    args.outform = "text"
    args.verbose_report = True
    
    return args


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Mythril MCP tools."""
    return [
        Tool(
            name="analyze_contract",
            description=(
                "Analyze a Solidity smart contract for security vulnerabilities. "
                "Detects issues like reentrancy, integer overflows, unprotected functions, etc. "
                "Accepts either Solidity source code or bytecode."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_code": {
                        "type": "string",
                        "description": "Solidity source code or bytecode to analyze"
                    },
                    "contract_address": {
                        "type": "string",
                        "description": "Blockchain address to analyze (alternative to contract_code)"
                    },
                    "solc_version": {
                        "type": "string",
                        "description": "Solidity compiler version (e.g., '0.8.0')"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum recursion depth for symbolic execution (default: 128)"
                    },
                    "execution_timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds (default: 86400)"
                    },
                    "strategy": {
                        "type": "string",
                        "description": "Search strategy: 'dfs' or 'bfs' (default: 'dfs')"
                    },
                    "enable_onchain_data": {
                        "type": "boolean",
                        "description": "Enable fetching onchain storage data (default: false)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="disassemble_contract",
            description=(
                "Disassemble EVM bytecode into readable assembly instructions. "
                "Useful for understanding contract behavior at the opcode level."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_code": {
                        "type": "string",
                        "description": "Solidity source code or bytecode to disassemble"
                    },
                    "contract_address": {
                        "type": "string",
                        "description": "Blockchain address to disassemble (alternative to contract_code)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_detectors",
            description="List all available security detection modules in Mythril",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for Mythril operations."""
    
    try:
        if name == "analyze_contract":
            return await analyze_contract_tool(arguments)
        elif name == "disassemble_contract":
            return await disassemble_contract_tool(arguments)
        elif name == "list_detectors":
            return await list_detectors_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        log.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def analyze_contract_tool(arguments: Dict[str, Any]) -> list[TextContent]:
    """Analyze a smart contract for vulnerabilities."""
    
    contract_code = arguments.get("contract_code")
    contract_address = arguments.get("contract_address")
    solc_version = arguments.get("solc_version")
    
    if not contract_code and not contract_address:
        return [TextContent(
            type="text",
            text="Error: Either 'contract_code' or 'contract_address' must be provided"
        )]
    
    # Create arguments
    args = create_default_args()
    args.max_depth = arguments.get("max_depth", 128)
    args.execution_timeout = arguments.get("execution_timeout", 86400)
    args.strategy = arguments.get("strategy", "dfs")
    args.no_onchain_data = not arguments.get("enable_onchain_data", False)
    args.solv = solc_version
    args.address = contract_address
    args.code = contract_code
    
    try:
        # Initialize config
        config = MythrilConfig()
        
        if not args.no_onchain_data:
            if args.rpc:
                config.set_api_rpc(rpc=args.rpc, rpctls=args.rpctls)
            else:
                config.set_api_from_config_path()
        
        # Initialize disassembler
        disassembler = MythrilDisassembler(
            eth=config.eth,
            solc_version=solc_version,
            solc_settings_json=None,
        )
        
        # Load contract
        if contract_address:
            disassembler.load_from_address(contract_address)
        elif contract_code:
            # Determine if it's source code or bytecode
            if contract_code.strip().startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in contract_code.strip()):
                # It's bytecode
                disassembler.load_from_bytecode(contract_code)
            else:
                # It's source code
                disassembler.load_from_solidity([contract_code])
        
        # Create analyzer
        analyzer = MythrilAnalyzer(
            disassembler=disassembler,
            cmd_args=args,
            strategy=args.strategy,
            address=contract_address,
        )
        
        # Execute analysis
        issues = analyzer.fire_lasers(
            modules=args.modules,
            verbose_report=args.verbose_report,
        )
        
        # Format report
        report = Report(verbose=args.verbose_report, issues=issues)
        output = report.as_text()
        
        return [TextContent(
            type="text",
            text=output if output else "No issues found."
        )]
        
    except CriticalError as e:
        return [TextContent(
            type="text",
            text=f"Critical Error: {str(e)}"
        )]
    except Exception as e:
        log.error(f"Analysis error: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error during analysis: {str(e)}"
        )]


async def disassemble_contract_tool(arguments: Dict[str, Any]) -> list[TextContent]:
    """Disassemble a smart contract into EVM assembly."""
    
    contract_code = arguments.get("contract_code")
    contract_address = arguments.get("contract_address")
    
    if not contract_code and not contract_address:
        return [TextContent(
            type="text",
            text="Error: Either 'contract_code' or 'contract_address' must be provided"
        )]
    
    try:
        # Initialize config
        config = MythrilConfig()
        
        # Initialize disassembler
        disassembler = MythrilDisassembler(
            eth=config.eth,
            solc_version=None,
            solc_settings_json=None,
        )
        
        # Load contract
        if contract_address:
            disassembler.load_from_address(contract_address)
        elif contract_code:
            # Determine if it's source code or bytecode
            if contract_code.strip().startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in contract_code.strip()):
                # It's bytecode
                disassembler.load_from_bytecode(contract_code)
            else:
                # It's source code  
                disassembler.load_from_solidity([contract_code])
        
        # Get disassembly
        if disassembler.contracts:
            contract = disassembler.contracts[0]
            output = contract.get_easm()
            
            return [TextContent(
                type="text",
                text=output if output else "No disassembly available."
            )]
        else:
            return [TextContent(
                type="text",
                text="Error: Could not load contract for disassembly"
            )]
            
    except Exception as e:
        log.error(f"Disassembly error: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error during disassembly: {str(e)}"
        )]


async def list_detectors_tool(arguments: Dict[str, Any]) -> list[TextContent]:
    """List all available detection modules."""
    
    try:
        from mythril.analysis.module import ModuleLoader
        
        module_loader = ModuleLoader()
        modules = module_loader.get_modules()
        
        output = "Available Detection Modules:\n\n"
        for module_name in sorted(modules.keys()):
            module = modules[module_name]
            output += f"- {module_name}: {module.__doc__ or 'No description'}\n"
        
        return [TextContent(
            type="text",
            text=output
        )]
        
    except Exception as e:
        log.error(f"List detectors error: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error listing detectors: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr  # Log to stderr to keep stdout clean for MCP protocol
    )
    
    log.info("Starting Mythril MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
