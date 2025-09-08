# MCP-A2A-LangChain Multi-Agent System - Complete Documentation

## 🌟 Overview

This is a comprehensive multi-agent system that integrates three powerful protocols and frameworks:

- **MCP (Model Context Protocol)**: Provides standardized tool and context management
- **A2A (Agent-to-Agent)**: Enables structured communication between AI agents
- **LangChain**: Orchestrates complex workflows and agent interactions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATOR AGENT                        │
│                   (LangChain + OpenAI)                     │
│              Orchestrates Multi-Agent Workflows            │
└─────────────────────┬───────────────────────────────────────┘
                      │ A2A Protocol
          ┌───────────┼───────────┐
          │           │           │
    ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐ ┌──────▼──────┐
    │Math Agent │ │Web    │ │File Agent │ │Analysis     │
    │           │ │Agent  │ │           │ │Agent        │
    └─────┬─────┘ └───┬───┘ └─────┬─────┘ └──────┬──────┘
          │ MCP       │ MCP       │ MCP          │
    ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐      │
    │Math MCP   │ │Web MCP│ │File MCP   │      │
    │Server     │ │Server │ │Server     │      │
    └───────────┘ └───────┘ └───────────┘      │
                                               │
                    ┌──────────────────────────┘
                    │ Direct Analysis (No MCP Server)
                    ▼
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone or setup the project
cd /workspace

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (especially OPENAI_API_KEY)
nano .env
```

### 2. Installation

```bash
# Option 1: Use the startup script (recommended)
./start.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start the System

```bash
# Start all components
python main.py

# Or with system tests
python main.py --test
```

### 4. Verify Installation

```bash
# Run tests
python examples/test_multi_agent.py

# Run simple examples
python examples/simple_usage.py

# Run workflow examples
python examples/workflow_examples.py
```

## 📊 Components

### MCP Servers (Port 9001-9003)

**Math MCP Server (9001)**
- Basic calculations (`calculate`)
- Equation solving (`solve_quadratic`)
- Statistical analysis (`statistics`)
- Matrix operations (`matrix_operations`)

**Web MCP Server (9002)**
- Web search (`search_web`)
- Webpage scraping (`scrape_webpage`)
- URL status checking (`check_url_status`)
- Email extraction (`extract_emails`)

**File MCP Server (9003)**
- File operations (`read_file`, `write_file`)
- Directory listing (`list_directory`)
- File search (`search_in_files`)
- File information (`file_info`)
- Hash calculation (`calculate_file_hash`)

### A2A Agents (Port 8001-8004)

**Math Agent (8001)**
- Connects to Math MCP Server
- Capabilities: calculate, solve_equation, statistics, matrix_operations
- Can collaborate with Analysis Agent

**Web Agent (8002)**
- Connects to Web MCP Server
- Capabilities: search_web, scrape_webpage, research_topic, verify_information
- Can collaborate with File Agent

**File Agent (8003)**
- Connects to File MCP Server
- Capabilities: read_file, write_file, manage_data, search_files, file_analysis
- Can collaborate with Math Agent

**Analysis Agent (8004)**
- Standalone analysis capabilities
- Capabilities: analyze_data, pattern_recognition, generate_insights, compare_datasets
- Works with data from other agents

### Coordinator Agent (Port 8000)

**LangChain Integration**
- Uses OpenAI GPT-4 for intelligent task orchestration
- Breaks down complex tasks into subtasks
- Routes tasks to appropriate agents
- Synthesizes results from multiple agents

**Endpoints:**
- `POST /execute_task`: Execute complex tasks
- `GET /agents`: List registered agents
- `POST /register_agent`: Register new agents
- `GET /health`: Health check

## 🎯 Usage Examples

### Simple Task Execution

```python
import httpx
import asyncio

async def simple_example():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/execute_task",
            json={
                "description": "Calculate the square root of 144 and then find what percentage it is of 100"
            }
        )
        result = response.json()
        print(result["result"])

asyncio.run(simple_example())
```

### Complex Workflow

```python
workflow_description = """
Perform a comprehensive data analysis:
1. Create a dataset with monthly sales: [1000, 1200, 1100, 1300, 1400, 1350, 1500, 1600, 1450, 1700, 1800, 1900]
2. Calculate statistical measures (mean, median, std dev)
3. Identify trends and patterns
4. Generate insights and recommendations
5. Save results to a structured report file
"""

response = await client.post(
    "http://localhost:8000/execute_task",
    json={"description": workflow_description}
)
```

### Direct Agent Communication

```python
# Direct A2A message to Math Agent
message = {
    "type": "task_request",
    "sender_id": "client",
    "recipient_id": "math_agent",
    "payload": {
        "task_type": "calculate",
        "description": "Calculate compound interest",
        "parameters": {"expression": "1000 * (1 + 0.05) ** 10"}
    }
}

response = await client.post(
    "http://localhost:8001/a2a/message",
    json=message
)
```

## 🔧 Configuration

### Environment Variables

