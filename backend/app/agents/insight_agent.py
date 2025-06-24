# Insight Agent - Pattern Recognition and Business Intelligence

from typing import Dict, Any, List, Optional, Tuple
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

from app.agents.base_agent import BaseAgent


class InsightAgent(BaseAgent):
    """Advanced pattern recognition and business insight generation specialist"""
    
    def __init__(self):
        super().__init__("Insight Agent")
        self.analysis_methods = [
            "trend_analysis",
            "anomaly_detection", 
            "correlation_analysis",
            "segmentation",
            "forecasting",
            "comparative_analysis"
        ]
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business insights from data and query results"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Insight Agent"}
        
        # Get data sources
        sql_results = state.get("sql_results", [])
        data_profile = state.get("data_profile", {})
        query_intent = state.get("query_intent", {})
        context_summary = state.get("context_summary", {})
        
        # Convert SQL results to DataFrame if available
        df = None
        if sql_results:
            df = pd.DataFrame(sql_results)
        
        # Determine analysis methods based on intent and data
        analysis_plan = self._create_analysis_plan(query_intent, data_profile, df)
        
        # Execute selected analyses
        insights = await self._execute_analyses(df, analysis_plan, query_intent)
        
        # Generate business recommendations
        recommendations = await self._generate_business_recommendations(insights, query_intent)
        
        # Create executive summary
        executive_summary = await self._create_executive_summary(insights, recommendations, query_intent)
        
        # Update state with insights
        state.update({
            "insights": insights,
            "business_recommendations": recommendations,
            "executive_summary": executive_summary,
            "analysis_methods_used": analysis_plan["methods"]
        })
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "executive_summary": executive_summary,
            "analysis_confidence": self._calculate_confidence_score(insights),
            "agent": self.agent_name,
            "status": "completed"
        }
    
    def _create_analysis_plan(
        self, 
        query_intent: Dict[str, Any], 
        data_profile: Dict[str, Any], 
        df: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """Create analysis plan based on intent and available data"""
        
        plan = {
            "methods": [],
            "priority": "high",
            "complexity": "medium"
        }
        
        # Determine methods based on query intent
        primary_intent = query_intent.get("primary_intent", "analyze")
        
        if primary_intent in ["analyze", "explore"]:
            plan["methods"] = ["trend_analysis", "correlation_analysis", "anomaly_detection"]
        elif primary_intent == "compare":
            plan["methods"] = ["comparative_analysis", "trend_analysis"]
        elif primary_intent == "forecast":
            plan["methods"] = ["forecasting", "trend_analysis"]
        elif primary_intent == "segment":
            plan["methods"] = ["segmentation", "correlation_analysis"]
        else:
            plan["methods"] = ["trend_analysis", "correlation_analysis"]
        
        # Adjust based on data characteristics
        if df is not None:
            # Check if we have time series data
            date_cols = [col for col in df.columns if any(word in col.lower() for word in ["date", "time", "day", "month", "year"])]
            if date_cols:
                plan["methods"].append("trend_analysis")
            
            # Check for numeric data
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                plan["methods"].append("correlation_analysis")
            
            # Check data size for complexity
            if len(df) > 1000:
                plan["complexity"] = "high"
                if "segmentation" not in plan["methods"]:
                    plan["methods"].append("segmentation")
        
        # Remove duplicates
        plan["methods"] = list(set(plan["methods"]))
        
        return plan
    
    async def _execute_analyses(
        self, 
        df: Optional[pd.DataFrame], 
        analysis_plan: Dict[str, Any], 
        query_intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute the planned analyses"""
        
        insights = []
        
        if df is None or df.empty:
            # Generate insights from data profile only
            return await self._generate_profile_insights(query_intent)
        
        # Execute each analysis method
        for method in analysis_plan["methods"]:
            try:
                if method == "trend_analysis":
                    insight = await self._analyze_trends(df)
                elif method == "anomaly_detection":
                    insight = await self._detect_anomalies(df)
                elif method == "correlation_analysis":
                    insight = await self._analyze_correlations(df)
                elif method == "segmentation":
                    insight = await self._perform_segmentation(df)
                elif method == "forecasting":
                    insight = await self._generate_forecasts(df)
                elif method == "comparative_analysis":
                    insight = await self._perform_comparative_analysis(df)
                else:
                    continue
                
                if insight:
                    insight["method"] = method
                    insight["confidence"] = self._calculate_method_confidence(method, df)
                    insights.append(insight)
                    
            except Exception as e:
                print(f"⚠️ Error in {method}: {str(e)}")
                continue
        
        return insights
    
    async def _analyze_trends(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze trends in the data"""
        
        # Find date/time columns
        date_cols = [col for col in df.columns if any(word in col.lower() for word in ["date", "time", "day", "month", "year"])]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not date_cols or not numeric_cols:
            return None
        
        trends = []
        
        # Analyze each numeric column over time
        for date_col in date_cols[:1]:  # Use first date column
            try:
                # Convert to datetime
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df_sorted = df.sort_values(date_col).dropna(subset=[date_col])
                
                for num_col in numeric_cols[:3]:  # Limit to 3 numeric columns
                    if df_sorted[num_col].count() < 3:
                        continue
                    
                    # Calculate trend
                    x = np.arange(len(df_sorted))
                    y = df_sorted[num_col].values
                    
                    # Remove NaN values
                    mask = ~np.isnan(y)
                    if mask.sum() < 3:
                        continue
                    
                    x_clean = x[mask]
                    y_clean = y[mask]
                    
                    # Linear regression for trend
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
                    
                    # Determine trend direction and strength
                    if abs(r_value) > 0.7 and p_value < 0.05:
                        if slope > 0:
                            direction = "increasing"
                        else:
                            direction = "decreasing"
                        
                        strength = "strong" if abs(r_value) > 0.8 else "moderate"
                        
                        trends.append({
                            "metric": num_col,
                            "direction": direction,
                            "strength": strength,
                            "correlation": float(r_value),
                            "p_value": float(p_value),
                            "slope": float(slope),
                            "significance": "significant" if p_value < 0.05 else "not_significant"
                        })
            
            except Exception as e:
                print(f"⚠️ Error analyzing trend for {date_col}: {str(e)}")
                continue
        
        if not trends:
            return None
        
        return {
            "type": "trend_analysis",
            "title": "Trend Analysis Results",
            "findings": trends,
            "summary": f"Analyzed trends for {len(trends)} metrics over time",
            "impact": "high" if any(t["strength"] == "strong" for t in trends) else "medium"
        }
    
    async def _detect_anomalies(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Detect anomalies in numeric data"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return None
        
        anomalies = []
        
        for col in numeric_cols[:5]:  # Limit to 5 columns
            try:
                series = df[col].dropna()
                if len(series) < 10:
                    continue
                
                # Use IQR method for anomaly detection
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                
                if len(outliers) > 0:
                    anomaly_percentage = (len(outliers) / len(series)) * 100
                    
                    anomalies.append({
                        "column": col,
                        "anomaly_count": len(outliers),
                        "anomaly_percentage": float(anomaly_percentage),
                        "threshold_lower": float(lower_bound),
                        "threshold_upper": float(upper_bound),
                        "severity": "high" if anomaly_percentage > 10 else "medium" if anomaly_percentage > 5 else "low",
                        "sample_values": outliers.head(5).tolist()
                    })
            
            except Exception as e:
                print(f"⚠️ Error detecting anomalies in {col}: {str(e)}")
                continue
        
        if not anomalies:
            return None
        
        return {
            "type": "anomaly_detection",
            "title": "Anomaly Detection Results",
            "findings": anomalies,
            "summary": f"Found anomalies in {len(anomalies)} out of {len(numeric_cols)} numeric columns",
            "impact": "high" if any(a["severity"] == "high" for a in anomalies) else "medium"
        }
    
    async def _analyze_correlations(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze correlations between numeric variables"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return None
        
        # Calculate correlation matrix
        try:
            corr_matrix = df[numeric_cols].corr()
            
            # Find strong correlations
            strong_correlations = []
            
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) > 0.6:  # Strong correlation threshold
                        strength = "very_strong" if abs(corr_value) > 0.8 else "strong"
                        direction = "positive" if corr_value > 0 else "negative"
                        
                        strong_correlations.append({
                            "variable1": numeric_cols[i],
                            "variable2": numeric_cols[j],
                            "correlation": float(corr_value),
                            "strength": strength,
                            "direction": direction
                        })
            
            if not strong_correlations:
                return None
            
            return {
                "type": "correlation_analysis",
                "title": "Correlation Analysis Results",
                "findings": strong_correlations,
                "summary": f"Found {len(strong_correlations)} strong correlations",
                "impact": "high" if any(c["strength"] == "very_strong" for c in strong_correlations) else "medium"
            }
            
        except Exception as e:
            print(f"⚠️ Error in correlation analysis: {str(e)}")
            return None
    
    async def _perform_segmentation(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Perform customer/data segmentation using clustering"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2 or len(df) < 10:
            return None
        
        try:
            # Prepare data for clustering
            cluster_data = df[numeric_cols].dropna()
            
            if len(cluster_data) < 10:
                return None
            
            # Standardize data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(cluster_data)
            
            # Determine optimal number of clusters (2-5)
            optimal_k = min(5, max(2, len(cluster_data) // 10))
            
            # Perform k-means clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_data)
            
            # Analyze clusters
            cluster_analysis = []
            for i in range(optimal_k):
                cluster_mask = clusters == i
                cluster_subset = cluster_data[cluster_mask]
                
                if len(cluster_subset) > 0:
                    cluster_analysis.append({
                        "cluster_id": i,
                        "size": len(cluster_subset),
                        "percentage": float((len(cluster_subset) / len(cluster_data)) * 100),
                        "characteristics": {
                            col: {
                                "mean": float(cluster_subset[col].mean()),
                                "median": float(cluster_subset[col].median())
                            }
                            for col in numeric_cols[:3]  # Limit to 3 columns
                        }
                    })
            
            return {
                "type": "segmentation",
                "title": "Data Segmentation Results",
                "findings": cluster_analysis,
                "summary": f"Identified {optimal_k} distinct segments in the data",
                "impact": "medium"
            }
            
        except Exception as e:
            print(f"⚠️ Error in segmentation: {str(e)}")
            return None
    
    async def _generate_forecasts(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Generate simple forecasts for time series data"""
        
        # Find date and numeric columns
        date_cols = [col for col in df.columns if any(word in col.lower() for word in ["date", "time", "day", "month", "year"])]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not date_cols or not numeric_cols or len(df) < 5:
            return None
        
        forecasts = []
        
        try:
            # Use first date column
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_sorted = df.sort_values(date_col).dropna(subset=[date_col])
            
            for num_col in numeric_cols[:2]:  # Limit to 2 columns
                if df_sorted[num_col].count() < 5:
                    continue
                
                # Simple linear regression forecast
                x = np.arange(len(df_sorted))
                y = df_sorted[num_col].values
                
                # Remove NaN values
                mask = ~np.isnan(y)
                if mask.sum() < 5:
                    continue
                
                x_clean = x[mask]
                y_clean = y[mask]
                
                # Fit linear regression
                model = LinearRegression()
                model.fit(x_clean.reshape(-1, 1), y_clean)
                
                # Forecast next 3 periods
                future_x = np.array([len(df_sorted) + i for i in range(1, 4)])
                forecast_values = model.predict(future_x.reshape(-1, 1))
                
                # Calculate confidence (R-squared)
                r_squared = model.score(x_clean.reshape(-1, 1), y_clean)
                
                forecasts.append({
                    "metric": num_col,
                    "forecast_values": [float(v) for v in forecast_values],
                    "confidence": float(r_squared),
                    "trend": "increasing" if model.coef_[0] > 0 else "decreasing",
                    "model_type": "linear_regression"
                })
            
            if not forecasts:
                return None
            
            return {
                "type": "forecasting",
                "title": "Forecast Analysis Results",
                "findings": forecasts,
                "summary": f"Generated forecasts for {len(forecasts)} metrics",
                "impact": "medium"
            }
            
        except Exception as e:
            print(f"⚠️ Error in forecasting: {str(e)}")
            return None
    
    async def _perform_comparative_analysis(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Perform comparative analysis between groups"""
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not categorical_cols or not numeric_cols:
            return None
        
        comparisons = []
        
        try:
            # Compare numeric metrics across categorical dimensions
            for cat_col in categorical_cols[:2]:  # Limit to 2 categorical columns
                unique_values = df[cat_col].nunique()
                
                # Only compare if we have 2-10 unique values
                if 2 <= unique_values <= 10:
                    for num_col in numeric_cols[:2]:  # Limit to 2 numeric columns
                        groups = df.groupby(cat_col)[num_col].agg(['mean', 'median', 'count']).dropna()
                        
                        if len(groups) >= 2:
                            # Find best and worst performing groups
                            best_group = groups['mean'].idxmax()
                            worst_group = groups['mean'].idxmin()
                            
                            difference = groups.loc[best_group, 'mean'] - groups.loc[worst_group, 'mean']
                            percentage_diff = (difference / groups.loc[worst_group, 'mean'] * 100) if groups.loc[worst_group, 'mean'] != 0 else 0
                            
                            comparisons.append({
                                "dimension": cat_col,
                                "metric": num_col,
                                "best_performer": str(best_group),
                                "worst_performer": str(worst_group),
                                "best_value": float(groups.loc[best_group, 'mean']),
                                "worst_value": float(groups.loc[worst_group, 'mean']),
                                "absolute_difference": float(difference),
                                "percentage_difference": float(percentage_diff),
                                "significance": "high" if abs(percentage_diff) > 20 else "medium" if abs(percentage_diff) > 10 else "low"
                            })
            
            if not comparisons:
                return None
            
            return {
                "type": "comparative_analysis",
                "title": "Comparative Analysis Results",
                "findings": comparisons,
                "summary": f"Compared performance across {len(comparisons)} metric-dimension combinations",
                "impact": "high" if any(c["significance"] == "high" for c in comparisons) else "medium"
            }
            
        except Exception as e:
            print(f"⚠️ Error in comparative analysis: {str(e)}")
            return None
    
    async def _generate_profile_insights(self, query_intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights when no data is available, using profile information"""
        
        return [{
            "type": "general",
            "title": "Data Analysis Recommendations",
            "findings": [{
                "recommendation": "Upload data file to enable detailed analysis",
                "priority": "high",
                "reason": "No data available for analysis"
            }],
            "summary": "Waiting for data to perform comprehensive analysis",
            "impact": "low"
        }]
    
    def _calculate_method_confidence(self, method: str, df: pd.DataFrame) -> float:
        """Calculate confidence score for analysis method"""
        
        base_confidence = {
            "trend_analysis": 0.8,
            "anomaly_detection": 0.7,
            "correlation_analysis": 0.85,
            "segmentation": 0.6,
            "forecasting": 0.5,
            "comparative_analysis": 0.75
        }
        
        confidence = base_confidence.get(method, 0.5)
        
        # Adjust based on data quality
        if df is not None:
            # More data = higher confidence
            if len(df) > 1000:
                confidence += 0.1
            elif len(df) < 50:
                confidence -= 0.2
            
            # Less missing data = higher confidence
            missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            confidence -= missing_ratio * 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_confidence_score(self, insights: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for insights"""
        
        if not insights:
            return 0.0
        
        # Average confidence of all methods
        confidences = [insight.get("confidence", 0.5) for insight in insights]
        return sum(confidences) / len(confidences)
    
    async def _generate_business_recommendations(
        self, 
        insights: List[Dict[str, Any]], 
        query_intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable business recommendations"""
        
        recommendations = []
        
        # Analyze insights to generate recommendations
        for insight in insights:
            insight_type = insight.get("type", "")
            impact = insight.get("impact", "medium")
            
            if insight_type == "trend_analysis":
                for finding in insight.get("findings", []):
                    if finding.get("strength") == "strong":
                        direction = finding.get("direction", "")
                        metric = finding.get("metric", "")
                        
                        if direction == "increasing":
                            recommendations.append({
                                "category": "growth_opportunity",
                                "priority": "high" if impact == "high" else "medium",
                                "title": f"Leverage positive trend in {metric}",
                                "description": f"{metric} shows strong upward trend - consider scaling efforts",
                                "action_items": [
                                    f"Investigate factors driving {metric} growth",
                                    "Allocate additional resources to maintain momentum",
                                    "Set aggressive targets based on trend trajectory"
                                ]
                            })
                        else:
                            recommendations.append({
                                "category": "risk_mitigation",
                                "priority": "high",
                                "title": f"Address declining trend in {metric}",
                                "description": f"{metric} shows concerning downward trend",
                                "action_items": [
                                    f"Investigate root causes of {metric} decline",
                                    "Implement corrective measures immediately",
                                    "Monitor progress weekly"
                                ]
                            })
            
            elif insight_type == "anomaly_detection":
                high_severity_anomalies = [f for f in insight.get("findings", []) if f.get("severity") == "high"]
                if high_severity_anomalies:
                    recommendations.append({
                        "category": "data_quality",
                        "priority": "high",
                        "title": "Investigate data anomalies",
                        "description": f"Found significant anomalies in {len(high_severity_anomalies)} metrics",
                        "action_items": [
                            "Review data collection processes",
                            "Validate outlier values with source systems",
                            "Implement data quality monitoring"
                        ]
                    })
            
            elif insight_type == "comparative_analysis":
                high_impact_comparisons = [f for f in insight.get("findings", []) if f.get("significance") == "high"]
                for comparison in high_impact_comparisons:
                    best_performer = comparison.get("best_performer", "")
                    worst_performer = comparison.get("worst_performer", "")
                    metric = comparison.get("metric", "")
                    
                    recommendations.append({
                        "category": "performance_improvement",
                        "priority": "medium",
                        "title": f"Replicate success from {best_performer}",
                        "description": f"{best_performer} significantly outperforms {worst_performer} in {metric}",
                        "action_items": [
                            f"Analyze practices and strategies used by {best_performer}",
                            f"Develop improvement plan for {worst_performer}",
                            "Establish best practice sharing process"
                        ]
                    })
        
        # Add general recommendations if none generated
        if not recommendations:
            recommendations.append({
                "category": "data_analysis",
                "priority": "medium",
                "title": "Continue monitoring key metrics",
                "description": "Regular analysis will help identify opportunities and risks",
                "action_items": [
                    "Establish regular reporting cadence",
                    "Set up automated alerts for significant changes",
                    "Expand data collection for deeper insights"
                ]
            })
        
        return recommendations
    
    async def _create_executive_summary(
        self, 
        insights: List[Dict[str, Any]], 
        recommendations: List[Dict[str, Any]], 
        query_intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create executive summary of all insights"""
        
        # Count insights by impact level
        high_impact = len([i for i in insights if i.get("impact") == "high"])
        medium_impact = len([i for i in insights if i.get("impact") == "medium"])
        
        # Count recommendations by priority
        high_priority_recs = len([r for r in recommendations if r.get("priority") == "high"])
        
        # Generate key findings
        key_findings = []
        for insight in insights[:3]:  # Top 3 insights
            findings = insight.get("findings", [])
            if findings:
                key_findings.append(insight.get("summary", "Insight found"))
        
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_insights": len(insights),
            "high_impact_insights": high_impact,
            "medium_impact_insights": medium_impact,
            "total_recommendations": len(recommendations),
            "high_priority_recommendations": high_priority_recs,
            "key_findings": key_findings,
            "overall_health": "good" if high_impact == 0 else "attention_needed" if high_impact < 3 else "critical",
            "next_steps": [r.get("title", "") for r in recommendations[:3]]  # Top 3 recommendations
        }
        
        return summary
    
    def get_required_fields(self) -> List[str]:
        """Required fields for insight agent"""
        return []  # Can work with various input combinations
