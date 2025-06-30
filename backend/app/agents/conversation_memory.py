"""
Agent Conversation Memory System
Task 105: Set up agent conversation memory
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4
import json
from collections import defaultdict

# Import the base memory system
from .memory import MemoryManager, MemoryType, ConversationMemory

logger = logging.getLogger(__name__)


class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class ConversationTurn(str, Enum):
    """Conversation turn types"""
    INPUT = "input"           # User input
    PROCESSING = "processing" # Agent processing
    OUTPUT = "output"         # Agent response
    CLARIFICATION = "clarification"  # Agent asking for clarification
    ERROR = "error"          # Error occurred


@dataclass
class ConversationMessage:
    """Individual message in conversation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Agent-specific fields
    agent_id: Optional[str] = None
    execution_id: Optional[str] = None
    confidence: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None
    processing_time: Optional[float] = None
    
    # Context fields
    context_used: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    memory_retrieved: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "agent_id": self.agent_id,
            "execution_id": self.execution_id,
            "confidence": self.confidence,
            "token_usage": self.token_usage,
            "processing_time": self.processing_time,
            "context_used": self.context_used,
            "tools_used": self.tools_used,
            "memory_retrieved": self.memory_retrieved
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        message = cls()
        message.id = data.get("id", str(uuid4()))
        message.role = MessageRole(data.get("role", "user"))
        message.content = data.get("content", "")
        message.timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc)
        message.metadata = data.get("metadata", {})
        message.agent_id = data.get("agent_id")
        message.execution_id = data.get("execution_id")
        message.confidence = data.get("confidence")
        message.token_usage = data.get("token_usage")
        message.processing_time = data.get("processing_time")
        message.context_used = data.get("context_used", [])
        message.tools_used = data.get("tools_used", [])
        message.memory_retrieved = data.get("memory_retrieved", [])
        return message