```bash
# API Keys
OPENAI_API_KEY=your_openai_key_here          # Required for Coordinator
ANTHROPIC_API_KEY=your_anthropic_key_here    # Optional
GOOGLE_API_KEY=your_google_key_here          # Optional
SERPER_API_KEY=your_serper_key_here          # Optional

# Port Configuration
COORDINATOR_PORT=8000
MATH_AGENT_PORT=8001
WEB_AGENT_PORT=8002
FILE_AGENT_PORT=8003
ANALYSIS_AGENT_PORT=8004
MCP_MATH_PORT=9001
MCP_WEB_PORT=9002
MCP_FILE_PORT=9003

# Logging
LOG_LEVEL=INFO
```

### Allowed File Paths (Security)

The File MCP Server restricts file operations to specific directories:
- `/workspace` (default)
- `/tmp`

To modify allowed paths, edit the `FileMCPServer` initialization in `main.py`.

## 🤝 Agent Collaboration Patterns

### 1. Sequential Collaboration
```
Math Agent → Analysis Agent → File Agent
(Calculate) → (Analyze) → (Save Results)
```

### 2. Parallel Processing
```
Web Agent ──┐
            ├─→ Analysis Agent
Math Agent ──┘
```

### 3. Complex Workflows
```
Web Agent → File Agent → Math Agent → Analysis Agent → File Agent
(Search) → (Save) → (Calculate) → (Analyze) → (Report)
```

## 🛠️ Extending the System

### Adding New MCP Tools

```python
# In your MCP server
@server.tool(
    name="new_tool",
    description="Description of the new tool",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)
async def new_tool(param1: str) -> str:
    # Tool implementation
    return f"Processed: {param1}"
```

### Adding New Agent Capabilities

```python
# In your agent class
self.register_capability(
    name="new_capability",
    description="Description of new capability",
    input_schema={...},
    output_schema={...},
    cost=1.0
)
```

### Creating Custom Agents

```python
from agents.base import BaseA2AAgent

class CustomAgent(BaseA2AAgent):
    def __init__(self, port: int = 8005):
        super().__init__(
            agent_id="custom_agent",
            name="Custom Agent",
            description="Custom agent description",
            port=port
        )
        self._register_capabilities()
    
    async def process_task(self, task_request):
        # Custom task processing logic
        return {"result": "Custom processing complete"}
```

## 📈 Monitoring and Debugging

### Health Checks

```bash
# Check all agent health
curl http://localhost:8000/health  # Coordinator
curl http://localhost:8001/health  # Math Agent
curl http://localhost:8002/health  # Web Agent
curl http://localhost:8003/health  # File Agent
curl http://localhost:8004/health  # Analysis Agent
```

### Agent Capabilities

```bash
# Get agent capabilities
curl http://localhost:8001/capabilities
curl http://localhost:8002/capabilities
curl http://localhost:8003/capabilities
curl http://localhost:8004/capabilities
```

### System Status

```python
from utils.helpers import SystemMonitor

monitor = SystemMonitor(agent_registry)
status = await monitor.get_system_status()
print(status)
```

## 🚨 Troubleshooting

### Common Issues

1. **Coordinator fails to start**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Check OpenAI API key validity

2. **Agents can't communicate**
   - Verify all agents are running on correct ports
   - Check firewall settings
   - Ensure no port conflicts

3. **MCP tools not working**
   - Check MCP server logs
   - Verify MCP server endpoints are accessible
   - Ensure proper MCP protocol format

4. **File operations fail**
   - Check file permissions
   - Verify paths are within allowed directories
   - Ensure sufficient disk space

### Debugging Tips

1. **Enable verbose logging**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Use system tests**
   ```bash
   python main.py --test
   python examples/test_multi_agent.py
   ```

3. **Monitor agent health**
   ```python
   from utils.helpers import AgentHealthChecker
   checker = AgentHealthChecker(agent_registry)
   health = await checker.check_all_agents()
   ```

## 📚 API Reference

### Coordinator Endpoints

**POST /execute_task**
```json
{
  "description": "Task description",
  "context": {"key": "value"}  // Optional
}
```

**Response:**
```json
{
  "result": "Task execution result",
  "status": "completed"
}
```

### A2A Message Format

```json
{
  "id": "unique_message_id",
  "type": "task_request",
  "sender_id": "sender_agent_id",
  "recipient_id": "recipient_agent_id",
  "timestamp": "2024-01-01T00:00:00Z",
  "payload": {
    "task_id": "unique_task_id",
    "task_type": "task_type",
    "description": "Task description",
    "parameters": {}
  }
}
```

### MCP Request Format

```json
{
  "id": "unique_request_id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {}
  }
}
```

## 🔒 Security Considerations

1. **File System Access**: Limited to configured allowed paths
2. **API Keys**: Store securely in environment variables
3. **Network Security**: Consider firewall rules for production
4. **Input Validation**: All inputs are validated before processing
5. **Error Handling**: Comprehensive error handling prevents system crashes

## 🎓 Best Practices

1. **Task Design**: Break complex tasks into clear, specific subtasks
2. **Error Handling**: Always handle potential errors gracefully
3. **Resource Management**: Monitor system resources during heavy workflows
4. **Logging**: Use appropriate log levels for debugging and monitoring
5. **Testing**: Test individual agents before complex workflows

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🆘 Support

For issues and questions:
1. Check this documentation
2. Run the test suite
3. Check system logs
4. Review example implementations