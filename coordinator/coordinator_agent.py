"""
Coordinator Agent - Main orchestration agent using LangChain
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI
import uvicorn
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from coordinator.langchain_tools import create_langchain_tools
import logging

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """Main coordinator agent that orchestrates multi-agent workflows"""
    
    def __init__(self, port: int = 8000, openai_api_key: Optional[str] = None):
        self.port = port
        self.agent_registry = {}
        
        # Initialize OpenAI LLM
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
        
        # Initialize FastAPI app
        self.app = FastAPI(title="Coordinator Agent")
        self._setup_endpoints()
        
        # Initialize LangChain agent
        self.agent_executor = None
        self._initialize_agent()
    
    def _setup_endpoints(self):
        """Setup HTTP endpoints"""
        
        @self.app.post("/execute_task")
        async def execute_task(task_data: Dict[str, Any]):
            """Execute a complex task using the multi-agent system"""
            try:
                task_description = task_data.get("description", "")
                context = task_data.get("context", {})
                
                if not task_description:
                    return {"error": "Task description is required"}
                
                result = await self.execute_task(task_description, context)
                return {"result": result, "status": "completed"}
                
            except Exception as e:
                logger.error(f"Error executing task: {e}")
                return {"error": str(e), "status": "failed"}
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            return {"agents": self.agent_registry}
        
        @self.app.post("/register_agent")
        async def register_agent(agent_data: Dict[str, str]):
            """Register a new agent"""
            agent_id = agent_data.get("agent_id")
            endpoint = agent_data.get("endpoint")
            
            if not agent_id or not endpoint:
                return {"error": "agent_id and endpoint are required"}
            
            self.register_agent(agent_id, endpoint)
            return {"message": f"Agent {agent_id} registered successfully"}
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "registered_agents": len(self.agent_registry)}
    
    def register_agent(self, agent_id: str, endpoint: str):
        """Register an agent with the coordinator"""
        self.agent_registry[agent_id] = endpoint
        logger.info(f"Registered agent: {agent_id} at {endpoint}")
        
        # Reinitialize agent with updated registry
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize LangChain agent with tools"""
        if not self.agent_registry:
            logger.warning("No agents registered yet. Agent will be initialized when agents are registered.")
            return
        
        # Create tools
        tools = create_langchain_tools(self.agent_registry)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Coordinator Agent in a multi-agent system. Your role is to:

1. Analyze complex tasks and break them down into subtasks
2. Delegate subtasks to appropriate specialized agents
3. Coordinate between agents when collaboration is needed
4. Synthesize results from multiple agents into a comprehensive response

Available agents and their capabilities:
- math_agent: Mathematical calculations, equation solving, statistical analysis, matrix operations
- web_agent: Web search, webpage scraping, research, information verification
- file_agent: File operations, data storage, text processing, structured data management
- analysis_agent: Data analysis, pattern recognition, insight generation, dataset comparison

Guidelines:
- Always use the agent_registry tool first to check current agent status
- Choose the most appropriate agent for each subtask
- When tasks require multiple agents, coordinate their work effectively
- Provide clear, comprehensive responses that synthesize all results
- Handle errors gracefully and provide alternative approaches when needed

