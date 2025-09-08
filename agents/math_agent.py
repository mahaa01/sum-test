"""
Math Agent - Specialized in mathematical computations
"""
import uuid
from typing import Dict, Any
from agents.base import BaseA2AAgent
from protocols.a2a import TaskRequest
import logging

logger = logging.getLogger(__name__)

class MathAgent(BaseA2AAgent):
    """Agent specialized in mathematical operations"""
    
    def __init__(self, port: int = 8001, mcp_math_port: int = 9001):
        super().__init__(
            agent_id="math_agent",
            name="Math Agent",
            description="Specialized agent for mathematical computations and analysis",
            port=port
        )
        
        # Connect to Math MCP server
        self.add_mcp_server("math", f"http://localhost:{mcp_math_port}")
        
        # Register capabilities
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register mathematical capabilities"""
        
        self.register_capability(
            name="calculate",
            description="Evaluate mathematical expressions",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression"}
                },
                "required": ["expression"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "Calculation result"}
                }
            },
            cost=1.0
        )
        
        self.register_capability(
            name="solve_equation",
            description="Solve mathematical equations",
            input_schema={
                "type": "object",
                "properties": {
                    "equation_type": {"type": "string", "enum": ["quadratic", "linear"]},
                    "coefficients": {"type": "object", "description": "Equation coefficients"}
                },
                "required": ["equation_type", "coefficients"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "solution": {"type": "string", "description": "Equation solution"}
                }
            },
            cost=2.0
        )
        
        self.register_capability(
            name="statistics",
            description="Calculate statistical measures",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"type": "number"}},
                    "measures": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "statistics": {"type": "object", "description": "Statistical results"}
                }
            },
            cost=1.5
        )
        
        self.register_capability(
            name="matrix_operations",
            description="Perform matrix operations",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["multiply", "add", "subtract", "determinant", "transpose", "inverse"]},
                    "matrices": {"type": "array", "description": "Input matrices"}
                },
                "required": ["operation", "matrices"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "object", "description": "Operation result"}
                }
            },
            cost=2.5
        )
    
    async def process_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process mathematical tasks"""
        task_type = task_request.task_type
        params = task_request.parameters
        
        try:
            if task_type == "calculate":
                expression = params.get("expression")
                if not expression:
                    raise ValueError("Expression is required for calculation")
                
                result = await self.mcp_client.call_tool(
                    "math", "calculate", {"expression": expression}
                )
                
                return {"result": result, "type": "calculation"}
            
            elif task_type == "solve_equation":
                equation_type = params.get("equation_type")
                coefficients = params.get("coefficients", {})
                
                if equation_type == "quadratic":
                    a = coefficients.get("a")
                    b = coefficients.get("b")
                    c = coefficients.get("c")
                    
                    if None in [a, b, c]:
                        raise ValueError("Quadratic equation requires coefficients a, b, and c")
                    
                    result = await self.mcp_client.call_tool(
                        "math", "solve_quadratic", {"a": a, "b": b, "c": c}
                    )
                    
                    return {"solution": result, "type": "equation_solution"}
                else:
                    raise ValueError(f"Unsupported equation type: {equation_type}")
            
            elif task_type == "statistics":
                data = params.get("data")
                if not data:
                    raise ValueError("Data is required for statistical analysis")
                
                result = await self.mcp_client.call_tool(
                    "math", "statistics", {"data": data}
                )
                
                return {"statistics": result, "type": "statistical_analysis"}
            
            elif task_type == "matrix_operations":
                operation = params.get("operation")
                matrices = params.get("matrices", [])
                
                if not operation:
                    raise ValueError("Operation is required for matrix operations")
                
                if not matrices:
                    raise ValueError("At least one matrix is required")
                
                # Prepare arguments based on operation
                if operation in ["multiply", "add", "subtract"]:
                    if len(matrices) < 2:
                        raise ValueError(f"Operation '{operation}' requires two matrices")
                    
                    result = await self.mcp_client.call_tool(
                        "math", "matrix_operations", {
                            "operation": operation,
                            "matrix_a": matrices[0],
                            "matrix_b": matrices[1]
                        }
                    )
                else:
                    result = await self.mcp_client.call_tool(
                        "math", "matrix_operations", {
                            "operation": operation,
                            "matrix_a": matrices[0]
                        }
                    )
                
                return {"result": result, "type": "matrix_operation"}
            
            elif task_type == "complex_calculation":
                # Handle complex multi-step calculations
                steps = params.get("steps", [])
                results = []
                
                for i, step in enumerate(steps):
                    step_result = await self.mcp_client.call_tool(
                        "math", "calculate", {"expression": step}
                    )
                    results.append(f"Step {i+1}: {step_result}")
                
                return {"results": results, "type": "complex_calculation"}
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        
        except Exception as e:
            logger.error(f"Error processing math task: {e}")
            raise
    
    async def collaborate_with_analysis_agent(self, data: list, analysis_type: str) -> Dict[str, Any]:
        """Collaborate with analysis agent for complex data analysis"""
        try:
            # First, calculate basic statistics
            stats_result = await self.process_task(TaskRequest(
                task_id=str(uuid.uuid4()),
                task_type="statistics",
                description="Calculate basic statistics",
                parameters={"data": data}
            ))
            
            # Then request analysis from analysis agent
            analysis_response = await self.request_task_from_peer(
                "analysis_agent",
                "analyze_data",
                f"Perform {analysis_type} analysis on statistical results",
                {
                    "statistics": stats_result,
                    "raw_data": data,
                    "analysis_type": analysis_type
                }
            )
            
            return {
                "statistics": stats_result,
                "analysis": analysis_response.result,
                "collaboration": "math_agent + analysis_agent"
            }
            
        except Exception as e:
            logger.error(f"Error in collaboration: {e}")
            raise

if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = MathAgent()
        await agent.start()
    
    asyncio.run(main())