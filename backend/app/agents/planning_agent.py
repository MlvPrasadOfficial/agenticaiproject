# Planning Agent - Central Orchestrator

from typing import Dict, Any, List
import json
import re

from app.agents.base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    """Central orchestrator that analyzes queries and plans agent execution"""
    
    def __init__(self):
        super().__init__("Planning Agent")
        self.query_patterns = {
            "data_exploration": [
                r"(?i)profile|explore|analyze data|data quality|missing values|distribution",
                r"(?i)dataset|columns|rows|data types|statistics"
            ],
            "visualization": [
                r"(?i)chart|graph|plot|visualize|dashboard|show me",
                r"(?i)bar chart|line chart|scatter|histogram|trends"
            ],
            "insight_generation": [
                r"(?i)insights|patterns|trends|anomalies|forecast|predict",
                r"(?i)what|why|how|correlation|relationship|impact"
            ],
            "sql_query": [
                r"(?i)select|filter|group by|aggregate|sum|count|average",
                r"(?i)join|where|having|order by"
            ],
            "report_generation": [
                r"(?i)report|summary|executive|findings|recommendations",
                r"(?i)document|presentation|export|download"
            ]
        }
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user query and create execution plan"""
        
        if not self.validate_input(state):
            return {"error": "Invalid input for Planning Agent"}
        
        user_query = state.get("user_query", "")
        file_context = state.get("file_context", [])
        
        # Analyze query type and complexity
        query_analysis = await self.analyze_query(user_query)
        
        # Determine agent execution plan
        execution_plan = await self.create_execution_plan(query_analysis, file_context)
        
        # Update state with planning results
        state.update({
            "query_type": query_analysis["primary_type"],
            "complexity_score": query_analysis["complexity_score"],
            "execution_plan": execution_plan,
            "required_agents": execution_plan["agents"],
            "estimated_time": execution_plan["estimated_time"]
        })
        
        return {
            "query_analysis": query_analysis,
            "execution_plan": execution_plan,
            "routing_decision": query_analysis["primary_type"],
            "agent": self.agent_name,
            "status": "completed"
        }
    
    async def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """Analyze user query to determine type and complexity"""
        
        # Pattern matching for query types
        detected_types = []
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_query):
                    detected_types.append(query_type)
                    break
        
        # LLM-based analysis for more nuanced understanding
        analysis_prompt = f"""
        Analyze this business intelligence query and provide structured analysis:
        
        Query: "{user_query}"
        
        Please provide:
        1. Primary intent (data_exploration, visualization, insight_generation, sql_query, report_generation)
        2. Complexity score (0.0-1.0)
        3. Required data types
        4. Expected output format
        5. Business context
        
        Respond in JSON format:
        {{
            "primary_intent": "...",
            "complexity_score": 0.0,
            "required_data": ["..."],
            "output_format": "...",
            "business_context": "...",
            "specific_requirements": ["..."]
        }}
        """
        
        llm_response = await self.call_ollama(
            prompt=analysis_prompt,
            system_prompt="You are an expert business intelligence analyst. Analyze queries precisely and respond only with valid JSON.",
            temperature=0.3
        )
        
        try:
            llm_analysis = json.loads(llm_response)
        except:
            # Fallback to pattern-based analysis
            llm_analysis = {
                "primary_intent": detected_types[0] if detected_types else "insight_generation",
                "complexity_score": 0.5,
                "required_data": ["structured"],
                "output_format": "mixed",
                "business_context": "general",
                "specific_requirements": []
            }
        
        # Combine pattern matching and LLM analysis
        primary_type = llm_analysis.get("primary_intent", detected_types[0] if detected_types else "insight_generation")
        
        # Calculate complexity score
        complexity_factors = {
            "query_length": len(user_query) / 500.0,  # Normalize by typical query length
            "multiple_types": len(detected_types) / 5.0,  # Multiple intent types
            "specific_terms": len([w for w in user_query.split() if w.lower() in [
                "correlation", "regression", "prediction", "forecast", "anomaly", "pattern",
                "statistical", "significance", "confidence", "distribution"
            ]]) / 10.0
        }
        
        complexity_score = min(
            sum(complexity_factors.values()) / len(complexity_factors) + 
            llm_analysis.get("complexity_score", 0.5),
            1.0
        ) / 2.0
        
        return {
            "primary_type": primary_type,
            "detected_types": detected_types,
            "complexity_score": complexity_score,
            "llm_analysis": llm_analysis,
            "query_metadata": {
                "length": len(user_query),
                "word_count": len(user_query.split()),
                "has_numbers": bool(re.search(r'\d+', user_query)),
                "has_time_refs": bool(re.search(r'(?i)last|this|next|quarter|month|year|day', user_query))
            }
        }
    
    async def create_execution_plan(self, query_analysis: Dict[str, Any], file_context: List[str]) -> Dict[str, Any]:
        """Create detailed execution plan for agents"""
        
        primary_type = query_analysis["primary_type"]
        complexity = query_analysis["complexity_score"]
        
        # Base agent requirements by query type
        agent_plans = {
            "data_exploration": {
                "agents": ["data", "cleaner"],
                "parallel": False,
                "estimated_time": 30
            },
            "visualization": {
                "agents": ["query", "retrieval", "chart"],
                "parallel": False,
                "estimated_time": 45
            },
            "insight_generation": {
                "agents": ["query", "retrieval", "sql", "insight"],
                "parallel": False,
                "estimated_time": 60
            },
            "sql_query": {
                "agents": ["query", "sql"],
                "parallel": False,
                "estimated_time": 20
            },
            "report_generation": {
                "agents": ["query", "retrieval", "sql", "insight", "chart", "narrative", "report"],
                "parallel": False,
                "estimated_time": 120
            }
        }
        
        base_plan = agent_plans.get(primary_type, agent_plans["insight_generation"])
        
        # Modify plan based on complexity
        if complexity > 0.7:
            # Add quality control for complex queries
            if "critique" not in base_plan["agents"]:
                base_plan["agents"].extend(["critique", "debate"])
            base_plan["estimated_time"] *= 1.5
        
        # Add file context processing if needed
        if file_context:
            if "data" not in base_plan["agents"]:
                base_plan["agents"].insert(0, "data")
            if "cleaner" not in base_plan["agents"]:
                base_plan["agents"].insert(1, "cleaner")
        
        # Determine parallel execution opportunities
        parallel_groups = []
        if complexity > 0.5 and len(base_plan["agents"]) > 3:
            # Group agents that can run in parallel
            if "sql" in base_plan["agents"] and "chart" in base_plan["agents"]:
                parallel_groups.append(["sql", "chart"])
        
        return {
            "agents": base_plan["agents"],
            "execution_order": self._determine_execution_order(base_plan["agents"]),
            "parallel_groups": parallel_groups,
            "estimated_time": int(base_plan["estimated_time"]),
            "priority": "high" if complexity > 0.7 else "medium",
            "requires_human_review": complexity > 0.8,
            "fallback_strategy": self._create_fallback_strategy(primary_type)
        }
    
    def _determine_execution_order(self, agents: List[str]) -> List[str]:
        """Determine optimal execution order for agents"""
        
        # Define dependencies
        dependencies = {
            "query": [],
            "data": [],
            "cleaner": ["data"],
            "retrieval": ["query"],
            "sql": ["query", "retrieval"],
            "insight": ["sql", "cleaner"],
            "chart": ["insight"],
            "critique": ["sql", "insight", "chart"],
            "debate": ["critique"],
            "narrative": ["insight", "chart"],
            "report": ["narrative"]
        }
        
        # Topological sort based on dependencies
        ordered = []
        remaining = agents.copy()
        
        while remaining:
            for agent in remaining[:]:
                deps = dependencies.get(agent, [])
                if all(dep in ordered or dep not in agents for dep in deps):
                    ordered.append(agent)
                    remaining.remove(agent)
                    break
            else:
                # Fallback: add remaining agents in original order
                ordered.extend(remaining)
                break
        
        return ordered
    
    def _create_fallback_strategy(self, primary_type: str) -> Dict[str, Any]:
        """Create fallback strategy for error recovery"""
        
        fallback_strategies = {
            "data_exploration": {
                "simplified_agents": ["data"],
                "fallback_output": "basic_summary"
            },
            "visualization": {
                "simplified_agents": ["chart"],
                "fallback_output": "simple_chart"
            },
            "insight_generation": {
                "simplified_agents": ["query", "insight"],
                "fallback_output": "basic_insights"
            },
            "report_generation": {
                "simplified_agents": ["narrative"],
                "fallback_output": "text_summary"
            }
        }
        
        return fallback_strategies.get(primary_type, {
            "simplified_agents": ["query"],
            "fallback_output": "text_response"
        })
    
    def get_required_fields(self) -> List[str]:
        """Required fields for planning agent"""
        return ["user_query"]
