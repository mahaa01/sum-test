"""
Test script for the Multi-Agent System
"""
import asyncio
import json
import httpx
from typing import Dict, Any

class MultiAgentTester:
    """Test suite for the multi-agent system"""
    
    def __init__(self):
        self.base_urls = {
            "coordinator": "http://localhost:8000",
            "math_agent": "http://localhost:8001",
            "web_agent": "http://localhost:8002",
            "file_agent": "http://localhost:8003",
            "analysis_agent": "http://localhost:8004"
        }
    
    async def test_health_checks(self):
        """Test health endpoints for all agents"""
        print("🔍 Testing health checks...")
        
        async with httpx.AsyncClient() as client:
            for agent_name, base_url in self.base_urls.items():
                try:
                    response = await client.get(f"{base_url}/health", timeout=5.0)
                    if response.status_code == 200:
                        print(f"  ✅ {agent_name}: Healthy")
                    else:
                        print(f"  ❌ {agent_name}: Unhealthy (status: {response.status_code})")
                except Exception as e:
                    print(f"  ❌ {agent_name}: Connection failed - {e}")
        print()
    
    async def test_agent_capabilities(self):
        """Test agent capability queries"""
        print("🔍 Testing agent capabilities...")
        
        async with httpx.AsyncClient() as client:
            for agent_name, base_url in self.base_urls.items():
                if agent_name == "coordinator":
                    continue  # Coordinator doesn't have capabilities endpoint
                
                try:
                    response = await client.get(f"{base_url}/capabilities", timeout=5.0)
                    if response.status_code == 200:
                        data = response.json()
                        capabilities = data.get("capabilities", [])
                        print(f"  ✅ {agent_name}: {len(capabilities)} capabilities")
                        for cap in capabilities[:2]:  # Show first 2
                            print(f"    - {cap.get('name', 'Unknown')}: {cap.get('description', 'No description')}")
                    else:
                        print(f"  ❌ {agent_name}: Failed to get capabilities")
                except Exception as e:
                    print(f"  ❌ {agent_name}: Error - {e}")
        print()
    
    async def test_math_agent(self):
        """Test math agent directly"""
        print("🔍 Testing Math Agent...")
        
        test_cases = [
            {
                "task_type": "calculate",
                "description": "Calculate 15 + 27 * 3",
                "parameters": {"expression": "15 + 27 * 3"}
            },
            {
                "task_type": "solve_equation",
                "description": "Solve quadratic equation x² - 5x + 6 = 0",
                "parameters": {
                    "equation_type": "quadratic",
                    "coefficients": {"a": 1, "b": -5, "c": 6}
                }
            },
            {
                "task_type": "statistics",
                "description": "Calculate statistics for sample data",
                "parameters": {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
            }
        ]
        
        await self._test_agent_tasks("math_agent", test_cases)
    
    async def test_web_agent(self):
        """Test web agent directly"""
        print("🔍 Testing Web Agent...")
        
        test_cases = [
            {
                "task_type": "search_web",
                "description": "Search for information about Python programming",
                "parameters": {"query": "Python programming language", "max_results": 3}
            },
            {
                "task_type": "check_url_status",
                "description": "Check if Google is accessible",
                "parameters": {"url": "https://www.google.com"}
            }
        ]
        
        await self._test_agent_tasks("web_agent", test_cases)
    
    async def test_file_agent(self):
        """Test file agent directly"""
        print("🔍 Testing File Agent...")
        
        test_cases = [
            {
                "task_type": "write_file",
                "description": "Create a test file",
                "parameters": {
                    "file_path": "/workspace/test_file.txt",
                    "content": "Hello from Multi-Agent System!\nThis is a test file created by the File Agent."
                }
            },
            {
                "task_type": "read_file",
                "description": "Read the test file",
                "parameters": {"file_path": "/workspace/test_file.txt"}
            },
            {
                "task_type": "list_directory",
                "description": "List workspace directory",
                "parameters": {"directory_path": "/workspace", "detailed": True}
            }
        ]
        
        await self._test_agent_tasks("file_agent", test_cases)
    
    async def test_analysis_agent(self):
        """Test analysis agent directly"""
        print("🔍 Testing Analysis Agent...")
        
        test_cases = [
            {
                "task_type": "analyze_data",
                "description": "Analyze sample dataset",
                "parameters": {
                    "data": {"values": [10, 20, 30, 40, 50], "type": "sales_data"},
                    "analysis_type": "descriptive",
                    "context": "Monthly sales analysis"
                }
            },
            {
                "task_type": "pattern_recognition",
                "description": "Identify trends in data",
                "parameters": {
                    "data": [1, 3, 5, 7, 9, 11, 13, 15],
                    "pattern_type": "trend"
                }
            }
        ]
        
        await self._test_agent_tasks("analysis_agent", test_cases)
    
    async def test_coordinator(self):
        """Test coordinator agent with complex tasks"""
        print("🔍 Testing Coordinator Agent...")
        
        if "coordinator" not in self.base_urls:
            print("  ⚠️  Coordinator not configured")
            return
        
        test_tasks = [
            "Calculate the square root of 144 and then find the factorial of that result",
            "Search for information about machine learning and save the results to a file",
            "Create a dataset with numbers 1 to 20, calculate statistics, and analyze patterns"
        ]
        
        async with httpx.AsyncClient() as client:
            for i, task in enumerate(test_tasks, 1):
                try:
                    print(f"  🎯 Task {i}: {task}")
                    
                    response = await client.post(
                        f"{self.base_urls['coordinator']}/execute_task",
                        json={"description": task},
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "completed":
                            print(f"    ✅ Completed successfully")
                            print(f"    📋 Result: {result.get('result', '')[:100]}...")
                        else:
                            print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"    ❌ HTTP Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                
                print()
    
    async def test_agent_collaboration(self):
        """Test agent collaboration through coordinator"""
        print("🔍 Testing Agent Collaboration...")
        
        collaboration_tasks = [
            {
                "description": "Use math agent to calculate statistics for data [1,2,3,4,5,6,7,8,9,10], then use analysis agent to identify patterns",
                "expected_agents": ["math_agent", "analysis_agent"]
            },
            {
                "description": "Search for Python tutorials online, save the results to a file, then analyze the content",
                "expected_agents": ["web_agent", "file_agent", "analysis_agent"]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for i, task_info in enumerate(collaboration_tasks, 1):
                try:
                    print(f"  🤝 Collaboration {i}: {task_info['description'][:60]}...")
                    
                    response = await client.post(
                        f"{self.base_urls['coordinator']}/execute_task",
                        json={"description": task_info["description"]},
                        timeout=120.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "completed":
                            print(f"    ✅ Collaboration successful")
                        else:
                            print(f"    ❌ Collaboration failed: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"    ❌ HTTP Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                
                print()
    
    async def _test_agent_tasks(self, agent_name: str, test_cases: list):
        """Helper method to test agent tasks"""
        async with httpx.AsyncClient() as client:
            for i, test_case in enumerate(test_cases, 1):
                try:
                    print(f"  🎯 Test {i}: {test_case['description']}")
                    
                    # Create A2A message
                    message = {
                        "id": f"test_{i}",
                        "type": "task_request",
                        "sender_id": "tester",
                        "recipient_id": agent_name,
                        "payload": {
                            "task_id": f"test_task_{i}",
                            "task_type": test_case["task_type"],
                            "description": test_case["description"],
                            "parameters": test_case["parameters"]
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_urls[agent_name]}/a2a/message",
                        json=message,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("type") == "task_response":
                            payload = result.get("payload", {})
                            if payload.get("status") == "completed":
                                print(f"    ✅ Success")
                            else:
                                print(f"    ❌ Failed: {payload.get('error', 'Unknown error')}")
                        else:
                            print(f"    ❌ Unexpected response type: {result.get('type')}")
                    else:
                        print(f"    ❌ HTTP Error: {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
        
        print()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Multi-Agent System Tests")
        print("=" * 50)
        
        # Basic connectivity tests
        await self.test_health_checks()
        await self.test_agent_capabilities()
        
        # Individual agent tests
        await self.test_math_agent()
        await self.test_web_agent()
        await self.test_file_agent()
        await self.test_analysis_agent()
        
        # Coordinator tests
        await self.test_coordinator()
        
        # Collaboration tests
        await self.test_agent_collaboration()
        
        print("=" * 50)
        print("🏁 Tests completed!")

async def main():
    """Main test function"""
    tester = MultiAgentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    print("Multi-Agent System Test Suite")
    print("Make sure the system is running (python main.py) before running tests")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"Test suite failed: {e}")