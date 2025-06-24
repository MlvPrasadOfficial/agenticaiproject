# Query Agent - Natural Language Understanding and Intent Parsing

from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent


class QueryAgent(BaseAgent):
    """Natural language understanding and intent parsing specialist"""
    
    def __init__(self):
        super().__init__("Query Agent")
        self.entity_patterns = {
            "metrics": [
                r"(?i)revenue|sales|profit|cost|margin|growth|performance|kpi",
                r"(?i)count|sum|total|average|mean|median|max|min|std|variance"
            ],
            "dimensions": [
                r"(?i)region|country|state|city|location|geography",
                r"(?i)product|category|department|division|segment",
                r"(?i)customer|client|user|account|demographic",
                r"(?i)time|date|month|quarter|year|period|seasonal"
            ],
            "time_ranges": [
                r"(?i)last\s+(\d+)\s+(day|week|month|quarter|year)s?",
                r"(?i)this\s+(week|month|quarter|year)",
                r"(?i)ytd|year\s+to\s+date|mtd|month\s+to\s+date",
                r"(?i)q[1-4]|quarter\s+[1-4]|\d{4}"
            ],
            "filters": [
                r"(?i)where|filter|only|exclude|include|not",
                r"(?i)greater\s+than|less\s+than|equal\s+to|between",
                r"(?i)contains|starts\s+with|ends\s+with|like"
            ],
            "aggregations": [
                r"(?i)group\s+by|grouped\s+by|by\s+\w+",
                r"(?i)breakdown|split|segment|categorize",
                r"(?i)summarize|aggregate|rollup"
            ]
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured information from user query"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Query Agent"}
        
        user_query = state.get("user_query", "")
        data_schema = state.get("data_schema", {})
        
        # Extract entities using pattern matching
        pattern_entities = self._extract_entities_by_patterns(user_query)
        
        # Use LLM for advanced entity extraction
        llm_entities = await self._extract_entities_with_llm(user_query, data_schema)
        
        # Combine and validate entities
        merged_entities = self._merge_entity_extractions(pattern_entities, llm_entities)
        
        # Generate structured query intent
        query_intent = await self._generate_query_intent(user_query, merged_entities)
        
        # Identify ambiguities and generate clarifying questions
        clarifications = self._identify_ambiguities(user_query, merged_entities, data_schema)
        
        # Update state with extracted information
        state.update({
            "extracted_entities": merged_entities,
            "query_intent": query_intent,
            "clarifications": clarifications,
            "confidence_score": query_intent.get("confidence", 0.8)
        })
        
        return {
            "entities": merged_entities,
            "intent": query_intent,
            "clarifications": clarifications,
            "confidence": query_intent.get("confidence", 0.8),
            "agent": self.agent_name,
            "status": "completed"
        }
    
    def _extract_entities_by_patterns(self, query: str) -> Dict[str, List[str]]:
        """Extract entities using regex patterns"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            found_entities = []
            for pattern in patterns:
                matches = re.findall(pattern, query)
                if matches:
                    found_entities.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
            
            if found_entities:
                entities[entity_type] = list(set(found_entities))  # Remove duplicates
        
        return entities
    
    async def _extract_entities_with_llm(self, query: str, schema: Dict) -> Dict[str, Any]:
        """Use LLM for advanced entity extraction"""
        
        schema_context = ""
        if schema:
            schema_context = f"Available data schema: {json.dumps(schema, indent=2)}"
        
        extraction_prompt = f"""
        Extract structured information from this business query:
        
        Query: "{query}"
        {schema_context}
        
        Please identify and extract:
        1. Business metrics requested
        2. Dimensions for grouping/filtering
        3. Time periods mentioned
        4. Filter conditions
        5. Aggregation requirements
        6. Comparison requests
        7. Calculation needs
        
        Respond in JSON format:
        {{
            "metrics": ["metric1", "metric2"],
            "dimensions": ["dim1", "dim2"],
            "time_period": {{
                "type": "relative/absolute",
                "value": "...",
                "start_date": "YYYY-MM-DD or null",
                "end_date": "YYYY-MM-DD or null"
            }},
            "filters": [
                {{
                    "column": "...",
                    "operator": "=|>|<|>=|<=|!=|LIKE|IN",
                    "value": "..."
                }}
            ],
            "aggregations": ["GROUP BY column", "SUM(metric)"],
            "comparisons": ["vs last year", "vs target"],
            "calculations": ["growth rate", "percentage change"],
            "output_format": "table|chart|summary"
        }}
        """
        
        llm_response = await self.call_ollama(
            prompt=extraction_prompt,
            system_prompt="You are an expert at extracting structured information from business queries. Respond only with valid JSON.",
            temperature=0.2
        )
        
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            # Fallback to empty structure
            return {
                "metrics": [],
                "dimensions": [],
                "time_period": {"type": "relative", "value": "current"},
                "filters": [],
                "aggregations": [],
                "comparisons": [],
                "calculations": [],
                "output_format": "table"
            }
    
    def _merge_entity_extractions(self, pattern_entities: Dict, llm_entities: Dict) -> Dict[str, Any]:
        """Merge pattern-based and LLM-based entity extractions"""
        
        merged = {
            "metrics": [],
            "dimensions": [],
            "time_period": llm_entities.get("time_period", {"type": "current"}),
            "filters": llm_entities.get("filters", []),
            "aggregations": [],
            "comparisons": llm_entities.get("comparisons", []),
            "calculations": llm_entities.get("calculations", []),
            "output_format": llm_entities.get("output_format", "table")
        }
        
        # Merge metrics
        merged["metrics"].extend(pattern_entities.get("metrics", []))
        merged["metrics"].extend(llm_entities.get("metrics", []))
        merged["metrics"] = list(set(merged["metrics"]))  # Remove duplicates
        
        # Merge dimensions
        merged["dimensions"].extend(pattern_entities.get("dimensions", []))
        merged["dimensions"].extend(llm_entities.get("dimensions", []))
        merged["dimensions"] = list(set(merged["dimensions"]))
        
        # Merge aggregations
        merged["aggregations"].extend(pattern_entities.get("aggregations", []))
        merged["aggregations"].extend(llm_entities.get("aggregations", []))
        merged["aggregations"] = list(set(merged["aggregations"]))
        
        return merged
    
    async def _generate_query_intent(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured query intent"""
        
        intent_prompt = f"""
        Based on this query and extracted entities, determine the user's intent:
        
        Query: "{query}"
        Entities: {json.dumps(entities, indent=2)}
        
        Determine:
        1. Primary intent (explore, analyze, compare, forecast, report)
        2. Secondary intents
        3. Business question being asked
        4. Expected deliverable
        5. Urgency level
        6. Confidence in understanding (0.0-1.0)
        
        Respond in JSON:
        {{
            "primary_intent": "...",
            "secondary_intents": ["..."],
            "business_question": "...",
            "expected_deliverable": "...",
            "urgency": "low|medium|high",
            "confidence": 0.0
        }}
        """
        
        llm_response = await self.call_ollama(
            prompt=intent_prompt,
            system_prompt="You are an expert business analyst. Understand user intent precisely.",
            temperature=0.3
        )
        
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            return {
                "primary_intent": "analyze",
                "secondary_intents": [],
                "business_question": query,
                "expected_deliverable": "insights",
                "urgency": "medium",
                "confidence": 0.6
            }
    
    def _identify_ambiguities(self, query: str, entities: Dict, schema: Dict) -> List[Dict[str, Any]]:
        """Identify ambiguities that need clarification"""
        
        clarifications = []
        
        # Check for ambiguous time references
        time_period = entities.get("time_period", {})
        if not time_period.get("start_date") and not time_period.get("end_date"):
            if any(word in query.lower() for word in ["recent", "latest", "current"]):
                clarifications.append({
                    "type": "time_period",
                    "question": "What specific time period would you like to analyze?",
                    "suggestions": ["Last 30 days", "This quarter", "Year to date", "Last 12 months"]
                })
        
        # Check for ambiguous metrics
        metrics = entities.get("metrics", [])
        if not metrics:
            clarifications.append({
                "type": "metrics",
                "question": "What specific metrics would you like to analyze?",
                "suggestions": ["Revenue", "Sales volume", "Profit margin", "Customer count"]
            })
        
        # Check for ambiguous dimensions
        dimensions = entities.get("dimensions", [])
        if "product" in query.lower() and not any("product" in dim.lower() for dim in dimensions):
            clarifications.append({
                "type": "dimension",
                "question": "Which product dimension would you like to group by?",
                "suggestions": ["Product category", "Product name", "Product line", "SKU"]
            })
        
        # Check for missing aggregation when multiple records expected
        if dimensions and not entities.get("aggregations"):
            clarifications.append({
                "type": "aggregation",
                "question": "How would you like to aggregate the data?",
                "suggestions": ["Sum", "Average", "Count", "Maximum", "Minimum"]
            })
        
        return clarifications
    
    def get_required_fields(self) -> List[str]:
        """Required fields for query agent"""
        return ["user_query"]
