# Data Processing Service

import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime


class DataProcessor:
    """Service for processing uploaded files and generating data profiles"""
    
    def __init__(self):
        self.supported_formats = {
            '.csv': self._read_csv,
            '.xlsx': self._read_excel,
            '.json': self._read_json,
            '.parquet': self._read_parquet
        }
    
    async def get_basic_file_info(self, file_path: str, file_extension: str) -> Dict[str, Any]:
        """Get basic file information without full processing"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Quick peek at file structure
            if file_extension == '.csv':
                # Read just first few rows
                df_preview = pd.read_csv(file_path, nrows=5)
                return {
                    "preview_rows": df_preview.shape[0],
                    "columns": list(df_preview.columns),
                    "estimated_total_rows": "calculating...",
                    "file_size_mb": round(file_size / (1024*1024), 2)
                }
            
            return {
                "file_size_mb": round(file_size / (1024*1024), 2),
                "format": file_extension,
                "status": "pending_analysis"
            }
        
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process file and generate comprehensive data profile"""
        try:
            # Detect file format
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Read file
            df = self.supported_formats[file_extension](file_path)
            
            # Generate data profile
            profile = await self._generate_data_profile(df)
            
            return {
                "file_path": file_path,
                "data_profile": profile,
                "processing_timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
        
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "status": "failed"
            }
    
    def _read_csv(self, file_path: str) -> pd.DataFrame:
        """Read CSV file"""
        return pd.read_csv(file_path)
    
    def _read_excel(self, file_path: str) -> pd.DataFrame:
        """Read Excel file"""
        return pd.read_excel(file_path)
    
    def _read_json(self, file_path: str) -> pd.DataFrame:
        """Read JSON file"""
        return pd.read_json(file_path)
    
    def _read_parquet(self, file_path: str) -> pd.DataFrame:
        """Read Parquet file"""
        return pd.read_parquet(file_path)
    
    async def _generate_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        
        profile = {
            "basic_info": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024*1024), 2)
            },
            "columns": {},
            "data_quality": {},
            "summary_statistics": {}
        }
        
        # Analyze each column
        for column in df.columns:
            column_analysis = await self._analyze_column(df[column])
            profile["columns"][column] = column_analysis
        
        # Overall data quality assessment
        profile["data_quality"] = await self._assess_data_quality(df)
        
        # Summary statistics
        profile["summary_statistics"] = await self._generate_summary_stats(df)
        
        return profile
    
    async def _analyze_column(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze individual column"""
        
        analysis = {
            "data_type": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": round(series.isnull().sum() / len(series) * 100, 2),
            "unique_count": int(series.nunique()),
            "unique_percentage": round(series.nunique() / len(series) * 100, 2)
        }
        
        # Type-specific analysis
        if pd.api.types.is_numeric_dtype(series):
            analysis.update({
                "inferred_type": "numeric",
                "min": float(series.min()) if not series.empty else None,
                "max": float(series.max()) if not series.empty else None,
                "mean": float(series.mean()) if not series.empty else None,
                "median": float(series.median()) if not series.empty else None,
                "std": float(series.std()) if not series.empty else None
            })
        elif pd.api.types.is_datetime64_any_dtype(series):
            analysis.update({
                "inferred_type": "datetime",
                "min_date": str(series.min()) if not series.empty else None,
                "max_date": str(series.max()) if not series.empty else None,
                "date_range_days": (series.max() - series.min()).days if not series.empty else None
            })
        else:
            analysis.update({
                "inferred_type": "categorical",
                "most_frequent": str(series.mode().iloc[0]) if not series.mode().empty else None,
                "most_frequent_count": int(series.value_counts().iloc[0]) if not series.empty else 0
            })
        
        return analysis
    
    async def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        
        quality_score = 1.0 - (null_cells / total_cells) if total_cells > 0 else 0.0
        
        return {
            "overall_quality_score": round(quality_score, 3),
            "total_missing_values": int(null_cells),
            "missing_percentage": round(null_cells / total_cells * 100, 2) if total_cells > 0 else 0,
            "complete_rows": int((~df.isnull().any(axis=1)).sum()),
            "complete_rows_percentage": round((~df.isnull().any(axis=1)).sum() / len(df) * 100, 2) if len(df) > 0 else 0,
            "duplicate_rows": int(df.duplicated().sum()),
            "data_quality_issues": self._identify_quality_issues(df)
        }
    
    def _identify_quality_issues(self, df: pd.DataFrame) -> List[str]:
        """Identify potential data quality issues"""
        issues = []
        
        # Check for high missing value columns
        high_missing = df.columns[df.isnull().sum() / len(df) > 0.5].tolist()
        if high_missing:
            issues.append(f"High missing values in columns: {', '.join(high_missing)}")
        
        # Check for duplicate rows
        if df.duplicated().sum() > 0:
            issues.append(f"Found {df.duplicated().sum()} duplicate rows")
        
        # Check for potential ID columns with missing values
        potential_ids = [col for col in df.columns if 'id' in col.lower()]
        id_missing = [col for col in potential_ids if df[col].isnull().sum() > 0]
        if id_missing:
            issues.append(f"ID columns with missing values: {', '.join(id_missing)}")
        
        return issues
    
    async def _generate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        summary = {
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "datetime_columns": len(datetime_cols),
            "column_distribution": {
                "numeric": numeric_cols,
                "categorical": categorical_cols,
                "datetime": datetime_cols
            }
        }
        
        # Numeric summary
        if numeric_cols:
            numeric_summary = df[numeric_cols].describe()
            summary["numeric_summary"] = numeric_summary.to_dict()
        
        # Categorical summary
        if categorical_cols:
            cat_summary = {}
            for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                cat_summary[col] = {
                    "unique_values": int(df[col].nunique()),
                    "top_values": df[col].value_counts().head(5).to_dict()
                }
            summary["categorical_summary"] = cat_summary
        
        return summary
