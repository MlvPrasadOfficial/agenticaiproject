"""
Agent Memory System
Task 99: Create agent memory system (conversation history, context retention)
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field
import asyncio
import sqlite3
import aiosqlite
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"  # Session-based, temporary
    LONG_TERM = "long_term"    # Persistent across sessions
    EPISODIC = "episodic"      # Specific conversations/events
    SEMANTIC = "semantic"      # General knowledge and facts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"        # Current task context


class MemoryImportance(str, Enum):
    """Importance levels for memory retention"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryItem:
    """Individual memory item"""
    id: str
    agent_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance: MemoryImportance
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    tags: List[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if memory item has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1


class ConversationMemory:
    """Memory for conversation history"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> messages
        self.summaries: Dict[str, str] = {}  # session_id -> summary
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        
        # Trim if too large
        if len(self.conversations[session_id]) > self.max_size:
            # Remove oldest messages but keep important ones
            self._trim_conversation(session_id)
    
    def get_conversation(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        messages = self.conversations.get(session_id, [])
        if limit:
            return messages[-limit:]
        return messages
    
    def get_context_window(self, session_id: str, window_size: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for context"""
        return self.get_conversation(session_id, window_size)
    
    def summarize_conversation(self, session_id: str) -> Optional[str]:
        """Get or create conversation summary"""
        if session_id in self.summaries:
            return self.summaries[session_id]
        
        messages = self.conversations.get(session_id, [])
        if not messages:
            return None
        
        # Simple summary creation (in a real implementation, this would use LLM)
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        ai_messages = [msg for msg in messages if msg["role"] == "assistant"]
        
        summary = f"Conversation with {len(user_messages)} user messages and {len(ai_messages)} AI responses. "
        summary += f"Started at {messages[0]['timestamp']} and last updated at {messages[-1]['timestamp']}."
        
        self.summaries[session_id] = summary
        return summary
    
    def _trim_conversation(self, session_id: str):
        """Trim conversation to fit within max_size"""
        messages = self.conversations[session_id]
        
        # Keep the most recent messages and any marked as important
        important_messages = [msg for msg in messages if msg.get("metadata", {}).get("important", False)]
        recent_messages = messages[-(self.max_size // 2):]
        
        # Combine and deduplicate
        kept_messages = []
        seen_timestamps = set()
        
        for msg in important_messages + recent_messages:
            timestamp = msg["timestamp"]
            if timestamp not in seen_timestamps:
                kept_messages.append(msg)
                seen_timestamps.add(timestamp)
        
        # Sort by timestamp
        kept_messages.sort(key=lambda x: x["timestamp"])
        self.conversations[session_id] = kept_messages


class SemanticMemory:
    """Memory for facts and knowledge"""
    
    def __init__(self):
        self.facts: Dict[str, Dict[str, Any]] = {}  # key -> fact data
        self.relationships: Dict[str, List[str]] = {}  # entity -> related entities
        self.concepts: Dict[str, Dict[str, Any]] = {}  # concept -> definition/data
    
    def store_fact(self, key: str, fact: str, confidence: float = 1.0, source: Optional[str] = None):
        """Store a factual statement"""
        self.facts[key] = {
            "fact": fact,
            "confidence": confidence,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "access_count": 0
        }
    
    def get_fact(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a fact"""
        fact = self.facts.get(key)
        if fact:
            fact["access_count"] += 1
        return fact
    
    def store_relationship(self, entity1: str, entity2: str, relationship_type: str = "related"):
        """Store a relationship between entities"""
        if entity1 not in self.relationships:
            self.relationships[entity1] = []
        if entity2 not in self.relationships:
            self.relationships[entity2] = []
        
        relation_data = f"{relationship_type}:{entity2}"
        if relation_data not in self.relationships[entity1]:
            self.relationships[entity1].append(relation_data)
        
        # Bidirectional relationship
        reverse_relation = f"{relationship_type}:{entity1}"
        if reverse_relation not in self.relationships[entity2]:
            self.relationships[entity2].append(reverse_relation)
    
    def get_related(self, entity: str) -> List[str]:
        """Get entities related to given entity"""
        return self.relationships.get(entity, [])
    
    def store_concept(self, concept: str, definition: str, examples: Optional[List[str]] = None):
        """Store a concept definition"""
        self.concepts[concept] = {
            "definition": definition,
            "examples": examples or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "access_count": 0
        }
    
    def get_concept(self, concept: str) -> Optional[Dict[str, Any]]:
        """Retrieve a concept"""
        concept_data = self.concepts.get(concept)
        if concept_data:
            concept_data["access_count"] += 1
        return concept_data


class WorkingMemory:
    """Memory for current task context"""
    
    def __init__(self, capacity: int = 7):  # Miller's magic number
        self.capacity = capacity
        self.items: List[Dict[str, Any]] = []
        self.current_task: Optional[str] = None
        self.context: Dict[str, Any] = {}
    
    def set_current_task(self, task: str):
        """Set the current task"""
        self.current_task = task
        self.clear()  # Clear working memory when task changes
    
    def add_item(self, item: Dict[str, Any], priority: int = 0):
        """Add item to working memory"""
        memory_item = {
            "content": item,
            "priority": priority,
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.items.append(memory_item)
        
        # Sort by priority and keep only top items
        self.items.sort(key=lambda x: x["priority"], reverse=True)
        if len(self.items) > self.capacity:
            self.items = self.items[:self.capacity]
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items in working memory"""
        return [item["content"] for item in self.items]
    
    def update_context(self, key: str, value: Any):
        """Update context variable"""
        self.context[key] = value
    
    def get_context(self, key: str = None) -> Union[Any, Dict[str, Any]]:
        """Get context variable or all context"""
        if key:
            return self.context.get(key)
        return self.context.copy()
    
    def clear(self):
        """Clear working memory"""
        self.items.clear()
        self.context.clear()


class MemoryManager:
    """Central manager for all memory types"""
    
    def __init__(self, agent_id: str, db_path: Optional[str] = None):
        self.agent_id = agent_id
        self.db_path = db_path or f"memory_{agent_id}.db"
        
        # Memory components
        self.conversation_memory = ConversationMemory()
        self.semantic_memory = SemanticMemory()
        self.working_memory = WorkingMemory()
        
        # Memory storage
        self.short_term: Dict[str, MemoryItem] = {}
        self.long_term: Dict[str, MemoryItem] = {}
        
        # Initialize database
        asyncio.create_task(self._init_db())
    
    async def _init_db(self):
        """Initialize SQLite database for persistent memory"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    memory_type TEXT,
                    content TEXT,
                    importance TEXT,
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER,
                    tags TEXT,
                    session_id TEXT,
                    expires_at TEXT,
                    metadata TEXT
                )
            """)
            await db.commit()
    
    async def store_memory(self, memory_item: MemoryItem) -> bool:
        """Store a memory item"""
        try:
            if memory_item.memory_type == MemoryType.SHORT_TERM:
                self.short_term[memory_item.id] = memory_item
            else:
                self.long_term[memory_item.id] = memory_item
                # Persist to database
                await self._persist_memory(memory_item)
            
            return True
        except Exception as e:
            logger.error(f"Failed to store memory {memory_item.id}: {e}")
            return False
    
    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item"""
        # Check short-term first
        memory_item = self.short_term.get(memory_id)
        if memory_item:
            memory_item.touch()
            return memory_item
        
        # Check long-term
        memory_item = self.long_term.get(memory_id)
        if memory_item:
            memory_item.touch()
            await self._update_access(memory_item)
            return memory_item
        
        # Load from database
        memory_item = await self._load_memory(memory_id)
        if memory_item:
            memory_item.touch()
            self.long_term[memory_id] = memory_item
            await self._update_access(memory_item)
        
        return memory_item
    
    async def search_memories(
        self, 
        query: str, 
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """Search memories by content, type, or tags"""
        results = []
        
        # Search in-memory items
        all_memories = {**self.short_term, **self.long_term}
        
        for memory_item in all_memories.values():
            if memory_item.is_expired():
                continue
            
            # Filter by type
            if memory_type and memory_item.memory_type != memory_type:
                continue
            
            # Filter by tags
            if tags and not any(tag in memory_item.tags for tag in tags):
                continue
            
            # Simple text search in content
            content_str = json.dumps(memory_item.content, default=str).lower()
            if query.lower() in content_str:
                results.append(memory_item)
        
        # Sort by relevance (access count and recency)
        results.sort(key=lambda x: (x.access_count, x.last_accessed), reverse=True)
        
        return results[:limit]
    
    async def cleanup_expired(self):
        """Remove expired memory items"""
        expired_short_term = [
            item_id for item_id, item in self.short_term.items()
            if item.is_expired()
        ]
        
        expired_long_term = [
            item_id for item_id, item in self.long_term.items()
            if item.is_expired()
        ]
        
        # Remove from memory
        for item_id in expired_short_term:
            del self.short_term[item_id]
        
        for item_id in expired_long_term:
            del self.long_term[item_id]
        
        # Remove from database
        if expired_long_term:
            await self._delete_memories(expired_long_term)
        
        logger.info(f"Cleaned up {len(expired_short_term)} short-term and {len(expired_long_term)} long-term memories")
    
    async def _persist_memory(self, memory_item: MemoryItem):
        """Persist memory item to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO memory_items 
                (id, agent_id, memory_type, content, importance, created_at, 
                 last_accessed, access_count, tags, session_id, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_item.id,
                memory_item.agent_id,
                memory_item.memory_type.value,
                json.dumps(memory_item.content),
                memory_item.importance.value,
                memory_item.created_at.isoformat(),
                memory_item.last_accessed.isoformat(),
                memory_item.access_count,
                json.dumps(memory_item.tags),
                memory_item.session_id,
                memory_item.expires_at.isoformat() if memory_item.expires_at else None,
                json.dumps(memory_item.metadata)
            ))
            await db.commit()
    
    async def _load_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Load memory item from database"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM memory_items WHERE id = ?", (memory_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return MemoryItem(
                        id=row[0],
                        agent_id=row[1],
                        memory_type=MemoryType(row[2]),
                        content=json.loads(row[3]),
                        importance=MemoryImportance(row[4]),
                        created_at=datetime.fromisoformat(row[5]),
                        last_accessed=datetime.fromisoformat(row[6]),
                        access_count=row[7],
                        tags=json.loads(row[8]),
                        session_id=row[9],
                        expires_at=datetime.fromisoformat(row[10]) if row[10] else None,
                        metadata=json.loads(row[11])
                    )
                return None
    
    async def _update_access(self, memory_item: MemoryItem):
        """Update access information in database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE memory_items 
                SET last_accessed = ?, access_count = ?
                WHERE id = ?
            """, (
                memory_item.last_accessed.isoformat(),
                memory_item.access_count,
                memory_item.id
            ))
            await db.commit()
    
    async def _delete_memories(self, memory_ids: List[str]):
        """Delete memories from database"""
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ",".join("?" * len(memory_ids))
            await db.execute(
                f"DELETE FROM memory_items WHERE id IN ({placeholders})",
                memory_ids
            )
            await db.commit()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "working_memory_items": len(self.working_memory.items),
            "working_memory_capacity": self.working_memory.capacity,
            "current_task": self.working_memory.current_task,
            "conversation_sessions": len(self.conversation_memory.conversations),
            "semantic_facts": len(self.semantic_memory.facts),
            "semantic_concepts": len(self.semantic_memory.concepts),
            "semantic_relationships": len(self.semantic_memory.relationships)
        }


# Global memory managers by agent ID
_memory_managers: Dict[str, MemoryManager] = {}


def get_memory_manager(agent_id: str) -> MemoryManager:
    """Get or create memory manager for an agent"""
    if agent_id not in _memory_managers:
        _memory_managers[agent_id] = MemoryManager(agent_id)
    return _memory_managers[agent_id]


async def cleanup_all_memories():
    """Cleanup expired memories for all agents"""
    for manager in _memory_managers.values():
        await manager.cleanup_expired()
