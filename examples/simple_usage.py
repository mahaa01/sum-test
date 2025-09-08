"""
Simple Usage Examples for the Multi-Agent System
"""
import asyncio
import httpx
import json

async def simple_math_calculation():
    """Simple math calculation example"""
    print("🧮 Simple Math Calculation")
    print("-" * 30)
    
    # Direct call to coordinator
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/execute_task",
                json={
                    "description": "Calculate the result of 15 * 8 + 42 / 6"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Result: {result.get('result', 'No result')}")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

async def simple_web_search():
    """Simple web search example"""
    print("🔍 Simple Web Search")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/execute_task",
                json={
                    "description": "Search for information about machine learning and summarize the key points"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Search completed")
                print(f"📋 Summary: {result.get('result', 'No result')[:200]}...")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

async def simple_file_operation():
    """Simple file operation example"""
    print("📁 Simple File Operation")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/execute_task",
                json={
                    "description": "Create a file called 'hello.txt' with the content 'Hello from Multi-Agent System!' and then read it back"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ File operation completed")
                print(f"📄 Result: {result.get('result', 'No result')[:200]}...")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

async def simple_data_analysis():
    """Simple data analysis example"""
    print("📊 Simple Data Analysis")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/execute_task",
                json={
                    "description": "Analyze this dataset [10, 15, 20, 25, 30, 35, 40] and provide statistical insights"
                },
                timeout=45.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Analysis completed")
                print(f"📈 Insights: {result.get('result', 'No result')[:300]}...")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

async def combined_task_example():
    """Example combining multiple agents"""
    print("🤝 Combined Multi-Agent Task")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/execute_task",
                json={
                    "description": "Calculate the mean and standard deviation of [5, 10, 15, 20, 25], then analyze the pattern and save the results to a file called 'analysis_results.txt'"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Combined task completed")
                print(f"🎯 Result: {result.get('result', 'No result')[:400]}...")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()

async def check_system_status():
    """Check if the system is running"""
    print("🔍 Checking System Status")
    print("-" * 30)
    
    agents = {
        "Coordinator": "http://localhost:8000/health",
        "Math Agent": "http://localhost:8001/health",
        "Web Agent": "http://localhost:8002/health",
        "File Agent": "http://localhost:8003/health",
        "Analysis Agent": "http://localhost:8004/health"
    }
    
    async with httpx.AsyncClient() as client:
        for name, url in agents.items():
            try:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    print(f"  ✅ {name}: Running")
                else:
                    print(f"  ❌ {name}: Error (HTTP {response.status_code})")
            except Exception as e:
                print(f"  ❌ {name}: Not accessible ({e})")
    
    print()

async def main():
    """Run simple usage examples"""
    print("🚀 Multi-Agent System - Simple Usage Examples")
    print("=" * 50)
    print()
    
    # Check system status first
    await check_system_status()
    
    # Run simple examples
    await simple_math_calculation()
    await simple_web_search()
    await simple_file_operation()
    await simple_data_analysis()
    await combined_task_example()
    
    print("=" * 50)
    print("🎉 Simple examples completed!")
    print()
    print("💡 Tips:")
    print("  • For more complex workflows, see workflow_examples.py")
    print("  • For comprehensive testing, run test_multi_agent.py")
    print("  • Check the /workspace directory for created files")

if __name__ == "__main__":
    print("Simple Usage Examples for Multi-Agent System")
    print("Make sure the system is running (python main.py) first!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Examples failed: {e}")
        print("\nMake sure the system is running with: python main.py")