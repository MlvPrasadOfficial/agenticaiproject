"""
Conversation Manager Service
Handles conversation history and messaging
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Conversation:
    conversation_id: str
    session_id: str
    messages: List[ConversationMessage]
    timestamp: datetime
    status: str

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.session_messages: Dict[str, List[ConversationMessage]] = {}
        self.is_healthy = True
    
    async def add_message(
        self,
        session_id: str,
        message: ConversationMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Add a message to a conversation and get agent response."""
        from app.services.session_manager import session_manager
        
        conversation_id = str(uuid.uuid4())
        
        # Initialize session messages if not exists
        if session_id not in self.session_messages:
            self.session_messages[session_id] = []
        
        # Add user message
        user_message = ConversationMessage(
            role=message.role,
            content=message.content,
            timestamp=message.timestamp or datetime.now(),
            metadata=message.metadata or {}
        )
        self.session_messages[session_id].append(user_message)
        
        # Generate agent response (simplified for now)
        agent_response = await self._generate_agent_response(
            user_message.content,
            context or {},
            self.session_messages[session_id]
        )
        
        agent_message = ConversationMessage(
            role="assistant",
            content=agent_response,
            timestamp=datetime.now(),
            metadata={"type": "agent_response", "context": context}
        )
        self.session_messages[session_id].append(agent_message)
        
        # Create conversation record
        conversation = Conversation(
            conversation_id=conversation_id,
            session_id=session_id,
            messages=[user_message, agent_message],
            timestamp=datetime.now(),
            status="completed"
        )
        
        self.conversations[conversation_id] = conversation
        
        # Update session conversation count
        await session_manager.increment_conversation_count(session_id)
        
        logger.info(f"Added message to conversation: {conversation_id}")
        return conversation
    
    async def _generate_agent_response(
        self,
        user_message: str,
        context: Dict[str, Any],
        conversation_history: List[ConversationMessage]
    ) -> str:
        """Generate agent response based on user message and context."""
        # This is a simplified response generator
        # In production, this would integrate with the actual LLM/agent system
        
        # Analyze message intent
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["analyze", "analysis", "data"]):
            return f"I'll analyze the data for you. Based on your request '{user_message}', I can help you understand patterns, trends, and insights in your dataset. What specific aspect would you like me to focus on?"
        
        elif any(word in message_lower for word in ["upload", "file", "import"]):
            return "I can help you upload and process data files. I support CSV, Excel, and JSON formats. Once uploaded, I'll automatically analyze the structure and provide insights. Would you like to upload a file?"
        
        elif any(word in message_lower for word in ["insight", "trend", "pattern"]):
            return f"I'll generate insights for you. Looking at your query '{user_message}', I can identify key trends, anomalies, and business opportunities. Let me process this and provide detailed findings."
        
        elif any(word in message_lower for word in ["help", "how", "what"]):
            return "I'm your Enterprise Insights Copilot! I can help you:\n\n• Upload and analyze data files\n• Generate business insights and trends\n• Create visualizations and reports\n• Answer questions about your data\n• Provide recommendations based on analysis\n\nWhat would you like to explore today?"
        
        else:
            return f"I understand you're asking about '{user_message}'. I'm here to help with data analysis, insights generation, and business intelligence. Could you provide more context about what specific analysis or insights you're looking for?"
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationMessage]:
        """Get conversation history for a session."""
        if session_id not in self.session_messages:
            return []
        
        messages = self.session_messages[session_id]
        
        # Sort by timestamp (most recent first)
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply pagination
        start = offset
        end = offset + limit
        
        return messages[start:end]
    
    async def clear_conversation_history(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        if session_id in self.session_messages:
            del self.session_messages[session_id]
            
            # Also clear related conversation records
            to_delete = [
                conv_id for conv_id, conv in self.conversations.items()
                if conv.session_id == session_id
            ]
            for conv_id in to_delete:
                del self.conversations[conv_id]
            
            logger.info(f"Cleared conversation history for session: {session_id}")
            return True
        return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID."""
        return self.conversations.get(conversation_id)
    
    async def health_check(self) -> bool:
        """Check if conversation manager is healthy."""
        return self.is_healthy

# Global instance
conversation_manager = ConversationManager()
