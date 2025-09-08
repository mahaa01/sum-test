"""
MCP (Model Context Protocol) Implementation
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn
import logging

logger = logging.getLogger(__name__)

class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    
    class Config:
        arbitrary_types_allowed = True

class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = {}

class MCPContext(BaseModel):
    """MCP Context definition"""
    name: str
    description: str
    content: str
    metadata: Dict[str, Any] = {}

class MCPRequest(BaseModel):
    """MCP Request format"""
    id: str
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    """MCP Response format"""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPServer:
    """MCP Server implementation"""
    
    def __init__(self, name: str, description: str = "", port: int = 9000):
        self.name = name
        self.description = description
        self.port = port
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.contexts: Dict[str, MCPContext] = {}
        self.app = FastAPI(title=f"MCP Server: {name}")
        
        # Setup MCP endpoints
        self._setup_endpoints()
    
    def _setup_endpoints(self):
        """Setup MCP protocol endpoints"""
        
        @self.app.post("/mcp/request")
        async def handle_mcp_request(request: MCPRequest):
            """Handle MCP requests"""
            try:
                if request.method == "tools/list":
                    return MCPResponse(
                        id=request.id,
                        result={
                            "tools": [
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "inputSchema": tool.input_schema
                                }
                                for tool in self.tools.values()
                            ]
                        }
                    ).dict()
                
                elif request.method == "tools/call":
                    tool_name = request.params.get("name")
                    tool_args = request.params.get("arguments", {})
                    
                    if tool_name not in self.tools:
                        return MCPResponse(
                            id=request.id,
                            error={"code": -32601, "message": f"Tool not found: {tool_name}"}
                        ).dict()
                    
                    tool = self.tools[tool_name]
                    if not tool.handler:
                        return MCPResponse(
                            id=request.id,
                            error={"code": -32603, "message": f"No handler for tool: {tool_name}"}
                        ).dict()
                    
                    try:
                        result = await self._call_tool_handler(tool.handler, tool_args)
                        return MCPResponse(
                            id=request.id,
                            result={"content": [{"type": "text", "text": str(result)}]}
                        ).dict()
                    except Exception as e:
                        return MCPResponse(
                            id=request.id,
                            error={"code": -32603, "message": str(e)}
                        ).dict()
                
                elif request.method == "resources/list":
                    return MCPResponse(
                        id=request.id,
                        result={
                            "resources": [
                                {
                                    "uri": resource.uri,
                                    "name": resource.name,
                                    "description": resource.description,
                                    "mimeType": resource.mime_type
                                }
                                for resource in self.resources.values()
                            ]
                        }
                    ).dict()
                
                elif request.method == "resources/read":
                    uri = request.params.get("uri")
                    if uri not in self.resources:
                        return MCPResponse(
                            id=request.id,
                            error={"code": -32601, "message": f"Resource not found: {uri}"}
                        ).dict()
                    
                    resource = self.resources[uri]
                    return MCPResponse(
                        id=request.id,
                        result={
                            "contents": [{
                                "uri": resource.uri,
                                "mimeType": resource.mime_type,
                                "text": resource.metadata.get("content", "")
                            }]
                        }
                    ).dict()
                
                else:
                    return MCPResponse(
                        id=request.id,
                        error={"code": -32601, "message": f"Method not found: {request.method}"}
                    ).dict()
                    
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return MCPResponse(
                    id=request.id,
                    error={"code": -32603, "message": str(e)}
                ).dict()
    
    async def _call_tool_handler(self, handler: Callable, args: Dict[str, Any]) -> Any:
        """Call tool handler with proper async handling"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(**args)
        else:
            return handler(**args)
    
    def add_tool(self, tool: MCPTool):
        """Add a tool to the MCP server"""
        self.tools[tool.name] = tool
        logger.info(f"Added tool: {tool.name}")
    
    def add_resource(self, resource: MCPResource):
        """Add a resource to the MCP server"""
        self.resources[resource.uri] = resource
        logger.info(f"Added resource: {resource.uri}")
    
    def add_context(self, context: MCPContext):
        """Add a context to the MCP server"""
        self.contexts[context.name] = context
        logger.info(f"Added context: {context.name}")
    
    def tool(self, name: str, description: str, input_schema: Dict[str, Any]):
        """Decorator for adding tools"""
        def decorator(func: Callable):
            tool = MCPTool(
                name=name,
                description=description,
                input_schema=input_schema,
                handler=func
            )
            self.add_tool(tool)
            return func
        return decorator
    
    async def start(self, host: str = "localhost"):
        """Start the MCP server"""
        config = uvicorn.Config(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self, host: str = "localhost"):
        """Run the MCP server (blocking)"""
        uvicorn.run(self.app, host=host, port=self.port)

class MCPClient:
    """MCP Client for connecting to MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, str] = {}  # name -> endpoint
    
    def add_server(self, name: str, endpoint: str):
        """Add an MCP server endpoint"""
        self.servers[name] = endpoint
        logger.info(f"Added MCP server: {name} at {endpoint}")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
        
        endpoint = self.servers[server_name]
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )
        
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{endpoint}/mcp/request",
                    json=request.dict(),
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if "error" in result and result["error"]:
                    raise Exception(f"MCP Error: {result['error']['message']}")
                
                # Extract text content from MCP response
                content = result.get("result", {}).get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
                return result.get("result", {})
                
            except Exception as e:
                logger.error(f"Failed to call tool {tool_name} on server {server_name}: {e}")
                raise
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List available tools on an MCP server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
        
        endpoint = self.servers[server_name]
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="tools/list"
        )
        
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{endpoint}/mcp/request",
                    json=request.dict(),
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if "error" in result and result["error"]:
                    raise Exception(f"MCP Error: {result['error']['message']}")
                
                return result.get("result", {}).get("tools", [])
                
            except Exception as e:
                logger.error(f"Failed to list tools on server {server_name}: {e}")
                raise