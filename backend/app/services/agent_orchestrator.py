# Agent Orchestrator - Central LangGraph Workflow Management

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, TypedDict
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import AsyncCallbackHandler

from app.agents.planning_agent import PlanningAgent
from app.agents.query_agent import QueryAgent
from app.agents.data_agent import DataAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.sql_agent import SQLAgent
from app.agents.insight_agent import InsightAgent
from app.agents.chart_agent import ChartAgent
from app.agents.critique_agent import CritiqueAgent
from app.agents.debate_agent import DebateAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.report_agent import ReportAgent

from app.core.config import settings


class AgentState(TypedDict):
    """State object for agent workflow"""
    session_id: str
    user_query: str
    file_context: Optional[Dict[str, Any]]
    query_type: str
    complexity_score: float
    retrieved_context: List[Dict[str, Any]]
    data_profile: Dict[str, Any]
    cleaned_data: Optional[Dict[str, Any]]
    sql_results: Optional[Dict[str, Any]]
    insights: Dict[str, Any]
    chart_specs: Dict[str, Any]
    critique_feedback: Dict[str, Any]
    debate_consensus: Dict[str, Any]
    business_narrative: Dict[str, Any]
    quality_score: float
    error_flags: List[str]
    narrative: str
    final_report: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]
    agent_outputs: Dict[str, Any]


