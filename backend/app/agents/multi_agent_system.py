"""
Multi-Agent System using LangGraph
Task 97: Set up multi-agent system using LangGraph
"""

from typing import Dict, List, Any, Optional, Callable, TypedDict, Annotated
import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput, AgentRegistry, get_agent_registry
from app.agents.base_agent import AgentCapability, AgentStatus

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Multi-agent workflow status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(str, Enum):
    """Roles in multi-agent workflow"""
    COORDINATOR = "coordinator"
    ANALYST = "analyst"
    RESEARCHER = "researcher"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"


class MultiAgentState(TypedDict):
    """State for multi-agent workflow"""
    messages: List[BaseMessage]
    current_agent: Optional[str]
    workflow_status: WorkflowStatus
    session_id: str
    user_query: str
    context: Dict[str, Any]
    results: Dict[str, Any]
    errors: List[str]
    execution_trace: List[Dict[str, Any]]
    final_response: Optional[str]


class AgentNode:
    """Node representing an agent in the workflow graph"""
    
    def __init__(self, agent_id: str, role: AgentRole, agent_type: str):
        self.agent_id = agent_id
        self.role = role
        self.agent_type = agent_type
        self.registry = get_agent_registry()
    
    async def execute(self, state: MultiAgentState) -> MultiAgentState:
        """Execute this agent node"""
        try:
            # Get the agent from registry
            agent = self.registry.get_agent(self.agent_id)
            if not agent:
                # Create agent if it doesn't exist
                await self.registry.create_agent(self.agent_type, self.agent_id)
                agent = self.registry.get_agent(self.agent_id)
            
            if not agent:
                raise RuntimeError(f"Failed to create agent {self.agent_id}")
            
            # Prepare input for the agent
            agent_input = AgentInput(
                message=state["user_query"],
                context=state["context"],
                session_id=state["session_id"],
                metadata={"role": self.role.value, "workflow_step": len(state["execution_trace"])}
            )
            
            # Execute the agent
            start_time = datetime.now(timezone.utc)
            output = await agent.execute(agent_input)
            end_time = datetime.now(timezone.utc)
            
            # Update state
            state["current_agent"] = self.agent_id
            state["results"][self.agent_id] = output.model_dump()
            
            # Add execution trace
            state["execution_trace"].append({
                "agent_id": self.agent_id,
                "role": self.role.value,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": (end_time - start_time).total_seconds(),
                "status": output.status.value,
                "response_length": len(output.response)
            })
            
            # Add AI message to conversation
            state["messages"].append(AIMessage(
                content=output.response,
                additional_kwargs={"agent_id": self.agent_id, "role": self.role.value}
            ))
            
            # Handle errors
            if output.status == AgentStatus.ERROR:
                state["errors"].append(f"Agent {self.agent_id} failed: {output.response}")
            
            return state
            
        except Exception as e:
            logger.error(f"Agent node {self.agent_id} execution failed: {e}")
            state["errors"].append(f"Agent {self.agent_id} execution failed: {str(e)}")
            state["workflow_status"] = WorkflowStatus.FAILED
            return state


