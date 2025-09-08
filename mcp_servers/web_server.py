"""
Web MCP Server - Provides web search and scraping tools
"""
import aiohttp
import json
import re
from typing import Optional, Dict, Any, List
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from protocols.mcp import MCPServer
import logging

logger = logging.getLogger(__name__)

class WebMCPServer(MCPServer):
    """MCP Server for web operations"""
    
    def __init__(self, port: int = 9002):
        super().__init__("Web Server", "Web search and scraping tools", port)
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup web tools"""
        
        @self.tool(
            name="search_web",
            description="Search the web using DuckDuckGo",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        async def search_web(query: str, max_results: int = 5) -> str:
            """Search the web using DuckDuckGo"""
            try:
                # Use DuckDuckGo instant answer API
                url = "https://api.duckduckgo.com/"
                params = {
                    "q": query,
                    "format": "json",
                    "no_html": "1",
                    "skip_disambig": "1"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            results = []
                            
                            # Add instant answer if available
                            if data.get("AbstractText"):
                                results.append({
                                    "title": data.get("AbstractSource", "DuckDuckGo"),
                                    "snippet": data.get("AbstractText"),
                                    "url": data.get("AbstractURL", "")
                                })
                            
                            # Add related topics
                            for topic in data.get("RelatedTopics", [])[:max_results-len(results)]:
                                if isinstance(topic, dict) and topic.get("Text"):
                                    results.append({
                                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                                        "snippet": topic.get("Text"),
                                        "url": topic.get("FirstURL", "")
                                    })
                            
                            if not results:
                                return f"No results found for query: {query}"
                            
                            formatted_results = f"Search results for '{query}':\n\n"
                            for i, result in enumerate(results[:max_results], 1):
                                formatted_results += f"{i}. {result['title']}\n"
                                formatted_results += f"   {result['snippet']}\n"
                                if result['url']:
                                    formatted_results += f"   URL: {result['url']}\n"
                                formatted_results += "\n"
                            
                            return formatted_results.strip()
                        else:
                            return f"Search failed with status: {response.status}"
                            
            except Exception as e:
                return f"Error searching web: {str(e)}"
        
        @self.tool(
            name="scrape_webpage",
            description="Scrape content from a webpage",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "Extract clean text content",
                        "default": True
                    },
                    "extract_links": {
                        "type": "boolean",
                        "description": "Extract all links",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        )
        async def scrape_webpage(url: str, extract_text: bool = True, extract_links: bool = False) -> str:
            """Scrape content from a webpage"""
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=30) as response:
                        if response.status != 200:
                            return f"Failed to fetch webpage. Status: {response.status}"
                        
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.extract()
                        
                        result = f"Content from: {url}\n\n"
                        
                        if extract_text:
                            # Extract title
                            title = soup.find('title')
                            if title:
                                result += f"Title: {title.get_text().strip()}\n\n"
                            
                            # Extract main content
                            text = soup.get_text()
                            lines = (line.strip() for line in text.splitlines())
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            text = ' '.join(chunk for chunk in chunks if chunk)
                            
                            # Limit text length
                            if len(text) > 5000:
                                text = text[:5000] + "... [truncated]"
                            
                            result += f"Content:\n{text}\n"
                        
                        if extract_links:
                            links = []
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                text = link.get_text().strip()
                                if href.startswith('http') or href.startswith('/'):
                                    if href.startswith('/'):
                                        href = urljoin(url, href)
                                    links.append({"url": href, "text": text})
                            
                            if links:
                                result += f"\nLinks found ({len(links)}):\n"
                                for i, link in enumerate(links[:20], 1):  # Limit to 20 links
                                    result += f"{i}. {link['text']} - {link['url']}\n"
                        
                        return result
                        
            except Exception as e:
                return f"Error scraping webpage: {str(e)}"
        
        @self.tool(
            name="check_url_status",
            description="Check if a URL is accessible and get basic info",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to check"
                    }
                },
                "required": ["url"]
            }
        )
        async def check_url_status(url: str) -> str:
            """Check URL status and basic information"""
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.head(url, headers=headers, timeout=10) as response:
                        result = f"URL Status Check: {url}\n"
                        result += f"Status Code: {response.status}\n"
                        result += f"Status: {'✓ Accessible' if response.status == 200 else '✗ Not accessible'}\n"
                        
                        # Get some headers
                        content_type = response.headers.get('content-type', 'Unknown')
                        content_length = response.headers.get('content-length', 'Unknown')
                        server = response.headers.get('server', 'Unknown')
                        
                        result += f"Content Type: {content_type}\n"
                        result += f"Content Length: {content_length}\n"
                        result += f"Server: {server}\n"
                        
                        return result
                        
            except Exception as e:
                return f"Error checking URL status: {str(e)}"
        
        @self.tool(
            name="extract_emails",
            description="Extract email addresses from text or webpage",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to extract emails from"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to scrape and extract emails from (alternative to text)"
                    }
                }
            }
        )
        async def extract_emails(text: str = None, url: str = None) -> str:
            """Extract email addresses from text or webpage"""
            try:
                content = text
                
                if url and not text:
                    # Scrape webpage first
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, timeout=30) as response:
                            if response.status == 200:
                                html_content = await response.text()
                                soup = BeautifulSoup(html_content, 'html.parser')
                                content = soup.get_text()
                            else:
                                return f"Failed to fetch webpage. Status: {response.status}"
                
                if not content:
                    return "No content provided to extract emails from"
                
                # Email regex pattern
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, content)
                
                # Remove duplicates and sort
                unique_emails = sorted(list(set(emails)))
                
                if not unique_emails:
                    return "No email addresses found"
                
                result = f"Found {len(unique_emails)} email address(es):\n"
                for i, email in enumerate(unique_emails, 1):
                    result += f"{i}. {email}\n"
                
                return result.strip()
                
            except Exception as e:
                return f"Error extracting emails: {str(e)}"

if __name__ == "__main__":
    import asyncio
    
    async def main():
        server = WebMCPServer()
        await server.start()
    
    asyncio.run(main())