class AgentOrchestrator:
    """Central orchestrator for multi-agent workflow using LangGraph"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.graph = self._build_langgraph()
        self.stream_queue = None
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents"""
        return {
            "planning": PlanningAgent(),
            "query": QueryAgent(),
            "data": DataAgent(),
            "retrieval": RetrievalAgent(),
            "sql": SQLAgent(),
            "insight": InsightAgent(),
            "chart": ChartAgent(),
            "critique": CritiqueAgent(),
            "debate": DebateAgent(),
            "narrative_gen": NarrativeAgent(),
            "report": ReportAgent()
        }
    
    def _build_langgraph(self) -> StateGraph:
        """Build LangGraph workflow"""
        graph = StateGraph(AgentState)
        
        # Add nodes for each agent
        for agent_name, agent in self.agents.items():
            graph.add_node(agent_name, self._create_agent_node(agent_name, agent))
          # Define workflow edges
        self._define_workflow_edges(graph)
        
        return graph.compile()
    
    def _create_agent_node(self, agent_name: str, agent):
        """Create a graph node for an agent"""
        async def agent_node(state: AgentState) -> AgentState:
            try:
                print(f"🤖 Executing {agent_name} agent...")
                
                # Stream update
                if self.stream_queue:
                    await self.stream_queue.put({
                        "type": "agent_start",
                        "agent_name": agent_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Execute agent with timeout
                start_time = time.time()
                try:
                    print(f"🤖 {agent_name}: Starting execution with timeout protection")
                    # Use 20 second timeout for each agent
                    result = await asyncio.wait_for(agent.execute(state), timeout=20)
                    print(f"🤖 {agent_name}: Execution completed successfully")
                except asyncio.TimeoutError:
                    print(f"❌ {agent_name}: Execution timed out after 20 seconds")
                    # Provide fallback response for timeout
                    result = {
                        "error": f"{agent_name} execution timed out after 20 seconds",
                        "status": "timeout",
                        "agent": agent_name
                    }
                
                execution_time = time.time() - start_time
                  # Update state with agent results
                state["agent_outputs"][agent_name] = result
                
                # Merge agent results back into state for next agents
                if isinstance(result, dict) and "status" in result and result["status"] == "completed":
                    # Remove status and agent info to avoid conflicts
                    clean_result = {}
                    for k, v in result.items():
                        if k not in ["status", "agent", "error"]:
                            clean_result[k] = v
                    
                    state.update(clean_result)
                    print(f"🔍 Updated state with {agent_name} results: {list(clean_result.keys())}")
                
                state["execution_trace"].append({
                    "agent": agent_name,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Stream completion
                if self.stream_queue:
                    await self.stream_queue.put({
                        "type": "agent_complete",
                        "agent_name": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "execution_time": execution_time,
                        "result_summary": self._get_result_summary(result)
                    })
                
                return state
                
            except Exception as e:
                error_msg = f"Error in {agent_name} agent: {str(e)}"
                print(f"❌ {error_msg}")
                
                state["error_flags"].append(error_msg)
                
                if self.stream_queue:
                    await self.stream_queue.put({
                        "type": "agent_error",
                        "agent_name": agent_name,
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
                    })
                
                return state
        
        return agent_node
    def _define_workflow_edges(self, graph: StateGraph):
        """Define the agent workflow edges"""
        
        # Entry point - start with planning
        graph.add_edge(START, "planning")
        
        # Planning agent routes to appropriate agents based on query type
        graph.add_conditional_edges(
            "planning",
            self._route_from_planning,
            {
                "insight_generation": "query", 
                "visualization": "chart",
                "complex_analysis": "query"
            }
        )
        
        # Query processing flow - include data analysis and retrieval
        graph.add_edge("query", "data")
        graph.add_edge("data", "retrieval")
        graph.add_edge("retrieval", "sql")
        
        # Analysis convergence
        graph.add_edge("sql", "insight")
        graph.add_edge("insight", "chart")
          # Quality assurance and narrative generation pipeline
        graph.add_edge("chart", "critique")
        graph.add_edge("critique", "debate")
        graph.add_edge("debate", "narrative_gen")
        
        # Final output generation
        graph.add_edge("narrative_gen", "report")
        graph.add_edge("report", END)
        
    def _route_from_planning(self, state: AgentState) -> str:
        """Route based on planning agent's decision"""
        query_type = state.get("query_type", "").lower()
        complexity = state.get("complexity_score", 0.0)
        
        print(f"🔍 PLANNING ROUTER DEBUG: query_type = {query_type}, complexity = {complexity}")
        
        # Skip data exploration for now since data agent is disabled
        if complexity > 0.7:
            route = "complex_analysis"
        elif "chart" in query_type or "visualize" in query_type:
            route = "visualization"
        else:
            route = "insight_generation"
            
        print(f"🔍 PLANNING ROUTER DEBUG: Routing to {route}")
        return route
    
    def _quality_control_router(self, state: AgentState) -> str:
        """Route based on quality control results"""
        quality_score = state.get("quality_score", 0.0)
        error_flags = state.get("error_flags", [])
        complexity = state.get("complexity_score", 0.0)
        
        if error_flags or quality_score < 0.5:
            return "retry"
        elif complexity > 0.8 and quality_score > 0.7:
            return "pass"  # Go to debate for complex queries
        else:
            return "continue"  # Skip debate for simple queries
    
    def _get_result_summary(self, result: Dict[str, Any]) -> str:
        """Generate a summary of agent result for streaming"""
        if not result:
            return "No output generated"
        
        # Customize based on result structure
        if "insights" in result:
            return f"Generated {len(result['insights'])} insights"
        elif "charts" in result:
            return f"Created {len(result['charts'])} visualizations"
        elif "narrative" in result:
            return "Generated business narrative"
        else:
            return "Processing completed"
    async def process_query(
        self,
        session_id: str,
        user_query: str,
        file_context: Optional[Dict[str, Any]] = None,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user query through agent workflow"""
        
        print("🔍 ORCHESTRATOR DEBUG: Starting query processing")
        print(f"🔍 ORCHESTRATOR DEBUG: user_query = {user_query}")
        print(f"🔍 ORCHESTRATOR DEBUG: file_context = {file_context}")
        print(f"🔍 ORCHESTRATOR DEBUG: query_type = {query_type}")
          # Load file data if file_context contains file_id
        file_data = None
        file_path = None
        if file_context and isinstance(file_context, dict) and "file_id" in file_context:
            file_id = file_context["file_id"]
            # Construct file path from uploads directory
            import os
            import glob
            upload_dir = "uploads"  # Relative to backend working directory
            # Find the uploaded file with this file_id
            pattern = os.path.join(upload_dir, f"{file_id}_*")
            matching_files = glob.glob(pattern)
            if matching_files:
                file_path = matching_files[0]
                print(f"🔍 ORCHESTRATOR DEBUG: Found file at {file_path}")
                
                # Load the data using pandas
                try:
                    import pandas as pd
                    if file_path.endswith('.csv'):
                        file_data = pd.read_csv(file_path)
                        print(f"🔍 ORCHESTRATOR DEBUG: Loaded CSV with {len(file_data)} rows, {len(file_data.columns)} columns")
                        print(f"🔍 ORCHESTRATOR DEBUG: Columns: {list(file_data.columns)}")
                        # Convert DataFrame to dict for JSON serialization
                        file_data_dict = {
                            "columns": list(file_data.columns),
                            "data": file_data.to_dict('records'),
                            "shape": file_data.shape,
                            "dtypes": file_data.dtypes.to_dict()
                        }
                        file_data = file_data_dict
                    else:
                        print(f"🔍 ORCHESTRATOR DEBUG: Unsupported file type for {file_path}")
                except Exception as e:
                    print(f"❌ ORCHESTRATOR ERROR: Failed to load file data: {e}")
            else:
                print(f"🔍 ORCHESTRATOR DEBUG: No file found for file_id: {file_id} in pattern: {pattern}")
                # Debug: list all files in uploads directory
                try:
                    all_files = os.listdir(upload_dir)
                    print(f"🔍 ORCHESTRATOR DEBUG: Files in upload dir: {all_files}")
                except Exception as e:
                    print(f"🔍 ORCHESTRATOR DEBUG: Error listing upload dir: {e}")
          # Initialize state
        state = {
            "session_id": session_id,
            "user_query": user_query,
            "file_context": file_context or {},
            "file_path": file_path,
            "file_data": file_data,
            "query_type": query_type or "general",
            "complexity_score": 0.0,
            "retrieved_context": [],
            "data_profile": {},
            "cleaned_data": None,
            "sql_results": None,
            "insights": {},
            "chart_specs": {},
            "critique_feedback": {},
            "debate_consensus": {},
            "business_narrative": {},
            "quality_score": 0.0,
            "error_flags": [],
            "narrative": "",
            "final_report": {},
            "execution_trace": [],
            "agent_outputs": {}
        }
        
        print(f"🔍 ORCHESTRATOR DEBUG: Initial state keys = {list(state.keys())}")
        print(f"🔍 ORCHESTRATOR DEBUG: State = {state}")
        
        try:            # Execute workflow
            start_time = time.time()
            print("🔍 ORCHESTRATOR DEBUG: About to call graph.ainvoke")
            final_state = await self.graph.ainvoke(state)
            execution_time = time.time() - start_time
            
            print("🔍 ORCHESTRATOR DEBUG: Graph execution completed")
            print(f"🔍 ORCHESTRATOR DEBUG: Final state keys = {list(final_state.keys())}")
            print(f"🔍 ORCHESTRATOR DEBUG: Final state = {final_state}")
              # Compile final result
            result = {
                "session_id": session_id,
                "insights": final_state.get("insights", {}),
                "charts": final_state.get("chart_specs", {}),
                "critique_feedback": final_state.get("critique_feedback", {}),
                "debate_consensus": final_state.get("debate_consensus", {}),
                "business_narrative": final_state.get("business_narrative", {}),
                "narrative": final_state.get("narrative", ""),
                "report": final_state.get("final_report", {}),
                "execution_time": execution_time,
                "agent_trace": final_state.get("execution_trace", []),
                "quality_score": final_state.get("quality_score", 0.0),
                "errors": final_state.get("error_flags", [])
            }
            
            print(f"🔍 ORCHESTRATOR DEBUG: Compiled result = {result}")
            return result
            
        except Exception as e:
            print(f"❌ ORCHESTRATOR ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "session_id": session_id,
                "error": str(e),
                "execution_time": 0,
                "status": "failed"
            }
    
    async def stream_query_processing(
        self,
        session_id: str,
        user_query: str,
        file_context: Optional[List[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream query processing with real-time updates"""
        
        # Initialize stream queue
        self.stream_queue = asyncio.Queue()
        
        # Start processing task
        process_task = asyncio.create_task(
            self.process_query(session_id, user_query, file_context)
        )
        
        try:
            # Stream updates until processing is complete
            while not process_task.done():
                try:
                    # Wait for update with timeout
                    update = await asyncio.wait_for(
                        self.stream_queue.get(),
                        timeout=1.0
                    )
                    yield update
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Get final result
            final_result = await process_task
            yield {
                "type": "final_result",
                "result": final_result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:            yield {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self.stream_queue = None
    
    async def trigger_upload_agents(
        self,
        file_id: str,
        file_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger Data Agent and Retrieval Agent for file upload"""
        state = AgentState()
        state.update({
            "session_id": f"upload_{file_id}",
            "file_data": file_data,
            "file_path": file_data.get("file_path"),  # Extract file_path from processor result
            "query_type": "data_exploration"
        })
        
        try:
            print(f"🔍 Processing file upload for file_id: {file_id}")
            
            # Execute Data Agent
            print("🔍 Executing Data Agent...")
            data_result = await self.agents["data"].execute(state)
            state["data_profile"] = data_result
            print(f"✅ Data Agent completed: {data_result.get('status', 'unknown')}")
              # Execute Retrieval Agent to index the data
            print("🔍 Executing Retrieval Agent for indexing...")
            retrieval_result = await self.agents["retrieval"].index_file_data(state)
            state["vector_storage"] = retrieval_result
            print(f"✅ Retrieval Agent completed: {retrieval_result.get('status', 'unknown')}")
            print(f"📊 Vectors added: {retrieval_result.get('vectors_added', 0)}")
            
            # Log vector count details if available
            if 'vectors_before' in retrieval_result and 'vectors_after' in retrieval_result:
                vectors_before = retrieval_result['vectors_before']
                vectors_after = retrieval_result['vectors_after']
                actual_added = retrieval_result.get('actual_vectors_added', vectors_after - vectors_before)
                print(f"📊 Pinecone Vector Count - Before: {vectors_before}, After: {vectors_after}, Added: {actual_added}")
            
            return {
                "file_id": file_id,
                "data_profile": data_result,
                "vector_storage": retrieval_result,
                "status": "completed"
            }
        
        except Exception as e:
            print(f"❌ Error in upload processing: {str(e)}")
            return {
                "file_id": file_id,
                "error": str(e),
                "status": "failed"
            }
