# Narrative Agent - Business Narrative Generation

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from app.agents.base_agent import BaseAgent


class NarrativeAgent(BaseAgent):
    """Business narrative generation specialist"""
    
    def __init__(self):
        super().__init__("Narrative Agent")
        self.narrative_templates = {
            "data_story": "Data-driven Business Story",
            "insight_narrative": "Insight-driven Narrative",
            "trend_story": "Trend Analysis Story",
            "comparative_narrative": "Comparative Analysis Narrative",
            "performance_story": "Performance Analysis Story"
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compelling business narrative from analysis results"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Narrative Agent"}
        
        # Gather all analysis components
        query_intent = state.get("query_intent", {})
        insights = state.get("insights", {})
        sql_results = state.get("sql_results", {})
        chart_specs = state.get("chart_specs", {})
        critique_feedback = state.get("critique_feedback", {})
        debate_consensus = state.get("debate_consensus", {})
        data_profile = state.get("data_profile", {})
        
        # Generate narrative structure
        narrative_structure = await self._create_narrative_structure(
            query_intent, insights, sql_results, critique_feedback, debate_consensus
        )
        
        # Create compelling narrative
        business_narrative = await self._generate_business_narrative(
            narrative_structure, insights, sql_results, chart_specs, data_profile
        )
        
        # Add executive insights
        executive_insights = await self._generate_executive_insights(
            business_narrative, debate_consensus, critique_feedback
        )
        
        return {
            "status": "completed",
            "agent": "narrative",
            "business_narrative": business_narrative,
            "executive_insights": executive_insights,
            "narrative_structure": narrative_structure,
            "narrative_confidence": self._calculate_narrative_confidence(
                insights, sql_results, critique_feedback, debate_consensus
            ),
            "key_storylines": self._extract_key_storylines(business_narrative),
            "actionable_recommendations": self._extract_actionable_items(
                business_narrative, executive_insights
            )
        }
    
    async def _create_narrative_structure(
        self, 
        query_intent: Dict[str, Any], 
        insights: Dict[str, Any],
        sql_results: Dict[str, Any],
        critique_feedback: Dict[str, Any],
        debate_consensus: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create the overall narrative structure"""
        
        # Determine narrative type based on content
        narrative_type = self._determine_narrative_type(query_intent, insights, sql_results)
        
        # Create story arc
        story_arc = {
            "opening": self._create_opening_hook(query_intent, insights),
            "context": self._establish_business_context(insights, sql_results),
            "findings": self._structure_key_findings(insights, sql_results, critique_feedback),
            "implications": self._derive_business_implications(debate_consensus, insights),
            "conclusion": self._craft_conclusion(debate_consensus, critique_feedback)
        }
        
        return {
            "narrative_type": narrative_type,
            "story_arc": story_arc,
            "tone": self._determine_narrative_tone(critique_feedback, debate_consensus),
            "target_audience": self._identify_target_audience(query_intent),
            "key_messages": self._extract_key_messages(insights, debate_consensus)
        }
    
    async def _generate_business_narrative(
        self,
        narrative_structure: Dict[str, Any],
        insights: Dict[str, Any],
        sql_results: Dict[str, Any],
        chart_specs: Dict[str, Any],
        data_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the complete business narrative"""
        
        story_arc = narrative_structure.get("story_arc", {})
        narrative_type = narrative_structure.get("narrative_type", "data_story")
        tone = narrative_structure.get("tone", "professional")
        
        # Generate each section
        sections = {}
        
        # Opening section
        sections["opening"] = self._write_opening_section(
            story_arc.get("opening", ""), insights, tone
        )
        
        # Context section
        sections["context"] = self._write_context_section(
            story_arc.get("context", ""), data_profile, sql_results
        )
        
        # Findings section
        sections["findings"] = self._write_findings_section(
            story_arc.get("findings", ""), insights, sql_results, chart_specs
        )
        
        # Implications section
        sections["implications"] = self._write_implications_section(
            story_arc.get("implications", ""), insights
        )
        
        # Conclusion section
        sections["conclusion"] = self._write_conclusion_section(
            story_arc.get("conclusion", ""), insights
        )
        
        # Assemble full narrative
        full_narrative = self._assemble_narrative_text(sections, narrative_type)
        
        return {
            "sections": sections,
            "full_narrative": full_narrative,
            "narrative_type": narrative_type,
            "word_count": len(full_narrative.split()),
            "reading_time_minutes": max(1, len(full_narrative.split()) // 200)
        }
    
    async def _generate_executive_insights(
        self,
        business_narrative: Dict[str, Any],
        debate_consensus: Dict[str, Any],
        critique_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive-level insights and recommendations"""
        
        # Extract key insights from consensus and critique
        strategic_insights = self._extract_strategic_insights(debate_consensus)
        risk_considerations = self._extract_risk_considerations(critique_feedback)
        opportunity_areas = self._extract_opportunities(debate_consensus, critique_feedback)
        
        # Generate executive summary points
        executive_summary = self._create_executive_summary(
            strategic_insights, risk_considerations, opportunity_areas
        )
        
        # Create action priorities
        action_priorities = self._prioritize_actions(
            strategic_insights, opportunity_areas, risk_considerations
        )
        
        return {
            "executive_summary": executive_summary,
            "strategic_insights": strategic_insights,
            "risk_considerations": risk_considerations,
            "opportunity_areas": opportunity_areas,
            "action_priorities": action_priorities,
            "confidence_level": self._assess_insight_confidence(
                debate_consensus, critique_feedback
            )
        }
    
    def _determine_narrative_type(
        self, 
        query_intent: Dict[str, Any], 
        insights: Dict[str, Any], 
        sql_results: Dict[str, Any]
    ) -> str:
        """Determine the most appropriate narrative type"""
        
        query_type = query_intent.get("type", "").lower()
        has_trends = bool(insights.get("trends", []))
        has_comparisons = bool(insights.get("comparisons", []))
        has_performance_data = bool(sql_results.get("performance_metrics", []))
        
        if "trend" in query_type or has_trends:
            return "trend_story"
        elif "compare" in query_type or has_comparisons:
            return "comparative_narrative"
        elif "performance" in query_type or has_performance_data:
            return "performance_story"
        elif insights.get("business_insights"):
            return "insight_narrative"
        else:
            return "data_story"
    
    def _create_opening_hook(
        self, 
        query_intent: Dict[str, Any], 
        insights: Dict[str, Any]
    ) -> str:
        """Create compelling opening hook"""
        
        # Extract the most significant finding
        key_insight = self._find_most_significant_insight(insights)
        query_context = query_intent.get("business_context", "")
        
        if key_insight:
            impact = key_insight.get("business_impact", "")
            if impact:
                return f"Analysis reveals {impact.lower()}, fundamentally shifting our understanding of {query_context}."
        
        return f"Our analysis of {query_context} uncovers critical insights that demand immediate attention."
    
    def _establish_business_context(
        self, 
        insights: Dict[str, Any], 
        sql_results: Dict[str, Any]
    ) -> str:
        """Establish relevant business context"""
        
        data_timeframe = sql_results.get("timeframe", "recent period")
        data_scope = sql_results.get("scope", "organizational data")
        key_metrics = insights.get("key_metrics", [])
        
        context = f"This analysis examines {data_scope} across {data_timeframe}"
        
        if key_metrics:
            metrics_text = ", ".join([m.get("name", "") for m in key_metrics[:3]])
            context += f", focusing on {metrics_text}"
        
        context += "."
        return context
    
    def _structure_key_findings(
        self,
        insights: Dict[str, Any],
        sql_results: Dict[str, Any],
        critique_feedback: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Structure and prioritize key findings"""
        
        findings = []
        
        # Business insights
        business_insights = insights.get("business_insights", [])
        for insight in business_insights[:5]:  # Top 5 insights
            confidence = critique_feedback.get("insight_confidence", {}).get(
                insight.get("id", ""), 0.7
            )
            findings.append({
                "type": "business_insight",
                "content": insight,
                "confidence": confidence,
                "priority": insight.get("priority", "medium")
            })
        
        # Data patterns
        patterns = insights.get("patterns", [])
        for pattern in patterns[:3]:  # Top 3 patterns
            findings.append({
                "type": "data_pattern",
                "content": pattern,
                "confidence": 0.8,
                "priority": "medium"
            })
        
        # Sort by priority and confidence
        findings.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}.get(x["priority"], 2),
            x["confidence"]
        ), reverse=True)
        
        return findings
    
    def _derive_business_implications(
        self,
        debate_consensus: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Derive business implications from consensus and insights"""
        
        implications = []
        
        # Strategic implications from consensus
        consensus_points = debate_consensus.get("consensus_points", [])
        for point in consensus_points:
            if point.get("category") == "strategic":
                implications.append({
                    "type": "strategic",
                    "implication": point.get("description", ""),
                    "impact_level": point.get("impact_level", "medium"),
                    "timeframe": point.get("timeframe", "medium-term")
                })
        
        # Operational implications
        operational_insights = insights.get("operational_insights", [])
        for insight in operational_insights:
            implications.append({
                "type": "operational",
                "implication": insight.get("implication", ""),
                "impact_level": insight.get("impact_level", "medium"),
                "timeframe": "short-term"
            })
        
        return implications
    
    def _craft_conclusion(
        self,
        debate_consensus: Dict[str, Any],
        critique_feedback: Dict[str, Any]
    ) -> str:
        """Craft compelling conclusion"""
        
        final_recommendation = debate_consensus.get("final_recommendation", "")
        confidence_level = critique_feedback.get("overall_confidence", 0.7)
        
        if confidence_level > 0.8:
            confidence_phrase = "with high confidence"
        elif confidence_level > 0.6:
            confidence_phrase = "with reasonable confidence"
        else:
            confidence_phrase = "while noting areas for further investigation"
        
        conclusion = f"The analysis concludes {confidence_phrase} that {final_recommendation}"
        conclusion += " This evidence-based insight provides a clear foundation for strategic decision-making."
        
        return conclusion
    
    def _write_opening_section(
        self, 
        opening_hook: str, 
        insights: Dict[str, Any], 
        tone: str
    ) -> str:
        """Write the opening section of the narrative"""
        
        section = opening_hook
        
        # Add context and scope
        key_metrics = insights.get("key_metrics", [])
        if key_metrics:
            metric_names = [m.get("name", "") for m in key_metrics[:2]]
            section += f" Our examination of {' and '.join(metric_names)} reveals patterns that reshape conventional understanding."
        
        return section
    
    def _write_context_section(
        self,
        context: str,
        data_profile: Dict[str, Any],
        sql_results: Dict[str, Any]
    ) -> str:
        """Write the context section"""
        
        section = context
        
        # Add data characteristics
        record_count = data_profile.get("total_records", 0)
        if record_count > 0:
            section += f" Drawing from {record_count:,} data points, "
            section += "our analysis provides comprehensive coverage of the business landscape."
        
        return section
    
    def _write_findings_section(
        self,
        findings: List[Dict[str, Any]],
        insights: Dict[str, Any],
        sql_results: Dict[str, Any],
        chart_specs: Dict[str, Any]
    ) -> str:
        """Write the findings section"""
        
        section = "Key findings emerge from multiple analytical perspectives:\n\n"
        
        for i, finding in enumerate(findings[:5], 1):
            content = finding.get("content", {})
            finding_type = finding.get("type", "")
            
            if finding_type == "business_insight":
                description = content.get("description", "")
                impact = content.get("business_impact", "")
                section += f"{i}. {description}"
                if impact:
                    section += f" This translates to {impact.lower()}."
                section += "\n\n"
            elif finding_type == "data_pattern":
                pattern_desc = content.get("description", "")
                section += f"{i}. Data reveals {pattern_desc.lower()}.\n\n"
        
        return section.strip()
    
    def _write_implications_section(
        self, 
        implications: List[Dict[str, Any]], 
        insights: Dict[str, Any]
    ) -> str:
        """Write the implications section"""
        
        section = "These findings carry significant business implications:\n\n"
        
        # Group by type
        strategic_implications = [i for i in implications if i.get("type") == "strategic"]
        operational_implications = [i for i in implications if i.get("type") == "operational"]
        
        if strategic_implications:
            section += "Strategic Considerations:\n"
            for impl in strategic_implications[:3]:
                section += f"• {impl.get('implication', '')}\n"
            section += "\n"
        
        if operational_implications:
            section += "Operational Impact:\n"
            for impl in operational_implications[:3]:
                section += f"• {impl.get('implication', '')}\n"
            section += "\n"
        
        return section.strip()
    
    def _write_conclusion_section(
        self, 
        conclusion: str, 
        insights: Dict[str, Any]
    ) -> str:
        """Write the conclusion section"""
        
        section = conclusion
        
        # Add forward-looking statement
        recommendations = insights.get("recommendations", [])
        if recommendations:
            section += f" Immediate priorities include {recommendations[0].get('description', '').lower()}."
        
        section += " Organizations that act on these insights position themselves for sustained competitive advantage."
        
        return section
    
    def _assemble_narrative_text(
        self, 
        sections: Dict[str, Any], 
        narrative_type: str
    ) -> str:
        """Assemble complete narrative text"""
        
        narrative_parts = []
        
        # Title based on narrative type
        titles = {
            "data_story": "Data-Driven Business Insights",
            "insight_narrative": "Strategic Business Analysis",
            "trend_story": "Trend Analysis Report",
            "comparative_narrative": "Comparative Business Analysis",
            "performance_story": "Performance Analysis Summary"
        }
        
        title = titles.get(narrative_type, "Business Analysis Report")
        narrative_parts.append(f"# {title}\n")
        
        # Assemble sections
        section_order = ["opening", "context", "findings", "implications", "conclusion"]
        
        for section_name in section_order:
            if section_name in sections and sections[section_name]:
                narrative_parts.append(f"\n{sections[section_name]}\n")
        
        return "\n".join(narrative_parts)
    
    def _calculate_narrative_confidence(
        self,
        insights: Dict[str, Any],
        sql_results: Dict[str, Any],
        critique_feedback: Dict[str, Any],
        debate_consensus: Dict[str, Any]
    ) -> float:
        """Calculate overall narrative confidence score"""
        
        scores = []
        
        # Insight quality
        insight_count = len(insights.get("business_insights", []))
        if insight_count > 0:
            scores.append(min(1.0, insight_count / 5))
        
        # Data quality
        data_quality = sql_results.get("data_quality_score", 0.7)
        scores.append(data_quality)
        
        # Critique feedback
        critique_confidence = critique_feedback.get("overall_confidence", 0.7)
        scores.append(critique_confidence)
        
        # Consensus strength
        consensus_strength = debate_consensus.get("consensus_strength", 0.7)
        scores.append(consensus_strength)
        
        return sum(scores) / len(scores) if scores else 0.7
    
    def _extract_key_storylines(self, business_narrative: Dict[str, Any]) -> List[str]:
        """Extract key storylines from narrative"""
        
        storylines = []
        
        findings_section = business_narrative.get("sections", {}).get("findings", "")
        if findings_section:
            # Extract numbered points
            lines = findings_section.split("\n")
            for line in lines:
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("•")):
                    storylines.append(line.strip())
        
        return storylines[:5]  # Top 5 storylines
    
    def _extract_actionable_items(
        self,
        business_narrative: Dict[str, Any],
        executive_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract actionable recommendations"""
        
        actionable_items = []
        
        # From executive insights
        action_priorities = executive_insights.get("action_priorities", [])
        for priority in action_priorities:
            actionable_items.append({
                "action": priority.get("action", ""),
                "priority": priority.get("priority", "medium"),
                "timeframe": priority.get("timeframe", "medium-term"),
                "impact": priority.get("expected_impact", "")
            })
        
        # From opportunity areas
        opportunities = executive_insights.get("opportunity_areas", [])
        for opp in opportunities:
            actionable_items.append({
                "action": f"Pursue {opp.get('description', '').lower()}",
                "priority": "medium",
                "timeframe": opp.get("timeframe", "medium-term"),
                "impact": opp.get("potential_value", "")
            })
        
        return actionable_items[:7]  # Top 7 actions
    
    # Helper methods for executive insights
    def _extract_strategic_insights(self, debate_consensus: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract strategic insights from debate consensus"""
        
        strategic_insights = []
        consensus_points = debate_consensus.get("consensus_points", [])
        
        for point in consensus_points:
            if point.get("category") == "strategic":
                strategic_insights.append({
                    "insight": point.get("description", ""),
                    "confidence": point.get("confidence", 0.7),
                    "impact_level": point.get("impact_level", "medium"),
                    "supporting_evidence": point.get("supporting_evidence", [])
                })
        
        return strategic_insights
    
    def _extract_risk_considerations(self, critique_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract risk considerations from critique feedback"""
        
        risks = []
        quality_issues = critique_feedback.get("quality_issues", [])
        
        for issue in quality_issues:
            if issue.get("severity", "").lower() in ["high", "critical"]:
                risks.append({
                    "risk": issue.get("description", ""),
                    "severity": issue.get("severity", "medium"),
                    "mitigation": issue.get("recommendation", ""),
                    "likelihood": issue.get("likelihood", "medium")
                })
        
        return risks
    
    def _extract_opportunities(
        self,
        debate_consensus: Dict[str, Any],
        critique_feedback: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract opportunity areas"""
        
        opportunities = []
        
        # From consensus
        consensus_opportunities = debate_consensus.get("opportunities", [])
        for opp in consensus_opportunities:
            opportunities.append({
                "description": opp.get("description", ""),
                "potential_value": opp.get("potential_value", ""),
                "timeframe": opp.get("timeframe", "medium-term"),
                "requirements": opp.get("requirements", [])
            })
        
        # From critique improvements
        improvements = critique_feedback.get("improvement_areas", [])
        for improvement in improvements:
            opportunities.append({
                "description": f"Improve {improvement.get('area', '').lower()}",
                "potential_value": improvement.get("expected_benefit", ""),
                "timeframe": "short-term",
                "requirements": improvement.get("action_items", [])
            })
        
        return opportunities
    
    def _create_executive_summary(
        self,
        strategic_insights: List[Dict[str, Any]],
        risk_considerations: List[Dict[str, Any]],
        opportunity_areas: List[Dict[str, Any]]
    ) -> List[str]:
        """Create executive summary points"""
        
        summary_points = []
        
        # Top strategic insight
        if strategic_insights:
            top_insight = strategic_insights[0]
            summary_points.append(f"Key Finding: {top_insight.get('insight', '')}")
        
        # Primary opportunity
        if opportunity_areas:
            top_opportunity = opportunity_areas[0]
            summary_points.append(f"Primary Opportunity: {top_opportunity.get('description', '')}")
        
        # Main risk
        if risk_considerations:
            top_risk = risk_considerations[0]
            summary_points.append(f"Key Risk: {top_risk.get('risk', '')}")
        
        return summary_points
    
    def _prioritize_actions(
        self,
        strategic_insights: List[Dict[str, Any]],
        opportunity_areas: List[Dict[str, Any]],
        risk_considerations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize action items"""
        
        actions = []
        
        # High-impact opportunities
        for opp in opportunity_areas:
            if "high" in opp.get("potential_value", "").lower():
                actions.append({
                    "action": f"Capitalize on {opp.get('description', '').lower()}",
                    "priority": "high",
                    "timeframe": opp.get("timeframe", "medium-term"),
                    "expected_impact": opp.get("potential_value", "")
                })
        
        # Risk mitigation
        for risk in risk_considerations:
            if risk.get("severity", "").lower() == "high":
                actions.append({
                    "action": f"Mitigate {risk.get('risk', '').lower()}",
                    "priority": "high",
                    "timeframe": "short-term",
                    "expected_impact": f"Reduce {risk.get('severity', '')} risk"
                })
        
        # Strategic initiatives
        for insight in strategic_insights:
            if insight.get("impact_level", "").lower() == "high":
                actions.append({
                    "action": f"Implement strategy based on {insight.get('insight', '').lower()}",
                    "priority": "medium",
                    "timeframe": "medium-term",
                    "expected_impact": insight.get("impact_level", "")
                })
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 2), reverse=True)
        
        return actions[:5]  # Top 5 actions
    
    def _assess_insight_confidence(
        self,
        debate_consensus: Dict[str, Any],
        critique_feedback: Dict[str, Any]
    ) -> str:
        """Assess overall confidence in insights"""
        
        consensus_strength = debate_consensus.get("consensus_strength", 0.7)
        critique_confidence = critique_feedback.get("overall_confidence", 0.7)
        
        avg_confidence = (consensus_strength + critique_confidence) / 2
        
        if avg_confidence > 0.8:
            return "high"
        elif avg_confidence > 0.6:
            return "medium"
        else:
            return "low"
    
    def _find_most_significant_insight(self, insights: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the most significant insight"""
        
        business_insights = insights.get("business_insights", [])
        if not business_insights:
            return None
        
        # Find highest priority or highest confidence insight
        significant_insight = None
        max_score = 0
        
        for insight in business_insights:
            priority_score = {"high": 3, "medium": 2, "low": 1}.get(
                insight.get("priority", "medium"), 2
            )
            confidence_score = insight.get("confidence", 0.7)
            total_score = priority_score + confidence_score
            
            if total_score > max_score:
                max_score = total_score
                significant_insight = insight
        
        return significant_insight
    
    def _determine_narrative_tone(
        self,
        critique_feedback: Dict[str, Any],
        debate_consensus: Dict[str, Any]
    ) -> str:
        """Determine appropriate narrative tone"""
        
        confidence_level = critique_feedback.get("overall_confidence", 0.7)
        consensus_strength = debate_consensus.get("consensus_strength", 0.7)
        
        if confidence_level > 0.8 and consensus_strength > 0.8:
            return "confident"
        elif confidence_level > 0.6:
            return "professional"
        else:
            return "cautious"
    
    def _identify_target_audience(self, query_intent: Dict[str, Any]) -> str:
        """Identify target audience for narrative"""
        
        business_context = query_intent.get("business_context", "").lower()
        
        if "executive" in business_context or "strategic" in business_context:
            return "executives"
        elif "operational" in business_context or "tactical" in business_context:
            return "managers"
        elif "technical" in business_context:
            return "analysts"
        else:
            return "general_business"
    
    def _extract_key_messages(
        self,
        insights: Dict[str, Any],
        debate_consensus: Dict[str, Any]
    ) -> List[str]:
        """Extract key messages for narrative"""
        
        messages = []
        
        # From insights
        business_insights = insights.get("business_insights", [])
        for insight in business_insights[:3]:
            impact = insight.get("business_impact", "")
            if impact:
                messages.append(impact)
        
        # From consensus
        consensus_points = debate_consensus.get("consensus_points", [])
        for point in consensus_points[:2]:
            description = point.get("description", "")
            if description:
                messages.append(description)
        
        return messages[:5]  # Top 5 messages
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        return ["insights", "sql_results", "critique_feedback", "debate_consensus"]
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input state for narrative generation"""
        
        # Check for essential components
        has_insights = bool(state.get("insights", {}).get("business_insights", []))
        has_results = bool(state.get("sql_results"))
        has_critique = bool(state.get("critique_feedback"))
        has_debate = bool(state.get("debate_consensus"))
        
        # Need at least insights or results plus some feedback
        return (has_insights or has_results) and (has_critique or has_debate)
