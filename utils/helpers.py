"""
Utility functions and helpers for the Multi-Agent System
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

def load_config(config_file: str = ".env") -> Dict[str, str]:
    """Load configuration from file"""
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def save_results(results: Dict[str, Any], filename: str, format: str = "json"):
    """Save results to file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if format.lower() == "json":
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif format.lower() == "txt":
            with open(filename, 'w') as f:
                f.write(str(results))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Results saved to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        return False

class AgentHealthChecker:
    """Utility class to check agent health and status"""
    
    def __init__(self, agent_registry: Dict[str, str]):
        self.agent_registry = agent_registry
    
    async def check_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered agents"""
        results = {}
        
        async with httpx.AsyncClient() as client:
            for agent_id, endpoint in self.agent_registry.items():
                results[agent_id] = await self.check_agent(client, agent_id, endpoint)
        
        return results
    
    async def check_agent(self, client: httpx.AsyncClient, agent_id: str, endpoint: str) -> Dict[str, Any]:
        """Check health of a specific agent"""
        try:
            # Health check
            health_response = await client.get(f"{endpoint}/health", timeout=5.0)
            health_status = health_response.status_code == 200
            
            # Capabilities check (if available)
            capabilities = []
            try:
                if agent_id != "coordinator":  # Coordinator doesn't have capabilities endpoint
                    cap_response = await client.get(f"{endpoint}/capabilities", timeout=5.0)
                    if cap_response.status_code == 200:
                        cap_data = cap_response.json()
                        capabilities = cap_data.get("capabilities", [])
            except:
                pass
            
            return {
                "status": "healthy" if health_status else "unhealthy",
                "endpoint": endpoint,
                "capabilities_count": len(capabilities),
                "last_checked": datetime.utcnow().isoformat(),
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "endpoint": endpoint,
                "capabilities_count": 0,
                "last_checked": datetime.utcnow().isoformat(),
                "error": str(e)
            }

class TaskExecutor:
    """Utility class for executing tasks on agents"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8000"):
        self.coordinator_url = coordinator_url
    
    async def execute_simple_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a simple task via coordinator"""
        async with httpx.AsyncClient() as client:
            try:
                payload = {"description": description}
                if context:
                    payload["context"] = context
                
                response = await client.post(
                    f"{self.coordinator_url}/execute_task",
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}",
                        "status": "failed",
                        "response": response.text
                    }
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "failed"
                }
    
    async def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a multi-step workflow"""
        results = {}
        
        for i, step in enumerate(workflow_steps):
            step_name = step.get("name", f"step_{i}")
            description = step.get("description", "")
            context = step.get("context", {})
            
            # Add previous results to context
            context["previous_results"] = results
            
            logger.info(f"Executing workflow step: {step_name}")
            
            step_result = await self.execute_simple_task(description, context)
            results[step_name] = step_result
            
            # Stop on error if specified
            if step.get("stop_on_error", False) and step_result.get("status") == "failed":
                break
        
        return {
            "workflow_results": results,
            "completed_steps": len(results),
            "total_steps": len(workflow_steps)
        }

class DataProcessor:
    """Utility class for processing and formatting data"""
    
    @staticmethod
    def format_agent_response(response: Dict[str, Any]) -> str:
        """Format agent response for display"""
        if response.get("status") == "completed":
            result = response.get("result", "")
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            return str(result)
        else:
            return f"Error: {response.get('error', 'Unknown error')}"
    
    @staticmethod
    def extract_numerical_data(text: str) -> List[float]:
        """Extract numerical data from text"""
        import re
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in numbers if n]
    
    @staticmethod
    def create_summary_report(results: Dict[str, Any]) -> str:
        """Create a summary report from results"""
        report = f"Summary Report - Generated at {datetime.utcnow().isoformat()}\n"
        report += "=" * 60 + "\n\n"
        
        for key, value in results.items():
            report += f"{key.replace('_', ' ').title()}:\n"
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    report += f"  {sub_key}: {sub_value}\n"
            else:
                report += f"  {value}\n"
            report += "\n"
        
        return report

class SystemMonitor:
    """System monitoring utilities"""
    
    def __init__(self, agent_registry: Dict[str, str]):
        self.agent_registry = agent_registry
        self.health_checker = AgentHealthChecker(agent_registry)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_health = await self.health_checker.check_all_agents()
        
        total_agents = len(self.agent_registry)
        healthy_agents = sum(1 for status in agent_health.values() if status["status"] == "healthy")
        
        return {
            "system_status": "healthy" if healthy_agents == total_agents else "degraded",
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "unhealthy_agents": total_agents - healthy_agents,
            "agent_details": agent_health,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def monitor_system(self, interval: int = 30, duration: int = 300):
        """Monitor system for a specified duration"""
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            status = await self.get_system_status()
            
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] System Status: {status['system_status']}")
            print(f"  Healthy: {status['healthy_agents']}/{status['total_agents']} agents")
            
            if status['system_status'] != 'healthy':
                unhealthy = [
                    agent_id for agent_id, details in status['agent_details'].items()
                    if details['status'] != 'healthy'
                ]
                print(f"  Issues with: {', '.join(unhealthy)}")
            
            await asyncio.sleep(interval)

def create_test_data(data_type: str = "numerical", size: int = 10) -> List[Any]:
    """Create test data for examples"""
    import random
    
    if data_type == "numerical":
        return [random.randint(1, 100) for _ in range(size)]
    elif data_type == "sales":
        return [random.randint(1000, 5000) for _ in range(12)]  # Monthly sales
    elif data_type == "text":
        words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
        return [random.choice(words) for _ in range(size)]
    else:
        return list(range(1, size + 1))

def validate_agent_response(response: Dict[str, Any]) -> bool:
    """Validate agent response format"""
    required_fields = ["status"]
    
    if not isinstance(response, dict):
        return False
    
    for field in required_fields:
        if field not in response:
            return False
    
    if response["status"] not in ["completed", "failed", "pending"]:
        return False
    
    return True

def format_execution_time(start_time: float, end_time: float) -> str:
    """Format execution time"""
    duration = end_time - start_time
    
    if duration < 1:
        return f"{duration*1000:.0f}ms"
    elif duration < 60:
        return f"{duration:.1f}s"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.1f}s"