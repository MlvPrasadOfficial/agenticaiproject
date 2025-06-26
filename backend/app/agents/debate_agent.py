# Debate Agent - Multi-Perspective Analysis and Validation

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import asyncio

from app.agents.base_agent import BaseAgent


class DebateAgent(BaseAgent):
    """Multi-perspective analyst that evaluates different approaches and provides balanced views"""
    
    def __init__(self):
        super().__init__("Debate Agent")
        self.perspectives = ["optimistic", "conservative", "neutral", "critical"]
        self.debate_frameworks = {
            "sql": ["performance", "accuracy", "completeness"],
            "insight": ["relevance", "depth", "actionability"],
            "chart": ["clarity", "accuracy", "usefulness"]
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate agent output vs critique feedback and provide balanced perspective"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Debate Agent"}
        
        # Get inputs for debate
        agent_type = state.get("agent_type", "unknown")
        agent_output = state.get("agent_output", {})
        critique_results = state.get("critique_results", {})
        query_context = state.get("query", "")
        
        try:
            # Generate multiple perspectives
            perspectives = await self._generate_perspectives(
                agent_type, agent_output, critique_results, query_context
            )
            
            # Conduct debate analysis
            debate_analysis = await self._conduct_debate_analysis(perspectives, agent_type)
            
            # Reach consensus
            consensus = await self._reach_consensus(perspectives, debate_analysis)
            
            return {
                "agent": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "agent_type_debated": agent_type,
                "perspectives": perspectives,
                "debate_analysis": debate_analysis,
                "consensus": consensus,
                "recommendation": consensus.get("final_recommendation", ""),
                "confidence_level": consensus.get("confidence", 0.0)
            }
            
        except Exception as e:
            error_msg = f"Error in debate execution: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    async def _generate_perspectives(
        self, 
        agent_type: str, 
        agent_output: Dict[str, Any], 
        critique_results: Dict[str, Any], 
        query: str
    ) -> Dict[str, Any]:
        """Generate multiple perspectives on the agent output and critique"""
        
        perspectives = {}
        
        # Optimistic perspective (pro-agent output)
        perspectives["optimistic"] = await self._optimistic_view(agent_output, critique_results)
        
        # Conservative perspective (pro-critique)
        perspectives["conservative"] = await self._conservative_view(agent_output, critique_results)
        
        # Neutral perspective (balanced analysis)
        perspectives["neutral"] = await self._neutral_view(agent_output, critique_results)
        
        # Critical perspective (identify gaps)
        perspectives["critical"] = await self._critical_view(agent_output, critique_results, query)
        
        return perspectives
    
    async def _optimistic_view(self, agent_output: Dict[str, Any], critique_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimistic perspective favoring the agent output"""
        view = {
            "stance": "pro_agent_output",
            "arguments": [],
            "evidence": [],
            "confidence": 0.0
        }
        
        # Look for strengths in agent output
        if "results" in agent_output and agent_output["results"]:
            view["arguments"].append("Agent successfully produced results")
            view["evidence"].append("Non-empty output generated")
        
        # Minimize critique concerns
        if critique_results.get("strengths"):
            for strength in critique_results["strengths"]:
                view["arguments"].append(f"Critique acknowledged: {strength}")
                view["evidence"].append("Positive validation from quality review")
        
        # Address issues positively
        issues = critique_results.get("issues_found", [])
        if len(issues) <= 1:
            view["arguments"].append("Minimal issues identified in quality review")
            view["confidence"] = 0.8
        elif len(issues) <= 2:
            view["arguments"].append("Only minor issues found, overall output acceptable")
            view["confidence"] = 0.6
        else:
            view["arguments"].append("Issues are addressable with minor adjustments")
            view["confidence"] = 0.4
        
        return view
    
    async def _conservative_view(self, agent_output: Dict[str, Any], critique_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conservative perspective favoring the critique concerns"""
        view = {
            "stance": "pro_critique_concerns",
            "arguments": [],
            "evidence": [],
            "confidence": 0.0
        }
        
        # Emphasize critique issues
        issues = critique_results.get("issues_found", [])
        if issues:
            view["arguments"].append(f"Quality review identified {len(issues)} significant concerns")
            for issue in issues:
                view["evidence"].append(f"Issue: {issue}")
            view["confidence"] = min(0.9, 0.6 + len(issues) * 0.1)
        
        # Question agent output quality
        if not agent_output.get("results"):
            view["arguments"].append("Agent failed to produce meaningful results")
            view["evidence"].append("Empty or missing output")
        
        # Highlight recommendations
        recommendations = critique_results.get("recommendations", [])
        if recommendations:
            view["arguments"].append("Multiple improvements recommended by quality review")
            for rec in recommendations:
                view["evidence"].append(f"Recommendation: {rec}")
        
        # Default conservative stance
        if not view["arguments"]:
            view["arguments"].append("Quality assurance is essential for reliable results")
            view["confidence"] = 0.5
        
        return view
    
    async def _neutral_view(self, agent_output: Dict[str, Any], critique_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate balanced neutral perspective"""
        view = {
            "stance": "balanced_analysis",
            "arguments": [],
            "evidence": [],
            "confidence": 0.0
        }
        
        # Count positives and negatives
        strengths = len(critique_results.get("strengths", []))
        issues = len(critique_results.get("issues_found", []))
        
        view["arguments"].append(f"Analysis shows {strengths} strengths and {issues} issues")
        view["evidence"].append(f"Strength/Issue ratio: {strengths}:{issues}")
        
        # Balanced assessment
        if strengths > issues:
            view["arguments"].append("Output quality leans positive with room for improvement")
            view["confidence"] = 0.7
        elif issues > strengths:
            view["arguments"].append("Output needs improvement but has salvageable elements")
            view["confidence"] = 0.4
        else:
            view["arguments"].append("Output shows balanced strengths and weaknesses")
            view["confidence"] = 0.5
        
        # Consider output completeness
        if agent_output and "results" in agent_output:
            view["arguments"].append("Agent provided structured output for evaluation")
        else:
            view["arguments"].append("Output structure may need enhancement")
        
        return view
    
    async def _critical_view(self, agent_output: Dict[str, Any], critique_results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate critical perspective identifying gaps and missing elements"""
        view = {
            "stance": "identify_gaps",
            "arguments": [],
            "evidence": [],
            "confidence": 0.0
        }
        
        # Look for missing elements
        gaps = []
        
        # Check query fulfillment
        if query and agent_output:
            query_keywords = query.lower().split()
            output_text = str(agent_output).lower()
            missing_keywords = [kw for kw in query_keywords if kw not in output_text]
            
            if missing_keywords:
                gaps.append(f"Query elements not addressed: {', '.join(missing_keywords[:3])}")
        
        # Check completeness of critique
        if not critique_results.get("checks_performed"):
            gaps.append("Incomplete quality review process")
        
        # Check for edge cases
        if "error" in agent_output:
            gaps.append("Error handling and recovery not demonstrated")
        
        # Critical assessment
        if gaps:
            view["arguments"].append(f"Identified {len(gaps)} critical gaps")
            for gap in gaps:
                view["evidence"].append(f"Gap: {gap}")
            view["confidence"] = 0.8
        else:
            view["arguments"].append("No major gaps identified in current analysis")
            view["confidence"] = 0.3
        
        return view
    
    async def _conduct_debate_analysis(self, perspectives: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Analyze the debate between different perspectives"""
        analysis = {
            "framework": self.debate_frameworks.get(agent_type, ["quality", "relevance", "completeness"]),
            "perspective_summary": {},
            "conflicts": [],
            "agreements": [],
            "key_points": []
        }
        
        # Summarize each perspective
        for name, perspective in perspectives.items():
            analysis["perspective_summary"][name] = {
                "stance": perspective.get("stance", "unknown"),
                "argument_count": len(perspective.get("arguments", [])),
                "confidence": perspective.get("confidence", 0.0)
            }
        
        # Identify conflicts
        optimistic_conf = perspectives.get("optimistic", {}).get("confidence", 0)
        conservative_conf = perspectives.get("conservative", {}).get("confidence", 0)
        
        if abs(optimistic_conf - conservative_conf) > 0.3:
            analysis["conflicts"].append("Significant disagreement between optimistic and conservative views")
        
        # Identify agreements
        neutral_args = perspectives.get("neutral", {}).get("arguments", [])
        if neutral_args:
            analysis["agreements"].append("Neutral perspective provides balanced framework")
        
        # Extract key points
        all_args = []
        for perspective in perspectives.values():
            all_args.extend(perspective.get("arguments", []))
        
        # Simple key point extraction (most common themes)
        analysis["key_points"] = all_args[:3]  # Top 3 arguments
        
        return analysis
    
    async def _reach_consensus(self, perspectives: Dict[str, Any], debate_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Reach consensus based on perspective analysis"""
        
        # Calculate weighted confidence
        confidences = [p.get("confidence", 0.0) for p in perspectives.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Determine recommendation based on perspective balance
        optimistic_conf = perspectives.get("optimistic", {}).get("confidence", 0)
        conservative_conf = perspectives.get("conservative", {}).get("confidence", 0)
        neutral_conf = perspectives.get("neutral", {}).get("confidence", 0)
        
        if optimistic_conf > 0.7 and conservative_conf < 0.5:
            recommendation = "APPROVE - Output meets quality standards with minor concerns"
            confidence = optimistic_conf
        elif conservative_conf > 0.7 and optimistic_conf < 0.5:
            recommendation = "REVISE - Significant improvements needed before approval"
            confidence = conservative_conf
        elif neutral_conf > 0.6:
            recommendation = "CONDITIONAL APPROVE - Address identified issues"
            confidence = neutral_conf
        else:
            recommendation = "REVIEW REQUIRED - Conflicting assessments need resolution"
            confidence = avg_confidence
        
        return {
            "final_recommendation": recommendation,
            "confidence": round(confidence, 2),
            "consensus_strength": "strong" if max(confidences) > 0.8 else "moderate" if max(confidences) > 0.6 else "weak",
            "rationale": f"Based on average confidence of {round(avg_confidence, 2)} across {len(perspectives)} perspectives"
        }
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        return ["agent_type", "agent_output", "critique_results"]
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input for debate operations"""
        if not isinstance(state, dict):
            return False
        
        required_fields = self.get_required_fields()
        return all(field in state for field in required_fields)
