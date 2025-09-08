# MCP-A2A-LangChain Multi-Agent System

A comprehensive multi-agent system implementation that combines:
- **MCP (Model Context Protocol)** for tool and context management
- **A2A (Agent-to-Agent)** protocol for inter-agent communication
- **LangChain** for agent orchestration and workflow management

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Coordinator    │    │   Math Agent    │    │   Web Agent     │
│    Agent        │◄──►│                 │    │                 │
│   (LangChain)   │    │   (A2A + MCP)   │    │   (A2A + MCP)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Agent    │    │  Analysis Agent │    │   MCP Servers   │
│                 │    │                 │    │                 │
│   (A2A + MCP)   │    │   (A2A + MCP)   │    │  (Tools & Data) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

- **Multi-Agent Coordination**: Centralized coordinator manages task distribution
- **MCP Integration**: Standardized tool and context protocol
- **A2A Communication**: Structured agent-to-agent messaging
- **LangChain Orchestration**: Advanced workflow management
- **Extensible Architecture**: Easy to add new agents and capabilities

## Quick Start

1. **Setup Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the System**:
   ```bash
   python main.py
   ```

4. **Test the System**:
   ```bash
   python examples/test_multi_agent.py
   ```

## Usage Examples

### Basic Multi-Agent Task
```python
from coordinator import CoordinatorAgent

coordinator = CoordinatorAgent()
result = await coordinator.execute_task(
    "Calculate the square root of 144, then search for information about that number in mathematics"
)
print(result)
```

### Custom Agent Integration
```python
from agents.base import BaseA2AAgent
from mcp_servers.custom_server import CustomMCPServer

class CustomAgent(BaseA2AAgent):
    def __init__(self):
        super().__init__("custom_agent", port=8005)
        self.mcp_server = CustomMCPServer()
    
    async def process_task(self, task):
        # Custom processing logic
        return await self.mcp_server.execute_tool(task)
```

## Components

- `coordinator/`: Main coordination agent using LangChain
- `agents/`: Specialized A2A agents (math, web, file, analysis)
- `mcp_servers/`: MCP servers providing tools and context
- `protocols/`: A2A and MCP protocol implementations
- `examples/`: Usage examples and demos
- `utils/`: Shared utilities and helpers

## License

MIT License - see LICENSE file for details.