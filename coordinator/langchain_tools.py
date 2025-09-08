"""
LangChain Tools for A2A Agent Integration
"""
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

class A2ATaskInput(BaseModel):
    """Input schema for A2A task execution"""
    agent_id: str = Field(description="ID of the agent to send task to")
    task_type: str = Field(description="Type of task to execute")
    description: str = Field(description="Description of the task")
    parameters: Dict[str, Any] = Field(default={}, description="Task parameters")

class A2ATool(BaseTool):
    """LangChain tool for executing tasks on A2A agents"""
    
    name: str = "a2a_task"
    description: str = "Execute tasks on A2A agents in the multi-agent system"
    args_schema: Type[BaseModel] = A2ATaskInput
    
    def __init__(self, agent_registry: Dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.agent_registry = agent_registry  # agent_id -> endpoint mapping
    
    def _run(
        self, 
        agent_id: str, 
        task_type: str, 
        description: str, 
        parameters: Dict[str, Any] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous execution (not recommended for async operations)"""
        return asyncio.run(self._arun(agent_id, task_type, description, parameters))
    
    async def _arun(
        self, 
        agent_id: str, 
        task_type: str, 
        description: str, 
        parameters: Dict[str, Any] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Execute task on A2A agent"""
        try:
            if agent_id not in self.agent_registry:
                return f"Error: Unknown agent ID '{agent_id}'. Available agents: {list(self.agent_registry.keys())}"
            
            endpoint = self.agent_registry[agent_id]
            parameters = parameters or {}
            
            # Create A2A message
            message = {
                "id": f"langchain_{asyncio.get_event_loop().time()}",
                "type": "task_request",
                "sender_id": "coordinator",
                "recipient_id": agent_id,
                "payload": {
                    "task_id": f"task_{asyncio.get_event_loop().time()}",
                    "task_type": task_type,
                    "description": description,
                    "parameters": parameters
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{endpoint}/a2a/message",
                    json=message
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("type") == "task_response":
                    payload = result.get("payload", {})
                    if payload.get("status") == "completed":
                        return f"Task completed successfully: {payload.get('result', {})}"
                    else:
                        return f"Task failed: {payload.get('error', 'Unknown error')}"
                else:
                    return f"Unexpected response: {result}"
        
        except Exception as e:
            logger.error(f"Error executing A2A task: {e}")
            return f"Error executing task: {str(e)}"

class MathToolInput(BaseModel):
    """Input schema for math operations"""
    operation: str = Field(description="Math operation: calculate, solve_equation, statistics, matrix_operations")
    parameters: Dict[str, Any] = Field(description="Operation parameters")

class MathTool(BaseTool):
    """LangChain tool for math operations via Math Agent"""
    
    name: str = "math"
    description: str = "Perform mathematical calculations, solve equations, and statistical analysis"
    args_schema: Type[BaseModel] = MathToolInput
    
    def __init__(self, math_agent_endpoint: str, **kwargs):
        super().__init__(**kwargs)
        self.math_agent_endpoint = math_agent_endpoint
    
    def _run(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self._arun(operation, parameters))
    
    async def _arun(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        try:
            a2a_tool = A2ATool({"math_agent": self.math_agent_endpoint})
            result = await a2a_tool._arun("math_agent", operation, f"Perform {operation}", parameters)
            return result
        except Exception as e:
            return f"Math operation failed: {str(e)}"

class WebToolInput(BaseModel):
    """Input schema for web operations"""
    operation: str = Field(description="Web operation: search_web, scrape_webpage, research_topic, verify_information")
    parameters: Dict[str, Any] = Field(description="Operation parameters")

class WebTool(BaseTool):
    """LangChain tool for web operations via Web Agent"""
    
    name: str = "web"
    description: str = "Search the web, scrape webpages, conduct research, and verify information"
    args_schema: Type[BaseModel] = WebToolInput
    
    def __init__(self, web_agent_endpoint: str, **kwargs):
        super().__init__(**kwargs)
        self.web_agent_endpoint = web_agent_endpoint
    
    def _run(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self._arun(operation, parameters))
    
    async def _arun(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        try:
            a2a_tool = A2ATool({"web_agent": self.web_agent_endpoint})
            result = await a2a_tool._arun("web_agent", operation, f"Perform {operation}", parameters)
            return result
        except Exception as e:
            return f"Web operation failed: {str(e)}"

class FileToolInput(BaseModel):
    """Input schema for file operations"""
    operation: str = Field(description="File operation: read_file, write_file, list_directory, search_files, manage_data")
    parameters: Dict[str, Any] = Field(description="Operation parameters")

class FileTool(BaseTool):
    """LangChain tool for file operations via File Agent"""
    
    name: str = "file"
    description: str = "Read/write files, manage directories, search content, and handle structured data"
    args_schema: Type[BaseModel] = FileToolInput
    
    def __init__(self, file_agent_endpoint: str, **kwargs):
        super().__init__(**kwargs)
        self.file_agent_endpoint = file_agent_endpoint
    
    def _run(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self._arun(operation, parameters))
    
    async def _arun(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        try:
            a2a_tool = A2ATool({"file_agent": self.file_agent_endpoint})
            result = await a2a_tool._arun("file_agent", operation, f"Perform {operation}", parameters)
            return result
        except Exception as e:
            return f"File operation failed: {str(e)}"

class AnalysisToolInput(BaseModel):
    """Input schema for analysis operations"""
    operation: str = Field(description="Analysis operation: analyze_data, pattern_recognition, generate_insights, compare_datasets")
    parameters: Dict[str, Any] = Field(description="Operation parameters")

class AnalysisTool(BaseTool):
    """LangChain tool for analysis operations via Analysis Agent"""
    
    name: str = "analysis"
    description: str = "Analyze data, identify patterns, generate insights, and compare datasets"
    args_schema: Type[BaseModel] = AnalysisToolInput
    
    def __init__(self, analysis_agent_endpoint: str, **kwargs):
        super().__init__(**kwargs)
        self.analysis_agent_endpoint = analysis_agent_endpoint
    
    def _run(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self._arun(operation, parameters))
    
    async def _arun(self, operation: str, parameters: Dict[str, Any], run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        try:
            a2a_tool = A2ATool({"analysis_agent": self.analysis_agent_endpoint})
            result = await a2a_tool._arun("analysis_agent", operation, f"Perform {operation}", parameters)
            return result
        except Exception as e:
            return f"Analysis operation failed: {str(e)}"

class AgentRegistryTool(BaseTool):
    """Tool to query available agents and their capabilities"""
    
    name: str = "agent_registry"
    description: str = "Query available agents and their capabilities in the multi-agent system"
    
    def __init__(self, agent_registry: Dict[str, str], **kwargs):
        super().__init__(**kwargs)
        self.agent_registry = agent_registry
    
    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self._arun())
    
    async def _arun(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Query all agents for their capabilities"""
        try:
            agent_info = {}
            
            for agent_id, endpoint in self.agent_registry.items():
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{endpoint}/capabilities")
                        if response.status_code == 200:
                            agent_info[agent_id] = response.json()
                        else:
                            agent_info[agent_id] = {"error": f"Failed to get capabilities: {response.status_code}"}
                except Exception as e:
                    agent_info[agent_id] = {"error": str(e)}
            
            # Format the response
            result = "Available Agents and Capabilities:\n\n"
            for agent_id, info in agent_info.items():
                result += f"Agent: {agent_id}\n"
                if "error" in info:
                    result += f"  Status: Error - {info['error']}\n"
                else:
                    result += f"  Name: {info.get('name', 'Unknown')}\n"
                    result += f"  Description: {info.get('description', 'No description')}\n"
                    capabilities = info.get('capabilities', [])
                    if capabilities:
                        result += "  Capabilities:\n"
                        for cap in capabilities:
                            result += f"    - {cap.get('name', 'Unknown')}: {cap.get('description', 'No description')}\n"
                    else:
                        result += "  Capabilities: None registered\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error querying agent registry: {str(e)}"

def create_langchain_tools(agent_registry: Dict[str, str]) -> List[BaseTool]:
    """Create LangChain tools for all agents"""
    tools = []
    
    # Add general A2A tool
    tools.append(A2ATool(agent_registry))
    
    # Add agent registry tool
    tools.append(AgentRegistryTool(agent_registry))
    
    # Add specialized tools for each agent type
    if "math_agent" in agent_registry:
        tools.append(MathTool(agent_registry["math_agent"]))
    
    if "web_agent" in agent_registry:
        tools.append(WebTool(agent_registry["web_agent"]))
    
    if "file_agent" in agent_registry:
        tools.append(FileTool(agent_registry["file_agent"]))
    
    if "analysis_agent" in agent_registry:
        tools.append(AnalysisTool(agent_registry["analysis_agent"]))
    
    return tools