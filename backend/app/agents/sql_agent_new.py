# SQL Agent - Enhanced for File Data Processing

from typing import Dict, Any, List, Optional, Tuple
import json
import re
import pandas as pd

from app.agents.base_agent import BaseAgent


class SQLAgent(BaseAgent):
    """SQL query generation and execution specialist for file data"""
    
    def __init__(self):
        super().__init__("SQL Agent")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and execute SQL queries based on requirements"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for SQL Agent"}
        
        # Check if we have file data to process
        file_data = state.get("file_data")
        if file_data and isinstance(file_data, dict):
            print(f"🔍 SQL Agent: Processing file data with {len(file_data.get('data', []))} rows")
            return await self._process_file_data(state, file_data)
        
        # If no file data, return a message
        return {
            "error": "No data available for SQL processing",
            "message": "Please upload a data file to enable SQL queries",
            "agent": self.agent_name,
            "status": "completed"
        }
    
    async def _process_file_data(self, state: Dict[str, Any], file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process SQL queries against file data using pandas"""
        try:
            # Convert file data back to DataFrame
            df = pd.DataFrame(file_data["data"])
            columns = file_data["columns"]
            
            print(f"🔍 SQL Agent: DataFrame shape: {df.shape}, columns: {columns}")
            
            # Get query components
            query_intent = state.get("query_intent", {})
            extracted_entities = state.get("extracted_entities", {})
            user_query = state.get("user_query", "")
            
            # Process the query using pandas operations
            result_data = await self._execute_pandas_query(df, user_query, query_intent, extracted_entities)
            
            return {
                "success": True,
                "data": result_data["data"],
                "metadata": result_data["metadata"],
                "summary": result_data["summary"],
                "generated_sql": result_data.get("equivalent_sql", "N/A"),
                "agent": self.agent_name,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ SQL Agent file processing error: {str(e)}")
            return {
                "error": f"Failed to process file data: {str(e)}",
                "agent": self.agent_name,
                "status": "failed"
            }
    
    async def _execute_pandas_query(self, df: pd.DataFrame, user_query: str, query_intent: Dict, entities: Dict) -> Dict[str, Any]:
        """Execute query logic using pandas operations"""
        
        try:
            query_lower = user_query.lower()
            
            # Check for SQL-style queries
            if "select" in query_lower and ("group by" in query_lower or "sum(" in query_lower):
                return await self._process_sql_style_query(df, user_query)
            else:
                # Process as natural language query
                return await self._process_natural_query(df, user_query, query_intent, entities)
                
        except Exception as e:
            print(f"❌ Pandas query execution error: {str(e)}")
            # Fallback: return basic data summary
            return {
                "data": df.head(10).to_dict('records'),
                "metadata": {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns)
                },
                "summary": f"Data overview: {len(df)} rows, {len(df.columns)} columns"
            }
    
    async def _process_sql_style_query(self, df: pd.DataFrame, sql_query: str) -> Dict[str, Any]:
        """Process SQL-style queries using pandas"""
        try:
            query_lower = sql_query.lower()
            
            # Handle GROUP BY SUM queries
            if "sum(" in query_lower and "group by" in query_lower:
                group_col = self._extract_group_column(sql_query, df.columns)
                sum_col = self._extract_sum_column(sql_query, df.columns)
                
                if group_col and sum_col and group_col in df.columns and sum_col in df.columns:
                    # Convert sum column to numeric if needed
                    df[sum_col] = pd.to_numeric(df[sum_col], errors='coerce')
                    
                    result = df.groupby(group_col)[sum_col].sum().reset_index()
                    result = result.sort_values(sum_col, ascending=False)
                    
                    return {
                        "data": result.to_dict('records'),
                        "metadata": {
                            "row_count": len(result),
                            "column_count": len(result.columns),
                            "columns": list(result.columns),
                            "aggregation": f"SUM of {sum_col} grouped by {group_col}"
                        },
                        "summary": f"Aggregated {sum_col} by {group_col}, showing {len(result)} categories",
                        "equivalent_sql": sql_query
                    }
            
            # Fallback to basic query
            result_df = df.head(20)
            return {
                "data": result_df.to_dict('records'),
                "metadata": {
                    "row_count": len(result_df),
                    "column_count": len(result_df.columns),
                    "columns": list(result_df.columns)
                },
                "summary": f"Showing first 20 rows of data",
                "equivalent_sql": "SELECT * FROM data LIMIT 20"
            }
            
        except Exception as e:
            print(f"❌ SQL-style query processing error: {str(e)}")
            raise e
    
    def _extract_group_column(self, sql_query: str, available_columns: List[str]) -> Optional[str]:
        """Extract GROUP BY column from SQL query"""
        # Look for GROUP BY pattern
        pattern = r'group\s+by\s+(\w+)'
        match = re.search(pattern, sql_query, re.IGNORECASE)
        
        if match:
            column = match.group(1)
            # Find best match in available columns
            for col in available_columns:
                if col.lower() == column.lower():
                    return col
        
        return None
    
    def _extract_sum_column(self, sql_query: str, available_columns: List[str]) -> Optional[str]:
        """Extract SUM column from SQL query"""
        # Look for SUM(column) pattern
        pattern = r'sum\s*\(\s*(\w+)\s*\)'
        match = re.search(pattern, sql_query, re.IGNORECASE)
        
        if match:
            column = match.group(1)
            # Find best match in available columns
            for col in available_columns:
                if col.lower() == column.lower():
                    return col
        
        return None
    
    async def _process_natural_query(self, df: pd.DataFrame, user_query: str, query_intent: Dict, entities: Dict) -> Dict[str, Any]:
        """Process natural language queries"""
        
        query_lower = user_query.lower()
        
        # Look for sales/revenue analysis
        if any(word in query_lower for word in ["sales", "revenue", "total"]):
            sales_col = None
            for col in df.columns:
                if any(word in col.lower() for word in ["sales", "revenue", "amount", "total"]):
                    sales_col = col
                    break
            
            if sales_col:
                # Convert to numeric
                df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
                
                # Simple aggregation
                total_sales = df[sales_col].sum()
                avg_sales = df[sales_col].mean()
                
                summary_data = [
                    {"metric": "Total Sales", "value": float(total_sales)},
                    {"metric": "Average Sales", "value": float(avg_sales)},
                    {"metric": "Number of Records", "value": len(df)}
                ]
                
                return {
                    "data": summary_data,
                    "metadata": {
                        "row_count": len(summary_data),
                        "column_count": 2,
                        "columns": ["metric", "value"],
                        "source_column": sales_col
                    },
                    "summary": f"Sales analysis based on {sales_col} column"
                }
        
        # Look for category/grouping analysis
        if any(word in query_lower for word in ["category", "group", "by"]):
            # Find category column
            category_cols = [col for col in df.columns if 'category' in col.lower()]
            if category_cols:
                category_col = category_cols[0]
                value_counts = df[category_col].value_counts().head(10)
                
                result_data = [
                    {"category": str(idx), "count": int(val)} 
                    for idx, val in value_counts.items()
                ]
                
                return {
                    "data": result_data,
                    "metadata": {
                        "row_count": len(result_data),
                        "column_count": 2,
                        "columns": ["category", "count"],
                        "source_column": category_col
                    },
                    "summary": f"Category breakdown by {category_col}"
                }
        
        # Default: return sample of data
        result_df = df.head(10)
        return {
            "data": result_df.to_dict('records'),
            "metadata": {
                "row_count": len(result_df),
                "column_count": len(result_df.columns),
                "columns": list(result_df.columns)
            },
            "summary": f"Data sample: showing first 10 rows of {len(df)} total rows"
        }
    
    def get_required_fields(self) -> List[str]:
        """Required fields for SQL agent - relaxed since we handle file data"""
        return ["user_query"]  # Only require user_query, make query_intent optional
