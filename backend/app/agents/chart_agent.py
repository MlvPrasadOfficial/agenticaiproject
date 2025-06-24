# Chart Agent - Data Visualization and Chart Generation

from typing import Dict, Any, List, Optional, Tuple
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import io

from app.agents.base_agent import BaseAgent


class ChartAgent(BaseAgent):
    """Data visualization and chart generation specialist"""
    
    def __init__(self):
        super().__init__("Chart Agent")
        self.chart_types = {
            "line": ["time_series", "trend", "progression"],
            "bar": ["comparison", "categorical", "ranking"],
            "scatter": ["correlation", "relationship", "distribution"],
            "histogram": ["distribution", "frequency"],
            "box": ["outliers", "quartiles", "summary"],
            "heatmap": ["correlation", "matrix", "density"],
            "pie": ["composition", "percentage", "share"]
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate visualizations based on data and intent"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Chart Agent"}
        
        # Get data sources
        sql_results = state.get("sql_results", [])
        insights = state.get("insights", [])
        query_intent = state.get("query_intent", {})
        extracted_entities = state.get("extracted_entities", {})
        
        # Convert to DataFrame
        df = None
        if sql_results:
            df = pd.DataFrame(sql_results)
        
        # Determine chart recommendations
        chart_recommendations = await self._recommend_charts(df, query_intent, extracted_entities, insights)
        
        # Generate charts
        generated_charts = []
        for recommendation in chart_recommendations[:5]:  # Limit to 5 charts
            chart_result = await self._generate_chart(df, recommendation)
            if chart_result:
                generated_charts.append(chart_result)
        
        # Create dashboard layout
        dashboard_config = await self._create_dashboard_layout(generated_charts)
        
        # Update state with chart results
        state.update({
            "generated_charts": generated_charts,
            "chart_recommendations": chart_recommendations,
            "dashboard_config": dashboard_config
        })
        
        return {
            "charts": generated_charts,
            "recommendations": chart_recommendations,
            "dashboard": dashboard_config,
            "total_charts": len(generated_charts),
            "agent": self.agent_name,
            "status": "completed"
        }
    
    async def _recommend_charts(
        self, 
        df: Optional[pd.DataFrame], 
        query_intent: Dict[str, Any], 
        entities: Dict[str, Any],
        insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Recommend appropriate chart types based on data and intent"""
        
        recommendations = []
        
        if df is None or df.empty:
            return [{
                "chart_type": "placeholder",
                "title": "No Data Available",
                "description": "Upload data to generate visualizations",
                "priority": "low"
            }]
        
        # Analyze data structure
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = [col for col in df.columns if any(word in col.lower() for word in ["date", "time", "day", "month", "year"])]
        
        # Intent-based recommendations
        primary_intent = query_intent.get("primary_intent", "analyze")
        
        if primary_intent == "trend" or "trend" in query_intent.get("business_question", "").lower():
            if date_cols and numeric_cols:
                recommendations.append({
                    "chart_type": "line",
                    "title": "Trend Analysis",
                    "description": "Show trends over time",
                    "x_axis": date_cols[0],
                    "y_axis": numeric_cols[0],
                    "priority": "high"
                })
        
        if primary_intent == "compare" or len(categorical_cols) > 0:
            if categorical_cols and numeric_cols:
                recommendations.append({
                    "chart_type": "bar",
                    "title": "Comparative Analysis",
                    "description": "Compare values across categories",
                    "x_axis": categorical_cols[0],
                    "y_axis": numeric_cols[0],
                    "priority": "high"
                })
        
        # Data-driven recommendations
        if len(numeric_cols) >= 2:
            recommendations.append({
                "chart_type": "scatter",
                "title": "Correlation Analysis",
                "description": f"Relationship between {numeric_cols[0]} and {numeric_cols[1]}",
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1],
                "priority": "medium"
            })
        
        # Distribution analysis
        for col in numeric_cols[:2]:  # Limit to 2 columns
            recommendations.append({
                "chart_type": "histogram",
                "title": f"Distribution of {col}",
                "description": f"Show frequency distribution of {col}",
                "x_axis": col,
                "priority": "medium"
            })
        
        # Insight-driven recommendations
        for insight in insights:
            if insight.get("type") == "correlation_analysis":
                findings = insight.get("findings", [])
                for finding in findings[:2]:  # Limit to 2 correlations
                    var1 = finding.get("variable1")
                    var2 = finding.get("variable2")
                    if var1 and var2:
                        recommendations.append({
                            "chart_type": "scatter",
                            "title": f"Correlation: {var1} vs {var2}",
                            "description": f"Strong correlation ({finding.get('correlation', 0):.2f})",
                            "x_axis": var1,
                            "y_axis": var2,
                            "priority": "high"
                        })
        
        # Heatmap for correlation matrix
        if len(numeric_cols) > 3:
            recommendations.append({
                "chart_type": "heatmap",
                "title": "Correlation Matrix",
                "description": "Correlation between all numeric variables",
                "data_subset": numeric_cols,
                "priority": "medium"
            })
        
        # Remove duplicates and sort by priority
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            key = f"{rec['chart_type']}_{rec.get('x_axis', '')}_{rec.get('y_axis', '')}"
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        unique_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 1), reverse=True)
        
        return unique_recommendations
    
    async def _generate_chart(self, df: pd.DataFrame, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a specific chart based on recommendation"""
        
        try:
            chart_type = recommendation.get("chart_type")
            
            if chart_type == "line":
                chart_fig = self._create_line_chart(df, recommendation)
            elif chart_type == "bar":
                chart_fig = self._create_bar_chart(df, recommendation)
            elif chart_type == "scatter":
                chart_fig = self._create_scatter_chart(df, recommendation)
            elif chart_type == "histogram":
                chart_fig = self._create_histogram(df, recommendation)
            elif chart_type == "heatmap":
                chart_fig = self._create_heatmap(df, recommendation)
            elif chart_type == "pie":
                chart_fig = self._create_pie_chart(df, recommendation)
            elif chart_type == "box":
                chart_fig = self._create_box_plot(df, recommendation)
            else:
                return None
            
            if chart_fig is None:
                return None
            
            # Convert to JSON for API response
            chart_json = chart_fig.to_json()
            
            # Generate static image as base64 (optional)
            img_bytes = chart_fig.to_image(format="png", width=800, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return {
                "id": f"chart_{len(str(hash(recommendation)))}",
                "type": chart_type,
                "title": recommendation.get("title", "Chart"),
                "description": recommendation.get("description", ""),
                "config": json.loads(chart_json),
                "image_base64": img_base64,
                "priority": recommendation.get("priority", "medium"),
                "insights": self._extract_chart_insights(df, recommendation, chart_fig)
            }
            
        except Exception as e:
            print(f"❌ Error generating {chart_type} chart: {str(e)}")
            return None
    
    def _create_line_chart(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create line chart for time series data"""
        
        x_col = rec.get("x_axis")
        y_col = rec.get("y_axis")
        
        if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
            return None
        
        # Clean and sort data
        chart_data = df[[x_col, y_col]].dropna()
        
        if len(chart_data) == 0:
            return None
        
        # Convert x-axis to datetime if it looks like a date
        try:
            chart_data[x_col] = pd.to_datetime(chart_data[x_col])
            chart_data = chart_data.sort_values(x_col)
        except Exception:
            pass
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=chart_data[x_col],
            y=chart_data[y_col],
            mode='lines+markers',
            name=y_col,
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=rec.get("title", f"{y_col} over {x_col}"),
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create bar chart for categorical comparisons"""
        
        x_col = rec.get("x_axis")
        y_col = rec.get("y_axis")
        
        if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
            return None
        
        # Aggregate data if needed
        if df[x_col].dtype in ['object', 'category']:
            # Group by categorical variable and aggregate numeric
            chart_data = df.groupby(x_col)[y_col].mean().reset_index()
        else:
            chart_data = df[[x_col, y_col]].dropna()
        
        if len(chart_data) == 0:
            return None
        
        # Limit to top 15 categories for readability
        if len(chart_data) > 15:
            chart_data = chart_data.nlargest(15, y_col)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=chart_data[x_col],
            y=chart_data[y_col],
            name=y_col,
            marker=dict(color='#1f77b4')
        ))
        
        fig.update_layout(
            title=rec.get("title", f"{y_col} by {x_col}"),
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white",
            height=400,
            xaxis_tickangle=45
        )
        
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create scatter plot for correlation analysis"""
        
        x_col = rec.get("x_axis")
        y_col = rec.get("y_axis")
        
        if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
            return None
        
        chart_data = df[[x_col, y_col]].dropna()
        
        if len(chart_data) == 0:
            return None
        
        # Calculate correlation
        correlation = chart_data[x_col].corr(chart_data[y_col])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=chart_data[x_col],
            y=chart_data[y_col],
            mode='markers',
            name=f'Correlation: {correlation:.3f}',
            marker=dict(
                color='#1f77b4',
                size=8,
                opacity=0.6
            )
        ))
        
        # Add trend line
        z = np.polyfit(chart_data[x_col], chart_data[y_col], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=chart_data[x_col],
            y=p(chart_data[x_col]),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title=rec.get("title", f"{y_col} vs {x_col}"),
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_histogram(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create histogram for distribution analysis"""
        
        x_col = rec.get("x_axis")
        
        if not x_col or x_col not in df.columns:
            return None
        
        chart_data = df[x_col].dropna()
        
        if len(chart_data) == 0:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=chart_data,
            name=x_col,
            marker=dict(color='#1f77b4'),
            nbinsx=min(30, len(chart_data) // 10) or 10
        ))
        
        fig.update_layout(
            title=rec.get("title", f"Distribution of {x_col}"),
            xaxis_title=x_col,
            yaxis_title="Frequency",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_heatmap(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create heatmap for correlation matrix"""
        
        data_subset = rec.get("data_subset", [])
        
        if not data_subset:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            data_subset = numeric_cols[:10]  # Limit to 10 columns
        
        if len(data_subset) < 2:
            return None
        
        # Calculate correlation matrix
        corr_matrix = df[data_subset].corr()
        
        fig = go.Figure()
        
        fig.add_trace(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title=rec.get("title", "Correlation Matrix"),
            template="plotly_white",
            height=500,
            width=500
        )
        
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create pie chart for composition analysis"""
        
        x_col = rec.get("x_axis")
        y_col = rec.get("y_axis", None)
        
        if not x_col or x_col not in df.columns:
            return None
        
        if y_col and y_col in df.columns:
            # Aggregate by category
            chart_data = df.groupby(x_col)[y_col].sum().reset_index()
            values = chart_data[y_col]
            labels = chart_data[x_col]
        else:
            # Count occurrences
            value_counts = df[x_col].value_counts()
            values = value_counts.values
            labels = value_counts.index
        
        # Limit to top 10 slices
        if len(values) > 10:
            top_indices = np.argsort(values)[-10:]
            values = values[top_indices]
            labels = labels[top_indices]
        
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            name=x_col
        ))
        
        fig.update_layout(
            title=rec.get("title", f"Composition by {x_col}"),
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _create_box_plot(self, df: pd.DataFrame, rec: Dict[str, Any]) -> Optional[go.Figure]:
        """Create box plot for outlier analysis"""
        
        y_col = rec.get("y_axis")
        x_col = rec.get("x_axis", None)
        
        if not y_col or y_col not in df.columns:
            return None
        
        fig = go.Figure()
        
        if x_col and x_col in df.columns:
            # Box plot by category
            categories = df[x_col].unique()
            for category in categories[:10]:  # Limit to 10 categories
                category_data = df[df[x_col] == category][y_col].dropna()
                if len(category_data) > 0:
                    fig.add_trace(go.Box(
                        y=category_data,
                        name=str(category),
                        boxpoints='outliers'
                    ))
        else:
            # Single box plot
            fig.add_trace(go.Box(
                y=df[y_col].dropna(),
                name=y_col,
                boxpoints='outliers'
            ))
        
        fig.update_layout(
            title=rec.get("title", f"Box Plot of {y_col}"),
            yaxis_title=y_col,
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def _extract_chart_insights(self, df: pd.DataFrame, rec: Dict[str, Any], fig: go.Figure) -> List[str]:
        """Extract insights from generated chart"""
        
        insights = []
        chart_type = rec.get("chart_type")
        
        if chart_type == "line":
            insights.append("Shows trend over time")
            # Could add trend direction analysis
        elif chart_type == "bar":
            insights.append("Compares values across categories")
            # Could add highest/lowest performers
        elif chart_type == "scatter":
            x_col = rec.get("x_axis")
            y_col = rec.get("y_axis")
            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                corr = df[x_col].corr(df[y_col])
                if abs(corr) > 0.7:
                    insights.append(f"Strong correlation ({corr:.2f}) between variables")
                elif abs(corr) > 0.3:
                    insights.append(f"Moderate correlation ({corr:.2f}) between variables")
                else:
                    insights.append("Weak correlation between variables")
        elif chart_type == "histogram":
            insights.append("Shows data distribution and frequency")
        
        return insights
    
    async def _create_dashboard_layout(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create dashboard layout configuration"""
        
        if not charts:
            return {"layout": "empty", "charts": []}
        
        # Simple grid layout based on number of charts
        num_charts = len(charts)
        
        if num_charts == 1:
            layout = {"rows": 1, "cols": 1}
        elif num_charts <= 2:
            layout = {"rows": 1, "cols": 2}
        elif num_charts <= 4:
            layout = {"rows": 2, "cols": 2}
        elif num_charts <= 6:
            layout = {"rows": 2, "cols": 3}
        else:
            layout = {"rows": 3, "cols": 3}
        
        # Arrange charts by priority
        chart_positions = []
        for i, chart in enumerate(charts):
            row = i // layout["cols"]
            col = i % layout["cols"]
            chart_positions.append({
                "chart_id": chart.get("id"),
                "row": row,
                "col": col,
                "priority": chart.get("priority", "medium")
            })
        
        return {
            "layout": layout,
            "chart_positions": chart_positions,
            "total_charts": num_charts,
            "theme": "plotly_white"
        }
    
    def get_required_fields(self) -> List[str]:
        """Required fields for chart agent"""
        return []  # Can work with various input combinations
