#!/usr/bin/env python3
"""
Basic usage example for Talk to Your PC MCP Server
"""

import asyncio
import os
from src.talk_to_your_pc_mcp_server.server import run_diagnosis, get_pc_settings, execute_troubleshooting

async def main():
    """Example usage of the MCP server tools"""
    
    # Make sure you have an API key set
    if not any(os.getenv(key) for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "AZURE_OPENAI_API_KEY"]):
        print("Please set an LLM API key environment variable")
        return
    
    print("Talk to Your PC - Basic Usage Example")
    print("=" * 50)
    
    # Example 1: Diagnose why computer is slow
    print("\n1. Diagnosing system performance...")
    result = await run_diagnosis("why is my computer running slow?")
    print(f"Diagnosis: {result}")
    
    # Example 2: Get WiFi information
    print("\n2. Checking WiFi status...")
    result = await get_pc_settings("what wifi network am I connected to?")
    print(f"WiFi Info: {result}")
    
    # Example 3: Check battery (on laptops)
    print("\n3. Checking battery status...")
    result = await get_pc_settings("what is my battery percentage?")
    print(f"Battery: {result}")
    
    print("\nExamples completed!")
    print("\nTo use with Claude Desktop, add this server to your claude_desktop_config.json")
    print("See examples/claude_desktop_config.json for the exact configuration.")


if __name__ == "__main__":
    asyncio.run(main())