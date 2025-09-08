"""
File MCP Server - Provides file operations and text processing tools
"""
import os
import json
import csv
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
from protocols.mcp import MCPServer
import logging

logger = logging.getLogger(__name__)

class FileMCPServer(MCPServer):
    """MCP Server for file operations"""
    
    def __init__(self, port: int = 9003, allowed_paths: List[str] = None):
        super().__init__("File Server", "File operations and text processing tools", port)
        # Security: limit file operations to specific paths
        self.allowed_paths = allowed_paths or ["/workspace", "/tmp"]
        self._setup_tools()
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(allowed)) 
                  for allowed in self.allowed_paths)
    
    def _setup_tools(self):
        """Setup file operation tools"""
        
        @self.tool(
            name="read_file",
            description="Read content from a text file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["file_path"]
            }
        )
        async def read_file(file_path: str, encoding: str = "utf-8") -> str:
            """Read content from a file"""
            try:
                if not self._is_path_allowed(file_path):
                    return f"Error: Access denied to path: {file_path}"
                
                if not os.path.exists(file_path):
                    return f"Error: File not found: {file_path}"
                
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                return f"Content of {file_path}:\n\n{content}"
                
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @self.tool(
            name="write_file",
            description="Write content to a text file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "Append to file instead of overwriting",
                        "default": False
                    }
                },
                "required": ["file_path", "content"]
            }
        )
        async def write_file(file_path: str, content: str, encoding: str = "utf-8", append: bool = False) -> str:
            """Write content to a file"""
            try:
                if not self._is_path_allowed(file_path):
                    return f"Error: Access denied to path: {file_path}"
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                mode = 'a' if append else 'w'
                with open(file_path, mode, encoding=encoding) as f:
                    f.write(content)
                
                action = "Appended to" if append else "Written to"
                return f"{action} file: {file_path} ({len(content)} characters)"
                
            except Exception as e:
                return f"Error writing file: {str(e)}"
        
        @self.tool(
            name="list_directory",
            description="List contents of a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory to list"
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Show hidden files (starting with .)",
                        "default": False
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Show detailed file information",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        )
        async def list_directory(directory_path: str, show_hidden: bool = False, detailed: bool = False) -> str:
            """List directory contents"""
            try:
                if not self._is_path_allowed(directory_path):
                    return f"Error: Access denied to path: {directory_path}"
                
                if not os.path.exists(directory_path):
                    return f"Error: Directory not found: {directory_path}"
                
                if not os.path.isdir(directory_path):
                    return f"Error: Path is not a directory: {directory_path}"
                
                items = []
                for item in os.listdir(directory_path):
                    if not show_hidden and item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(directory_path, item)
                    
                    if detailed:
                        stat = os.stat(item_path)
                        size = stat.st_size
                        is_dir = os.path.isdir(item_path)
                        items.append({
                            "name": item,
                            "type": "directory" if is_dir else "file",
                            "size": size if not is_dir else None
                        })
                    else:
                        items.append(item)
                
                result = f"Contents of {directory_path}:\n\n"
                
                if detailed:
                    for item in sorted(items, key=lambda x: (x["type"] != "directory", x["name"])):
                        type_indicator = "📁" if item["type"] == "directory" else "📄"
                        size_info = f" ({item['size']} bytes)" if item["size"] is not None else ""
                        result += f"{type_indicator} {item['name']}{size_info}\n"
                else:
                    for item in sorted(items):
                        result += f"  {item}\n"
                
                return result.strip()
                
            except Exception as e:
                return f"Error listing directory: {str(e)}"
        
        @self.tool(
            name="file_info",
            description="Get detailed information about a file or directory",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file or directory"
                    }
                },
                "required": ["path"]
            }
        )
        async def file_info(path: str) -> str:
            """Get detailed file/directory information"""
            try:
                if not self._is_path_allowed(path):
                    return f"Error: Access denied to path: {path}"
                
                if not os.path.exists(path):
                    return f"Error: Path not found: {path}"
                
                stat = os.stat(path)
                is_dir = os.path.isdir(path)
                
                result = f"Information for: {path}\n\n"
                result += f"Type: {'Directory' if is_dir else 'File'}\n"
                
                if not is_dir:
                    result += f"Size: {stat.st_size} bytes\n"
                    mime_type, _ = mimetypes.guess_type(path)
                    result += f"MIME Type: {mime_type or 'Unknown'}\n"
                
                result += f"Created: {stat.st_ctime}\n"
                result += f"Modified: {stat.st_mtime}\n"
                result += f"Accessed: {stat.st_atime}\n"
                result += f"Permissions: {oct(stat.st_mode)[-3:]}\n"
                
                return result
                
            except Exception as e:
                return f"Error getting file info: {str(e)}"
        
        @self.tool(
            name="search_in_files",
            description="Search for text within files in a directory",
            input_schema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for"
                    },
                    "file_extension": {
                        "type": "string",
                        "description": "File extension to filter by (e.g., '.txt', '.py')",
                        "default": ""
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case sensitive search",
                        "default": False
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["directory", "pattern"]
            }
        )
        async def search_in_files(directory: str, pattern: str, file_extension: str = "", 
                                case_sensitive: bool = False, max_results: int = 10) -> str:
            """Search for text within files"""
            try:
                if not self._is_path_allowed(directory):
                    return f"Error: Access denied to path: {directory}"
                
                if not os.path.exists(directory):
                    return f"Error: Directory not found: {directory}"
                
                results = []
                search_pattern = pattern if case_sensitive else pattern.lower()
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file_extension and not file.endswith(file_extension):
                            continue
                        
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    search_line = line if case_sensitive else line.lower()
                                    if search_pattern in search_line:
                                        results.append({
                                            "file": file_path,
                                            "line": line_num,
                                            "content": line.strip()
                                        })
                                        
                                        if len(results) >= max_results:
                                            break
                        except Exception:
                            continue  # Skip files that can't be read
                        
                        if len(results) >= max_results:
                            break
                    
                    if len(results) >= max_results:
                        break
                
                if not results:
                    return f"No matches found for pattern '{pattern}' in {directory}"
                
                result_text = f"Found {len(results)} matches for '{pattern}':\n\n"
                for i, result in enumerate(results, 1):
                    result_text += f"{i}. {result['file']}:{result['line']}\n"
                    result_text += f"   {result['content']}\n\n"
                
                return result_text.strip()
                
            except Exception as e:
                return f"Error searching in files: {str(e)}"
        
        @self.tool(
            name="calculate_file_hash",
            description="Calculate hash (MD5, SHA1, SHA256) of a file",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "hash_type": {
                        "type": "string",
                        "enum": ["md5", "sha1", "sha256"],
                        "description": "Type of hash to calculate",
                        "default": "sha256"
                    }
                },
                "required": ["file_path"]
            }
        )
        async def calculate_file_hash(file_path: str, hash_type: str = "sha256") -> str:
            """Calculate file hash"""
            try:
                if not self._is_path_allowed(file_path):
                    return f"Error: Access denied to path: {file_path}"
                
                if not os.path.exists(file_path):
                    return f"Error: File not found: {file_path}"
                
                if os.path.isdir(file_path):
                    return f"Error: Path is a directory, not a file: {file_path}"
                
                hash_functions = {
                    "md5": hashlib.md5(),
                    "sha1": hashlib.sha1(),
                    "sha256": hashlib.sha256()
                }
                
                if hash_type not in hash_functions:
                    return f"Error: Unsupported hash type: {hash_type}"
                
                hasher = hash_functions[hash_type]
                
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                
                hash_value = hasher.hexdigest()
                file_size = os.path.getsize(file_path)
                
                return f"File: {file_path}\nSize: {file_size} bytes\n{hash_type.upper()}: {hash_value}"
                
            except Exception as e:
                return f"Error calculating file hash: {str(e)}"

if __name__ == "__main__":
    import asyncio
    
    async def main():
        server = FileMCPServer()
        await server.start()
    
    asyncio.run(main())