@dataclass
class ConversationTopic:
    """Topic or theme in conversation"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    importance: float = 1.0  # 0.0 to 1.0
    first_mentioned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_mentioned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mention_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "importance": self.importance,
            "first_mentioned": self.first_mentioned.isoformat(),
            "last_mentioned": self.last_mentioned.isoformat(),
            "mention_count": self.mention_count
        }


@dataclass
class ConversationContext:
    """Context information for conversation"""
    session_id: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    conversation_type: str = "general"  # general, data_analysis, support, etc.
    language: str = "en"
    domain: Optional[str] = None  # finance, healthcare, etc.
    
    # User preferences
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    communication_style: str = "formal"  # formal, casual, technical, etc.
    detail_level: str = "medium"  # brief, medium, detailed
    
    # Current context
    current_dataset: Optional[str] = None
    current_task: Optional[str] = None
    active_tools: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "conversation_type": self.conversation_type,
            "language": self.language,
            "domain": self.domain,
            "user_preferences": self.user_preferences,
            "communication_style": self.communication_style,
            "detail_level": self.detail_level,
            "current_dataset": self.current_dataset,
            "current_task": self.current_task,
            "active_tools": self.active_tools
        }


class ConversationMemoryManager:
    """Enhanced conversation memory management"""
    
    def __init__(self, agent_id: str, max_history_length: int = 1000):
        self.agent_id = agent_id
        self.max_history_length = max_history_length
        
        # Base memory manager
        self.memory_manager = MemoryManager(agent_id)
        
        # Conversation-specific storage
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.conversation_topics: Dict[str, List[ConversationTopic]] = defaultdict(list)
        self.conversation_summaries: Dict[str, str] = {}
        
        # Conversation statistics
        self.conversation_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Memory retrieval cache
        self._retrieval_cache: Dict[str, Tuple[List[ConversationMessage], datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
    
    async def start_conversation(
        self, 
        session_id: str, 
        context: ConversationContext
    ) -> ConversationContext:
        """Start a new conversation or resume existing one"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.conversation_stats[session_id] = {
                "start_time": datetime.now(timezone.utc),
                "message_count": 0,
                "total_tokens": 0,
                "avg_response_time": 0.0
            }
        
        self.conversation_contexts[session_id] = context
        
        # Load conversation history if resuming
        if session_id in self.conversations and self.conversations[session_id]:
            logger.info(f"Resuming conversation {session_id} with {len(self.conversations[session_id])} messages")
        else:
            logger.info(f"Starting new conversation {session_id}")
        
        return context
    
    async def add_message(
        self, 
        session_id: str, 
        message: ConversationMessage
    ) -> ConversationMessage:
        """Add a message to conversation"""
        if session_id not in self.conversations:
            raise ValueError(f"Conversation {session_id} not found. Call start_conversation first.")
        
        # Set agent ID if not set
        if not message.agent_id:
            message.agent_id = self.agent_id
        
        # Add to conversation
        self.conversations[session_id].append(message)
        
        # Update statistics
        self._update_conversation_stats(session_id, message)
        
        # Extract and update topics
        await self._extract_topics(session_id, message)
        
        # Maintain conversation length
        await self._maintain_conversation_length(session_id)
        
        # Store in base memory system for long-term retention
        await self._store_in_base_memory(session_id, message)
        
        # Clear retrieval cache for this session
        if session_id in self._retrieval_cache:
            del self._retrieval_cache[session_id]
        
        logger.debug(f"Added message to conversation {session_id}: {message.role.value}")
        
        return message
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None,
        include_context: bool = True
    ) -> List[ConversationMessage]:
        """Get conversation history"""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        
        if limit:
            messages = messages[-limit:]
        
        if include_context:
            # Add conversation context as system message
            context = self.conversation_contexts.get(session_id)
            if context:
                context_message = ConversationMessage(
                    role=MessageRole.SYSTEM,
                    content=f"Conversation context: {json.dumps(context.to_dict(), indent=2)}",
                    agent_id=self.agent_id,
                    metadata={"type": "context"}
                )
                messages = [context_message] + messages
        
        return messages
    
    async def get_relevant_context(
        self, 
        session_id: str, 
        query: str, 
        max_messages: int = 10
    ) -> List[ConversationMessage]:
        """Get relevant conversation context for a query"""
        # Check cache first
        cache_key = f"{session_id}:{query}:{max_messages}"
        if cache_key in self._retrieval_cache:
            cached_messages, cache_time = self._retrieval_cache[cache_key]
            if datetime.now(timezone.utc) - cache_time < self._cache_ttl:
                return cached_messages
        
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        
        # Simple relevance scoring based on keyword matching
        scored_messages = []
        query_words = set(query.lower().split())
        
        for message in messages:
            score = 0.0
            content_words = set(message.content.lower().split())
            
            # Keyword overlap
            overlap = len(query_words.intersection(content_words))
            score += overlap * 2
            
            # Recent messages get higher scores
            age_hours = (datetime.now(timezone.utc) - message.timestamp).total_seconds() / 3600
            recency_score = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
            score += recency_score
            
            # Role-based scoring
            if message.role == MessageRole.ASSISTANT:
                score += 1  # Assistant responses often contain important context
            
            scored_messages.append((score, message))
        
        # Sort by score and take top messages
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        relevant_messages = [msg for score, msg in scored_messages[:max_messages]]
        
        # Cache the result
        self._retrieval_cache[cache_key] = (relevant_messages, datetime.now(timezone.utc))
        
        return relevant_messages
    
    async def summarize_conversation(
        self, 
        session_id: str, 
        force_refresh: bool = False
    ) -> str:
        """Generate conversation summary"""
        if not force_refresh and session_id in self.conversation_summaries:
            return self.conversation_summaries[session_id]
        
        if session_id not in self.conversations:
            return "No conversation found."
        
        messages = self.conversations[session_id]
        if not messages:
            return "Empty conversation."
        
        # Simple summary generation (in production, would use LLM)
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
        
        topics = self.conversation_topics.get(session_id, [])
        main_topics = [t.name for t in sorted(topics, key=lambda x: x.importance, reverse=True)[:3]]
        
        summary_parts = []
        summary_parts.append(f"Conversation with {len(messages)} messages")
        summary_parts.append(f"Duration: {len(user_messages)} user turns")
        
        if main_topics:
            summary_parts.append(f"Main topics: {', '.join(main_topics)}")
        
        # Get conversation context
        context = self.conversation_contexts.get(session_id)
        if context:
            summary_parts.append(f"Type: {context.conversation_type}")
            if context.current_dataset:
                summary_parts.append(f"Working with dataset: {context.current_dataset}")
        
        summary = ". ".join(summary_parts) + "."
        self.conversation_summaries[session_id] = summary
        
        return summary
    
    async def get_conversation_topics(self, session_id: str) -> List[ConversationTopic]:
        """Get topics discussed in conversation"""
        return self.conversation_topics.get(session_id, [])
    
    async def update_conversation_context(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> ConversationContext:
        """Update conversation context"""
        if session_id not in self.conversation_contexts:
            raise ValueError(f"Conversation {session_id} not found")
        
        context = self.conversation_contexts[session_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        return context
    
    async def get_conversation_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get conversation statistics"""
        if session_id not in self.conversation_stats:
            return {}
        
        stats = self.conversation_stats[session_id].copy()
        
        # Add current statistics
        if session_id in self.conversations:
            messages = self.conversations[session_id]
            stats["current_message_count"] = len(messages)
            
            if messages:
                stats["last_activity"] = messages[-1].timestamp.isoformat()
                stats["conversation_duration"] = (
                    messages[-1].timestamp - messages[0].timestamp
                ).total_seconds()
        
        return stats
    
    async def search_conversations(
        self, 
        query: str, 
        session_ids: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Tuple[str, ConversationMessage]]:
        """Search across conversations"""
        results = []
        query_words = set(query.lower().split())
        
        search_sessions = session_ids or list(self.conversations.keys())
        
        for session_id in search_sessions:
            messages = self.conversations.get(session_id, [])
            
            for message in messages:
                content_words = set(message.content.lower().split())
                overlap = len(query_words.intersection(content_words))
                
                if overlap > 0:
                    results.append((session_id, message))
        
        # Sort by relevance (simple overlap count for now)
        results.sort(key=lambda x: len(set(query.lower().split()).intersection(
            set(x[1].content.lower().split()))), reverse=True)
        
        return results[:limit]
    
    async def _extract_topics(self, session_id: str, message: ConversationMessage):
        """Extract topics from message (simplified implementation)"""
        # Simple keyword-based topic extraction
        # In production, would use NLP techniques
        
        content = message.content.lower()
        
        # Predefined topic keywords
        topic_keywords = {
            "data_analysis": ["analyze", "analysis", "data", "statistics", "chart", "graph"],
            "file_upload": ["upload", "file", "csv", "excel", "import"],
            "visualization": ["plot", "chart", "graph", "visualize", "display"],
            "machine_learning": ["model", "predict", "classification", "regression", "ai"],
            "database": ["database", "sql", "query", "table", "column"],
            "export": ["export", "download", "save", "output"]
        }
        
        for topic_name, keywords in topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                # Find or create topic
                topics = self.conversation_topics[session_id]
                topic = next((t for t in topics if t.name == topic_name), None)
                
                if not topic:
                    topic = ConversationTopic(
                        name=topic_name,
                        keywords=keywords,
                        description=f"Topic about {topic_name.replace('_', ' ')}"
                    )
                    topics.append(topic)
                
                # Update topic
                topic.last_mentioned = message.timestamp
                topic.mention_count += 1
                topic.importance = min(1.0, topic.mention_count * 0.1)
    
    def _update_conversation_stats(self, session_id: str, message: ConversationMessage):
        """Update conversation statistics"""
        stats = self.conversation_stats[session_id]
        stats["message_count"] += 1
        
        if message.token_usage:
            stats["total_tokens"] += sum(message.token_usage.values())
        
        if message.processing_time:
            # Update average response time
            current_avg = stats.get("avg_response_time", 0.0)
            message_count = stats["message_count"]
            stats["avg_response_time"] = (
                (current_avg * (message_count - 1) + message.processing_time) / message_count
            )
    
    async def _maintain_conversation_length(self, session_id: str):
        """Maintain conversation length within limits"""
        messages = self.conversations[session_id]
        
        if len(messages) > self.max_history_length:
            # Remove oldest messages, but keep some context
            keep_count = int(self.max_history_length * 0.8)  # Keep 80%
            removed_messages = messages[:-keep_count]
            self.conversations[session_id] = messages[-keep_count:]
            
            # Store removed messages in long-term memory
            for message in removed_messages:
                await self._store_in_base_memory(session_id, message, long_term=True)
            
            logger.info(f"Trimmed conversation {session_id}: removed {len(removed_messages)} messages")
    
    async def _store_in_base_memory(
        self, 
        session_id: str, 
        message: ConversationMessage, 
        long_term: bool = False
    ):
        """Store message in base memory system"""
        memory_data = {
            "session_id": session_id,
            "message": message.to_dict(),
            "conversation_context": self.conversation_contexts.get(session_id, {}).to_dict()
        }
        
        memory_type = MemoryType.LONG_TERM if long_term else MemoryType.CONVERSATION
        
        await self.memory_manager.store_memory(
            memory_id=f"conversation_{session_id}_{message.id}",
            content=message.content,
            memory_type=memory_type,
            metadata=memory_data
        )


# Global conversation memory managers
_conversation_managers: Dict[str, ConversationMemoryManager] = {}


def get_conversation_manager(agent_id: str) -> ConversationMemoryManager:
    """Get or create conversation memory manager for an agent"""
    if agent_id not in _conversation_managers:
        _conversation_managers[agent_id] = ConversationMemoryManager(agent_id)
    return _conversation_managers[agent_id]


async def create_user_message(
    content: str, 
    session_id: str, 
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ConversationMessage:
    """Create a user message"""
    return ConversationMessage(
        role=MessageRole.USER,
        content=content,
        metadata=metadata or {},
        execution_id=f"user_input_{session_id}_{datetime.now(timezone.utc).timestamp()}"
    )


async def create_assistant_message(
    content: str,
    agent_id: str,
    execution_id: str,
    confidence: Optional[float] = None,
    token_usage: Optional[Dict[str, int]] = None,
    processing_time: Optional[float] = None,
    tools_used: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ConversationMessage:
    """Create an assistant message"""
    return ConversationMessage(
        role=MessageRole.ASSISTANT,
        content=content,
        agent_id=agent_id,
        execution_id=execution_id,
        confidence=confidence,
        token_usage=token_usage,
        processing_time=processing_time,
        tools_used=tools_used or [],
        metadata=metadata or {}
    )
