"""
Base Agent Framework with LangChain
Task 96: Create base agent framework with LangChain
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type
from enum import Enum
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser
from langchain_core.runnables import Runnable

from app.core.ollama_config import get_ollama_manager, OllamaManager

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentCapability(str, Enum):
    """Agent capabilities"""
    TEXT_GENERATION = "text_generation"
    DATA_ANALYSIS = "data_analysis"
    FILE_PROCESSING = "file_processing"
    CONVERSATION = "conversation"
    REASONING = "reasoning"
    RESEARCH = "research"
    PLANNING = "planning"
    CODE_GENERATION = "code_generation"


class AgentInput(BaseModel):
    """Input model for agent execution"""
    message: str = Field(..., description="Input message or query")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentOutput(BaseModel):
    """Output model for agent execution"""
    response: str = Field(..., description="Agent response")
    status: AgentStatus = Field(..., description="Execution status")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Response confidence")
    reasoning: Optional[str] = Field(default=None, description="Agent reasoning process")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: float = Field(default=0.0, description="Execution time in seconds")
    token_usage: Dict[str, int] = Field(default_factory=dict, description="Token usage statistics")


class AgentConfig(BaseModel):
    """Configuration for base agent"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    system_prompt: Optional[str] = Field(default=None, description="System prompt template")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=2048, ge=1, description="Maximum tokens")
    timeout: int = Field(default=300, ge=1, description="Execution timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    enable_logging: bool = Field(default=True, description="Enable execution logging")


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = str(uuid.uuid4())
        self.status = AgentStatus.IDLE
        self.ollama_manager: Optional[OllamaManager] = None
        self.created_at = datetime.now(timezone.utc)
        self.last_execution = None
        self.execution_count = 0
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{self.config.name}")
        if self.config.enable_logging:
            self.logger.setLevel(logging.INFO)
    
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            self.ollama_manager = await get_ollama_manager()
            if not self.ollama_manager.is_ready():
                self.logger.error("Ollama manager is not ready")
                return False
            
            self.logger.info(f"Agent {self.config.name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            return False
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return output"""
        pass
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute the agent with error handling and monitoring"""
        start_time = datetime.now(timezone.utc)
        self.execution_count += 1
        
        try:
            self.status = AgentStatus.THINKING
            self.last_execution = start_time
            
            # Validate input
            if not input_data.message.strip():
                raise ValueError("Input message cannot be empty")
            
            # Process with timeout
            output = await asyncio.wait_for(
                self.process(input_data),
                timeout=self.config.timeout
            )
            
            # Calculate execution time
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            output.execution_time = execution_time
            
            self.status = AgentStatus.COMPLETED
            self.logger.info(f"Agent execution completed in {execution_time:.2f}s")
            
            return output
            
        except asyncio.TimeoutError:
            self.status = AgentStatus.ERROR
            self.logger.error("Agent execution timed out")
            return AgentOutput(
                response="I apologize, but the request timed out. Please try again with a simpler query.",
                status=AgentStatus.ERROR,
                execution_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Agent execution failed: {e}")
            return AgentOutput(
                response=f"I encountered an error while processing your request: {str(e)}",
                status=AgentStatus.ERROR,
                execution_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Ollama"""
        if not self.ollama_manager:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # Use configured system prompt if none provided
        if system_prompt is None and self.config.system_prompt:
            system_prompt = self.config.system_prompt
        
        # Set default parameters from config
        generation_kwargs = {
            "temperature": self.config.temperature,
            "num_predict": self.config.max_tokens,
            **kwargs
        }
        
        return await self.ollama_manager.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **generation_kwargs
        )
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Chat using conversation format"""
        if not self.ollama_manager:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        generation_kwargs = {
            "temperature": self.config.temperature,
            "num_predict": self.config.max_tokens,
            **kwargs
        }
        
        return await self.ollama_manager.chat(messages, **generation_kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "id": self.id,
            "name": self.config.name,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.config.capabilities],
            "execution_count": self.execution_count,
            "created_at": self.created_at.isoformat(),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "is_ready": self.ollama_manager is not None and self.ollama_manager.is_ready()
        }
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.config.capabilities


class ConversationAgent(BaseAgent):
    """Agent specialized for conversational interactions"""
    
    def __init__(self):
        config = AgentConfig(
            name="ConversationAgent",
            description="General-purpose conversational AI agent",
            capabilities=[
                AgentCapability.CONVERSATION,
                AgentCapability.TEXT_GENERATION,
                AgentCapability.REASONING
            ],
            system_prompt="You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user queries.",
            temperature=0.7,
            max_tokens=2048
        )
        super().__init__(config)
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process conversational input"""
        try:
            # Generate response
            result = await self.generate_response(
                prompt=input_data.message,
                **input_data.context
            )
            
            if result["success"]:
                return AgentOutput(
                    response=result["response"],
                    status=AgentStatus.COMPLETED,
                    confidence=0.8,
                    token_usage={
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0)
                    }
                )
            else:
                raise RuntimeError(result.get("error", "Unknown error"))
                
        except Exception as e:
            raise RuntimeError(f"Failed to process conversation: {e}")


class DataAnalysisAgent(BaseAgent):
    """Agent specialized for data analysis tasks"""
    
    def __init__(self):
        config = AgentConfig(
            name="DataAnalysisAgent",
            description="AI agent specialized in data analysis and insights",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REASONING,
                AgentCapability.TEXT_GENERATION
            ],
            system_prompt="""You are a data analysis expert. Analyze data, identify patterns, 
            provide insights, and suggest actionable recommendations. Always be thorough and precise.""",
            temperature=0.3,  # Lower temperature for more focused analysis
            max_tokens=3072
        )
        super().__init__(config)
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process data analysis requests"""
        try:
            # Prepare analysis prompt
            analysis_prompt = f"""
            Data Analysis Request: {input_data.message}
            
            Context: {input_data.context}
            
            Please provide:
            1. Analysis summary
            2. Key findings
            3. Patterns and trends
            4. Recommendations
            5. Next steps
            """
            
            result = await self.generate_response(analysis_prompt)
            
            if result["success"]:
                return AgentOutput(
                    response=result["response"],
                    status=AgentStatus.COMPLETED,
                    confidence=0.9,
                    reasoning="Analyzed data using statistical methods and pattern recognition",
                    suggestions=[
                        "Review additional data sources",
                        "Validate findings with domain experts",
                        "Implement recommended actions"
                    ],
                    token_usage={
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0)
                    }
                )
            else:
                raise RuntimeError(result.get("error", "Unknown error"))
                
        except Exception as e:
            raise RuntimeError(f"Failed to process data analysis: {e}")


class AgentFactory:
    """Factory for creating different types of agents"""
    
    _agent_types = {
        "conversation": ConversationAgent,
        "data_analysis": DataAnalysisAgent,
    }
    
    @classmethod
    def create_agent(cls, agent_type: str) -> BaseAgent:
        """Create an agent of the specified type"""
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return cls._agent_types[agent_type]()
    
    @classmethod
    def register_agent_type(cls, name: str, agent_class: Type[BaseAgent]):
        """Register a new agent type"""
        cls._agent_types[name] = agent_class
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available agent types"""
        return list(cls._agent_types.keys())


# Agent registry for managing multiple agents
class AgentRegistry:
    """Registry for managing multiple agent instances"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    async def create_agent(self, agent_type: str, agent_id: Optional[str] = None) -> str:
        """Create and register a new agent"""
        agent = AgentFactory.create_agent(agent_type)
        
        if agent_id is None:
            agent_id = agent.id
        
        # Initialize the agent
        if not await agent.initialize():
            raise RuntimeError(f"Failed to initialize agent of type {agent_type}")
        
        self._agents[agent_id] = agent
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self._agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from registry"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.get_status() for agent in self._agents.values()]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Get agents with a specific capability"""
        return [
            agent for agent in self._agents.values()
            if agent.has_capability(capability)
        ]


# Global registry instance
_agent_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry"""
    return _agent_registry
