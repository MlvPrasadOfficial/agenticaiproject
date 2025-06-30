"""AI agents and LangChain integration"""

# Import all agent modules for easy access
from .base_agent import ConversationAgent, DataAnalysisAgent, AgentFactory, AgentRegistry
from .multi_agent_system import MultiAgentOrchestrator, WorkflowRegistry
from .communication import CommunicationBus, AgentCommunicator
from .memory import MemoryManager, ConversationMemory, SemanticMemory, WorkingMemory
from .state_management import AgentStateManager, StateMachine
from .io_models import AgentInputV2, AgentOutputV2, AgentMessage, ConversationRequest, ConversationResponse
from .execution_framework import ExecutionEngine, ExecutionContext
from .error_handling import (
    AgentError, ValidationError, TimeoutError, RateLimitError, LLMError,
    ErrorHandler, RetryManager, get_error_handler, get_retry_manager,
    with_retry, with_circuit_breaker, handle_errors
)
from .performance_monitoring import (
    PerformanceMonitor, get_performance_monitor, monitor_performance,
    start_all_monitoring, stop_all_monitoring, get_system_performance
)
from .conversation_memory import (
    ConversationMemoryManager, ConversationMessage, ConversationContext,
    get_conversation_manager, create_user_message, create_assistant_message
)
from .capability_assessment import (
    CapabilityManager, Capability, CapabilityAssessment, CapabilityType, CapabilityLevel,
    get_capability_manager, assess_agent_capabilities, get_agent_capability_summary,
    update_agent_capability_metric
)

__all__ = [
    # Base agents
    'ConversationAgent', 'DataAnalysisAgent', 'AgentFactory', 'AgentRegistry',
    
    # Multi-agent system
    'MultiAgentOrchestrator', 'WorkflowRegistry',
    
    # Communication
    'CommunicationBus', 'AgentCommunicator',
    
    # Memory
    'MemoryManager', 'ConversationMemory', 'SemanticMemory', 'WorkingMemory',
    
    # State management
    'AgentStateManager', 'StateMachine',
    
    # I/O models
    'AgentInputV2', 'AgentOutputV2', 'AgentMessage', 'ConversationRequest', 'ConversationResponse',
    
    # Execution framework
    'ExecutionEngine', 'ExecutionContext',
    
    # Error handling
    'AgentError', 'ValidationError', 'TimeoutError', 'RateLimitError', 'LLMError',
    'ErrorHandler', 'RetryManager', 'get_error_handler', 'get_retry_manager',
    'with_retry', 'with_circuit_breaker', 'handle_errors',
    
    # Performance monitoring
    'PerformanceMonitor', 'get_performance_monitor', 'monitor_performance',
    'start_all_monitoring', 'stop_all_monitoring', 'get_system_performance',
    
    # Conversation memory
    'ConversationMemoryManager', 'ConversationMessage', 'ConversationContext',
    'get_conversation_manager', 'create_user_message', 'create_assistant_message',
    
    # Capability assessment
    'CapabilityManager', 'Capability', 'CapabilityAssessment', 'CapabilityType', 'CapabilityLevel',
    'get_capability_manager', 'assess_agent_capabilities', 'get_agent_capability_summary',
    'update_agent_capability_metric'
]
