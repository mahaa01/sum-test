"""
Base A2A Agent Implementation
"""
import asyncio
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
import uvicorn
from protocols.a2a import A2AProtocol, A2AMessage, TaskRequest, TaskResponse, TaskStatus, AgentCapability
from protocols.mcp import MCPClient
import logging

logger = logging.getLogger(__name__)

class BaseA2AAgent:
    """Base class for A2A agents"""
    
    def __init__(self, agent_id: str, name: str, description: str, port: int):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.port = port
        
        # Initialize A2A protocol
        self.a2a = A2AProtocol(agent_id, port=port)
        
        # Initialize MCP client
        self.mcp_client = MCPClient()
        
        # FastAPI app for HTTP endpoints
        self.app = FastAPI(title=f"A2A Agent: {name}")
        
        # Setup endpoints
        self._setup_endpoints()
        
        # Override task handler
        self.a2a.message_handlers[self.a2a.MessageType.TASK_REQUEST] = self._handle_task_request
    
    def _setup_endpoints(self):
        """Setup HTTP endpoints for A2A communication"""
        
        @self.app.post("/a2a/message")
        async def handle_a2a_message(message_data: Dict[str, Any]):
            """Handle incoming A2A messages"""
            return await self.a2a.process_message(message_data)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agent_id": self.agent_id}
        
        @self.app.get("/capabilities")
        async def get_capabilities():
            """Get agent capabilities"""
            return {
                "agent_id": self.agent_id,
                "name": self.name,
                "description": self.description,
                "capabilities": [cap.dict() for cap in self.a2a.capabilities.values()]
            }
    
    async def _handle_task_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle task requests"""
        try:
            task_request = TaskRequest(**message.payload)
            
            # Process the task
            result = await self.process_task(task_request)
            
            response = TaskResponse(
                task_id=task_request.task_id,
                status=TaskStatus.COMPLETED,
                result=result
            )
            
            return {
                "type": self.a2a.MessageType.TASK_RESPONSE,
                "payload": response.dict()
            }
            
        except Exception as e:
            logger.error(f"Error handling task request: {e}")
            
            task_id = message.payload.get("task_id", "unknown")
            response = TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=str(e)
            )
            
            return {
                "type": self.a2a.MessageType.TASK_RESPONSE,
                "payload": response.dict()
            }
    
    async def process_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process a task - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement process_task method")
    
    def register_capability(self, name: str, description: str, input_schema: Dict[str, Any], 
                          output_schema: Dict[str, Any], cost: Optional[float] = None):
        """Register a capability"""
        capability = AgentCapability(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            cost=cost
        )
        self.a2a.register_capability(capability)
    
    def add_mcp_server(self, name: str, endpoint: str):
        """Add an MCP server connection"""
        self.mcp_client.add_server(name, endpoint)
    
    def add_peer_agent(self, agent_id: str, endpoint: str):
        """Add a peer agent"""
        self.a2a.register_peer_agent(agent_id, endpoint)
    
    async def request_task_from_peer(self, peer_id: str, task_type: str, description: str, 
                                   parameters: Dict[str, Any] = None) -> TaskResponse:
        """Request task execution from a peer agent"""
        task_request = TaskRequest(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            description=description,
            parameters=parameters or {}
        )
        
        return await self.a2a.request_task(peer_id, task_request)
    
    async def start(self, host: str = "localhost"):
        """Start the agent server"""
        logger.info(f"Starting agent {self.name} on {host}:{self.port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self, host: str = "localhost"):
        """Run the agent server (blocking)"""
        uvicorn.run(self.app, host=host, port=self.port)