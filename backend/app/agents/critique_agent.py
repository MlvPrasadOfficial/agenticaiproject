# Critique Agent - Quality Review and Validation

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import asyncio

from app.agents.base_agent import BaseAgent


class CritiqueAgent(BaseAgent):
    """Quality assurance specialist that reviews and validates agent outputs"""
    
    def __init__(self):
        super().__init__("Critique Agent")
        self.quality_thresholds = {
            "sql_accuracy": 0.8,
            "insight_relevance": 0.7,
            "chart_clarity": 0.8,
            "data_completeness": 0.9
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Review and critique agent outputs for quality and accuracy"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Critique Agent"}
        
        # Get the agent output to critique
        agent_type = state.get("agent_type", "unknown")
        agent_output = state.get("agent_output", {})
        query_context = state.get("query", "")
        
        try:
            # Perform different critiques based on agent type
            if agent_type == "sql":
                critique_result = await self._critique_sql_output(agent_output, query_context)
            elif agent_type == "insight":
                critique_result = await self._critique_insight_output(agent_output, query_context)
            elif agent_type == "chart":
                critique_result = await self._critique_chart_output(agent_output, query_context)
            else:
                critique_result = await self._general_critique(agent_output, query_context)
            
            # Generate overall quality assessment
            quality_assessment = await self._assess_overall_quality(critique_result)
            
            return {
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "agent_type_reviewed": agent_type,
                "critique_results": critique_result,
                "quality_assessment": quality_assessment,
                "recommendations": critique_result.get("recommendations", []),
                "approval_status": quality_assessment.get("approved", False),
                "quality_score": quality_assessment.get("score", 0.0)
            }
            
        except Exception as e:
            error_msg = f"Error in critique execution: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    async def _critique_sql_output(self, sql_output: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Critique SQL agent output for accuracy and completeness"""
        critique = {
            "category": "sql_analysis",
            "checks_performed": [],
            "issues_found": [],
            "recommendations": [],
            "strengths": []
        }
        
        # Check data completeness
        if "results" in sql_output:
            results = sql_output["results"]
            if isinstance(results, dict) and "data" in results:
                data_rows = len(results["data"]) if results["data"] else 0
                critique["checks_performed"].append("data_completeness")
                
                if data_rows > 0:
                    critique["strengths"].append(f"Retrieved {data_rows} data rows")
                else:
                    critique["issues_found"].append("No data returned from SQL query")
                    critique["recommendations"].append("Verify data filters and query logic")
        
        # Check for error handling
        if "error" in sql_output:
            critique["checks_performed"].append("error_analysis")
            critique["issues_found"].append(f"SQL execution error: {sql_output['error']}")
            critique["recommendations"].append("Review SQL syntax and data schema")
        
        # Check query relevance
        if query and "results" in sql_output:
            critique["checks_performed"].append("query_relevance")
            # Simple relevance check based on query keywords
            query_keywords = query.lower().split()
            if any(keyword in str(sql_output["results"]).lower() for keyword in query_keywords):
                critique["strengths"].append("Results appear relevant to user query")
            else:
                critique["issues_found"].append("Results may not be fully relevant to query")
                critique["recommendations"].append("Refine query to better match user intent")
        
        return critique
    
    async def _critique_insight_output(self, insight_output: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Critique Insight agent output for business relevance and depth"""
        critique = {
            "category": "insight_analysis",
            "checks_performed": [],
            "issues_found": [],
            "recommendations": [],
            "strengths": []
        }
        
        # Check insight depth
        if "insights" in insight_output:
            insights = insight_output["insights"]
            critique["checks_performed"].append("insight_depth")
            
            if isinstance(insights, list) and len(insights) >= 3:
                critique["strengths"].append(f"Generated {len(insights)} distinct insights")
            elif isinstance(insights, str) and len(insights) > 100:
                critique["strengths"].append("Provided detailed insight analysis")
            else:
                critique["issues_found"].append("Insights appear shallow or insufficient")
                critique["recommendations"].append("Generate more comprehensive business insights")
        
        # Check business relevance
        business_keywords = ["revenue", "profit", "growth", "trend", "performance", "efficiency"]
        if "insights" in insight_output:
            content = str(insight_output["insights"]).lower()
            critique["checks_performed"].append("business_relevance")
            
            relevant_keywords = [kw for kw in business_keywords if kw in content]
            if relevant_keywords:
                critique["strengths"].append(f"Contains business-relevant terms: {', '.join(relevant_keywords)}")
            else:
                critique["issues_found"].append("Insights lack clear business relevance")
                critique["recommendations"].append("Focus on business impact and actionable insights")
        
        return critique
    
    async def _critique_chart_output(self, chart_output: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Critique Chart agent output for clarity and appropriateness"""
        critique = {
            "category": "chart_analysis", 
            "checks_performed": [],
            "issues_found": [],
            "recommendations": [],
            "strengths": []
        }
        
        # Check chart type appropriateness
        if "chart_type" in chart_output:
            chart_type = chart_output["chart_type"]
            critique["checks_performed"].append("chart_type_validation")
            
            valid_types = ["bar", "line", "pie", "scatter", "histogram", "box"]
            if chart_type.lower() in valid_types:
                critique["strengths"].append(f"Using appropriate chart type: {chart_type}")
            else:
                critique["issues_found"].append(f"Unusual chart type: {chart_type}")
                critique["recommendations"].append("Consider using standard chart types for clarity")
        
        # Check data configuration
        if "chart_config" in chart_output:
            config = chart_output["chart_config"]
            critique["checks_performed"].append("chart_configuration")
            
            required_fields = ["x_axis", "y_axis", "title"]
            missing_fields = [field for field in required_fields if field not in config]
            
            if not missing_fields:
                critique["strengths"].append("Chart configuration is complete")
            else:
                critique["issues_found"].append(f"Missing chart elements: {', '.join(missing_fields)}")
                critique["recommendations"].append("Ensure all required chart elements are specified")
        
        return critique
    
    async def _general_critique(self, output: Dict[str, Any], query: str) -> Dict[str, Any]:
        """General critique for unknown agent types"""
        return {
            "category": "general_review",
            "checks_performed": ["basic_structure"],
            "issues_found": [] if isinstance(output, dict) else ["Output format appears invalid"],
            "recommendations": ["Ensure proper output structure"] if not isinstance(output, dict) else [],
            "strengths": ["Valid output format"] if isinstance(output, dict) else []
        }
    
    async def _assess_overall_quality(self, critique: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall quality and provide approval status"""
        issues_count = len(critique.get("issues_found", []))
        strengths_count = len(critique.get("strengths", []))
        
        # Calculate quality score
        if issues_count == 0 and strengths_count > 0:
            score = 0.95
        elif issues_count <= 1 and strengths_count >= 2:
            score = 0.85
        elif issues_count <= 2 and strengths_count >= 1:
            score = 0.70
        else:
            score = max(0.3, 0.8 - (issues_count * 0.15))
        
        # Determine approval
        approved = score >= 0.75 and issues_count <= 1
        
        return {
            "score": round(score, 2),
            "approved": approved,
            "confidence": "high" if score >= 0.85 else "medium" if score >= 0.65 else "low",
            "summary": f"Quality score: {round(score, 2)}, Issues: {issues_count}, Strengths: {strengths_count}"
        }
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        return ["agent_type", "agent_output"]
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input for critique operations"""
        if not isinstance(state, dict):
            return False
        
        # Check for required agent output
        if "agent_output" not in state:
            return False
        
        # Agent type should be specified
        if "agent_type" not in state:
            return False
        
        return True
