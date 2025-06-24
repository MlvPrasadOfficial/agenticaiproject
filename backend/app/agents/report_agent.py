# Report Agent - Report Generation and Documentation

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import io
from pathlib import Path

from app.agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):
    """Business report generation and documentation specialist"""
    
    def __init__(self):
        super().__init__("Report Agent")
        self.report_templates = {
            "executive_summary": "Executive Summary Report",
            "detailed_analysis": "Detailed Analysis Report", 
            "data_quality": "Data Quality Assessment",
            "trend_report": "Trend Analysis Report",
            "comparative_report": "Comparative Analysis Report"
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive business report"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Report Agent"}
        
        # Gather all analysis results
        query_intent = state.get("query_intent", {})
        insights = state.get("insights", [])
        recommendations = state.get("business_recommendations", [])
        executive_summary = state.get("executive_summary", {})
        charts = state.get("generated_charts", [])
        data_profile = state.get("data_profile", {})
        sql_results = state.get("sql_results", [])
        
        # Determine report type
        report_type = self._determine_report_type(query_intent, insights)
        
        # Generate report sections
        report_sections = await self._generate_report_sections(
            report_type, query_intent, insights, recommendations, 
            executive_summary, charts, data_profile, sql_results
        )
        
        # Create final report
        final_report = await self._assemble_final_report(report_sections, report_type)
        
        # Generate metadata
        report_metadata = self._create_report_metadata(final_report, state)
        
        # Update state
        state.update({
            "final_report": final_report,
            "report_metadata": report_metadata,
            "report_type": report_type
        })
        
        return {
            "report": final_report,
            "metadata": report_metadata,
            "report_type": report_type,
            "sections": len(report_sections),
            "agent": self.agent_name,
            "status": "completed"
        }
    
    def _determine_report_type(self, query_intent: Dict[str, Any], insights: List[Dict[str, Any]]) -> str:
        """Determine appropriate report type based on analysis"""
        
        primary_intent = query_intent.get("primary_intent", "analyze")
        business_question = query_intent.get("business_question", "").lower()
        
        # Check for specific report types
        if "executive" in business_question or "summary" in business_question:
            return "executive_summary"
        elif "data quality" in business_question or "quality" in business_question:
            return "data_quality"
        elif "trend" in business_question or primary_intent == "forecast":
            return "trend_report"
        elif "compare" in business_question or primary_intent == "compare":
            return "comparative_report"
        else:
            return "detailed_analysis"
    
    async def _generate_report_sections(
        self,
        report_type: str,
        query_intent: Dict[str, Any],
        insights: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        executive_summary: Dict[str, Any],
        charts: List[Dict[str, Any]],
        data_profile: Dict[str, Any],
        sql_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate all report sections"""
        
        sections = []
        
        # Title section
        sections.append(await self._create_title_section(query_intent, report_type))
        
        # Executive summary (for all report types)
        if executive_summary:
            sections.append(await self._create_executive_summary_section(executive_summary))
        
        # Data overview
        if data_profile or sql_results:
            sections.append(await self._create_data_overview_section(data_profile, sql_results))
        
        # Key findings
        if insights:
            sections.append(await self._create_key_findings_section(insights))
        
        # Detailed analysis
        sections.append(await self._create_detailed_analysis_section(insights, charts))
        
        # Recommendations
        if recommendations:
            sections.append(await self._create_recommendations_section(recommendations))
        
        # Charts and visualizations
        if charts:
            sections.append(await self._create_charts_section(charts))
        
        # Methodology (for detailed reports)
        if report_type == "detailed_analysis":
            sections.append(await self._create_methodology_section(insights))
        
        # Appendix
        sections.append(await self._create_appendix_section(data_profile, sql_results))
        
        return sections
    
    async def _create_title_section(self, query_intent: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Create title and introduction section"""
        
        business_question = query_intent.get("business_question", "Data Analysis")
        report_title = self.report_templates.get(report_type, "Business Intelligence Report")
        
        content = f"""
# {report_title}

## Business Question
{business_question}

## Report Overview
This report provides comprehensive analysis and insights based on your data and business requirements. 
The analysis was conducted using advanced AI-powered business intelligence tools to extract meaningful 
patterns, trends, and actionable recommendations.

**Generated on:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        """.strip()
        
        return {
            "type": "title",
            "title": "Report Introduction",
            "content": content,
            "order": 1
        }
    
    async def _create_executive_summary_section(self, executive_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary section"""
        
        total_insights = executive_summary.get("total_insights", 0)
        high_impact = executive_summary.get("high_impact_insights", 0)
        key_findings = executive_summary.get("key_findings", [])
        overall_health = executive_summary.get("overall_health", "good")
        next_steps = executive_summary.get("next_steps", [])
        
        # Format health status
        health_emoji = "🟢" if overall_health == "good" else "🟡" if overall_health == "attention_needed" else "🔴"
        
        content = f"""
## Executive Summary

### Overall Assessment
**Status:** {health_emoji} {overall_health.replace('_', ' ').title()}

### Key Statistics
- **Total Insights Generated:** {total_insights}
- **High-Impact Findings:** {high_impact}
- **Analysis Date:** {executive_summary.get('analysis_date', datetime.now().isoformat())[:10]}

### Top Findings
"""
        
        for i, finding in enumerate(key_findings[:5], 1):
            content += f"\n{i}. {finding}"
        
        if next_steps:
            content += "\n\n### Immediate Next Steps"
            for i, step in enumerate(next_steps[:3], 1):
                content += f"\n{i}. {step}"
        
        return {
            "type": "executive_summary",
            "title": "Executive Summary",
            "content": content,
            "order": 2
        }
    
    async def _create_data_overview_section(self, data_profile: Dict[str, Any], sql_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create data overview section"""
        
        content = "## Data Overview\n\n"
        
        if data_profile:
            basic_info = data_profile.get("basic_info", {})
            content += f"""
### Dataset Characteristics
- **Total Records:** {basic_info.get('rows', 'N/A'):,}
- **Number of Variables:** {basic_info.get('columns', 'N/A')}
- **Data Size:** {basic_info.get('memory_usage_mb', 0):.1f} MB

### Data Quality Assessment
"""
            
            quality_assessment = data_profile.get("quality_assessment", {})
            if quality_assessment:
                quality_score = quality_assessment.get("overall_score", 0)
                quality_emoji = "🟢" if quality_score > 0.8 else "🟡" if quality_score > 0.6 else "🔴"
                
                content += f"""
- **Overall Quality Score:** {quality_emoji} {quality_score:.1%}
- **Data Completeness:** {quality_assessment.get('completeness_score', 0):.1%}
- **Data Uniqueness:** {quality_assessment.get('uniqueness_score', 0):.1%}
- **Missing Data:** {quality_assessment.get('missing_percentage', 0):.1f}%
"""
        
        if sql_results:
            content += f"\n\n### Query Results\n- **Records Retrieved:** {len(sql_results):,}"
        
        return {
            "type": "data_overview",
            "title": "Data Overview",
            "content": content,
            "order": 3
        }
    
    async def _create_key_findings_section(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create key findings section"""
        
        content = "## Key Findings\n\n"
        
        # Group insights by impact level
        high_impact = [i for i in insights if i.get("impact") == "high"]
        medium_impact = [i for i in insights if i.get("impact") == "medium"]
        
        if high_impact:
            content += "### High-Impact Findings\n"
            for i, insight in enumerate(high_impact, 1):
                title = insight.get("title", f"Finding {i}")
                summary = insight.get("summary", "No summary available")
                content += f"\n**{i}. {title}**\n{summary}\n"
        
        if medium_impact:
            content += "\n### Additional Insights\n"
            for i, insight in enumerate(medium_impact[:3], 1):  # Limit to 3
                title = insight.get("title", f"Insight {i}")
                summary = insight.get("summary", "No summary available")
                content += f"\n**{i}. {title}**\n{summary}\n"
        
        if not high_impact and not medium_impact:
            content += "No significant findings identified in the current analysis."
        
        return {
            "type": "key_findings",
            "title": "Key Findings",
            "content": content,
            "order": 4
        }
    
    async def _create_detailed_analysis_section(self, insights: List[Dict[str, Any]], charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed analysis section"""
        
        content = "## Detailed Analysis\n\n"
        
        # Group insights by analysis type
        analysis_types = {}
        for insight in insights:
            analysis_type = insight.get("type", "general")
            if analysis_type not in analysis_types:
                analysis_types[analysis_type] = []
            analysis_types[analysis_type].append(insight)
        
        for analysis_type, type_insights in analysis_types.items():
            type_title = analysis_type.replace('_', ' ').title()
            content += f"\n### {type_title}\n"
            
            for insight in type_insights:
                title = insight.get("title", "Analysis")
                summary = insight.get("summary", "")
                findings = insight.get("findings", [])
                
                content += f"\n**{title}**\n"
                if summary:
                    content += f"{summary}\n"
                
                if findings and isinstance(findings, list):
                    content += "\nKey Details:\n"
                    for finding in findings[:3]:  # Limit to 3 findings
                        if isinstance(finding, dict):
                            # Format finding based on its structure
                            if "metric" in finding and "direction" in finding:
                                content += f"- {finding.get('metric', '')}: {finding.get('direction', '')} trend\n"
                            elif "variable1" in finding and "variable2" in finding:
                                content += f"- {finding.get('variable1', '')} and {finding.get('variable2', '')}: {finding.get('correlation', 0):.2f} correlation\n"
                            else:
                                content += f"- {str(finding)[:100]}...\n"
                        else:
                            content += f"- {str(finding)[:100]}...\n"
                
                content += "\n"
        
        # Reference charts if available
        if charts:
            content += f"\n### Visualizations\n{len(charts)} charts have been generated to support these findings. See the Charts and Visualizations section for detailed graphics.\n"
        
        return {
            "type": "detailed_analysis",
            "title": "Detailed Analysis",
            "content": content,
            "order": 5
        }
    
    async def _create_recommendations_section(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create recommendations section"""
        
        content = "## Recommendations\n\n"
        
        # Group by priority
        high_priority = [r for r in recommendations if r.get("priority") == "high"]
        medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
        
        if high_priority:
            content += "### Immediate Actions Required\n"
            for i, rec in enumerate(high_priority, 1):
                title = rec.get("title", f"Recommendation {i}")
                description = rec.get("description", "")
                action_items = rec.get("action_items", [])
                
                content += f"\n**{i}. {title}**\n"
                if description:
                    content += f"{description}\n"
                
                if action_items:
                    content += "\nAction Items:\n"
                    for action in action_items[:3]:  # Limit to 3 actions
                        content += f"- {action}\n"
                content += "\n"
        
        if medium_priority:
            content += "\n### Additional Recommendations\n"
            for i, rec in enumerate(medium_priority[:3], 1):  # Limit to 3
                title = rec.get("title", f"Recommendation {i}")
                description = rec.get("description", "")
                content += f"\n**{i}. {title}**\n{description}\n"
        
        if not high_priority and not medium_priority:
            content += "Continue monitoring current performance. No immediate actions required based on current analysis."
        
        return {
            "type": "recommendations",
            "title": "Recommendations",
            "content": content,
            "order": 6
        }
    
    async def _create_charts_section(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create charts and visualizations section"""
        
        content = "## Charts and Visualizations\n\n"
        content += f"This analysis generated {len(charts)} visualizations to support the findings:\n\n"
        
        for i, chart in enumerate(charts, 1):
            title = chart.get("title", f"Chart {i}")
            description = chart.get("description", "")
            chart_type = chart.get("type", "unknown")
            insights = chart.get("insights", [])
            
            content += f"### {i}. {title}\n"
            content += f"**Type:** {chart_type.title()} Chart\n"
            if description:
                content += f"**Description:** {description}\n"
            
            if insights:
                content += "**Key Insights:**\n"
                for insight in insights:
                    content += f"- {insight}\n"
            
            content += f"\n*Chart ID: {chart.get('id', 'unknown')}*\n\n"
        
        return {
            "type": "charts",
            "title": "Charts and Visualizations",
            "content": content,
            "order": 7
        }
    
    async def _create_methodology_section(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create methodology section"""
        
        methods_used = set()
        for insight in insights:
            if "method" in insight:
                methods_used.add(insight["method"])
        
        content = """## Methodology

### Analysis Framework
This report was generated using advanced AI-powered business intelligence tools that employ multiple analytical methodologies:

"""
        
        method_descriptions = {
            "trend_analysis": "**Trend Analysis**: Statistical analysis of time-series data to identify patterns and directional changes",
            "anomaly_detection": "**Anomaly Detection**: Statistical outlier detection using IQR (Interquartile Range) method",
            "correlation_analysis": "**Correlation Analysis**: Pearson correlation analysis to identify relationships between variables",
            "segmentation": "**Segmentation**: K-means clustering to identify distinct groups in the data",
            "forecasting": "**Forecasting**: Linear regression modeling for predictive analysis",
            "comparative_analysis": "**Comparative Analysis**: Statistical comparison across categorical dimensions"
        }
        
        for method in sorted(methods_used):
            if method in method_descriptions:
                content += f"- {method_descriptions[method]}\n"
        
        content += """
### Data Processing
- Data validation and quality assessment
- Missing value analysis
- Outlier detection and handling
- Statistical significance testing where applicable

### Confidence Levels
- High confidence: Statistical significance p < 0.05
- Medium confidence: Observable patterns with statistical support
- Low confidence: Preliminary findings requiring further investigation
"""
        
        return {
            "type": "methodology",
            "title": "Methodology",
            "content": content,
            "order": 8
        }
    
    async def _create_appendix_section(self, data_profile: Dict[str, Any], sql_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create appendix section"""
        
        content = "## Appendix\n\n"
        
        # Data dictionary
        if data_profile and "column_info" in data_profile:
            content += "### Data Dictionary\n\n"
            column_info = data_profile["column_info"]
            for col_name, col_data in list(column_info.items())[:10]:  # Limit to 10 columns
                content += f"**{col_name}**\n"
                content += f"- Type: {col_data.get('dtype', 'Unknown')}\n"
                content += f"- Non-null count: {col_data.get('non_null_count', 0):,}\n"
                content += f"- Unique values: {col_data.get('unique_count', 0):,}\n"
                if col_data.get('null_percentage', 0) > 0:
                    content += f"- Missing: {col_data.get('null_percentage', 0):.1f}%\n"
                content += "\n"
        
        # Technical details
        content += """### Technical Details
- **Analysis Engine**: AI-Powered Business Intelligence Copilot
- **Statistical Framework**: Python (pandas, numpy, scipy, scikit-learn)
- **Visualization Engine**: Plotly
- **Report Generation**: Automated AI Report Agent

### Limitations
- Analysis is based on available data at time of generation
- Correlations do not imply causation
- Forecasts are estimates based on historical patterns
- Results should be validated with domain expertise

### Contact Information
For questions about this analysis or to request additional insights, please contact your BI team.
"""
        
        return {
            "type": "appendix",
            "title": "Appendix",
            "content": content,
            "order": 9
        }
    
    async def _assemble_final_report(self, sections: List[Dict[str, Any]], report_type: str) -> Dict[str, Any]:
        """Assemble final report from all sections"""
        
        # Sort sections by order
        sorted_sections = sorted(sections, key=lambda x: x.get("order", 999))
        
        # Combine all content
        full_content = ""
        section_list = []
        
        for section in sorted_sections:
            full_content += section.get("content", "") + "\n\n"
            section_list.append({
                "title": section.get("title", ""),
                "type": section.get("type", ""),
                "order": section.get("order", 0)
            })
        
        return {
            "title": self.report_templates.get(report_type, "Business Intelligence Report"),
            "type": report_type,
            "content": full_content.strip(),
            "sections": section_list,
            "word_count": len(full_content.split()),
            "generated_at": datetime.now().isoformat()
        }
    
    def _create_report_metadata(self, report: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Create report metadata"""
        
        return {
            "report_id": f"report_{int(datetime.now().timestamp())}",
            "generated_at": datetime.now().isoformat(),
            "report_type": report.get("type", "unknown"),
            "word_count": report.get("word_count", 0),
            "sections_count": len(report.get("sections", [])),
            "insights_included": len(state.get("insights", [])),
            "charts_included": len(state.get("generated_charts", [])),
            "recommendations_included": len(state.get("business_recommendations", [])),
            "data_sources": {
                "sql_results": bool(state.get("sql_results")),
                "data_profile": bool(state.get("data_profile")),
                "user_query": bool(state.get("user_query"))
            },
            "quality_indicators": {
                "has_executive_summary": bool(state.get("executive_summary")),
                "has_visualizations": bool(state.get("generated_charts")),
                "has_recommendations": bool(state.get("business_recommendations")),
                "analysis_depth": "comprehensive" if len(state.get("insights", [])) > 3 else "standard"
            }
        }
    
    def get_required_fields(self) -> List[str]:
        """Required fields for report agent"""
        return ["query_intent"]  # Minimum requirement
