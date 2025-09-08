"""
Math MCP Server - Provides mathematical computation tools
"""
import math
import numpy as np
from typing import Union, List
from protocols.mcp import MCPServer
import logging

logger = logging.getLogger(__name__)

class MathMCPServer(MCPServer):
    """MCP Server for mathematical operations"""
    
    def __init__(self, port: int = 9001):
        super().__init__("Math Server", "Mathematical computation tools", port)
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup mathematical tools"""
        
        @self.tool(
            name="calculate",
            description="Evaluate a mathematical expression safely",
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            }
        )
        async def calculate(expression: str) -> str:
            """Safely evaluate mathematical expressions"""
            try:
                # Create a safe evaluation environment
                safe_dict = {
                    "__builtins__": {},
                    "abs": abs, "round": round, "min": min, "max": max,
                    "sum": sum, "pow": pow, "divmod": divmod,
                    "math": math, "np": np,
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
                    "exp": math.exp, "pi": math.pi, "e": math.e
                }
                
                result = eval(expression, safe_dict, {})
                return f"Result: {expression} = {result}"
            except Exception as e:
                return f"Error evaluating expression '{expression}': {str(e)}"
        
        @self.tool(
            name="solve_quadratic",
            description="Solve quadratic equation ax² + bx + c = 0",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Coefficient of x²"},
                    "b": {"type": "number", "description": "Coefficient of x"},
                    "c": {"type": "number", "description": "Constant term"}
                },
                "required": ["a", "b", "c"]
            }
        )
        async def solve_quadratic(a: float, b: float, c: float) -> str:
            """Solve quadratic equations"""
            if a == 0:
                if b == 0:
                    return "Not a valid equation (both a and b are zero)"
                else:
                    x = -c / b
                    return f"Linear equation solution: x = {x}"
            
            discriminant = b**2 - 4*a*c
            
            if discriminant > 0:
                x1 = (-b + math.sqrt(discriminant)) / (2*a)
                x2 = (-b - math.sqrt(discriminant)) / (2*a)
                return f"Two real solutions: x₁ = {x1}, x₂ = {x2}"
            elif discriminant == 0:
                x = -b / (2*a)
                return f"One real solution: x = {x}"
            else:
                real_part = -b / (2*a)
                imag_part = math.sqrt(-discriminant) / (2*a)
                return f"Two complex solutions: x₁ = {real_part} + {imag_part}i, x₂ = {real_part} - {imag_part}i"
        
        @self.tool(
            name="statistics",
            description="Calculate statistical measures for a dataset",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Array of numerical data"
                    }
                },
                "required": ["data"]
            }
        )
        async def statistics(data: List[float]) -> str:
            """Calculate statistical measures"""
            if not data:
                return "Error: Empty dataset provided"
            
            try:
                arr = np.array(data)
                stats = {
                    "count": len(data),
                    "mean": float(np.mean(arr)),
                    "median": float(np.median(arr)),
                    "std_dev": float(np.std(arr)),
                    "variance": float(np.var(arr)),
                    "min": float(np.min(arr)),
                    "max": float(np.max(arr)),
                    "sum": float(np.sum(arr))
                }
                
                result = "Statistical Analysis:\n"
                for key, value in stats.items():
                    result += f"  {key.replace('_', ' ').title()}: {value}\n"
                
                return result.strip()
            except Exception as e:
                return f"Error calculating statistics: {str(e)}"
        
        @self.tool(
            name="matrix_operations",
            description="Perform matrix operations (multiply, add, determinant, etc.)",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["multiply", "add", "subtract", "determinant", "transpose", "inverse"],
                        "description": "Matrix operation to perform"
                    },
                    "matrix_a": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "number"}},
                        "description": "First matrix (2D array)"
                    },
                    "matrix_b": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "number"}},
                        "description": "Second matrix (2D array) - optional for some operations"
                    }
                },
                "required": ["operation", "matrix_a"]
            }
        )
        async def matrix_operations(operation: str, matrix_a: List[List[float]], 
                                  matrix_b: List[List[float]] = None) -> str:
            """Perform matrix operations"""
            try:
                A = np.array(matrix_a)
                
                if operation == "transpose":
                    result = np.transpose(A)
                    return f"Transpose:\n{result.tolist()}"
                
                elif operation == "determinant":
                    if A.shape[0] != A.shape[1]:
                        return "Error: Determinant requires a square matrix"
                    det = np.linalg.det(A)
                    return f"Determinant: {det}"
                
                elif operation == "inverse":
                    if A.shape[0] != A.shape[1]:
                        return "Error: Inverse requires a square matrix"
                    try:
                        inv = np.linalg.inv(A)
                        return f"Inverse:\n{inv.tolist()}"
                    except np.linalg.LinAlgError:
                        return "Error: Matrix is singular (not invertible)"
                
                elif operation in ["multiply", "add", "subtract"]:
                    if matrix_b is None:
                        return f"Error: Operation '{operation}' requires two matrices"
                    
                    B = np.array(matrix_b)
                    
                    if operation == "multiply":
                        if A.shape[1] != B.shape[0]:
                            return f"Error: Cannot multiply matrices with shapes {A.shape} and {B.shape}"
                        result = np.dot(A, B)
                    elif operation == "add":
                        if A.shape != B.shape:
                            return f"Error: Cannot add matrices with different shapes {A.shape} and {B.shape}"
                        result = A + B
                    elif operation == "subtract":
                        if A.shape != B.shape:
                            return f"Error: Cannot subtract matrices with different shapes {A.shape} and {B.shape}"
                        result = A - B
                    
                    return f"Result of {operation}:\n{result.tolist()}"
                
                else:
                    return f"Error: Unknown operation '{operation}'"
                    
            except Exception as e:
                return f"Error performing matrix operation: {str(e)}"

if __name__ == "__main__":
    import asyncio
    
    async def main():
        server = MathMCPServer()
        await server.start()
    
    asyncio.run(main())