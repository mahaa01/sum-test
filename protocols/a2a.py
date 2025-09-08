"""
A2A (Agent-to-Agent) Protocol Implementation
"""
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel
import httpx
import logging

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class A2AMessage(BaseModel):
    """Standard A2A message format"""
    id: str = None
    type: MessageType
    sender_id: str
    recipient_id: str
    timestamp: str = None
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    def __init__(self, **data):
        if data.get('id') is None:
            data['id'] = str(uuid.uuid4())
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.utcnow().isoformat()
        super().__init__(**data)

class TaskRequest(BaseModel):
    """Task request payload"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any] = {}
    priority: int = 5  # 1-10, 10 being highest
    timeout: Optional[int] = None  # seconds
    requires_capabilities: List[str] = []

class TaskResponse(BaseModel):
    """Task response payload"""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = {}

class AgentCapability(BaseModel):
    """Agent capability description"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    cost: Optional[float] = None  # relative cost metric

class A2AProtocol:
    """A2A Protocol Handler"""
    
    def __init__(self, agent_id: str, host: str = "localhost", port: int = 8000):
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.capabilities: Dict[str, AgentCapability] = {}
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.peer_agents: Dict[str, str] = {}  # agent_id -> endpoint
        
        # Setup default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.message_handlers[MessageType.CAPABILITY_QUERY] = self._handle_capability_query
        self.message_handlers[MessageType.TASK_REQUEST] = self._handle_task_request
        self.message_handlers[MessageType.STATUS_UPDATE] = self._handle_status_update
    
    def register_capability(self, capability: AgentCapability):
        """Register a new capability"""
        self.capabilities[capability.name] = capability
        logger.info(f"Registered capability: {capability.name}")
    
    def register_peer_agent(self, agent_id: str, endpoint: str):
        """Register a peer agent"""
        self.peer_agents[agent_id] = endpoint
        logger.info(f"Registered peer agent: {agent_id} at {endpoint}")
    
    async def send_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Send A2A message to another agent"""
        if message.recipient_id not in self.peer_agents:
            raise ValueError(f"Unknown recipient: {message.recipient_id}")
        
        endpoint = self.peer_agents[message.recipient_id]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{endpoint}/a2a/message",
                    json=message.dict(),
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to send message to {message.recipient_id}: {e}")
                raise
    
    async def request_task(self, recipient_id: str, task_request: TaskRequest) -> TaskResponse:
        """Request task execution from another agent"""
        message = A2AMessage(
            type=MessageType.TASK_REQUEST,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            payload=task_request.dict()
        )
        
        response_data = await self.send_message(message)
        return TaskResponse(**response_data['payload'])
    
    async def query_capabilities(self, recipient_id: str) -> List[AgentCapability]:
        """Query capabilities of another agent"""
        message = A2AMessage(
            type=MessageType.CAPABILITY_QUERY,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            payload={}
        )
        
        response_data = await self.send_message(message)
        capabilities = []
        for cap_data in response_data['payload']['capabilities']:
            capabilities.append(AgentCapability(**cap_data))
        return capabilities
    
    async def _handle_capability_query(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle capability query"""
        capabilities = [cap.dict() for cap in self.capabilities.values()]
        return {
            "type": MessageType.CAPABILITY_RESPONSE,
            "payload": {"capabilities": capabilities}
        }
    
    async def _handle_task_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle task request - to be overridden by agents"""
        task_request = TaskRequest(**message.payload)
        
        # Default implementation returns not implemented
        response = TaskResponse(
            task_id=task_request.task_id,
            status=TaskStatus.FAILED,
            error="Task handling not implemented"
        )
        
        return {
            "type": MessageType.TASK_RESPONSE,
            "payload": response.dict()
        }
    
    async def _handle_status_update(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle status update"""
        logger.info(f"Received status update: {message.payload}")
        return {"status": "acknowledged"}
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming A2A message"""
        try:
            message = A2AMessage(**message_data)
            handler = self.message_handlers.get(message.type)
            
            if not handler:
                return {
                    "type": MessageType.ERROR,
                    "payload": {"error": f"No handler for message type: {message.type}"}
                }
            
            return await handler(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "type": MessageType.ERROR,
                "payload": {"error": str(e)}
            }