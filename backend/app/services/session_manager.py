"""
Session Manager Service
Handles user sessions for conversation continuity
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class Session:
    session_id: str
    user_id: Optional[str]
    session_name: Optional[str]
    created_at: datetime
    last_activity: datetime
    status: str
    conversation_count: int
    metadata: Dict[str, Any]

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.is_healthy = True
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            session_name=session_name or f"Session {session_id[:8]}",
            created_at=now,
            last_activity=now,
            status="active",
            conversation_count=0,
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        if session_id in self.sessions:
            # Update last activity
            self.sessions[session_id].last_activity = datetime.now()
            return self.sessions[session_id]
        return None
    
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Session]:
        """List sessions, optionally filtered by user."""
        sessions = list(self.sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        # Sort by last activity (most recent first)
        sessions.sort(key=lambda s: s.last_activity, reverse=True)
        
        return sessions[:limit]
    
    async def update_session(
        self,
        session_id: str,
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Session]:
        """Update session details."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if session_name:
            session.session_name = session_name
        
        if metadata:
            session.metadata.update(metadata)
        
        session.last_activity = datetime.now()
        
        logger.info(f"Updated session: {session_id}")
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    async def increment_conversation_count(self, session_id: str) -> bool:
        """Increment conversation count for a session."""
        if session_id in self.sessions:
            self.sessions[session_id].conversation_count += 1
            self.sessions[session_id].last_activity = datetime.now()
            return True
        return False
    
    async def health_check(self) -> bool:
        """Check if session manager is healthy."""
        return self.is_healthy

# Global instance
session_manager = SessionManager()
