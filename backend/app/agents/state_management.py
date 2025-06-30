"""
Agent State Management
Task 100: Add agent state management
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from pydantic import BaseModel, Field
import uuid
from pathlib import Path
import aiosqlite

from app.agents.base_agent import AgentStatus
from app.agents.memory import MemoryManager, get_memory_manager

logger = logging.getLogger(__name__)


class StateType(str, Enum):
    """Types of agent state"""
    CONFIGURATION = "configuration"
    RUNTIME = "runtime"
    PERSISTENT = "persistent"
    SESSION = "session"
    TASK = "task"
    CONTEXT = "context"


class StatePersistence(str, Enum):
    """State persistence levels"""
    MEMORY_ONLY = "memory_only"      # Lost when agent restarts
    SESSION = "session"              # Persists for session duration
    TEMPORARY = "temporary"          # Persists with TTL
    PERMANENT = "permanent"          # Persists indefinitely


@dataclass
class StateVariable:
    """Individual state variable"""
    name: str
    value: Any
    state_type: StateType
    persistence: StatePersistence
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateVariable':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if state variable has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    def touch(self):
        """Update access information"""
        self.updated_at = datetime.now(timezone.utc)
        self.access_count += 1


class StateSnapshot:
    """Snapshot of agent state at a point in time"""
    
    def __init__(self, agent_id: str, snapshot_id: Optional[str] = None):
        self.snapshot_id = snapshot_id or str(uuid.uuid4())
        self.agent_id = agent_id
        self.created_at = datetime.now(timezone.utc)
        self.state_variables: Dict[str, StateVariable] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_variable(self, variable: StateVariable):
        """Add a state variable to the snapshot"""
        self.state_variables[variable.name] = variable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat(),
            "state_variables": {
                name: var.to_dict() for name, var in self.state_variables.items()
            },
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """Create snapshot from dictionary"""
        snapshot = cls(data["agent_id"], data["snapshot_id"])
        snapshot.created_at = datetime.fromisoformat(data["created_at"])
        snapshot.metadata = data.get("metadata", {})
        
        for name, var_data in data.get("state_variables", {}).items():
            snapshot.state_variables[name] = StateVariable.from_dict(var_data)
        
        return snapshot


class StateTransition:
    """Represents a state transition"""
    
    def __init__(
        self, 
        from_state: str, 
        to_state: str, 
        condition: Optional[Callable] = None,
        action: Optional[Callable] = None
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition  # Function that returns bool
        self.action = action        # Function to execute during transition
        self.transition_count = 0
        self.last_transition = None
    
    async def can_transition(self, context: Dict[str, Any]) -> bool:
        """Check if transition can occur"""
        if self.condition is None:
            return True
        
        try:
            if asyncio.iscoroutinefunction(self.condition):
                return await self.condition(context)
            else:
                return self.condition(context)
        except Exception as e:
            logger.error(f"Error checking transition condition: {e}")
            return False
    
    async def execute_transition(self, context: Dict[str, Any]) -> bool:
        """Execute the transition"""
        try:
            if self.action:
                if asyncio.iscoroutinefunction(self.action):
                    await self.action(context)
                else:
                    self.action(context)
            
            self.transition_count += 1
            self.last_transition = datetime.now(timezone.utc)
            return True
            
        except Exception as e:
            logger.error(f"Error executing transition action: {e}")
            return False


class StateMachine:
    """State machine for agent states"""
    
    def __init__(self, initial_state: str):
        self.current_state = initial_state
        self.states: set = {initial_state}
        self.transitions: Dict[str, List[StateTransition]] = {}
        self.state_history: List[Dict[str, Any]] = []
        self.entry_actions: Dict[str, Callable] = {}
        self.exit_actions: Dict[str, Callable] = {}
    
    def add_state(self, state: str):
        """Add a state to the machine"""
        self.states.add(state)
    
    def add_transition(self, transition: StateTransition):
        """Add a transition to the machine"""
        if transition.from_state not in self.transitions:
            self.transitions[transition.from_state] = []
        self.transitions[transition.from_state].append(transition)
    
    def set_entry_action(self, state: str, action: Callable):
        """Set action to execute when entering a state"""
        self.entry_actions[state] = action
    
    def set_exit_action(self, state: str, action: Callable):
        """Set action to execute when exiting a state"""
        self.exit_actions[state] = action
    
    async def transition_to(self, target_state: str, context: Dict[str, Any]) -> bool:
        """Attempt to transition to target state"""
        if target_state not in self.states:
            logger.error(f"Unknown state: {target_state}")
            return False
        
        # Find valid transition
        transitions = self.transitions.get(self.current_state, [])
        valid_transition = None
        
        for transition in transitions:
            if transition.to_state == target_state:
                if await transition.can_transition(context):
                    valid_transition = transition
                    break
        
        if not valid_transition:
            logger.warning(f"No valid transition from {self.current_state} to {target_state}")
            return False
        
        # Execute transition
        old_state = self.current_state
        
        # Exit current state
        if old_state in self.exit_actions:
            try:
                action = self.exit_actions[old_state]
                if asyncio.iscoroutinefunction(action):
                    await action(context)
                else:
                    action(context)
            except Exception as e:
                logger.error(f"Error executing exit action for {old_state}: {e}")
        
        # Execute transition action
        if not await valid_transition.execute_transition(context):
            logger.error(f"Transition action failed for {old_state} -> {target_state}")
            return False
        
        # Change state
        self.current_state = target_state
        
        # Enter new state
        if target_state in self.entry_actions:
            try:
                action = self.entry_actions[target_state]
                if asyncio.iscoroutinefunction(action):
                    await action(context)
                else:
                    action(context)
            except Exception as e:
                logger.error(f"Error executing entry action for {target_state}: {e}")
        
        # Record transition
        self.state_history.append({
            "from_state": old_state,
            "to_state": target_state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": context.copy()
        })
        
        logger.info(f"State transition: {old_state} -> {target_state}")
        return True
    
    def get_possible_transitions(self) -> List[str]:
        """Get possible target states from current state"""
        transitions = self.transitions.get(self.current_state, [])
        return [t.to_state for t in transitions]


class AgentStateManager:
    """Manager for agent state"""
    
    def __init__(self, agent_id: str, db_path: Optional[str] = None):
        self.agent_id = agent_id
        self.db_path = db_path or f"agent_state_{agent_id}.db"
        
        # State storage by type
        self.state_variables: Dict[str, StateVariable] = {}
        self.snapshots: Dict[str, StateSnapshot] = {}
        
        # State machine
        self.state_machine = StateMachine("idle")
        self._setup_default_state_machine()
        
        # Memory integration
        self.memory_manager = get_memory_manager(agent_id)
        
        # Observers for state changes
        self.observers: List[Callable] = []
        
        # Initialize database
        asyncio.create_task(self._init_db())
    
    async def _init_db(self):
        """Initialize state persistence database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS state_variables (
                    name TEXT PRIMARY KEY,
                    value TEXT,
                    state_type TEXT,
                    persistence TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    expires_at TEXT,
                    access_count INTEGER,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS state_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    created_at TEXT,
                    snapshot_data TEXT,
                    metadata TEXT
                )
            """)
            
            await db.commit()
    
    def _setup_default_state_machine(self):
        """Setup default state machine for agents"""
        # Add default states
        states = ["idle", "thinking", "executing", "waiting", "completed", "error"]
        for state in states:
            self.state_machine.add_state(state)
        
        # Add default transitions
        transitions = [
            ("idle", "thinking"),
            ("thinking", "executing"),
            ("thinking", "waiting"),
            ("executing", "completed"),
            ("executing", "error"),
            ("executing", "waiting"),
            ("waiting", "thinking"),
            ("waiting", "completed"),
            ("waiting", "error"),
            ("completed", "idle"),
            ("error", "idle")
        ]
        
        for from_state, to_state in transitions:
            self.state_machine.add_transition(
                StateTransition(from_state, to_state)
            )
    
    def set_variable(
        self, 
        name: str, 
        value: Any, 
        state_type: StateType = StateType.RUNTIME,
        persistence: StatePersistence = StatePersistence.MEMORY_ONLY,
        ttl: Optional[timedelta] = None
    ):
        """Set a state variable"""
        now = datetime.now(timezone.utc)
        expires_at = now + ttl if ttl else None
        
        if name in self.state_variables:
            # Update existing variable
            var = self.state_variables[name]
            var.value = value
            var.touch()
            if ttl:
                var.expires_at = expires_at
        else:
            # Create new variable
            var = StateVariable(
                name=name,
                value=value,
                state_type=state_type,
                persistence=persistence,
                created_at=now,
                updated_at=now,
                expires_at=expires_at
            )
            self.state_variables[name] = var
        
        # Persist if needed
        if persistence in [StatePersistence.SESSION, StatePersistence.TEMPORARY, StatePersistence.PERMANENT]:
            asyncio.create_task(self._persist_variable(var))
        
        # Notify observers
        self._notify_observers("variable_changed", {"name": name, "value": value})
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a state variable value"""
        var = self.state_variables.get(name)
        if var and not var.is_expired():
            var.touch()
            return var.value
        return default
    
    def delete_variable(self, name: str) -> bool:
        """Delete a state variable"""
        if name in self.state_variables:
            var = self.state_variables[name]
            del self.state_variables[name]
            
            # Remove from database if persistent
            if var.persistence != StatePersistence.MEMORY_ONLY:
                asyncio.create_task(self._delete_variable(name))
            
            self._notify_observers("variable_deleted", {"name": name})
            return True
        return False
    
    def get_variables_by_type(self, state_type: StateType) -> Dict[str, Any]:
        """Get all variables of a specific type"""
        result = {}
        for name, var in self.state_variables.items():
            if var.state_type == state_type and not var.is_expired():
                var.touch()
                result[name] = var.value
        return result
    
    async def create_snapshot(self, snapshot_id: Optional[str] = None) -> str:
        """Create a snapshot of current state"""
        snapshot = StateSnapshot(self.agent_id, snapshot_id)
        
        # Add all non-expired variables
        for var in self.state_variables.values():
            if not var.is_expired():
                snapshot.add_variable(var)
        
        # Add state machine state
        snapshot.metadata["current_state"] = self.state_machine.current_state
        snapshot.metadata["state_history"] = self.state_machine.state_history[-10:]  # Last 10 transitions
        
        self.snapshots[snapshot.snapshot_id] = snapshot
        
        # Persist snapshot
        await self._persist_snapshot(snapshot)
        
        self._notify_observers("snapshot_created", {"snapshot_id": snapshot.snapshot_id})
        return snapshot.snapshot_id
    
    async def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore state from a snapshot"""
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            # Try to load from database
            snapshot = await self._load_snapshot(snapshot_id)
            if not snapshot:
                return False
        
        # Clear current state
        self.state_variables.clear()
        
        # Restore variables
        for var in snapshot.state_variables.values():
            self.state_variables[var.name] = var
        
        # Restore state machine state
        if "current_state" in snapshot.metadata:
            self.state_machine.current_state = snapshot.metadata["current_state"]
        
        self._notify_observers("snapshot_restored", {"snapshot_id": snapshot_id})
        return True
    
    async def transition_state(self, target_state: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Transition to a new state"""
        context = context or {}
        context["agent_id"] = self.agent_id
        context["current_variables"] = {name: var.value for name, var in self.state_variables.items()}
        
        success = await self.state_machine.transition_to(target_state, context)
        if success:
            self.set_variable("current_state", target_state, StateType.RUNTIME)
            self._notify_observers("state_changed", {"new_state": target_state})
        
        return success
    
    def get_current_state(self) -> str:
        """Get current state machine state"""
        return self.state_machine.current_state
    
    def add_observer(self, observer: Callable):
        """Add state change observer"""
        self.observers.append(observer)
    
    def remove_observer(self, observer: Callable):
        """Remove state change observer"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers of state change"""
        for observer in self.observers:
            try:
                if asyncio.iscoroutinefunction(observer):
                    asyncio.create_task(observer(self.agent_id, event_type, data))
                else:
                    observer(self.agent_id, event_type, data)
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")
    
    async def cleanup_expired(self):
        """Remove expired state variables"""
        expired_vars = [
            name for name, var in self.state_variables.items()
            if var.is_expired()
        ]
        
        for name in expired_vars:
            self.delete_variable(name)
        
        if expired_vars:
            logger.info(f"Cleaned up {len(expired_vars)} expired state variables")
    
    async def _persist_variable(self, var: StateVariable):
        """Persist state variable to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO state_variables 
                (name, value, state_type, persistence, created_at, updated_at, 
                 expires_at, access_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                var.name,
                json.dumps(var.value, default=str),
                var.state_type.value,
                var.persistence.value,
                var.created_at.isoformat(),
                var.updated_at.isoformat(),
                var.expires_at.isoformat() if var.expires_at else None,
                var.access_count,
                json.dumps(var.metadata)
            ))
            await db.commit()
    
    async def _delete_variable(self, name: str):
        """Delete variable from database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM state_variables WHERE name = ?", (name,))
            await db.commit()
    
    async def _persist_snapshot(self, snapshot: StateSnapshot):
        """Persist snapshot to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO state_snapshots 
                (snapshot_id, agent_id, created_at, snapshot_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                snapshot.snapshot_id,
                snapshot.agent_id,
                snapshot.created_at.isoformat(),
                json.dumps(snapshot.to_dict()),
                json.dumps(snapshot.metadata)
            ))
            await db.commit()
    
    async def _load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load snapshot from database"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT snapshot_data FROM state_snapshots WHERE snapshot_id = ?",
                (snapshot_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    return StateSnapshot.from_dict(data)
                return None
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state"""
        return {
            "agent_id": self.agent_id,
            "current_state": self.state_machine.current_state,
            "variable_count": len(self.state_variables),
            "snapshot_count": len(self.snapshots),
            "variables_by_type": {
                state_type.value: len([
                    var for var in self.state_variables.values()
                    if var.state_type == state_type and not var.is_expired()
                ])
                for state_type in StateType
            },
            "possible_transitions": self.state_machine.get_possible_transitions(),
            "last_transitions": self.state_machine.state_history[-5:]  # Last 5 transitions
        }


# Global state managers by agent ID
_state_managers: Dict[str, AgentStateManager] = {}


def get_state_manager(agent_id: str) -> AgentStateManager:
    """Get or create state manager for an agent"""
    if agent_id not in _state_managers:
        _state_managers[agent_id] = AgentStateManager(agent_id)
    return _state_managers[agent_id]


async def cleanup_all_agent_states():
    """Cleanup expired state variables for all agents"""
    for manager in _state_managers.values():
        await manager.cleanup_expired()