class MultiAgentWorkflow:
    """Multi-agent workflow orchestrator using LangGraph"""
    
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.graph = StateGraph(MultiAgentState)
        self.checkpointer = MemorySaver()
        self.nodes: Dict[str, AgentNode] = {}
        self.compiled_graph = None
        
    def add_agent_node(self, node_name: str, agent_id: str, role: AgentRole, agent_type: str):
        """Add an agent node to the workflow"""
        node = AgentNode(agent_id, role, agent_type)
        self.nodes[node_name] = node
        self.graph.add_node(node_name, node.execute)
        
    def add_conditional_edge(
        self, 
        source: str, 
        condition: Callable[[MultiAgentState], str],
        condition_map: Dict[str, str]
    ):
        """Add a conditional edge to the workflow"""
        self.graph.add_conditional_edges(source, condition, condition_map)
        
    def add_edge(self, source: str, target: str):
        """Add a simple edge to the workflow"""
        self.graph.add_edge(source, target)
        
    def set_entry_point(self, node_name: str):
        """Set the entry point for the workflow"""
        self.graph.set_entry_point(node_name)
        
    def compile(self):
        """Compile the workflow graph"""
        self.compiled_graph = self.graph.compile(checkpointer=self.checkpointer)
        
    async def execute(
        self, 
        user_query: str, 
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the multi-agent workflow"""
        if not self.compiled_graph:
            raise RuntimeError("Workflow not compiled. Call compile() first.")
        
        if session_id is None:
            session_id = f"session_{datetime.now(timezone.utc).timestamp()}"
        
        # Initialize state
        initial_state: MultiAgentState = {
            "messages": [HumanMessage(content=user_query)],
            "current_agent": None,
            "workflow_status": WorkflowStatus.IN_PROGRESS,
            "session_id": session_id,
            "user_query": user_query,
            "context": context or {},
            "results": {},
            "errors": [],
            "execution_trace": [],
            "final_response": None
        }
        
        try:
            # Execute the workflow
            config = {"configurable": {"thread_id": session_id}}
            result = await self.compiled_graph.ainvoke(initial_state, config)
            
            # Determine final status
            if result["errors"]:
                result["workflow_status"] = WorkflowStatus.FAILED
            else:
                result["workflow_status"] = WorkflowStatus.COMPLETED
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                **initial_state,
                "workflow_status": WorkflowStatus.FAILED,
                "errors": [str(e)],
                "final_response": f"Workflow execution failed: {str(e)}"
            }


class DataAnalysisWorkflow(MultiAgentWorkflow):
    """Specialized workflow for data analysis tasks"""
    
    def __init__(self):
        super().__init__("data_analysis_workflow")
        self._setup_workflow()
    
    def _setup_workflow(self):
        """Setup the data analysis workflow structure"""
        
        # Add agent nodes
        self.add_agent_node("coordinator", "coord_agent", AgentRole.COORDINATOR, "conversation")
        self.add_agent_node("analyst", "analysis_agent", AgentRole.ANALYST, "data_analysis")
        self.add_agent_node("validator", "validator_agent", AgentRole.VALIDATOR, "conversation")
        self.add_agent_node("synthesizer", "synth_agent", AgentRole.SYNTHESIZER, "conversation")
        
        # Define workflow logic
        self.set_entry_point("coordinator")
        self.add_edge("coordinator", "analyst")
        self.add_edge("analyst", "validator")
        
        # Conditional logic for validation
        def validation_router(state: MultiAgentState) -> str:
            validator_result = state["results"].get("validator_agent", {})
            if "approve" in validator_result.get("response", "").lower():
                return "synthesizer"
            else:
                return "analyst"  # Re-analyze if validation fails
        
        self.add_conditional_edge(
            "validator",
            validation_router,
            {"synthesizer": "synthesizer", "analyst": "analyst"}
        )
        
        self.add_edge("synthesizer", END)
        
        # Compile the workflow
        self.compile()


class ConversationWorkflow(MultiAgentWorkflow):
    """Simple workflow for conversational interactions"""
    
    def __init__(self):
        super().__init__("conversation_workflow")
        self._setup_workflow()
    
    def _setup_workflow(self):
        """Setup the conversation workflow structure"""
        
        # Add single conversation agent
        self.add_agent_node("conversation", "conv_agent", AgentRole.COORDINATOR, "conversation")
        
        # Simple linear workflow
        self.set_entry_point("conversation")
        self.add_edge("conversation", END)
        
        # Compile the workflow
        self.compile()


class WorkflowRegistry:
    """Registry for managing different workflow types"""
    
    def __init__(self):
        self._workflows: Dict[str, MultiAgentWorkflow] = {}
        self._initialize_default_workflows()
    
    def _initialize_default_workflows(self):
        """Initialize default workflows"""
        self._workflows["data_analysis"] = DataAnalysisWorkflow()
        self._workflows["conversation"] = ConversationWorkflow()
    
    def get_workflow(self, workflow_type: str) -> Optional[MultiAgentWorkflow]:
        """Get a workflow by type"""
        return self._workflows.get(workflow_type)
    
    def register_workflow(self, name: str, workflow: MultiAgentWorkflow):
        """Register a custom workflow"""
        self._workflows[name] = workflow
    
    def list_workflows(self) -> List[str]:
        """List available workflow types"""
        return list(self._workflows.keys())
    
    async def execute_workflow(
        self, 
        workflow_type: str, 
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a workflow by type"""
        workflow = self.get_workflow(workflow_type)
        if not workflow:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        return await workflow.execute(user_query, context, session_id)


# Global workflow registry
_workflow_registry = WorkflowRegistry()


def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry"""
    return _workflow_registry


async def execute_multi_agent_query(
    query: str, 
    workflow_type: str = "conversation",
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """High-level function to execute multi-agent queries"""
    registry = get_workflow_registry()
    return await registry.execute_workflow(workflow_type, query, context, session_id)
