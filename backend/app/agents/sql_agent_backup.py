# SQL Agent - SQL Query Generation and Execution

from typing import Dict, Any, List, Optional, Tuple
import json
import re
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect
import pandas as pd

from app.agents.base_agent import BaseAgent
from app.core.database import get_database_url


class SQLAgent(BaseAgent):
    """SQL query generation, optimization, and execution specialist"""
      def __init__(self):
        super().__init__("SQL Agent")
        self.engine = None
        self.schema_cache = {}
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            database_url = get_database_url()
            self.engine = create_engine(database_url)
            await self._cache_schema_info()
        except Exception as e:
            print(f"❌ Error initializing SQL Agent: {str(e)}")
            raise e
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and execute SQL queries based on requirements"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for SQL Agent"}
        
        # Check if we have file data instead of database tables
        file_data = state.get("file_data")
        if file_data and isinstance(file_data, dict):
            print(f"🔍 SQL Agent: Processing file data with {len(file_data.get('data', []))} rows")
            return await self._process_file_data(state, file_data)
        
        # Original database processing logic
        # Initialize if needed
        if not self.engine:
            await self.initialize()
        
        query_intent = state.get("query_intent", {})
        extracted_entities = state.get("extracted_entities", {})
        data_schema = state.get("data_schema", {})
        execution_mode = state.get("sql_execution_mode", "generate_and_execute")
        
        # Generate SQL query
        sql_query = await self._generate_sql_query(query_intent, extracted_entities, data_schema)
        
        if not sql_query:
            return {"error": "Failed to generate SQL query"}
        
        # Validate and optimize query
        validation_result = await self._validate_query(sql_query)
        if not validation_result["valid"]:
            return {"error": f"Invalid SQL query: {validation_result['errors']}"}
        
        optimized_query = await self._optimize_query(sql_query)
        
        result = {"generated_sql": sql_query, "optimized_sql": optimized_query, "validation": validation_result}
        
        # Execute query if requested
        if execution_mode in ["execute", "generate_and_execute"]:
            execution_result = await self._execute_query(optimized_query)
            result.update(execution_result)
            
            # Update state with results
            if execution_result.get("success"):
                state.update({
                    "sql_query": optimized_query,
                    "sql_results": execution_result.get("data"),
                    "sql_metadata": execution_result.get("metadata")
                })
        
        result.update({"agent": self.agent_name, "status": "completed"})
        return result
    
    async def _process_file_data(self, state: Dict[str, Any], file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process SQL queries against file data using pandas"""
        try:
            import pandas as pd
            
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
        
        # Simple query processing based on the user query
        try:
            # For SQL-like queries, try to extract intent
            query_lower = user_query.lower()
            
            if "select" in query_lower and "group by" in query_lower:
                # SQL-style query - extract components
                return await self._process_sql_style_query(df, user_query)
            else:
                # Natural language query - use intent and entities
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
            # Simple SQL parsing for common patterns
            query_lower = sql_query.lower()
            
            # Extract SELECT columns
            if "select" in query_lower:
                # Look for aggregation functions
                if "sum(" in query_lower:
                    # Handle SUM aggregation
                    if "group by" in query_lower:
                        # Example: SELECT category, SUM(sales_amount) FROM data GROUP BY category
                        group_col = self._extract_group_column(sql_query, df.columns)
                        sum_col = self._extract_sum_column(sql_query, df.columns)
                        
                        if group_col and sum_col and group_col in df.columns and sum_col in df.columns:
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
            result_df = df.head(20)  # Limit results
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
        import re
        
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
        import re
        
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
        
        # Simple natural language processing
        query_lower = user_query.lower()
        
        # Look for common business intelligence patterns
        if any(word in query_lower for word in ["sales", "revenue", "total"]):
            # Find sales/revenue column
            sales_col = None
            for col in df.columns:
                if any(word in col.lower() for word in ["sales", "revenue", "amount", "total"]):
                    sales_col = col
                    break
            
            if sales_col:
                # Simple aggregation
                total_sales = df[sales_col].sum()
                avg_sales = df[sales_col].mean()
                
                summary_data = [
                    {"metric": "Total Sales", "value": total_sales},
                    {"metric": "Average Sales", "value": avg_sales},
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
            return {"error": "Failed to generate SQL query"}
        
        # Validate and optimize query
        validation_result = await self._validate_query(sql_query)
        if not validation_result["valid"]:
            return {"error": f"Invalid SQL query: {validation_result['errors']}"}
        
        optimized_query = await self._optimize_query(sql_query)
        
        result = {"generated_sql": sql_query, "optimized_sql": optimized_query, "validation": validation_result}
        
        # Execute query if requested
        if execution_mode in ["execute", "generate_and_execute"]:
            execution_result = await self._execute_query(optimized_query)
            result.update(execution_result)
            
            # Update state with results
            if execution_result.get("success"):
                state.update({
                    "sql_query": optimized_query,
                    "sql_results": execution_result.get("data"),
                    "sql_metadata": execution_result.get("metadata")
                })
        
        result.update({"agent": self.agent_name, "status": "completed"})
        return result
    
    async def _cache_schema_info(self):
        """Cache database schema information"""
        try:
            inspector = inspect(self.engine)
            
            # Get all table names
            tables = inspector.get_table_names()
            
            for table_name in tables:
                # Get column information
                columns = inspector.get_columns(table_name)
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                # Get indexes
                indexes = inspector.get_indexes(table_name)
                
                self.schema_cache[table_name] = {
                    "columns": columns,
                    "foreign_keys": foreign_keys,
                    "indexes": indexes
                }
            
            print(f"✅ Cached schema for {len(tables)} tables")
            
        except Exception as e:
            print(f"⚠️ Error caching schema: {str(e)}")
            self.schema_cache = {}
    
    async def _generate_sql_query(
        self, 
        query_intent: Dict[str, Any], 
        entities: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> Optional[str]:
        """Generate SQL query based on intent and entities"""
        
        # Extract key components
        metrics = entities.get("metrics", [])
        dimensions = entities.get("dimensions", [])
        filters = entities.get("filters", [])
        time_period = entities.get("time_period", {})
        aggregations = entities.get("aggregations", [])
        
        # Build SQL query using LLM
        query_context = self._build_query_context(metrics, dimensions, filters, time_period, schema)
        
        sql_prompt = f"""
        Generate a SQL query based on this business intelligence request:
        
        Intent: {query_intent.get('primary_intent', 'analyze')}
        Business Question: {query_intent.get('business_question', '')}
        
        Required Components:
        - Metrics: {metrics}
        - Dimensions: {dimensions}
        - Filters: {filters}
        - Time Period: {time_period}
        - Aggregations: {aggregations}
        
        Available Schema:
        {json.dumps(schema, indent=2)}
        
        Database Schema Information:
        {self._format_schema_context()}
        
        Please generate a valid SQL query that:
        1. Selects the requested metrics and dimensions
        2. Applies the specified filters
        3. Groups by the appropriate dimensions
        4. Includes time period restrictions
        5. Uses proper aggregation functions
        6. Follows SQL best practices
        
        Return only the SQL query without any explanation or markdown formatting.
        """
        
        sql_response = await self.call_ollama(
            prompt=sql_prompt,
            system_prompt="You are an expert SQL developer. Generate efficient, correct SQL queries based on business requirements.",
            temperature=0.1
        )
        
        # Clean and extract SQL
        sql_query = self._clean_sql_response(sql_response)
        
        # Fallback to template-based generation if LLM fails
        if not sql_query or not self._is_valid_sql_syntax(sql_query):
            sql_query = self._generate_template_sql(metrics, dimensions, filters, time_period, schema)
        
        return sql_query
    
    def _build_query_context(
        self, 
        metrics: List[str], 
        dimensions: List[str], 
        filters: List[Dict], 
        time_period: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context for SQL query generation"""
        
        # Map business terms to database columns
        column_mapping = self._map_business_terms_to_columns(metrics + dimensions, schema)
        
        return {
            "metrics": metrics,
            "dimensions": dimensions,
            "filters": filters,
            "time_period": time_period,
            "column_mapping": column_mapping,
            "available_tables": list(self.schema_cache.keys()),
            "relationships": self._identify_table_relationships()
        }
    
    def _map_business_terms_to_columns(self, terms: List[str], schema: Dict[str, Any]) -> Dict[str, str]:
        """Map business terms to actual database columns"""
        
        mapping = {}
        
        # Simple mapping based on column names in schema
        all_columns = []
        for table_info in self.schema_cache.values():
            for col in table_info.get("columns", []):
                all_columns.append(col["name"])
        
        for term in terms:
            term_lower = term.lower()
            
            # Direct match
            if term_lower in [col.lower() for col in all_columns]:
                mapping[term] = term_lower
                continue
            
            # Fuzzy matching
            for col in all_columns:
                if term_lower in col.lower() or col.lower() in term_lower:
                    mapping[term] = col
                    break
            
            # Business term mapping
            business_mappings = {
                "revenue": ["revenue", "sales", "amount", "total"],
                "customer": ["customer_id", "client_id", "user_id"],
                "product": ["product_id", "item_id", "sku"],
                "date": ["date", "created_at", "timestamp", "time"],
                "region": ["region", "location", "geography", "area"]
            }
            
            for key, possible_cols in business_mappings.items():
                if key in term_lower:
                    for possible in possible_cols:
                        matching_col = next((col for col in all_columns if possible in col.lower()), None)
                        if matching_col:
                            mapping[term] = matching_col
                            break
        
        return mapping
    
    def _identify_table_relationships(self) -> List[Dict[str, Any]]:
        """Identify relationships between tables based on foreign keys"""
        
        relationships = []
        
        for table_name, table_info in self.schema_cache.items():
            for fk in table_info.get("foreign_keys", []):
                relationships.append({
                    "from_table": table_name,
                    "from_column": fk["constrained_columns"][0],
                    "to_table": fk["referred_table"],
                    "to_column": fk["referred_columns"][0]
                })
        
        return relationships
    
    def _format_schema_context(self) -> str:
        """Format schema information for LLM context"""
        
        context_lines = []
        
        for table_name, table_info in self.schema_cache.items():
            context_lines.append(f"Table: {table_name}")
            
            # Add columns
            for col in table_info.get("columns", [])[:10]:  # Limit to first 10 columns
                col_type = col.get("type", "")
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                context_lines.append(f"  - {col['name']} ({col_type}, {nullable})")
            
            # Add foreign keys
            for fk in table_info.get("foreign_keys", []):
                context_lines.append(f"  FK: {fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}")
            
            context_lines.append("")  # Empty line between tables
        
        return "\n".join(context_lines)
    
    def _clean_sql_response(self, response: str) -> Optional[str]:
        """Clean and extract SQL from LLM response"""
        
        # Remove markdown code blocks
        response = re.sub(r"```sql\n", "", response)
        response = re.sub(r"```\n", "", response)
        response = re.sub(r"```", "", response)
        
        # Remove common prefixes
        response = re.sub(r"^(Here's the SQL query:|SQL Query:|Query:)", "", response, flags=re.IGNORECASE)
        
        # Extract SQL (look for SELECT statement)
        sql_match = re.search(r"(SELECT\s+.*?;?)\s*$", response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip()
            if not sql.endswith(";"):
                sql += ";"
            return sql
        
        # If no SELECT found, return cleaned response if it looks like SQL
        cleaned = response.strip()
        if cleaned.upper().startswith("SELECT"):
            if not cleaned.endswith(";"):
                cleaned += ";"
            return cleaned
        
        return None
    
    def _is_valid_sql_syntax(self, sql: str) -> bool:
        """Basic SQL syntax validation"""
        
        if not sql or not sql.strip():
            return False
        
        # Check for basic SQL structure
        sql_upper = sql.upper()
        
        # Must contain SELECT
        if "SELECT" not in sql_upper:
            return False
        
        # Check for balanced parentheses
        if sql.count("(") != sql.count(")"):
            return False
        
        # Check for dangerous operations (basic security)
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "UPDATE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True
    
    def _generate_template_sql(
        self, 
        metrics: List[str], 
        dimensions: List[str], 
        filters: List[Dict], 
        time_period: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> str:
        """Generate SQL using templates as fallback"""
        
        # Default template for simple aggregation
        if not self.schema_cache:
            return "SELECT COUNT(*) as total_records FROM uploads;"
        
        # Use first available table as default
        table_name = list(self.schema_cache.keys())[0]
        
        # Build SELECT clause
        select_parts = []
        
        # Add dimensions
        for dim in dimensions[:3]:  # Limit to 3 dimensions
            if dim.lower() in [col["name"].lower() for col in self.schema_cache[table_name]["columns"]]:
                select_parts.append(dim.lower())
        
        # Add metrics with aggregation
        for metric in metrics[:3]:  # Limit to 3 metrics
            if metric.lower() in ["count", "total"]:
                select_parts.append("COUNT(*) as total_count")
            else:
                # Try to find numeric column for aggregation
                numeric_cols = [
                    col["name"] for col in self.schema_cache[table_name]["columns"]
                    if str(col["type"]).lower() in ["integer", "float", "numeric", "decimal"]
                ]
                if numeric_cols:
                    select_parts.append(f"SUM({numeric_cols[0]}) as total_{metric.lower()}")
        
        if not select_parts:
            select_parts = ["COUNT(*) as total_records"]
        
        # Build SQL
        sql = f"SELECT {', '.join(select_parts)} FROM {table_name}"
        
        # Add WHERE clause for filters
        where_conditions = []
        
        # Add time period filter
        if time_period and time_period.get("start_date"):
            date_cols = [
                col["name"] for col in self.schema_cache[table_name]["columns"]
                if "date" in col["name"].lower() or "time" in col["name"].lower()
            ]
            if date_cols:
                where_conditions.append(f"{date_cols[0]} >= '{time_period['start_date']}'")
                if time_period.get("end_date"):
                    where_conditions.append(f"{date_cols[0]} <= '{time_period['end_date']}'")
        
        if where_conditions:
            sql += f" WHERE {' AND '.join(where_conditions)}"
        
        # Add GROUP BY for dimensions
        if len([part for part in select_parts if "(" not in part]) > 0:
            group_cols = [part for part in select_parts if "(" not in part and " as " not in part.lower()]
            if group_cols:
                sql += f" GROUP BY {', '.join(group_cols)}"
        
        sql += ";"
        return sql
    
    async def _validate_query(self, sql: str) -> Dict[str, Any]:
        """Validate SQL query"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "estimated_cost": "low"
        }
        
        # Syntax validation
        if not self._is_valid_sql_syntax(sql):
            validation_result["valid"] = False
            validation_result["errors"].append("Invalid SQL syntax")
            return validation_result
        
        # Security validation
        sql_upper = sql.upper()
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "UPDATE", "INSERT"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Dangerous keyword '{keyword}' not allowed")
        
        # Performance warnings
        if "SELECT *" in sql_upper:
            validation_result["warnings"].append("SELECT * may impact performance - consider selecting specific columns")
        
        if "ORDER BY" not in sql_upper and "LIMIT" not in sql_upper:
            validation_result["warnings"].append("Consider adding LIMIT clause for large result sets")
        
        # Try to explain query (if database supports it)
        try:
            with self.engine.connect() as conn:
                explain_sql = f"EXPLAIN {sql}"
                result = conn.execute(text(explain_sql))
                # Could analyze explain plan for cost estimation
                validation_result["estimated_cost"] = "medium"
        except Exception:
            # Explain not supported or query invalid
            pass
        
        return validation_result
    
    async def _optimize_query(self, sql: str) -> str:
        """Optimize SQL query"""
        
        optimized = sql
        
        # Add LIMIT if not present and no aggregation
        if "LIMIT" not in sql.upper() and "GROUP BY" not in sql.upper() and "COUNT" not in sql.upper():
            optimized = optimized.rstrip(";") + " LIMIT 1000;"
        
        # Replace SELECT * with specific columns (basic optimization)
        if "SELECT *" in sql.upper() and self.schema_cache:
            # Get first table columns
            first_table = list(self.schema_cache.keys())[0]
            columns = [col["name"] for col in self.schema_cache[first_table]["columns"][:10]]
            if columns:
                optimized = optimized.replace("SELECT *", f"SELECT {', '.join(columns)}")
        
        return optimized
    
    async def _execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # Convert to DataFrame
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                # Prepare metadata
                metadata = {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                    "execution_time": None  # Could add timing
                }
                
                return {
                    "success": True,
                    "data": df.to_dict("records"),
                    "metadata": metadata,
                    "summary": f"Query executed successfully. Retrieved {len(df)} rows."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "metadata": None,
                "summary": f"Query execution failed: {str(e)}"
            }
    
    def get_required_fields(self) -> List[str]:
        """Required fields for SQL agent"""
        return ["query_intent"]
