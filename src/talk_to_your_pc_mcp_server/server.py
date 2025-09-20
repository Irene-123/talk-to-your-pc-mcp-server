#!/usr/bin/env python3
"""
Simple MCP Server for Talk to Your PC
Just the 3 core tools: run_diagnosis, get_pc_settings, execute_troubleshooting
"""

import asyncio
import json
import subprocess
import platform
import os
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)


OS_TYPE = platform.system().lower()

# Dangerous keywords to watch for
RISKY_KEYWORDS = [
    "rm -rf", "del /f", "format", "fdisk", "dd if=", "mkfs", 
    "shutdown", "reboot", "sudo rm", "rmdir /s", "reg delete"
]


from .llm_config import get_llm_response

def execute_command(command: str) -> tuple[str, str, int]:
    """Execute system command safely"""
    try:
        # Check for risky keywords
        for keyword in RISKY_KEYWORDS:
            if keyword.lower() in command.lower():
                return f"BLOCKED: Command contains risky keyword: {keyword}", "", 1
        
        # Choose shell based on OS
        if OS_TYPE == "windows":
            process = subprocess.Popen(
                ["powershell", "-Command", command], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        else:  # Linux/Mac
            process = subprocess.Popen(
                ["bash", "-c", command], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        
        try:
            stdout, stderr = process.communicate(timeout=15)
            return stdout.decode('utf-8'), stderr.decode('utf-8'), process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            return "", "Command timed out", 1
        
    except Exception as e:
        return "", f"Execution error: {str(e)}", 1

async def run_diagnosis(input_text: str) -> str:
    """Run system diagnosis to find probable issues"""
    
    # Create OS-specific system prompt
    if OS_TYPE == "windows":
        system_prompt = """You are a Windows system analyst. Write a PowerShell command to diagnose the user's issue.
        Return ONLY a JSON object with key 'command'. No explanations, no json labels.
        Examples: Get-WmiObject, Get-EventLog, Test-NetConnection, Get-Process"""
    else:  # Linux/Mac
        system_prompt = """You are a Linux/macOS system analyst. Write a bash command to diagnose the user's issue.
        Return ONLY a JSON object with key 'command'. No explanations, no json labels.
        Examples: ps aux, netstat, dmesg, df -h, top"""
    
    # Get command from LLM
    response = get_llm_response(system_prompt, input_text)
    
    # DEBUG: Print the raw response
    # print(f"🔍 DEBUG - Raw LLM response: {repr(response)}")
    
    try:
        command_json = json.loads(response)
        # print(f"🔍 DEBUG - Parsed JSON: {command_json}")
        
        if 'command' not in command_json:
            return f"Error: LLM response missing 'command' key: {response}"
            
        command = command_json['command']
        # print(f"🔍 DEBUG - Command to execute: {command}")
        
        stdout, stderr, returncode = execute_command(command)
        # print(f"🔍 DEBUG - Command result: stdout='{stdout[:100]}...', stderr='{stderr}', returncode={returncode}")
        
        if returncode != 0:
            return f"Diagnosis failed: {stderr}"
        
        # Analyze results with LLM
        analysis_prompt = """Analyze this system diagnostic output and explain if any issues were found. 
        Output the system diagnostic output for user to see and verify as well.
        Be concise and helpful."""
        
        analysis_input = f"User issue: {input_text}\nDiagnostic output: {stdout}"
        analysis = get_llm_response(analysis_prompt, analysis_input)
        
        # print(f"🔍 DEBUG - Analysis response: {repr(analysis)}")
        
        return analysis
        
    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e}. Raw response: {response}"
    except KeyError as e:
        return f"Missing key in response: {e}. Response: {response}"
    except Exception as e:
        return f"Diagnosis error: {str(e)}"

async def get_pc_settings(input_text: str) -> str:
    """Get PC settings information"""
        
    if OS_TYPE == "windows":
        system_prompt = """You are a Windows system analyst. Write a PowerShell command to get the PC setting requested.
        IMPORTANT: Return ONLY raw JSON, no markdown, no explanations, no code blocks.
        Format: {"command": "your-powershell-command-here"}"""
    else:
        system_prompt = """You are a Linux/macOS system analyst. Write a bash command to get the PC setting requested.
        IMPORTANT: Return ONLY raw JSON, no markdown, no explanations, no code blocks.
        Format: {"command": "your-bash-command-here"}"""
    # Get command from LLM
    response = get_llm_response(system_prompt, input_text)
    try:
        clean_response = extract_json_from_response(response)
        command_json = json.loads(clean_response)
        stdout, stderr, returncode = execute_command(command_json['command'])
        
        if returncode != 0:
            return f"Could not get setting: {stderr}"
        
        # Format results with LLM
        format_prompt = """Format this system output into a user-friendly response."""
        
        format_input = f"User requested: {input_text}\nSystem output: {stdout}"
        formatted = get_llm_response(format_prompt, format_input)
        
        return formatted
        
    except Exception as e:
        return f"Settings error: {str(e)}"

async def execute_troubleshooting(input_text: str) -> str:
    """Execute troubleshooting commands"""
    
    # Create OS-specific system prompt
    if OS_TYPE == "windows":
        system_prompt = """You are a Windows troubleshooter. Write a PowerShell command to fix the user's issue.
        BE CAREFUL - avoid destructive commands. Return ONLY JSON with key 'command'.
        Examples: sfc /scannow, ipconfig /flushdns, netsh winsock reset"""
    else:  # Linux/Mac
        system_prompt = """You are a Linux/macOS troubleshooter. Write a bash command to fix the user's issue.
        BE CAREFUL - avoid destructive commands. Return ONLY JSON with key 'command'.
        Examples: sudo systemctl restart, killall, brew services restart"""
    
    # Get command from LLM
    response = get_llm_response(system_prompt, input_text)
    
    # DEBUG: Print the raw response
    # print(f"DEBUG - Raw LLM response: '{response}'")
    # print(f"DEBUG - Response length: {len(response)}")
    # print(f"DEBUG - Response type: {type(response)}")
    
    # Check for empty response
    if not response or response.strip() == "":
        return "Error: LLM returned empty response. Check API key and connection."
    try:
        clean_response = extract_json_from_response(response)
        command_json = json.loads(clean_response)
        if 'command' not in command_json:
            return f"Error: Response missing 'command' key. Got: {response}"
            
        command = command_json['command']
        
        # Extra safety check for troubleshooting
        if any(risky in command.lower() for risky in ["format", "rm -rf", "del /f"]):
            return "BLOCKED: Troubleshooting command too risky"
        
        stdout, stderr, returncode = execute_command(command)
        
        if returncode != 0:
            return f"Troubleshooting failed: {stderr}"
        
        # Summarize results
        summary_prompt = """Summarize what troubleshooting action was taken, result, andb output the command run and its output for user to see and verify. 
        Also as a reminder, do not run any risky commands that could damage the system. Inform the user if the command failed. 
        Suggest some next steps, and always output the command run and its output for user to see and verify."""
        
        summary_input = f"Action: {input_text}\nCommand: {command}\nOutput: {stdout}"
        summary = get_llm_response(summary_prompt, summary_input)
        
        return summary
        
    except json.JSONDecodeError as e:
        return f"JSON parsing error: {e}. Raw response: '{response}'"
    except Exception as e:
        return f"Troubleshooting error: {str(e)}"


def extract_json_from_response(response: str) -> str:
    """Extract JSON from markdown code blocks or return as-is"""
    # Remove markdown code blocks if present
    if response.strip().startswith('```'):
        # Find content between ```json and ```
        lines = response.strip().split('\n')
        json_lines = []
        in_json = False
        for line in lines:
            if line.strip().startswith('```json') or line.strip().startswith('```'):
                in_json = not in_json
                continue
            if in_json:
                json_lines.append(line)
        return '\n'.join(json_lines).strip()
    return response.strip()




# MCP Server Implementation
class SimpleTalkToPCServer:
    def __init__(self):
        self.tools = {
            "run_diagnosis": {
                "description": "Run system diagnosis to find probable issues",
                "function": run_diagnosis
            },
            "get_pc_settings": {
                "description": "Get PC settings like volume, WiFi, battery, etc.",
                "function": get_pc_settings  
            },
            "execute_troubleshooting": {
                "description": "Execute troubleshooting commands to fix issues",
                "function": execute_troubleshooting
            }
        }

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available tools"""
        return ListToolsResult(
            tools=[
                Tool(
                    name=name,
                    description=info["description"],
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "input_text": {
                                "type": "string",
                                "description": "The user's request or issue description"
                            }
                        },
                        "required": ["input_text"]
                    }
                )
                for name, info in self.tools.items()
            ]
        )

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Execute a tool"""
        try:
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            if tool_name not in self.tools:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Tool '{tool_name}' not found"
                    )],
                    isError=True
                )
            
            # Get the input text
            input_text = arguments.get("input_text", "")
            if not input_text:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="input_text parameter is required"
                    )],
                    isError=True
                )
            
            # Execute the tool
            result = await self.tools[tool_name]["function"](input_text)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )],
                isError=True
            )



from mcp.types import CallToolRequestParams, ServerCapabilities

async def main():
    """Run the MCP server"""
    server_instance = SimpleTalkToPCServer()
    
    async with stdio_server() as (read_stream, write_stream):
        server = Server("talk-to-pc-mcp")
        
        # Register handlers using decorators
        @server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            result = await server_instance.list_tools(ListToolsRequest())
            return result.tools
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list:
            request = CallToolRequest(
                params=CallToolRequestParams(name=name, arguments=arguments)
            )
            result = await server_instance.call_tool(request)
            return result.content
        
        print(f"🚀 Talk to Your PC MCP Server running on {OS_TYPE}")
        
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="talk-to-your-pc-mcp-server",
                server_version="0.1.0",
                capabilities=ServerCapabilities(
                    tools={} # type: ignore
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())