Remember: You can use multiple agents in sequence or parallel to accomplish complex tasks."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
        
        logger.info(f"Coordinator agent initialized with {len(tools)} tools")
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Execute a complex task using the multi-agent system"""
        if not self.agent_executor:
            return "Error: No agents registered. Cannot execute tasks."
        
        try:
            # Add context to the task if provided
            full_input = task_description
            if context:
                full_input += f"\n\nAdditional context: {context}"
            
            # Execute the task using LangChain agent
            result = await self.agent_executor.ainvoke({"input": full_input})
            
            return result.get("output", "Task completed but no output generated")
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return f"Error executing task: {str(e)}"
    
    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a predefined workflow with multiple steps"""
        results = {}
        
        try:
            for i, step in enumerate(workflow_steps):
                step_name = step.get("name", f"step_{i}")
                step_description = step.get("description", "")
                step_context = step.get("context", {})
                
                # Add results from previous steps to context
                step_context.update({"previous_results": results})
                
                logger.info(f"Executing workflow step: {step_name}")
                
                step_result = await self.execute_task(step_description, step_context)
                results[step_name] = step_result
                
                logger.info(f"Completed workflow step: {step_name}")
            
            return {
                "workflow_results": results,
                "status": "completed",
                "total_steps": len(workflow_steps)
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "workflow_results": results,
                "status": "failed",
                "error": str(e),
                "completed_steps": len(results)
            }
    
    async def analyze_and_plan(self, complex_task: str) -> Dict[str, Any]:
        """Analyze a complex task and create an execution plan"""
        try:
            planning_prompt = f"""
            Analyze this complex task and create a detailed execution plan:
            
            Task: {complex_task}
            
            Please:
            1. Break down the task into logical subtasks
            2. Identify which agents would be best for each subtask
            3. Determine if any subtasks need to be executed in sequence or can be parallel
            4. Identify any dependencies between subtasks
            5. Estimate the complexity and time for each subtask
            
            Provide a structured plan that can be executed step by step.
            """
            
            plan_result = await self.execute_task(planning_prompt)
            
            return {
                "original_task": complex_task,
                "execution_plan": plan_result,
                "status": "plan_created"
            }
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            return {
                "original_task": complex_task,
                "error": str(e),
                "status": "plan_failed"
            }
    
    async def start(self, host: str = "localhost"):
        """Start the coordinator agent server"""
        logger.info(f"Starting Coordinator Agent on {host}:{self.port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self, host: str = "localhost"):
        """Run the coordinator agent server (blocking)"""
        uvicorn.run(self.app, host=host, port=self.port)

# Example usage and predefined workflows
class WorkflowTemplates:
    """Predefined workflow templates for common tasks"""
    
    @staticmethod
    def data_analysis_workflow(data_source: str) -> List[Dict[str, Any]]:
        """Workflow for comprehensive data analysis"""
        return [
            {
                "name": "data_collection",
                "description": f"Collect and load data from {data_source}",
                "context": {"data_source": data_source}
            },
            {
                "name": "statistical_analysis",
                "description": "Perform statistical analysis on the collected data",
                "context": {"analysis_type": "descriptive"}
            },
            {
                "name": "pattern_recognition",
                "description": "Identify patterns and trends in the data",
                "context": {"pattern_types": ["trend", "seasonal", "anomaly"]}
            },
            {
                "name": "insight_generation",
                "description": "Generate actionable insights from the analysis results",
                "context": {"business_context": "data analysis project"}
            },
            {
                "name": "report_generation",
                "description": "Create a comprehensive report with all findings and recommendations",
                "context": {"report_format": "detailed"}
            }
        ]
    
    @staticmethod
    def research_workflow(research_topic: str) -> List[Dict[str, Any]]:
        """Workflow for comprehensive research"""
        return [
            {
                "name": "initial_research",
                "description": f"Conduct initial web research on {research_topic}",
                "context": {"topic": research_topic, "depth": "comprehensive"}
            },
            {
                "name": "source_verification",
                "description": "Verify the credibility of found sources and information",
                "context": {"verification_level": "high"}
            },
            {
                "name": "data_compilation",
                "description": "Compile and organize all research findings into structured format",
                "context": {"format": "structured_report"}
            },
            {
                "name": "analysis",
                "description": "Analyze the compiled research data for insights and patterns",
                "context": {"analysis_type": "comprehensive"}
            },
            {
                "name": "summary_generation",
                "description": "Generate executive summary and key findings",
                "context": {"audience": "general"}
            }
        ]

if __name__ == "__main__":
    import asyncio
    
    async def main():
        coordinator = CoordinatorAgent()
        
        # Register default agents (assuming they're running)
        coordinator.register_agent("math_agent", "http://localhost:8001")
        coordinator.register_agent("web_agent", "http://localhost:8002")
        coordinator.register_agent("file_agent", "http://localhost:8003")
        coordinator.register_agent("analysis_agent", "http://localhost:8004")
        
        await coordinator.start()
    
    asyncio.run(main())