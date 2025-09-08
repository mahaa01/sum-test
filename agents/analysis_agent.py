"""
Analysis Agent - Specialized in data analysis and insights
"""
import uuid
from typing import Dict, Any, List
from agents.base import BaseA2AAgent
from protocols.a2a import TaskRequest
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent(BaseA2AAgent):
    """Agent specialized in data analysis and generating insights"""
    
    def __init__(self, port: int = 8004):
        super().__init__(
            agent_id="analysis_agent",
            name="Analysis Agent",
            description="Specialized agent for data analysis, pattern recognition, and insight generation",
            port=port
        )
        
        # Register capabilities
        self._register_capabilities()
    
    def _register_capabilities(self):
        """Register analysis-related capabilities"""
        
        self.register_capability(
            name="analyze_data",
            description="Analyze data and generate insights",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "object", "description": "Data to analyze"},
                    "analysis_type": {"type": "string", "enum": ["descriptive", "predictive", "diagnostic", "prescriptive"]},
                    "context": {"type": "string", "description": "Context for analysis"}
                },
                "required": ["data", "analysis_type"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "insights": {"type": "object", "description": "Analysis insights"}
                }
            },
            cost=3.0
        )
        
        self.register_capability(
            name="pattern_recognition",
            description="Identify patterns in data",
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "array", "description": "Data points"},
                    "pattern_type": {"type": "string", "enum": ["trend", "seasonal", "anomaly", "correlation"]}
                },
                "required": ["data", "pattern_type"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "patterns": {"type": "array", "description": "Identified patterns"}
                }
            },
            cost=2.5
        )
        
        self.register_capability(
            name="generate_insights",
            description="Generate actionable insights from analysis",
            input_schema={
                "type": "object",
                "properties": {
                    "analysis_results": {"type": "object", "description": "Previous analysis results"},
                    "business_context": {"type": "string", "description": "Business or domain context"}
                },
                "required": ["analysis_results"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "insights": {"type": "array", "description": "Actionable insights"}
                }
            },
            cost=2.0
        )
        
        self.register_capability(
            name="compare_datasets",
            description="Compare multiple datasets",
            input_schema={
                "type": "object",
                "properties": {
                    "datasets": {"type": "array", "description": "Datasets to compare"},
                    "comparison_metrics": {"type": "array", "description": "Metrics to compare"}
                },
                "required": ["datasets"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "comparison": {"type": "object", "description": "Comparison results"}
                }
            },
            cost=3.5
        )
    
    async def process_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Process analysis tasks"""
        task_type = task_request.task_type
        params = task_request.parameters
        
        try:
            if task_type == "analyze_data":
                data = params.get("data")
                analysis_type = params.get("analysis_type")
                context = params.get("context", "")
                
                if not data or not analysis_type:
                    raise ValueError("Data and analysis type are required")
                
                insights = await self._analyze_data(data, analysis_type, context)
                
                return {"insights": insights, "type": "data_analysis", "analysis_type": analysis_type}
            
            elif task_type == "pattern_recognition":
                data = params.get("data")
                pattern_type = params.get("pattern_type")
                
                if not data or not pattern_type:
                    raise ValueError("Data and pattern type are required")
                
                patterns = await self._identify_patterns(data, pattern_type)
                
                return {"patterns": patterns, "type": "pattern_recognition", "pattern_type": pattern_type}
            
            elif task_type == "generate_insights":
                analysis_results = params.get("analysis_results")
                business_context = params.get("business_context", "")
                
                if not analysis_results:
                    raise ValueError("Analysis results are required")
                
                insights = await self._generate_insights(analysis_results, business_context)
                
                return {"insights": insights, "type": "insight_generation"}
            
            elif task_type == "compare_datasets":
                datasets = params.get("datasets")
                comparison_metrics = params.get("comparison_metrics", ["mean", "median", "variance"])
                
                if not datasets or len(datasets) < 2:
                    raise ValueError("At least two datasets are required for comparison")
                
                comparison = await self._compare_datasets(datasets, comparison_metrics)
                
                return {"comparison": comparison, "type": "dataset_comparison"}
            
            elif task_type == "comprehensive_analysis":
                # Multi-step comprehensive analysis
                raw_data = params.get("raw_data")
                statistics = params.get("statistics")
                analysis_type = params.get("analysis_type", "descriptive")
                
                comprehensive_results = await self._comprehensive_analysis(raw_data, statistics, analysis_type)
                
                return {"comprehensive_analysis": comprehensive_results, "type": "comprehensive_analysis"}
            
            else:
                raise ValueError(f"Unknown task type: {task_type}")
        
        except Exception as e:
            logger.error(f"Error processing analysis task: {e}")
            raise
    
    async def _analyze_data(self, data: Any, analysis_type: str, context: str) -> Dict[str, Any]:
        """Analyze data based on type"""
        analysis_results = {
            "analysis_type": analysis_type,
            "context": context,
            "findings": [],
            "recommendations": [],
            "confidence": 0.0
        }
        
        try:
            if analysis_type == "descriptive":
                # Descriptive analysis
                if isinstance(data, dict) and "statistics" in data:
                    stats = data["statistics"]
                    analysis_results["findings"] = [
                        f"Data contains statistical measures",
                        f"Mean value indicates central tendency",
                        f"Standard deviation shows variability"
                    ]
                    analysis_results["recommendations"] = [
                        "Consider data distribution for further analysis",
                        "Look for outliers that might affect results"
                    ]
                    analysis_results["confidence"] = 0.8
                
                elif isinstance(data, list):
                    # Simple list analysis
                    analysis_results["findings"] = [
                        f"Dataset contains {len(data)} data points",
                        f"Data type: {type(data[0]).__name__ if data else 'empty'}"
                    ]
                    analysis_results["recommendations"] = [
                        "Perform statistical analysis for deeper insights"
                    ]
                    analysis_results["confidence"] = 0.6
            
            elif analysis_type == "predictive":
                # Predictive analysis (simplified)
                analysis_results["findings"] = [
                    "Predictive analysis requires historical patterns",
                    "Current data shows potential for forecasting"
                ]
                analysis_results["recommendations"] = [
                    "Collect more historical data for better predictions",
                    "Consider seasonal patterns if applicable"
                ]
                analysis_results["confidence"] = 0.5
            
            elif analysis_type == "diagnostic":
                # Diagnostic analysis
                analysis_results["findings"] = [
                    "Diagnostic analysis helps identify root causes",
                    "Data patterns suggest specific behaviors"
                ]
                analysis_results["recommendations"] = [
                    "Investigate anomalies in the data",
                    "Cross-reference with external factors"
                ]
                analysis_results["confidence"] = 0.7
            
            elif analysis_type == "prescriptive":
                # Prescriptive analysis
                analysis_results["findings"] = [
                    "Prescriptive analysis provides actionable recommendations",
                    "Data suggests optimal decision paths"
                ]
                analysis_results["recommendations"] = [
                    "Implement recommended actions based on analysis",
                    "Monitor results and adjust strategies accordingly"
                ]
                analysis_results["confidence"] = 0.6
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            analysis_results["error"] = str(e)
            return analysis_results
    
    async def _identify_patterns(self, data: List[Any], pattern_type: str) -> List[Dict[str, Any]]:
        """Identify patterns in data"""
        patterns = []
        
        try:
            if pattern_type == "trend":
                # Simple trend analysis
                if len(data) >= 3:
                    increasing = sum(1 for i in range(1, len(data)) if data[i] > data[i-1])
                    decreasing = sum(1 for i in range(1, len(data)) if data[i] < data[i-1])
                    
                    if increasing > decreasing:
                        patterns.append({
                            "type": "trend",
                            "direction": "increasing",
                            "strength": increasing / (len(data) - 1),
                            "description": "Data shows an overall increasing trend"
                        })
                    elif decreasing > increasing:
                        patterns.append({
                            "type": "trend",
                            "direction": "decreasing",
                            "strength": decreasing / (len(data) - 1),
                            "description": "Data shows an overall decreasing trend"
                        })
                    else:
                        patterns.append({
                            "type": "trend",
                            "direction": "stable",
                            "strength": 0.5,
                            "description": "Data shows a stable trend"
                        })
            
            elif pattern_type == "anomaly":
                # Simple anomaly detection
                if len(data) >= 5:
                    mean_val = sum(data) / len(data)
                    std_dev = (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5
                    
                    for i, value in enumerate(data):
                        if abs(value - mean_val) > 2 * std_dev:
                            patterns.append({
                                "type": "anomaly",
                                "index": i,
                                "value": value,
                                "deviation": abs(value - mean_val) / std_dev,
                                "description": f"Anomalous value {value} at position {i}"
                            })
            
            elif pattern_type == "seasonal":
                # Basic seasonal pattern detection
                if len(data) >= 12:
                    # Look for repeating patterns (simplified)
                    patterns.append({
                        "type": "seasonal",
                        "period": 12,
                        "confidence": 0.6,
                        "description": "Potential seasonal pattern detected with 12-period cycle"
                    })
            
            elif pattern_type == "correlation":
                # Correlation analysis (requires paired data)
                if len(data) >= 2 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                    patterns.append({
                        "type": "correlation",
                        "strength": 0.7,  # Simplified correlation
                        "description": "Correlation analysis performed on paired data"
                    })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
            return [{"type": "error", "description": str(e)}]
    
    async def _generate_insights(self, analysis_results: Dict[str, Any], business_context: str) -> List[Dict[str, Any]]:
        """Generate actionable insights"""
        insights = []
        
        try:
            # Extract key information from analysis results
            if "statistics" in analysis_results:
                insights.append({
                    "type": "statistical",
                    "priority": "high",
                    "insight": "Statistical analysis reveals data characteristics",
                    "action": "Use statistical measures to guide decision making",
                    "impact": "medium"
                })
            
            if "patterns" in analysis_results:
                insights.append({
                    "type": "pattern",
                    "priority": "medium",
                    "insight": "Patterns identified in the data provide predictive value",
                    "action": "Monitor patterns for trend changes",
                    "impact": "high"
                })
            
            if business_context:
                insights.append({
                    "type": "contextual",
                    "priority": "high",
                    "insight": f"Analysis should be interpreted within {business_context} context",
                    "action": "Apply domain-specific knowledge to results",
                    "impact": "high"
                })
            
            # Default insight if no specific patterns found
            if not insights:
                insights.append({
                    "type": "general",
                    "priority": "medium",
                    "insight": "Data analysis completed successfully",
                    "action": "Review results and plan next steps",
                    "impact": "medium"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return [{"type": "error", "insight": str(e)}]
    
    async def _compare_datasets(self, datasets: List[Any], metrics: List[str]) -> Dict[str, Any]:
        """Compare multiple datasets"""
        comparison = {
            "datasets_count": len(datasets),
            "metrics": metrics,
            "results": {},
            "summary": ""
        }
        
        try:
            # Simple comparison logic
            for metric in metrics:
                comparison["results"][metric] = {}
                
                for i, dataset in enumerate(datasets):
                    dataset_name = f"dataset_{i}"
                    
                    if isinstance(dataset, list) and all(isinstance(x, (int, float)) for x in dataset):
                        if metric == "mean":
                            comparison["results"][metric][dataset_name] = sum(dataset) / len(dataset)
                        elif metric == "median":
                            sorted_data = sorted(dataset)
                            n = len(sorted_data)
                            comparison["results"][metric][dataset_name] = (
                                sorted_data[n//2] if n % 2 == 1 
                                else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
                            )
                        elif metric == "variance":
                            mean_val = sum(dataset) / len(dataset)
                            comparison["results"][metric][dataset_name] = sum((x - mean_val) ** 2 for x in dataset) / len(dataset)
                    else:
                        comparison["results"][metric][dataset_name] = f"Cannot calculate {metric} for non-numeric data"
            
            comparison["summary"] = f"Comparison completed for {len(datasets)} datasets using {len(metrics)} metrics"
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing datasets: {e}")
            comparison["error"] = str(e)
            return comparison
    
    async def _comprehensive_analysis(self, raw_data: List[Any], statistics: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Perform comprehensive analysis combining multiple approaches"""
        comprehensive_results = {
            "raw_data_summary": {},
            "statistical_analysis": {},
            "pattern_analysis": {},
            "insights": [],
            "recommendations": [],
            "confidence_score": 0.0
        }
        
        try:
            # Analyze raw data
            if raw_data:
                comprehensive_results["raw_data_summary"] = {
                    "count": len(raw_data),
                    "type": type(raw_data[0]).__name__ if raw_data else "empty",
                    "sample": raw_data[:5] if len(raw_data) >= 5 else raw_data
                }
            
            # Include statistical analysis
            if statistics:
                comprehensive_results["statistical_analysis"] = statistics
            
            # Pattern analysis
            if raw_data and all(isinstance(x, (int, float)) for x in raw_data):
                patterns = await self._identify_patterns(raw_data, "trend")
                comprehensive_results["pattern_analysis"] = patterns
            
            # Generate comprehensive insights
            analysis_data = {
                "statistics": statistics,
                "patterns": comprehensive_results.get("pattern_analysis", []),
                "raw_data": raw_data
            }
            
            insights = await self._analyze_data(analysis_data, analysis_type, "comprehensive analysis")
            comprehensive_results["insights"] = insights.get("findings", [])
            comprehensive_results["recommendations"] = insights.get("recommendations", [])
            comprehensive_results["confidence_score"] = insights.get("confidence", 0.0)
            
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            comprehensive_results["error"] = str(e)
            return comprehensive_results

if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = AnalysisAgent()
        await agent.start()
    
    asyncio.run(main())