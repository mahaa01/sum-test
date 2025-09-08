"""
Main launcher for the MCP-A2A-LangChain Multi-Agent System
"""
import asyncio
import os
import sys
import signal
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import all components
from mcp_servers.math_server import MathMCPServer
from mcp_servers.web_server import WebMCPServer
from mcp_servers.file_server import FileMCPServer
from agents.math_agent import MathAgent
from agents.web_agent import WebAgent
from agents.file_agent import FileAgent
from agents.analysis_agent import AnalysisAgent
from coordinator.coordinator_agent import CoordinatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configuration
        self.config = {
            "coordinator_port": int(os.getenv("COORDINATOR_PORT", 8000)),
            "math_agent_port": int(os.getenv("MATH_AGENT_PORT", 8001)),
            "web_agent_port": int(os.getenv("WEB_AGENT_PORT", 8002)),
            "file_agent_port": int(os.getenv("FILE_AGENT_PORT", 8003)),
            "analysis_agent_port": int(os.getenv("ANALYSIS_AGENT_PORT", 8004)),
            "mcp_math_port": int(os.getenv("MCP_MATH_PORT", 9001)),
            "mcp_web_port": int(os.getenv("MCP_WEB_PORT", 9002)),
            "mcp_file_port": int(os.getenv("MCP_FILE_PORT", 9003)),
        }
        
        # Components
        self.mcp_servers = {}
        self.agents = {}
        self.coordinator = None
        self.tasks = []
        
        # Shutdown event
        self.shutdown_event = asyncio.Event()
    
    async def start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info("Starting MCP servers...")
        
        # Math MCP Server
        math_server = MathMCPServer(self.config["mcp_math_port"])
        self.mcp_servers["math"] = math_server
        math_task = asyncio.create_task(math_server.start())
        self.tasks.append(math_task)
        
        # Web MCP Server
        web_server = WebMCPServer(self.config["mcp_web_port"])
        self.mcp_servers["web"] = web_server
        web_task = asyncio.create_task(web_server.start())
        self.tasks.append(web_task)
        
        # File MCP Server
        file_server = FileMCPServer(self.config["mcp_file_port"])
        self.mcp_servers["file"] = file_server
        file_task = asyncio.create_task(file_server.start())
        self.tasks.append(file_task)
        
        # Wait a bit for servers to start
        await asyncio.sleep(2)
        logger.info("MCP servers started successfully")
    
    async def start_agents(self):
        """Start all A2A agents"""
        logger.info("Starting A2A agents...")
        
        # Math Agent
        math_agent = MathAgent(
            port=self.config["math_agent_port"],
            mcp_math_port=self.config["mcp_math_port"]
        )
        self.agents["math_agent"] = math_agent
        
        # Web Agent
        web_agent = WebAgent(
            port=self.config["web_agent_port"],
            mcp_web_port=self.config["mcp_web_port"]
        )
        self.agents["web_agent"] = web_agent
        
        # File Agent
        file_agent = FileAgent(
            port=self.config["file_agent_port"],
            mcp_file_port=self.config["mcp_file_port"]
        )
        self.agents["file_agent"] = file_agent
        
        # Analysis Agent
        analysis_agent = AnalysisAgent(
            port=self.config["analysis_agent_port"]
        )
        self.agents["analysis_agent"] = analysis_agent
        
        # Setup peer connections
        agent_registry = {
            "math_agent": f"http://localhost:{self.config['math_agent_port']}",
            "web_agent": f"http://localhost:{self.config['web_agent_port']}",
            "file_agent": f"http://localhost:{self.config['file_agent_port']}",
            "analysis_agent": f"http://localhost:{self.config['analysis_agent_port']}"
        }
        
        for agent_id, agent in self.agents.items():
            for peer_id, peer_endpoint in agent_registry.items():
                if peer_id != agent_id:
                    agent.add_peer_agent(peer_id, peer_endpoint)
        
        # Start all agents
        for agent_id, agent in self.agents.items():
            agent_task = asyncio.create_task(agent.start())
            self.tasks.append(agent_task)
        
        # Wait a bit for agents to start
        await asyncio.sleep(2)
        logger.info("A2A agents started successfully")
        
        return agent_registry
    
    async def start_coordinator(self, agent_registry: Dict[str, str]):
        """Start the coordinator agent"""
        logger.info("Starting Coordinator Agent...")
        
        try:
            self.coordinator = CoordinatorAgent(port=self.config["coordinator_port"])
            
            # Register all agents
            for agent_id, endpoint in agent_registry.items():
                self.coordinator.register_agent(agent_id, endpoint)
            
            # Start coordinator
            coordinator_task = asyncio.create_task(self.coordinator.start())
            self.tasks.append(coordinator_task)
            
            # Wait a bit for coordinator to start
            await asyncio.sleep(2)
            logger.info("Coordinator Agent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start coordinator: {e}")
            logger.warning("Coordinator requires OpenAI API key. Set OPENAI_API_KEY environment variable.")
            # Continue without coordinator for basic functionality
    
    async def run_system_tests(self):
        """Run basic system tests"""
        logger.info("Running system tests...")
        
        try:
            if self.coordinator:
                # Test coordinator functionality
                test_result = await self.coordinator.execute_task(
                    "Test the system by checking agent registry and performing a simple calculation: 2 + 2"
                )
                logger.info(f"System test result: {test_result}")
            else:
                logger.info("Coordinator not available, skipping system tests")
                
        except Exception as e:
            logger.error(f"System test failed: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down Multi-Agent System...")
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("Multi-Agent System shutdown complete")
    
    async def start(self, run_tests: bool = False):
        """Start the complete multi-agent system"""
        try:
            logger.info("Starting MCP-A2A-LangChain Multi-Agent System...")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Start MCP servers
            await self.start_mcp_servers()
            
            # Start A2A agents
            agent_registry = await self.start_agents()
            
            # Start coordinator
            await self.start_coordinator(agent_registry)
            
            # Run tests if requested
            if run_tests:
                await self.run_system_tests()
            
            # Print system status
            self.print_system_status()
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"System startup failed: {e}")
            raise
        finally:
            await self.shutdown()
    
    def print_system_status(self):
        """Print system status and endpoints"""
        print("\n" + "="*80)
        print("MCP-A2A-LangChain Multi-Agent System - RUNNING")
        print("="*80)
        
        print("\n📊 MCP SERVERS:")
        print(f"  • Math Server:     http://localhost:{self.config['mcp_math_port']}")
        print(f"  • Web Server:      http://localhost:{self.config['mcp_web_port']}")
        print(f"  • File Server:     http://localhost:{self.config['mcp_file_port']}")
        
        print("\n🤖 A2A AGENTS:")
        print(f"  • Math Agent:      http://localhost:{self.config['math_agent_port']}")
        print(f"  • Web Agent:       http://localhost:{self.config['web_agent_port']}")
        print(f"  • File Agent:      http://localhost:{self.config['file_agent_port']}")
        print(f"  • Analysis Agent:  http://localhost:{self.config['analysis_agent_port']}")
        
        print("\n🎯 COORDINATOR:")
        if self.coordinator:
            print(f"  • Coordinator:     http://localhost:{self.config['coordinator_port']}")
            print(f"  • Task Endpoint:   http://localhost:{self.config['coordinator_port']}/execute_task")
        else:
            print("  • Coordinator:     NOT AVAILABLE (requires OpenAI API key)")
        
        print("\n📋 QUICK TESTS:")
        print("  • Health Check:    curl http://localhost:8001/health")
        print("  • Agent Registry:  curl http://localhost:8000/agents")
        if self.coordinator:
            print("  • Execute Task:    curl -X POST http://localhost:8000/execute_task \\")
            print("                       -H 'Content-Type: application/json' \\")
            print("                       -d '{\"description\": \"Calculate 15 + 27\"}'")
        
        print("\n🚀 EXAMPLE USAGE:")
        print("  • See examples/ directory for detailed usage examples")
        print("  • Run: python examples/test_multi_agent.py")
        
        print("\n" + "="*80)
        print("Press Ctrl+C to shutdown")
        print("="*80 + "\n")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP-A2A-LangChain Multi-Agent System")
    parser.add_argument("--test", action="store_true", help="Run system tests after startup")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Create and start the system
    system = MultiAgentSystem()
    await system.start(run_tests=args.test)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        logger.error(f"System failed: {e}")
        sys.exit(1)