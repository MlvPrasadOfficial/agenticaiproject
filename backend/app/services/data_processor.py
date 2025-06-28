"""
Data Processing Service for Enterprise Insights Copilot
Implements Tasks 51-60: Data parsing, validation, profiling, and quality assessment.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import chardet
import warnings

from app.core.logging import get_logger

logger = get_logger(__name__)

class DataType(str, Enum):
    """Enumeration of supported data types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"

class DataQuality(str, Enum):
    """Data quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class ColumnProfile:
    """Profile information for a single column."""
    name: str
    data_type: DataType
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    memory_usage: int
    
    # Type-specific statistics
    statistics: Dict[str, Any]
    
    # Data quality indicators
    quality_score: float
    quality_issues: List[str]
    
    # Sample values
    sample_values: List[Any]
    most_common_values: List[Tuple[Any, int]]

@dataclass
class DataProfile:
    """Comprehensive data profile for a dataset."""
    file_id: str
    filename: str
    row_count: int
    column_count: int
    memory_usage: int
    processing_time: float
    
    # Column profiles
    columns: List[ColumnProfile]
    
    # Overall data quality
    overall_quality: DataQuality
    quality_score: float
    data_issues: List[str]
    
    # Data statistics
    numeric_columns: int
    categorical_columns: int
    datetime_columns: int
    text_columns: int
    
    # Recommendations
    recommendations: List[str]
    
    # Preview data
    sample_data: List[Dict[str, Any]]

class DataProcessor:
    """Advanced data processing engine with comprehensive analysis capabilities."""
    
    def __init__(self):
        self.supported_formats = {'.csv', '.xlsx', '.xls', '.json', '.txt'}
        self.encoding_fallbacks = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
    async def process_file(self, file_path: Path, file_id: str) -> DataProfile:
        """
        Process uploaded file and generate comprehensive data profile.
        
        Args:
            file_path: Path to the uploaded file
            file_id: Unique identifier for the file
            
        Returns:
            DataProfile: Comprehensive analysis of the data
        """
        start_time = datetime.now()
        logger.info(f"Starting data processing for file: {file_path}")
        
        try:
            # Step 1: Load data
            df = await self._load_data(file_path)
            
            # Step 2: Infer and convert data types
            df = await self._infer_and_convert_types(df)
            
            # Step 3: Generate column profiles
            column_profiles = await self._generate_column_profiles(df)
            
            # Step 4: Assess overall data quality
            quality_assessment = await self._assess_data_quality(df, column_profiles)
            
            # Step 5: Generate recommendations
            recommendations = await self._generate_recommendations(df, column_profiles, quality_assessment)
            
            # Step 6: Create sample data
            sample_data = await self._create_sample_data(df)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Count column types
            type_counts = self._count_column_types(column_profiles)
            
            profile = DataProfile(
                file_id=file_id,
                filename=file_path.name,
                row_count=len(df),
                column_count=len(df.columns),
                memory_usage=df.memory_usage(deep=True).sum(),
                processing_time=processing_time,
                columns=column_profiles,
                overall_quality=quality_assessment['level'],
                quality_score=quality_assessment['score'],
                data_issues=quality_assessment['issues'],
                numeric_columns=type_counts[DataType.NUMERIC],
                categorical_columns=type_counts[DataType.CATEGORICAL],
                datetime_columns=type_counts[DataType.DATETIME],
                text_columns=type_counts[DataType.TEXT],
                recommendations=recommendations,
                sample_data=sample_data
            )
            
            logger.info(f"Data processing completed for {file_path}. Quality: {quality_assessment['level']}, Score: {quality_assessment['score']:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"Data processing failed for {file_path}: {str(e)}")
            raise
    
    async def _load_data(self, file_path: Path) -> pd.DataFrame:
        """Load data from file with intelligent format detection and encoding handling."""
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.csv':
                # Try to detect encoding
                encoding = await self._detect_encoding(file_path)
                
                # Try to detect delimiter
                delimiter = await self._detect_csv_delimiter(file_path, encoding)
                
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, low_memory=False)
                
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=0)  # Read first sheet
                
            elif file_extension == '.json':
                # Try different JSON structures
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If it's a single record, wrap in list
                    if all(not isinstance(v, (list, dict)) for v in data.values()):
                        df = pd.DataFrame([data])
                    else:
                        # Try to find the main data array
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                df = pd.DataFrame(value)
                                break
                        else:
                            df = pd.DataFrame([data])
                else:
                    raise ValueError("Unsupported JSON structure")
                    
            elif file_extension == '.txt':
                # Assume tab-delimited text file
                encoding = await self._detect_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding, delimiter='\t', low_memory=False)
                
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Basic validation
            if df.empty:
                raise ValueError("File appears to be empty or contains no data")
            
            if len(df.columns) == 0:
                raise ValueError("File contains no columns")
            
            logger.info(f"Successfully loaded data: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load data from {file_path}: {str(e)}")
            raise
    
    async def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding with fallback options."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                
                if result['confidence'] > 0.7:
                    return result['encoding']
        except Exception:
            pass
        
        # Try common encodings
        for encoding in self.encoding_fallbacks:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1000)  # Try to read first 1000 characters
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Default fallback
        return 'utf-8'
    
    async def _detect_csv_delimiter(self, file_path: Path, encoding: str) -> str:
        """Detect CSV delimiter."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline()
                
            # Count potential delimiters
            delimiters = [',', ';', '\t', '|']
            delimiter_counts = {d: first_line.count(d) for d in delimiters}
            
            # Return delimiter with highest count (and > 0)
            best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
            if delimiter_counts[best_delimiter] > 0:
                return best_delimiter
                
        except Exception:
            pass
        
        return ','  # Default to comma
    
    async def _infer_and_convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Intelligently infer and convert data types."""
        logger.info("Starting data type inference and conversion")
        
        for column in df.columns:
            try:
                # Skip if already numeric
                if pd.api.types.is_numeric_dtype(df[column]):
                    continue
                
                # Try to convert to numeric
                numeric_df = pd.to_numeric(df[column], errors='coerce')
                null_count_before = df[column].isnull().sum()
                null_count_after = numeric_df.isnull().sum()
                
                # If conversion doesn't create too many nulls, accept it
                if (null_count_after - null_count_before) / len(df) < 0.5:
                    df[column] = numeric_df
                    continue
                
                # Try to convert to datetime
                try:
                    datetime_series = pd.to_datetime(df[column], errors='coerce', infer_datetime_format=True)
                    null_count_datetime = datetime_series.isnull().sum()
                    
                    if (null_count_datetime - null_count_before) / len(df) < 0.5:
                        df[column] = datetime_series
                        continue
                except Exception:
                    pass
                
                # Try boolean conversion
                if df[column].dtype == 'object':
                    unique_values = df[column].dropna().unique()
                    if len(unique_values) <= 2:
                        # Check if values look like booleans
                        boolean_like = {'true', 'false', 'yes', 'no', '1', '0', 'y', 'n'}
                        if all(str(v).lower() in boolean_like for v in unique_values):
                            boolean_map = {'true': True, 'false': False, 'yes': True, 'no': False, 
                                          '1': True, '0': False, 'y': True, 'n': False}
                            df[column] = df[column].map(lambda x: boolean_map.get(str(x).lower(), x) if pd.notna(x) else x)
                            continue
                
                # Keep as categorical if reasonable number of unique values
                if df[column].dtype == 'object':
                    unique_ratio = df[column].nunique() / len(df)
                    if unique_ratio < 0.5:  # Less than 50% unique values
                        df[column] = df[column].astype('category')
                        
            except Exception as e:
                logger.warning(f"Type conversion failed for column {column}: {str(e)}")
                continue
        
        logger.info("Data type inference completed")
        return df
    
    async def _generate_column_profiles(self, df: pd.DataFrame) -> List[ColumnProfile]:
        """Generate detailed profiles for each column."""
        logger.info("Generating column profiles")
        
        profiles = []
        
        for column in df.columns:
            try:
                series = df[column]
                
                # Basic statistics
                null_count = series.isnull().sum()
                null_percentage = (null_count / len(series)) * 100
                unique_count = series.nunique()
                unique_percentage = (unique_count / len(series)) * 100
                memory_usage = series.memory_usage(deep=True)
                
                # Determine data type
                data_type = self._classify_data_type(series)
                
                # Type-specific statistics
                statistics = self._calculate_type_specific_stats(series, data_type)
                
                # Quality assessment for this column
                quality_score, quality_issues = self._assess_column_quality(series, data_type)
                
                # Sample values
                sample_values = self._get_sample_values(series)
                most_common = self._get_most_common_values(series)
                
                profile = ColumnProfile(
                    name=column,
                    data_type=data_type,
                    null_count=null_count,
                    null_percentage=null_percentage,
                    unique_count=unique_count,
                    unique_percentage=unique_percentage,
                    memory_usage=memory_usage,
                    statistics=statistics,
                    quality_score=quality_score,
                    quality_issues=quality_issues,
                    sample_values=sample_values,
                    most_common_values=most_common
                )
                
                profiles.append(profile)
                
            except Exception as e:
                logger.error(f"Failed to profile column {column}: {str(e)}")
                # Create a basic profile for failed columns
                profiles.append(ColumnProfile(
                    name=column,
                    data_type=DataType.UNKNOWN,
                    null_count=0,
                    null_percentage=0.0,
                    unique_count=0,
                    unique_percentage=0.0,
                    memory_usage=0,
                    statistics={},
                    quality_score=0.0,
                    quality_issues=[f"Profile generation failed: {str(e)}"],
                    sample_values=[],
                    most_common_values=[]
                ))
        
        logger.info(f"Generated profiles for {len(profiles)} columns")
        return profiles
    
    def _classify_data_type(self, series: pd.Series) -> DataType:
        """Classify the data type of a pandas Series."""
        if pd.api.types.is_numeric_dtype(series):
            return DataType.NUMERIC
        elif pd.api.types.is_datetime64_any_dtype(series):
            return DataType.DATETIME
        elif pd.api.types.is_bool_dtype(series):
            return DataType.BOOLEAN
        elif pd.api.types.is_categorical_dtype(series):
            return DataType.CATEGORICAL
        elif series.dtype == 'object':
            # Heuristic: if many unique values, treat as text
            unique_ratio = series.nunique() / len(series)
            if unique_ratio > 0.5:
                return DataType.TEXT
            else:
                return DataType.CATEGORICAL
        else:
            return DataType.UNKNOWN
    
    def _calculate_type_specific_stats(self, series: pd.Series, data_type: DataType) -> Dict[str, Any]:
        """Calculate statistics specific to the data type."""
        stats = {}
        
        try:
            if data_type == DataType.NUMERIC:
                stats.update({
                    'min': float(series.min()) if pd.notna(series.min()) else None,
                    'max': float(series.max()) if pd.notna(series.max()) else None,
                    'mean': float(series.mean()) if pd.notna(series.mean()) else None,
                    'median': float(series.median()) if pd.notna(series.median()) else None,
                    'std': float(series.std()) if pd.notna(series.std()) else None,
                    'variance': float(series.var()) if pd.notna(series.var()) else None,
                    'skewness': float(series.skew()) if pd.notna(series.skew()) else None,
                    'kurtosis': float(series.kurtosis()) if pd.notna(series.kurtosis()) else None,
                    'q25': float(series.quantile(0.25)) if pd.notna(series.quantile(0.25)) else None,
                    'q75': float(series.quantile(0.75)) if pd.notna(series.quantile(0.75)) else None,
                    'outliers_count': self._count_outliers(series)
                })
                
            elif data_type == DataType.DATETIME:
                non_null = series.dropna()
                if len(non_null) > 0:
                    stats.update({
                        'min_date': non_null.min().isoformat() if pd.notna(non_null.min()) else None,
                        'max_date': non_null.max().isoformat() if pd.notna(non_null.max()) else None,
                        'date_range_days': (non_null.max() - non_null.min()).days if len(non_null) > 1 else 0
                    })
                    
            elif data_type in [DataType.CATEGORICAL, DataType.TEXT]:
                non_null = series.dropna()
                if len(non_null) > 0:
                    stats.update({
                        'avg_length': float(non_null.astype(str).str.len().mean()),
                        'min_length': int(non_null.astype(str).str.len().min()),
                        'max_length': int(non_null.astype(str).str.len().max()),
                        'empty_strings': int((non_null.astype(str) == '').sum())
                    })
                    
            elif data_type == DataType.BOOLEAN:
                stats.update({
                    'true_count': int(series.sum()) if pd.notna(series.sum()) else 0,
                    'false_count': int(len(series) - series.sum() - series.isnull().sum())
                })
                
        except Exception as e:
            logger.warning(f"Failed to calculate statistics for series: {str(e)}")
            stats['calculation_error'] = str(e)
        
        return stats
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method."""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            return len(outliers)
        except Exception:
            return 0
    
    def _assess_column_quality(self, series: pd.Series, data_type: DataType) -> Tuple[float, List[str]]:
        """Assess quality of a single column."""
        issues = []
        score = 100.0
        
        # Check null percentage
        null_pct = (series.isnull().sum() / len(series)) * 100
        if null_pct > 50:
            issues.append(f"High null percentage: {null_pct:.1f}%")
            score -= 40
        elif null_pct > 20:
            issues.append(f"Moderate null percentage: {null_pct:.1f}%")
            score -= 20
        elif null_pct > 5:
            score -= 10
        
        # Check uniqueness issues
        unique_pct = (series.nunique() / len(series)) * 100
        if unique_pct == 100:
            issues.append("All values are unique (potential identifier column)")
            score -= 10
        elif unique_pct < 1 and data_type != DataType.BOOLEAN:
            issues.append(f"Very low uniqueness: {unique_pct:.1f}%")
            score -= 30
        
        # Type-specific checks
        if data_type == DataType.NUMERIC:
            if self._count_outliers(series) > len(series) * 0.1:
                issues.append("High number of outliers detected")
                score -= 15
                
        elif data_type in [DataType.TEXT, DataType.CATEGORICAL]:
            # Check for inconsistent formatting
            non_null = series.dropna().astype(str)
            if len(non_null) > 0:
                length_std = non_null.str.len().std()
                length_mean = non_null.str.len().mean()
                if length_std > length_mean:
                    issues.append("Inconsistent text length formatting")
                    score -= 10
        
        return max(score, 0), issues
    
    def _get_sample_values(self, series: pd.Series, n: int = 5) -> List[Any]:
        """Get sample values from the series."""
        try:
            non_null = series.dropna()
            if len(non_null) == 0:
                return []
            
            sample = non_null.sample(min(n, len(non_null)), random_state=42)
            return [self._serialize_value(v) for v in sample.tolist()]
        except Exception:
            return []
    
    def _get_most_common_values(self, series: pd.Series, n: int = 5) -> List[Tuple[Any, int]]:
        """Get most common values and their counts."""
        try:
            value_counts = series.value_counts().head(n)
            return [(self._serialize_value(k), int(v)) for k, v in value_counts.items()]
        except Exception:
            return []
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON compatibility."""
        if pd.isna(value):
            return None
        elif isinstance(value, (np.integer, int)):
            return int(value)
        elif isinstance(value, (np.floating, float)):
            return float(value)
        elif isinstance(value, (pd.Timestamp, datetime)):
            return value.isoformat()
        else:
            return str(value)
    
    async def _assess_data_quality(self, df: pd.DataFrame, column_profiles: List[ColumnProfile]) -> Dict[str, Any]:
        """Assess overall data quality."""
        logger.info("Assessing overall data quality")
        
        # Calculate overall quality score
        column_scores = [profile.quality_score for profile in column_profiles]
        overall_score = sum(column_scores) / len(column_scores) if column_scores else 0
        
        # Determine quality level
        if overall_score >= 90:
            quality_level = DataQuality.EXCELLENT
        elif overall_score >= 75:
            quality_level = DataQuality.GOOD
        elif overall_score >= 60:
            quality_level = DataQuality.FAIR
        else:
            quality_level = DataQuality.POOR
        
        # Collect data issues
        issues = []
        
        # Overall null percentage
        total_nulls = df.isnull().sum().sum()
        total_cells = df.shape[0] * df.shape[1]
        null_percentage = (total_nulls / total_cells) * 100
        
        if null_percentage > 20:
            issues.append(f"High overall null percentage: {null_percentage:.1f}%")
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            duplicate_percentage = (duplicate_count / len(df)) * 100
            issues.append(f"Duplicate rows found: {duplicate_count} ({duplicate_percentage:.1f}%)")
        
        # Check column count
        if df.shape[1] < 2:
            issues.append("Very few columns - limited analysis possible")
        elif df.shape[1] > 100:
            issues.append("Very many columns - consider feature selection")
        
        # Check row count
        if df.shape[0] < 100:
            issues.append("Small dataset - statistical significance may be limited")
        
        return {
            'level': quality_level,
            'score': overall_score,
            'issues': issues,
            'null_percentage': null_percentage,
            'duplicate_count': duplicate_count
        }
    
    async def _generate_recommendations(self, df: pd.DataFrame, column_profiles: List[ColumnProfile], quality_assessment: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on data analysis."""
        recommendations = []
        
        # Quality-based recommendations
        if quality_assessment['score'] < 70:
            recommendations.append("Consider data cleaning and preprocessing before analysis")
        
        if quality_assessment['null_percentage'] > 15:
            recommendations.append("Address missing values through imputation or removal")
        
        if quality_assessment['duplicate_count'] > 0:
            recommendations.append("Remove or investigate duplicate rows")
        
        # Column-specific recommendations
        high_null_columns = [p for p in column_profiles if p.null_percentage > 30]
        if high_null_columns:
            recommendations.append(f"Consider removing columns with high null rates: {', '.join([p.name for p in high_null_columns[:3]])}")
        
        # Data type recommendations
        text_columns = [p for p in column_profiles if p.data_type == DataType.TEXT and p.unique_percentage < 10]
        if text_columns:
            recommendations.append(f"Consider converting text columns to categorical: {', '.join([p.name for p in text_columns[:3]])}")
        
        numeric_columns = [p for p in column_profiles if p.data_type == DataType.NUMERIC]
        if len(numeric_columns) > 1:
            recommendations.append("Explore correlations between numeric variables")
        
        # Analysis recommendations
        categorical_columns = [p for p in column_profiles if p.data_type == DataType.CATEGORICAL]
        if categorical_columns and numeric_columns:
            recommendations.append("Consider groupby analysis using categorical variables")
        
        datetime_columns = [p for p in column_profiles if p.data_type == DataType.DATETIME]
        if datetime_columns and numeric_columns:
            recommendations.append("Consider time series analysis for temporal patterns")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _create_sample_data(self, df: pd.DataFrame, n: int = 10) -> List[Dict[str, Any]]:
        """Create sample data for preview."""
        try:
            sample_df = df.head(n)
            
            # Convert to JSON-serializable format
            sample_data = []
            for _, row in sample_df.iterrows():
                row_dict = {}
                for col, val in row.items():
                    row_dict[col] = self._serialize_value(val)
                sample_data.append(row_dict)
            
            return sample_data
        except Exception as e:
            logger.error(f"Failed to create sample data: {str(e)}")
            return []
    
    def _count_column_types(self, column_profiles: List[ColumnProfile]) -> Dict[DataType, int]:
        """Count columns by data type."""
        counts = {dtype: 0 for dtype in DataType}
        for profile in column_profiles:
            counts[profile.data_type] += 1
        return counts

# Global processor instance
data_processor = DataProcessor()
