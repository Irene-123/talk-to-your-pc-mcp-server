#!/usr/bin/env python3
"""
Command line interface for Talk to Your PC MCP Server
"""

import argparse
import asyncio
import sys
from .server import main

def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Talk to Your PC - MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  talk-to-your-pc-mcp-server                    # Start the MCP server
  talk-to-your-pc-mcp-server --help            # Show this help message

Environment Variables:
  OPENAI_API_KEY                   # OpenAI API key
  ANTHROPIC_API_KEY                # Claude/Anthropic API key
  AZURE_OPENAI_API_KEY             # Azure OpenAI API key
  AZURE_OPENAI_ENDPOINT            # Azure OpenAI endpoint
  AZURE_OPENAI_DEPLOYMENT_NAME     # Azure deployment name

For Claude Desktop setup, see: https://github.com/Irene-123/talk-to-your-pc-mcp-server
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="talk-to-your-pc-mcp-server 0.1.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        import asyncio
        asyncio.run(main())  # This is the fix - use asyncio.run()
    except KeyboardInterrupt:
        print("\n👋 Talk to Your PC MCP Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()