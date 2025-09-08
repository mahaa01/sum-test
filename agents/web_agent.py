"""
Web Agent - Specialized in web search and data retrieval
"""
import uuid
from typing import Dict, Any, List
from agents.base import BaseA2AAgent
from protocols.a2a import TaskRequest
import logging

logger = logging.getLogger(__name__)

class WebAgent(BaseA2AAgent):
    """Agent specialized in web operations and data retrieval"""
    
    def __init__(self, port: int = 8002, mcp_web_port: int = 9002):
        super().__init__(
            agent_id="web_agent",
            name="Web Agent",
            description="Specialized agent for web search, scraping, and data retrieval",
            port=port
        )
        
        # Connect to Web MCP server
        self.add_mcp_server("web", f"http://localhost:{mcp_web_port}")
        
        # Register capabilities
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register web-related capabilities"""
        
        self.register_capability(
            name="search_web",
            description="Search the web for information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Maximum results", "default": 5}
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {"type": "array", "description": "Search results"}
                }
            },
            cost=2.0
        )
        
        self.register_capability(
            name="scrape_webpage",
            description="Extract content from a webpage",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to scrape"},
                    "extract_text": {"type": "boolean", "default": True},
                    "extract_links": {"type": "boolean", "default": False}
                },
                "required": ["url"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Extracted content"}
                }
            },
            cost=1.5
        )
        
        self.register_capability(
            name="research_topic",
            description="Conduct comprehensive research on a topic",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                    "depth": {"type": "string", "enum": ["basic", "detailed", "comprehensive"], "default": "basic"}
                },
                "required": ["topic"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "research": {"type": "object", "description": "Research results"}
                }
            },
            cost=5.0
        )
        
        self.register_capability(
            name="verify_information",
            description="Verify information across multiple sources",
            input_schema={
                "type": "object",
                "properties": {
                    "claim": {"type": "string", "description": "Information to verify"},
                    "sources": {"type": "integer", "description": "Number of sources to check", "default": 3}
                },
                "required": ["claim"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "verification": {"type": "object", "description": "Verification results"}
                }
            },
            cost=3.0
        )
    
    async def process_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process web-related tasks"""
        task_type = task_request.task_type
        params = task_request.parameters
        
        try:
            if task_type == "search_web":
                query = params.get("query")
                max_results = params.get("max_results", 5)
                
                if not query:
                    raise ValueError("Query is required for web search")
                
                result = await self.mcp_client.call_tool(
                    "web", "search_web", {"query": query, "max_results": max_results}
                )
                
                return {"results": result, "type": "web_search", "query": query}
            
            elif task_type == "scrape_webpage":
                url = params.get("url")
                extract_text = params.get("extract_text", True)
                extract_links = params.get("extract_links", False)
                
                if not url:
                    raise ValueError("URL is required for webpage scraping")
                
                result = await self.mcp_client.call_tool(
                    "web", "scrape_webpage", {
                        "url": url,
                        "extract_text": extract_text,
                        "extract_links": extract_links
                    }
                )
                
                return {"content": result, "type": "webpage_scrape", "url": url}
            
            elif task_type == "research_topic":
                topic = params.get("topic")
                depth = params.get("depth", "basic")
                
                if not topic:
                    raise ValueError("Topic is required for research")
                
                # Multi-step research process
                research_results = await self._conduct_research(topic, depth)
                
                return {"research": research_results, "type": "topic_research", "topic": topic}
            
            elif task_type == "verify_information":
                claim = params.get("claim")
                sources = params.get("sources", 3)
                
                if not claim:
                    raise ValueError("Claim is required for verification")
                
                verification_results = await self._verify_information(claim, sources)
                
                return {"verification": verification_results, "type": "information_verification", "claim": claim}
            
            elif task_type == "check_url_status":
                url = params.get("url")
                
                if not url:
                    raise ValueError("URL is required for status check")
                
                result = await self.mcp_client.call_tool(
                    "web", "check_url_status", {"url": url}
                )
                
                return {"status": result, "type": "url_status", "url": url}
            
            elif task_type == "extract_emails":
                text = params.get("text")
                url = params.get("url")
                
                if not text and not url:
                    raise ValueError("Either text or URL is required for email extraction")
                
                args = {}
                if text:
                    args["text"] = text
                if url:
                    args["url"] = url
                
                result = await self.mcp_client.call_tool("web", "extract_emails", args)
                
                return {"emails": result, "type": "email_extraction"}
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        
        except Exception as e:
            logger.error(f"Error processing web task: {e}")
            raise
    
    async def _conduct_research(self, topic: str, depth: str) -> Dict[str, Any]:
        """Conduct comprehensive research on a topic"""
        research_results = {
            "topic": topic,
            "depth": depth,
            "sources": [],
            "summary": "",
            "key_points": []
        }
        
        try:
            # Initial search
            search_queries = [topic]
            
            if depth in ["detailed", "comprehensive"]:
                # Add more specific queries for deeper research
                search_queries.extend([
                    f"{topic} definition",
                    f"{topic} examples",
                    f"{topic} applications",
                    f"{topic} latest news"
                ])
            
            all_results = []
            for query in search_queries[:3 if depth == "basic" else 5]:
                search_result = await self.mcp_client.call_tool(
                    "web", "search_web", {"query": query, "max_results": 3}
                )
                all_results.append(search_result)
            
            research_results["sources"] = all_results
            research_results["summary"] = f"Research conducted on '{topic}' with {depth} depth analysis"
            research_results["key_points"] = [f"Query: {q}" for q in search_queries]
            
            return research_results
            
        except Exception as e:
            logger.error(f"Error conducting research: {e}")
            research_results["error"] = str(e)
            return research_results
    
    async def _verify_information(self, claim: str, sources: int) -> Dict[str, Any]:
        """Verify information across multiple sources"""
        verification_results = {
            "claim": claim,
            "sources_checked": 0,
            "verification_status": "unknown",
            "sources": [],
            "confidence": 0.0
        }
        
        try:
            # Search for the claim across multiple queries
            search_queries = [
                claim,
                f"{claim} fact check",
                f"{claim} verification",
                f"is {claim} true"
            ]
            
            supporting_sources = 0
            total_sources = 0
            
            for query in search_queries[:sources]:
                try:
                    search_result = await self.mcp_client.call_tool(
                        "web", "search_web", {"query": query, "max_results": 2}
                    )
                    
                    verification_results["sources"].append({
                        "query": query,
                        "results": search_result
                    })
                    
                    # Simple heuristic: if results contain the claim, it's supporting
                    if claim.lower() in search_result.lower():
                        supporting_sources += 1
                    
                    total_sources += 1
                    
                except Exception:
                    continue
            
            verification_results["sources_checked"] = total_sources
            
            if total_sources > 0:
                confidence = supporting_sources / total_sources
                verification_results["confidence"] = confidence
                
                if confidence >= 0.7:
                    verification_results["verification_status"] = "likely_true"
                elif confidence >= 0.3:
                    verification_results["verification_status"] = "uncertain"
                else:
                    verification_results["verification_status"] = "likely_false"
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error verifying information: {e}")
            verification_results["error"] = str(e)
            return verification_results
    
    async def collaborate_with_file_agent(self, urls: List[str]) -> Dict[str, Any]:
        """Collaborate with file agent to save scraped content"""
        try:
            scraped_data = []
            
            for url in urls:
                # Scrape webpage
                scrape_result = await self.process_task(TaskRequest(
                    task_id=str(uuid.uuid4()),
                    task_type="scrape_webpage",
                    description=f"Scrape content from {url}",
                    parameters={"url": url}
                ))
                
                scraped_data.append({
                    "url": url,
                    "content": scrape_result["content"]
                })
            
            # Request file agent to save the data
            file_response = await self.request_task_from_peer(
                "file_agent",
                "save_scraped_data",
                "Save scraped web content to files",
                {"scraped_data": scraped_data}
            )
            
            return {
                "scraped_data": scraped_data,
                "file_operations": file_response.result,
                "collaboration": "web_agent + file_agent"
            }
            
        except Exception as e:
            logger.error(f"Error in collaboration: {e}")
            raise

if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = WebAgent()
        await agent.start()
    
    asyncio.run(main())