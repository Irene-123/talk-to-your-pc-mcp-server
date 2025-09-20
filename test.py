#!/usr/bin/env python3
"""
Test and Debug Script for Talk to PC MCP Server
Run this from the project root directory
"""

import os
import sys
import asyncio
import json
import traceback
from pathlib import Path

# Add src to Python path for testing
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("Talk to PC MCP Server - Test & Debug Script")
print("=" * 60)

def test_environment():
    """Test environment setup"""
    print("\n1. Environment Check:")
    print("-" * 30)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check working directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"Source path: {src_path}")
    
    # Check if source files exist
    server_file = src_path / "talk_to_your_pc_mcp_server" / "server.py"
    llm_file = src_path / "talk_to_your_pc_mcp_server" / "llm_config.py"
    
    print(f"server.py exists: {server_file.exists()}")
    print(f"llm_config.py exists: {llm_file.exists()}")
    
    # Check API keys
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    }
    
    print("\nAPI Keys:")
    for key, value in api_keys.items():
        if value:
            print(f"  {key}: Set (starts with: {value[:15]}...)")
        else:
            print(f"  {key}: Not set")
    
    return any(api_keys.values())

def test_imports():
    """Test importing modules"""
    print("\n2. Import Test:")
    print("-" * 30)
    
    try:
        # Test LLM config import
        from talk_to_your_pc_mcp_server.llm_config import get_llm_response, LLMClientFactory
        print("✅ llm_config import successful")
        
        # Test server import
        from talk_to_your_pc_mcp_server.server import run_diagnosis, get_pc_settings, execute_troubleshooting
        print("✅ server import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_llm_client():
    """Test LLM client functionality"""
    print("\n3. LLM Client Test:")
    print("-" * 30)
    
    try:
        from talk_to_your_pc_mcp_server.llm_config import get_llm_response, LLMClientFactory
        
        # Test factory
        client = LLMClientFactory.create_client()
        if not client:
            print("❌ No LLM client created - check API keys")
            return False
        
        print(f"✅ Created client: {type(client).__name__}")
        
        # Test simple response
        response = get_llm_response(
            'Return only this JSON: {"test": "success"}',
            'hello'
        )
        
        print(f"LLM response: {response}")
        print(f"Response length: {len(response)}")
        
        # Test JSON parsing
        try:
            if response.strip().startswith('```'):
                # Handle markdown
                lines = response.strip().split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                clean_response = '\n'.join(json_lines).strip()
            else:
                clean_response = response.strip()
            
            parsed = json.loads(clean_response)
            print(f"✅ JSON parsing successful: {parsed}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {repr(response)}")
            return False
            
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        traceback.print_exc()
        return False

async def test_mcp_functions():
    """Test individual MCP functions"""
    print("\n4. MCP Functions Test:")
    print("-" * 30)
    
    try:
        from talk_to_your_pc_mcp_server.server import run_diagnosis, get_pc_settings, execute_troubleshooting
        
        result = await get_pc_settings("what is my username")
        print(f"✅ get_pc_settings result: {result[:100]}...")
        print("\n\n\n-----------------------------------------------------------------------------")


        result = await run_diagnosis("check system memory usage")
        print(f"✅ run_diagnosis result: {result[:100]}...")
        print("\n\n\n-----------------------------------------------------------------------------")

        

        result = await execute_troubleshooting("check disk space")
        print(f"✅ execute_troubleshooting result: {result[:100]}...")
        print("\n\n\n-----------------------------------------------------------------------------")

        
        return True
        
    except Exception as e:
        print(f"❌ MCP functions test failed: {e}")
        traceback.print_exc()
        return False

def test_mcp_server():
    """Test MCP server startup"""
    print("\n5. MCP Server Startup Test:")
    print("-" * 30)
    
    try:
        from talk_to_your_pc_mcp_server.server import SimpleTalkToPCServer
        
        # Create server instance
        server = SimpleTalkToPCServer()
        print("✅ MCP server instance created")
        
        # Test tools list
        print(f"Available tools: {list(server.tools.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        traceback.print_exc()
        return False

def test_json_extraction():
    """Test JSON extraction from markdown"""
    print("\n6. JSON Extraction Test:")
    print("-" * 30)
    
    def extract_json_from_response(response: str) -> str:
        """Extract JSON from markdown code blocks or return as-is"""
        if response.strip().startswith('```'):
            lines = response.strip().split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('```'):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)
            return '\n'.join(json_lines).strip()
        return response.strip()
    
    # Test cases
    test_cases = [
        '{"command": "echo test"}',  # Plain JSON
        '```json\n{"command": "echo test"}\n```',  # Markdown JSON
        '```\n{"command": "echo test"}\n```',  # Markdown without json label
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            extracted = extract_json_from_response(test_case)
            parsed = json.loads(extracted)
            print(f"✅ Test case {i+1}: {parsed}")
        except Exception as e:
            print(f"❌ Test case {i+1} failed: {e}")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("Starting comprehensive test suite...")
    
    # Test 1: Environment
    has_api_key = test_environment()
    if not has_api_key:
        print("\n⚠️  Warning: No API keys found. Some tests will fail.")
    
    # Test 2: Imports
    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Import tests failed. Cannot continue.")
        return False
    
    # Test 3: JSON extraction
    test_json_extraction()
    
    if has_api_key:
        # Test 4: LLM client
        llm_ok = test_llm_client()
        
        # Test 5: MCP functions
        if llm_ok:
            asyncio.run(test_mcp_functions())
    
    # Test 6: MCP server
    test_mcp_server()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    if has_api_key:
        print("✅ All tests completed!")
        print("\nTo run the MCP server:")
        print("cd ~/talk-to-your-pc-mcp-server")
        print("python -m talk_to_your_pc_mcp_server.server")
    else:
        print("⚠️  Tests completed but no API key found.")
        print("Set an API key and run tests again:")
        print("export ANTHROPIC_API_KEY='your-key'")
    
    return True

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()