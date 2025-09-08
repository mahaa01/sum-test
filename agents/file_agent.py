"""
File Agent - Specialized in file operations and data management
"""
import uuid
import json
import os
from typing import Dict, Any, List
from agents.base import BaseA2AAgent
from protocols.a2a import TaskRequest
import logging

logger = logging.getLogger(__name__)

class FileAgent(BaseA2AAgent):
    """Agent specialized in file operations and data management"""
    
    def __init__(self, port: int = 8003, mcp_file_port: int = 9003):
        super().__init__(
            agent_id="file_agent",
            name="File Agent",
            description="Specialized agent for file operations, data storage, and text processing",
            port=port
        )
        
        # Connect to File MCP server
        self.add_mcp_server("file", f"http://localhost:{mcp_file_port}")
        
        # Register capabilities
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register file-related capabilities"""
        
        self.register_capability(
            name="read_file",
            description="Read content from a file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file"},
                    "encoding": {"type": "string", "default": "utf-8"}
                },
                "required": ["file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "File content"}
                }
            },
            cost=1.0
        )
        
        self.register_capability(
            name="write_file",
            description="Write content to a file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file"},
                    "content": {"type": "string", "description": "Content to write"},
                    "append": {"type": "boolean", "default": False}
                },
                "required": ["file_path", "content"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Write status"}
                }
            },
            cost=1.0
        )
        
        self.register_capability(
            name="manage_data",
            description="Manage structured data files (JSON, CSV)",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["create", "read", "update", "delete"]},
                    "file_path": {"type": "string", "description": "Path to data file"},
                    "data": {"type": "object", "description": "Data to manage"}
                },
                "required": ["operation", "file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "object", "description": "Operation result"}
                }
            },
            cost=1.5
        )
        
        self.register_capability(
            name="search_files",
            description="Search for content within files",
            input_schema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory to search"},
                    "pattern": {"type": "string", "description": "Search pattern"},
                    "file_extension": {"type": "string", "description": "File extension filter"}
                },
                "required": ["directory", "pattern"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "matches": {"type": "array", "description": "Search matches"}
                }
            },
            cost=2.0
        )
        
        self.register_capability(
            name="file_analysis",
            description="Analyze files and directories",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to analyze"},
                    "analysis_type": {"type": "string", "enum": ["info", "hash", "structure"]}
                },
                "required": ["path", "analysis_type"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "analysis": {"type": "object", "description": "Analysis results"}
                }
            },
            cost=1.5
        )
    
    async def process_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process file-related tasks"""
        task_type = task_request.task_type
        params = task_request.parameters
        
        try:
            if task_type == "read_file":
                file_path = params.get("file_path")
                encoding = params.get("encoding", "utf-8")
                
                if not file_path:
                    raise ValueError("File path is required for reading")
                
                result = await self.mcp_client.call_tool(
                    "file", "read_file", {"file_path": file_path, "encoding": encoding}
                )
                
                return {"content": result, "type": "file_read", "file_path": file_path}
            
            elif task_type == "write_file":
                file_path = params.get("file_path")
                content = params.get("content")
                append = params.get("append", False)
                
                if not file_path or content is None:
                    raise ValueError("File path and content are required for writing")
                
                result = await self.mcp_client.call_tool(
                    "file", "write_file", {
                        "file_path": file_path,
                        "content": content,
                        "append": append
                    }
                )
                
                return {"status": result, "type": "file_write", "file_path": file_path}
            
            elif task_type == "list_directory":
                directory_path = params.get("directory_path")
                show_hidden = params.get("show_hidden", False)
                detailed = params.get("detailed", False)
                
                if not directory_path:
                    raise ValueError("Directory path is required")
                
                result = await self.mcp_client.call_tool(
                    "file", "list_directory", {
                        "directory_path": directory_path,
                        "show_hidden": show_hidden,
                        "detailed": detailed
                    }
                )
                
                return {"listing": result, "type": "directory_list", "directory": directory_path}
            
            elif task_type == "search_files":
                directory = params.get("directory")
                pattern = params.get("pattern")
                file_extension = params.get("file_extension", "")
                
                if not directory or not pattern:
                    raise ValueError("Directory and pattern are required for search")
                
                result = await self.mcp_client.call_tool(
                    "file", "search_in_files", {
                        "directory": directory,
                        "pattern": pattern,
                        "file_extension": file_extension
                    }
                )
                
                return {"matches": result, "type": "file_search", "pattern": pattern}
            
            elif task_type == "file_info":
                path = params.get("path")
                
                if not path:
                    raise ValueError("Path is required for file info")
                
                result = await self.mcp_client.call_tool(
                    "file", "file_info", {"path": path}
                )
                
                return {"info": result, "type": "file_info", "path": path}
            
            elif task_type == "calculate_hash":
                file_path = params.get("file_path")
                hash_type = params.get("hash_type", "sha256")
                
                if not file_path:
                    raise ValueError("File path is required for hash calculation")
                
                result = await self.mcp_client.call_tool(
                    "file", "calculate_file_hash", {
                        "file_path": file_path,
                        "hash_type": hash_type
                    }
                )
                
                return {"hash": result, "type": "file_hash", "file_path": file_path}
            
            elif task_type == "manage_data":
                operation = params.get("operation")
                file_path = params.get("file_path")
                data = params.get("data", {})
                
                if not operation or not file_path:
                    raise ValueError("Operation and file path are required")
                
                result = await self._manage_structured_data(operation, file_path, data)
                
                return {"result": result, "type": "data_management", "operation": operation}
            
            elif task_type == "save_scraped_data":
                # Special task for collaboration with web agent
                scraped_data = params.get("scraped_data", [])
                
                if not scraped_data:
                    raise ValueError("Scraped data is required")
                
                saved_files = []
                for i, data in enumerate(scraped_data):
                    url = data.get("url", f"unknown_{i}")
                    content = data.get("content", "")
                    
                    # Create safe filename from URL
                    safe_filename = url.replace("://", "_").replace("/", "_").replace("?", "_")
                    file_path = f"/workspace/scraped_data/{safe_filename}.txt"
                    
                    write_result = await self.mcp_client.call_tool(
                        "file", "write_file", {
                            "file_path": file_path,
                            "content": f"URL: {url}\n\n{content}"
                        }
                    )
                    
                    saved_files.append({
                        "url": url,
                        "file_path": file_path,
                        "status": write_result
                    })
                
                return {"saved_files": saved_files, "type": "scraped_data_save"}
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        
        except Exception as e:
            logger.error(f"Error processing file task: {e}")
            raise
    
    async def _manage_structured_data(self, operation: str, file_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage structured data files (JSON, CSV)"""
        try:
            if operation == "create":
                # Create new data file
                if file_path.endswith('.json'):
                    content = json.dumps(data, indent=2)
                elif file_path.endswith('.csv'):
                    # Simple CSV creation (assumes data is a list of dicts)
                    if isinstance(data, list) and data:
                        import csv
                        import io
                        output = io.StringIO()
                        writer = csv.DictWriter(output, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                        content = output.getvalue()
                    else:
                        raise ValueError("CSV data must be a list of dictionaries")
                else:
                    content = str(data)
                
                write_result = await self.mcp_client.call_tool(
                    "file", "write_file", {"file_path": file_path, "content": content}
                )
                
                return {"operation": "create", "status": write_result}
            
            elif operation == "read":
                # Read and parse data file
                read_result = await self.mcp_client.call_tool(
                    "file", "read_file", {"file_path": file_path}
                )
                
                if file_path.endswith('.json'):
                    # Extract JSON content from read result
                    content_lines = read_result.split('\n')
                    json_content = '\n'.join(content_lines[2:])  # Skip header lines
                    parsed_data = json.loads(json_content)
                else:
                    parsed_data = read_result
                
                return {"operation": "read", "data": parsed_data}
            
            elif operation == "update":
                # Update existing data file
                if file_path.endswith('.json'):
                    # Read existing data
                    try:
                        read_result = await self.mcp_client.call_tool(
                            "file", "read_file", {"file_path": file_path}
                        )
                        content_lines = read_result.split('\n')
                        json_content = '\n'.join(content_lines[2:])
                        existing_data = json.loads(json_content)
                    except:
                        existing_data = {}
                    
                    # Merge with new data
                    if isinstance(existing_data, dict) and isinstance(data, dict):
                        existing_data.update(data)
                    else:
                        existing_data = data
                    
                    # Write back
                    content = json.dumps(existing_data, indent=2)
                    write_result = await self.mcp_client.call_tool(
                        "file", "write_file", {"file_path": file_path, "content": content}
                    )
                    
                    return {"operation": "update", "status": write_result}
                else:
                    raise ValueError("Update operation currently only supports JSON files")
            
            elif operation == "delete":
                # Delete data file (using OS operations since MCP server doesn't have delete)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return {"operation": "delete", "status": f"Deleted {file_path}"}
                else:
                    return {"operation": "delete", "status": f"File not found: {file_path}"}
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
        
        except Exception as e:
            logger.error(f"Error managing structured data: {e}")
            raise
    
    async def collaborate_with_math_agent(self, data_file: str) -> Dict[str, Any]:
        """Collaborate with math agent to analyze data from files"""
        try:
            # Read data file
            read_result = await self.process_task(TaskRequest(
                task_id=str(uuid.uuid4()),
                task_type="read_file",
                description=f"Read data from {data_file}",
                parameters={"file_path": data_file}
            ))
            
            # Parse numerical data (simple approach)
            content = read_result["content"]
            numbers = []
            for line in content.split('\n'):
                try:
                    # Try to extract numbers from each line
                    import re
                    found_numbers = re.findall(r'-?\d+\.?\d*', line)
                    numbers.extend([float(n) for n in found_numbers])
                except:
                    continue
            
            if not numbers:
                return {"error": "No numerical data found in file"}
            
            # Request math analysis
            math_response = await self.request_task_from_peer(
                "math_agent",
                "statistics",
                f"Calculate statistics for data from {data_file}",
                {"data": numbers}
            )
            
            # Save analysis results
            analysis_file = data_file.replace('.txt', '_analysis.json').replace('.csv', '_analysis.json')
            analysis_data = {
                "source_file": data_file,
                "data_points": len(numbers),
                "statistics": math_response.result
            }
            
            save_result = await self.process_task(TaskRequest(
                task_id=str(uuid.uuid4()),
                task_type="manage_data",
                description="Save analysis results",
                parameters={
                    "operation": "create",
                    "file_path": analysis_file,
                    "data": analysis_data
                }
            ))
            
            return {
                "original_data": numbers[:10],  # First 10 numbers for reference
                "analysis": math_response.result,
                "saved_to": analysis_file,
                "collaboration": "file_agent + math_agent"
            }
            
        except Exception as e:
            logger.error(f"Error in collaboration: {e}")
            raise

if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = FileAgent()
        await agent.start()
    
    asyncio.run(main())