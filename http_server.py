#!/usr/bin/env python3
"""
HTTP MCP Server for Talk to Your PC
Exposes MCP functionality via HTTP API
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add src to path for imports
sys.path.append('src')
from server import run_diagnosis, get_pc_settings, execute_troubleshooting
from llm_config import get_llm_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Talk to Your PC MCP Server",
    description="Control and troubleshoot your PC using natural language",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ToolRequest(BaseModel):
    tool: str
    input_text: str
    
class ToolResponse(BaseModel):
    result: str
    timestamp: str
    tool: str
    input_text: str

class MCPToolsResponse(BaseModel):
    tools: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    server: str
    version: str
    timestamp: str
    available_tools: List[str]

# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        server="talk-to-your-pc-mcp",
        version="0.1.0",
        timestamp=datetime.now().isoformat(),
        available_tools=["run_diagnosis", "get_pc_settings", "execute_troubleshooting"]
    )

# MCP Tools listing
@app.get("/mcp/tools", response_model=MCPToolsResponse)
async def list_tools():
    """List available MCP tools"""
    tools = [
        {
            "name": "run_diagnosis",
            "description": "Run system diagnosis to find probable issues",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "Description of the issue or system check needed"
                    }
                },
                "required": ["input_text"]
            }
        },
        {
            "name": "get_pc_settings",
            "description": "Get PC settings like volume, WiFi, battery, etc.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "The setting or information you want to retrieve"
                    }
                },
                "required": ["input_text"]
            }
        },
        {
            "name": "execute_troubleshooting",
            "description": "Execute troubleshooting commands to fix system issues",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "Description of the issue to fix"
                    }
                },
                "required": ["input_text"]
            }
        }
    ]
    
    return MCPToolsResponse(tools=tools)

# Tool execution endpoint
@app.post("/mcp/tools/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """Execute an MCP tool"""
    logger.info(f"Tool call: {request.tool} with input: {request.input_text}")
    
    try:
        if request.tool == "run_diagnosis":
            result = await run_diagnosis(request.input_text)
        elif request.tool == "get_pc_settings":
            result = await get_pc_settings(request.input_text)
        elif request.tool == "execute_troubleshooting":
            result = await execute_troubleshooting(request.input_text)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.tool}")
        
        logger.info(f"Tool {request.tool} completed successfully")
        
        return ToolResponse(
            result=result,
            timestamp=datetime.now().isoformat(),
            tool=request.tool,
            input_text=request.input_text
        )
        
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

# Server-Sent Events endpoint for real-time updates
@app.post("/mcp/tools/stream")
async def stream_tool_execution(request: ToolRequest):
    """Execute tool with streaming response"""
    
    async def event_stream():
        try:
            yield f"data: {json.dumps({'status': 'started', 'tool': request.tool})}\n\n"
            
            if request.tool == "run_diagnosis":
                result = await run_diagnosis(request.input_text)
            elif request.tool == "get_pc_settings":
                result = await get_pc_settings(request.input_text)
            elif request.tool == "execute_troubleshooting":
                result = await execute_troubleshooting(request.input_text)
            else:
                yield f"data: {json.dumps({'error': f'Unknown tool: {request.tool}'})}\n\n"
                return
            
            yield f"data: {json.dumps({'status': 'completed', 'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/plain")

# Batch tool execution
@app.post("/mcp/tools/batch")
async def batch_tool_execution(requests: List[ToolRequest]):
    """Execute multiple tools in sequence"""
    results = []
    
    for req in requests:
        try:
            if req.tool == "run_diagnosis":
                result = await run_diagnosis(req.input_text)
            elif req.tool == "get_pc_settings":
                result = await get_pc_settings(req.input_text)
            elif req.tool == "execute_troubleshooting":
                result = await execute_troubleshooting(req.input_text)
            else:
                result = f"Error: Unknown tool {req.tool}"
            
            results.append({
                "tool": req.tool,
                "input_text": req.input_text,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            results.append({
                "tool": req.tool,
                "input_text": req.input_text,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    return {"results": results}

# Direct LLM endpoint (for testing)
@app.post("/llm/query")
async def query_llm(request: dict):
    """Direct LLM query endpoint"""
    try:
        system_prompt = request.get("system_prompt", "You are a helpful assistant.")
        user_prompt = request.get("user_prompt", "")
        
        response = get_llm_response(system_prompt, user_prompt)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")

# System info endpoint
@app.get("/system/info")
async def system_info():
    """Get basic system information"""
    import platform
    import psutil
    
    try:
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').total if platform.system() != 'Windows' else psutil.disk_usage('C:').total,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8081
    port = int(os.getenv("PORT", 8081))
    
    # Check if required environment variables are set
    api_keys = [
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("AZURE_OPENAI_API_KEY")
    ]
    
    if not any(api_keys):
        logger.warning("No LLM API keys found. Server will start but tools may not work.")
    else:
        logger.info("LLM API key found. Server ready.")
    
    logger.info(f"Starting Talk to Your PC MCP HTTP Server on port {port}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        access_log=True
    )