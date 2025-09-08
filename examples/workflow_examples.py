"""
Workflow Examples for the Multi-Agent System
"""
import asyncio
import json
import httpx
from typing import Dict, Any, List

class WorkflowExamples:
    """Examples of complex workflows using the multi-agent system"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8000"):
        self.coordinator_url = coordinator_url
    
    async def data_analysis_workflow(self):
        """Example: Comprehensive data analysis workflow"""
        print("📊 Data Analysis Workflow Example")
        print("-" * 40)
        
        workflow_description = """
        Perform a comprehensive data analysis workflow:
        
        1. Create a dataset with sales data for 12 months: [100, 120, 110, 130, 140, 135, 150, 160, 145, 170, 180, 190]
        2. Calculate comprehensive statistics (mean, median, standard deviation, etc.)
        3. Identify patterns and trends in the data
        4. Generate insights and recommendations
        5. Save all results to a structured report file
        
        Please coordinate between math, analysis, and file agents to complete this workflow.
        """
        
        await self._execute_workflow("Data Analysis", workflow_description)
    
    async def research_and_analysis_workflow(self):
        """Example: Research and analysis workflow"""
        print("🔍 Research and Analysis Workflow Example")
        print("-" * 40)
        
        workflow_description = """
        Conduct research and analysis on artificial intelligence:
        
        1. Search for recent information about artificial intelligence trends
        2. Collect and verify information from multiple sources
        3. Save the research findings to a structured file
        4. Analyze the collected data for key themes and patterns
        5. Generate a summary report with insights and recommendations
        
        Coordinate between web, file, and analysis agents for this comprehensive research task.
        """
        
        await self._execute_workflow("Research & Analysis", workflow_description)
    
    async def mathematical_modeling_workflow(self):
        """Example: Mathematical modeling and visualization workflow"""
        print("📐 Mathematical Modeling Workflow Example")
        print("-" * 40)
        
        workflow_description = """
        Create a mathematical model and analysis:
        
        1. Solve the quadratic equation: 2x² - 7x + 3 = 0
        2. Create a dataset of function values for f(x) = 2x² - 7x + 3 where x ranges from -5 to 5
        3. Calculate statistics for this dataset
        4. Identify patterns in the function behavior
        5. Save the mathematical model results and analysis to a comprehensive report
        
        Use math and analysis agents to complete this mathematical modeling task.
        """
        
        await self._execute_workflow("Mathematical Modeling", workflow_description)
    
    async def content_processing_workflow(self):
        """Example: Content processing and analysis workflow"""
        print("📄 Content Processing Workflow Example")
        print("-" * 40)
        
        workflow_description = """
        Process and analyze content:
        
        1. Create a sample text document about machine learning with key concepts and definitions
        2. Save this content to a file in the workspace
        3. Search the file for specific patterns and keywords related to AI and ML
        4. Analyze the content structure and extract key insights
        5. Generate a summary report of the content analysis
        
        Coordinate between file and analysis agents for this content processing task.
        """
        
        await self._execute_workflow("Content Processing", workflow_description)
    
    async def multi_agent_collaboration_workflow(self):
        """Example: Complex multi-agent collaboration"""
        print("🤝 Multi-Agent Collaboration Workflow Example")
        print("-" * 40)
        
        workflow_description = """
        Demonstrate complex multi-agent collaboration:
        
        1. Search the web for current stock market information or economic data
        2. Extract numerical data from the search results
        3. Perform statistical analysis on the extracted numbers
        4. Identify trends and patterns in the economic data
        5. Save all findings to a structured JSON report
        6. Generate actionable insights and recommendations based on the analysis
        
        This requires coordination between ALL agents: web, math, file, and analysis agents.
        """
        
        await self._execute_workflow("Multi-Agent Collaboration", workflow_description)
    
    async def _execute_workflow(self, workflow_name: str, description: str):
        """Execute a workflow and display results"""
        print(f"🚀 Starting {workflow_name} workflow...")
        print(f"📋 Task: {description[:100]}...")
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.coordinator_url}/execute_task",
                    json={"description": description},
                    timeout=120.0  # 2 minutes timeout for complex workflows
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("status") == "completed":
                        print("✅ Workflow completed successfully!")
                        print(f"📊 Result: {result.get('result', '')[:500]}...")
                        if len(result.get('result', '')) > 500:
                            print("    [Result truncated for display]")
                    else:
                        print("❌ Workflow failed!")
                        print(f"🚨 Error: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"🚨 Response: {response.text}")
                    
            except asyncio.TimeoutError:
                print("⏰ Workflow timed out (this is normal for complex tasks)")
            except Exception as e:
                print(f"🚨 Workflow execution error: {e}")
        
        print("\n" + "="*60 + "\n")
    
    async def run_predefined_workflow(self, workflow_type: str):
        """Run a predefined workflow using the coordinator's workflow templates"""
        print(f"🎯 Running Predefined {workflow_type} Workflow")
        print("-" * 40)
        
        # This would use the coordinator's WorkflowTemplates
        # For now, we'll demonstrate with a simple task
        if workflow_type.lower() == "data_analysis":
            await self.data_analysis_workflow()
        elif workflow_type.lower() == "research":
            await self.research_and_analysis_workflow()
        else:
            print(f"❌ Unknown workflow type: {workflow_type}")
    
    async def demonstrate_agent_capabilities(self):
        """Demonstrate individual agent capabilities"""
        print("🔧 Agent Capabilities Demonstration")
        print("-" * 40)
        
        capabilities_demo = [
            {
                "agent": "Math Agent",
                "task": "Calculate the area of a circle with radius 7, then find the volume of a sphere with the same radius"
            },
            {
                "agent": "Web Agent", 
                "task": "Search for information about Python programming best practices"
            },
            {
                "agent": "File Agent",
                "task": "Create a CSV file with sample employee data and then read it back"
            },
            {
                "agent": "Analysis Agent",
                "task": "Analyze the pattern in this sequence: [2, 4, 8, 16, 32, 64] and predict the next number"
            }
        ]
        
        for demo in capabilities_demo:
            print(f"🤖 {demo['agent']}: {demo['task']}")
            await self._execute_workflow(demo['agent'], demo['task'])
    
    async def run_all_examples(self):
        """Run all workflow examples"""
        print("🌟 Multi-Agent System Workflow Examples")
        print("=" * 60)
        print()
        
        # Individual agent demonstrations
        await self.demonstrate_agent_capabilities()
        
        # Complex workflows
        await self.data_analysis_workflow()
        await self.research_and_analysis_workflow()
        await self.mathematical_modeling_workflow()
        await self.content_processing_workflow()
        await self.multi_agent_collaboration_workflow()
        
        print("🎉 All workflow examples completed!")
        print("=" * 60)

async def main():
    """Main function to run workflow examples"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent System Workflow Examples")
    parser.add_argument("--workflow", choices=["data_analysis", "research", "math", "content", "collaboration", "all"], 
                       default="all", help="Specific workflow to run")
    parser.add_argument("--coordinator-url", default="http://localhost:8000", 
                       help="Coordinator URL")
    
    args = parser.parse_args()
    
    examples = WorkflowExamples(args.coordinator_url)
    
    if args.workflow == "all":
        await examples.run_all_examples()
    elif args.workflow == "data_analysis":
        await examples.data_analysis_workflow()
    elif args.workflow == "research":
        await examples.research_and_analysis_workflow()
    elif args.workflow == "math":
        await examples.mathematical_modeling_workflow()
    elif args.workflow == "content":
        await examples.content_processing_workflow()
    elif args.workflow == "collaboration":
        await examples.multi_agent_collaboration_workflow()

if __name__ == "__main__":
    print("Multi-Agent System Workflow Examples")
    print("Make sure the system is running (python main.py) before running examples")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Examples failed: {e}")