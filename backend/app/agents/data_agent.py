# Data Agent - Data Profiling and Analysis

from typing import Dict, Any, List, Optional, Tuple
import json
import pandas as pd
import numpy as np
from datetime import datetime
import io
import os
from pathlib import Path

from app.agents.base_agent import BaseAgent


class DataAgent(BaseAgent):
    """Data profiling, quality assessment, and exploratory analysis specialist"""
    
    def __init__(self):
        super().__init__("Data Agent")
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze uploaded data files and generate comprehensive profile"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Data Agent"}
        
        file_path = state.get("file_path")
        data_content = state.get("data_content")
        analysis_type = state.get("analysis_type", "comprehensive")
        
        # Load data from file or content
        if file_path:
            df = await self._load_data_from_file(file_path)
        elif data_content:
            df = await self._load_data_from_content(data_content)
        else:
            return {"error": "No data file or content provided"}
        
        if df is None or df.empty:
            return {"error": "Failed to load or parse data"}
        
        # Perform data analysis based on type
        if analysis_type == "quick":
            analysis_result = await self._quick_analysis(df)
        else:
            analysis_result = await self._comprehensive_analysis(df)
        
        # Generate insights and recommendations
        insights = await self._generate_insights(df, analysis_result)
        recommendations = await self._generate_recommendations(df, analysis_result)
        
        # Update state with analysis results
        state.update({
            "data_profile": analysis_result,
            "data_insights": insights,
            "data_recommendations": recommendations,
            "data_schema": self._extract_schema(df),
            "row_count": len(df),
            "column_count": len(df.columns),
            "data_types": df.dtypes.to_dict()
        })
        
        return {
            "data_profile": analysis_result,
            "insights": insights,
            "recommendations": recommendations,
            "schema": self._extract_schema(df),
            "statistics": {
                "rows": len(df),
                "columns": len(df.columns),
                "size_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            "agent": self.agent_name,
            "status": "completed"
        }
    
    async def _load_data_from_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from file path"""
        try:
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.csv':
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                return pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            
            elif file_ext == '.json':
                return pd.read_json(file_path)
            
            elif file_ext == '.parquet':
                return pd.read_parquet(file_path)
            
            else:
                print(f"⚠️ Unsupported file format: {file_ext}")
                return None
                
        except Exception as e:
            print(f"❌ Error loading file {file_path}: {str(e)}")
            return None
    
    async def _load_data_from_content(self, content: str) -> Optional[pd.DataFrame]:
        """Load data from string content"""
        try:
            # Try to parse as CSV first
            return pd.read_csv(io.StringIO(content))
        except Exception:
            # Try to parse as JSON
            try:
                return pd.read_json(io.StringIO(content))
            except Exception:
                print("❌ Failed to parse data content")
                return None
    
    async def _quick_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform quick data analysis"""
        
        analysis = {
            "basic_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            "column_info": {},
            "missing_data": {},
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
        # Analyze each column
        for col in df.columns:
            col_info = {
                "dtype": str(df[col].dtype),
                "non_null_count": df[col].count(),
                "null_count": df[col].isnull().sum(),
                "null_percentage": (df[col].isnull().sum() / len(df)) * 100,
                "unique_count": df[col].nunique()
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None
                })
            
            analysis["column_info"][col] = col_info
        
        # Missing data summary
        analysis["missing_data"] = {
            "total_missing": int(df.isnull().sum().sum()),
            "columns_with_missing": list(df.columns[df.isnull().any()]),
            "missing_percentage": float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
        }
        
        return analysis
    
    async def _comprehensive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive data analysis"""
        
        # Start with quick analysis
        analysis = await self._quick_analysis(df)
        
        # Add detailed statistics
        analysis["detailed_statistics"] = {}
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis["detailed_statistics"]["numeric"] = {}
            for col in numeric_cols:
                if df[col].count() > 0:  # Only if column has data
                    analysis["detailed_statistics"]["numeric"][col] = {
                        "quartiles": {
                            "q1": float(df[col].quantile(0.25)),
                            "median": float(df[col].median()),
                            "q3": float(df[col].quantile(0.75))
                        },
                        "outliers": self._detect_outliers(df[col]),
                        "distribution": self._analyze_distribution(df[col])
                    }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            analysis["detailed_statistics"]["categorical"] = {}
            for col in categorical_cols:
                if df[col].count() > 0:
                    value_counts = df[col].value_counts().head(10)
                    analysis["detailed_statistics"]["categorical"][col] = {
                        "top_values": value_counts.to_dict(),
                        "cardinality": int(df[col].nunique()),
                        "most_frequent": str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None
                    }
        
        # Data quality assessment
        analysis["quality_assessment"] = self._assess_data_quality(df)
          # Correlation analysis for numeric columns
        if len(numeric_cols) > 1:
            try:
                correlation_matrix = df[numeric_cols].corr()
                analysis["correlations"] = correlation_matrix.to_dict()
                analysis["strong_correlations"] = self._find_strong_correlations(correlation_matrix)
            except Exception:
                analysis["correlations"] = {}
                analysis["strong_correlations"] = []
        
        return analysis
    
    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        if series.dtype not in [np.number] or series.count() == 0:
            return {"count": 0, "method": "IQR", "outlier_values": []}
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "count": len(outliers),
            "percentage": (len(outliers) / len(series)) * 100,
            "method": "IQR",
            "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)},
            "outlier_values": outliers.head(10).tolist()
        }
    
    def _analyze_distribution(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze data distribution"""
        if series.dtype not in [np.number] or series.count() == 0:
            return {"type": "unknown", "skewness": None, "kurtosis": None}
        
        skewness = float(series.skew())
        kurtosis = float(series.kurtosis())
        
        # Determine distribution type based on skewness
        if abs(skewness) < 0.5:
            dist_type = "approximately_normal"
        elif skewness > 0.5:
            dist_type = "right_skewed"
        else:
            dist_type = "left_skewed"
        
        return {
            "type": dist_type,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "variance": float(series.var()),
            "coefficient_of_variation": float(series.std() / series.mean()) if series.mean() != 0 else None
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        
        # Calculate quality metrics
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        
        # Duplicate rows
        duplicate_count = df.duplicated().sum()
        
        # Data consistency checks
        consistency_issues = []
        
        # Check for mixed data types in object columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].apply(lambda x: type(x).__name__).nunique() > 2:  # More than str and NaN
                consistency_issues.append(f"Mixed data types in column '{col}'")
        
        # Check for suspicious patterns
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].count() > 0:
                if (df[col] == 0).sum() > len(df) * 0.8:  # More than 80% zeros
                    consistency_issues.append(f"High percentage of zeros in column '{col}'")
                
                if df[col].nunique() == 1:  # All same value
                    consistency_issues.append(f"Column '{col}' has constant values")
        
        # Overall quality score
        completeness_score = 1 - (missing_cells / total_cells)
        uniqueness_score = 1 - (duplicate_count / len(df))
        consistency_score = 1 - (len(consistency_issues) / len(df.columns))
        
        overall_score = (completeness_score + uniqueness_score + consistency_score) / 3
          # Determine quality level
        if overall_score > 0.8:
            quality_level = "high"
        elif overall_score > 0.6:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        return {
            "overall_score": float(overall_score),
            "completeness_score": float(completeness_score),
            "uniqueness_score": float(uniqueness_score),
            "consistency_score": float(consistency_score),
            "missing_percentage": float((missing_cells / total_cells) * 100),
            "duplicate_rows": int(duplicate_count),
            "consistency_issues": consistency_issues,
            "quality_level": quality_level
        }
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations between variables"""
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    strong_corrs.append({
                        "variable1": corr_matrix.columns[i],
                        "variable2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong" if abs(corr_value) >= 0.8 else "moderate"
                    })
        
        return sorted(strong_corrs, key=lambda x: abs(x["correlation"]), reverse=True)
    
    def _extract_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract data schema information"""
        
        schema = {
            "columns": {},
            "primary_key_candidates": [],
            "foreign_key_candidates": [],
            "indexes_recommended": []
        }
        
        for col in df.columns:
            col_info = {
                "name": col,
                "dtype": str(df[col].dtype),
                "nullable": bool(df[col].isnull().any()),
                "unique": bool(df[col].nunique() == len(df)),
                "cardinality": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(5).tolist()
            }
            
            # Suggest if column could be primary key
            if df[col].nunique() == len(df) and not df[col].isnull().any():
                schema["primary_key_candidates"].append(col)
            
            # Suggest if column should be indexed (high cardinality, frequently filtered)
            if 10 <= df[col].nunique() <= len(df) * 0.8:
                schema["indexes_recommended"].append(col)
            
            schema["columns"][col] = col_info
        
        return schema
    
    async def _generate_insights(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business insights from data analysis"""
        
        insights = []
        
        # Data volume insights
        if len(df) > 1000000:
            insights.append({
                "type": "volume",
                "priority": "high",
                "message": f"Large dataset with {len(df):,} rows may require optimization for processing",
                "recommendation": "Consider data sampling or chunked processing for better performance"
            })
        
        # Data quality insights
        quality_score = analysis.get("quality_assessment", {}).get("overall_score", 1.0)
        if quality_score < 0.7:
            insights.append({
                "type": "quality",
                "priority": "high",
                "message": f"Data quality score is {quality_score:.2f}, indicating potential issues",
                "recommendation": "Review and clean data before analysis"
            })
        
        # Missing data insights
        missing_pct = analysis.get("missing_data", {}).get("missing_percentage", 0)
        if missing_pct > 20:
            insights.append({
                "type": "completeness",
                "priority": "medium",
                "message": f"{missing_pct:.1f}% of data is missing",
                "recommendation": "Consider imputation strategies or investigate data collection issues"
            })
        
        # Strong correlations insights
        strong_corrs = analysis.get("strong_correlations", [])
        if strong_corrs:
            insights.append({
                "type": "correlation",
                "priority": "medium",
                "message": f"Found {len(strong_corrs)} strong correlations between variables",
                "recommendation": "Investigate causal relationships and consider feature selection"
            })
        
        # Outlier insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_cols = []
        for col in numeric_cols:
            if col in analysis.get("detailed_statistics", {}).get("numeric", {}):
                outlier_info = analysis["detailed_statistics"]["numeric"][col].get("outliers", {})
                if outlier_info.get("percentage", 0) > 5:  # More than 5% outliers
                    outlier_cols.append(col)
        
        if outlier_cols:
            insights.append({
                "type": "outliers",
                "priority": "medium",
                "message": f"Significant outliers detected in columns: {', '.join(outlier_cols)}",
                "recommendation": "Review outliers for data entry errors or genuine extreme values"
            })
        
        return insights
    
    async def _generate_recommendations(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Data cleaning recommendations
        missing_cols = analysis.get("missing_data", {}).get("columns_with_missing", [])
        if missing_cols:
            recommendations.append({
                "category": "data_cleaning",
                "action": "handle_missing_data",
                "description": f"Address missing values in {len(missing_cols)} columns",
                "columns": missing_cols,
                "priority": "high"
            })
        
        # Performance recommendations
        if len(df) > 100000:
            recommendations.append({
                "category": "performance",
                "action": "consider_indexing",
                "description": "Add database indexes for frequently queried columns",
                "columns": analysis.get("schema", {}).get("indexes_recommended", []),
                "priority": "medium"
            })
        
        # Analysis recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            recommendations.append({
                "category": "analysis",
                "action": "explore_correlations",
                "description": "Investigate relationships between numeric variables",
                "columns": numeric_cols.tolist(),
                "priority": "medium"
            })
        
        # Visualization recommendations
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            recommendations.append({
                "category": "visualization",
                "action": "create_distributions",
                "description": "Create distribution charts for categorical variables",
                "columns": categorical_cols.tolist(),
                "priority": "low"
            })
        
        return recommendations
    
    def get_required_fields(self) -> List[str]:
        """Required fields for data agent"""
        return []  # Either file_path or data_content will be provided
