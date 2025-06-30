"""
Agent Communication Protocols
Task 98: Implement agent communication protocols
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field
import uuid

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_COMPLETION = "task_completion"
    DATA_SHARE = "data_share"
    COORDINATION = "coordination"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProtocolType(str, Enum):
    """Communication protocol types"""
    DIRECT = "direct"  # Direct agent-to-agent
    BROADCAST = "broadcast"  # One-to-many
    PUBLISH_SUBSCRIBE = "publish_subscribe"  # Topic-based
    REQUEST_RESPONSE = "request_response"  # Synchronous request/response
    MESSAGE_QUEUE = "message_queue"  # Asynchronous queue-based


@dataclass
class Message:
    """Inter-agent message structure"""
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast messages
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None  # For request/response matching
    topic: Optional[str] = None  # For pub/sub
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


class MessageHandler:
    """Base class for message handlers"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.handlers: Dict[MessageType, Callable] = {}
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for a specific message type"""
        self.handlers[message_type] = handler
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle an incoming message"""
        if message.is_expired():
            logger.warning(f"Received expired message {message.id}")
            return None
        
        handler = self.handlers.get(message.message_type)
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                logger.error(f"Error handling message {message.id}: {e}")
                return self._create_error_response(message, str(e))
        else:
            logger.warning(f"No handler for message type {message.message_type}")
            return None
    
    def _create_error_response(self, original_message: Message, error: str) -> Message:
        """Create an error response message"""
        return Message(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            priority=MessagePriority.HIGH,
            content={"error": error, "original_message_id": original_message.id},
            timestamp=datetime.now(timezone.utc),
            correlation_id=original_message.correlation_id
        )


class CommunicationBus:
    """Central communication bus for agent messaging"""
    
    def __init__(self):
        self.agents: Dict[str, MessageHandler] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[str]] = {}  # topic -> agent_ids
        self.pending_requests: Dict[str, asyncio.Future] = {}  # correlation_id -> future
        self.message_history: List[Message] = []
        self.max_history = 1000
        self.running = False
        self._processor_task: Optional[asyncio.Task] = None
    
    def register_agent(self, agent_id: str, handler: MessageHandler):
        """Register an agent with the communication bus"""
        self.agents[agent_id] = handler
        logger.info(f"Agent {agent_id} registered with communication bus")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the communication bus"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove from all subscriptions
            for topic, subscribers in self.subscribers.items():
                if agent_id in subscribers:
                    subscribers.remove(agent_id)
            logger.info(f"Agent {agent_id} unregistered from communication bus")
    
    async def send_message(self, message: Message) -> bool:
        """Send a message through the communication bus"""
        if message.is_expired():
            logger.warning(f"Attempting to send expired message {message.id}")
            return False
        
        await self.message_queue.put(message)
        self._add_to_history(message)
        return True
    
    async def send_request(
        self, 
        sender_id: str, 
        recipient_id: str, 
        content: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[Message]:
        """Send a request and wait for response"""
        correlation_id = str(uuid.uuid4())
        
        request = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.REQUEST,
            priority=MessagePriority.NORMAL,
            content=content,
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id
        )
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[correlation_id] = future
        
        try:
            await self.send_message(request)
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"Request {correlation_id} timed out")
            return None
        finally:
            self.pending_requests.pop(correlation_id, None)
    
    def subscribe(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        if agent_id not in self.subscribers[topic]:
            self.subscribers[topic].append(agent_id)
            logger.info(f"Agent {agent_id} subscribed to topic {topic}")
    
    def unsubscribe(self, agent_id: str, topic: str):
        """Unsubscribe an agent from a topic"""
        if topic in self.subscribers and agent_id in self.subscribers[topic]:
            self.subscribers[topic].remove(agent_id)
            logger.info(f"Agent {agent_id} unsubscribed from topic {topic}")
    
    async def publish(self, sender_id: str, topic: str, content: Dict[str, Any]):
        """Publish a message to a topic"""
        subscribers = self.subscribers.get(topic, [])
        
        for subscriber_id in subscribers:
            if subscriber_id != sender_id:  # Don't send to self
                message = Message(
                    id=str(uuid.uuid4()),
                    sender_id=sender_id,
                    recipient_id=subscriber_id,
                    message_type=MessageType.NOTIFICATION,
                    priority=MessagePriority.NORMAL,
                    content=content,
                    timestamp=datetime.now(timezone.utc),
                    topic=topic
                )
                await self.send_message(message)
    
    async def broadcast(self, sender_id: str, content: Dict[str, Any], exclude_self: bool = True):
        """Broadcast a message to all agents"""
        for agent_id in self.agents.keys():
            if exclude_self and agent_id == sender_id:
                continue
            
            message = Message(
                id=str(uuid.uuid4()),
                sender_id=sender_id,
                recipient_id=agent_id,
                message_type=MessageType.BROADCAST,
                priority=MessagePriority.NORMAL,
                content=content,
                timestamp=datetime.now(timezone.utc)
            )
            await self.send_message(message)
    
    async def start(self):
        """Start the message processing loop"""
        if self.running:
            return
        
        self.running = True
        self._processor_task = asyncio.create_task(self._message_processor())
        logger.info("Communication bus started")
    
    async def stop(self):
        """Stop the message processing loop"""
        self.running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Communication bus stopped")
    
    async def _message_processor(self):
        """Process messages from the queue"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._deliver_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _deliver_message(self, message: Message):
        """Deliver a message to its recipient(s)"""
        if message.recipient_id:
            # Direct message
            await self._deliver_to_agent(message, message.recipient_id)
        else:
            # Broadcast message
            for agent_id in self.agents.keys():
                if agent_id != message.sender_id:
                    await self._deliver_to_agent(message, agent_id)
    
    async def _deliver_to_agent(self, message: Message, agent_id: str):
        """Deliver a message to a specific agent"""
        handler = self.agents.get(agent_id)
        if handler:
            try:
                response = await handler.handle_message(message)
                if response:
                    # Handle response for request/response pattern
                    if message.message_type == MessageType.REQUEST and response.correlation_id:
                        future = self.pending_requests.get(response.correlation_id)
                        if future and not future.done():
                            future.set_result(response)
                    else:
                        # Send response back through the bus
                        await self.send_message(response)
            except Exception as e:
                logger.error(f"Error delivering message {message.id} to agent {agent_id}: {e}")
        else:
            logger.warning(f"Agent {agent_id} not found for message delivery")
    
    def _add_to_history(self, message: Message):
        """Add message to history"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
    
    def get_message_history(
        self, 
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message history with optional filters"""
        filtered_messages = self.message_history
        
        if agent_id:
            filtered_messages = [
                msg for msg in filtered_messages 
                if msg.sender_id == agent_id or msg.recipient_id == agent_id
            ]
        
        if message_type:
            filtered_messages = [
                msg for msg in filtered_messages 
                if msg.message_type == message_type
            ]
        
        return filtered_messages[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication bus statistics"""
        total_messages = len(self.message_history)
        message_types = {}
        priority_distribution = {}
        
        for message in self.message_history:
            message_types[message.message_type.value] = message_types.get(message.message_type.value, 0) + 1
            priority_distribution[message.priority.value] = priority_distribution.get(message.priority.value, 0) + 1
        
        return {
            "total_messages": total_messages,
            "active_agents": len(self.agents),
            "message_types": message_types,
            "priority_distribution": priority_distribution,
            "topics": list(self.subscribers.keys()),
            "pending_requests": len(self.pending_requests),
            "queue_size": self.message_queue.qsize()
        }


class AgentCommunicator:
    """Helper class for agents to communicate via the bus"""
    
    def __init__(self, agent_id: str, bus: CommunicationBus):
        self.agent_id = agent_id
        self.bus = bus
        self.handler = MessageHandler(agent_id)
        
        # Register with the bus
        self.bus.register_agent(agent_id, self.handler)
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler"""
        self.handler.register_handler(message_type, handler)
    
    async def send_to(self, recipient_id: str, content: Dict[str, Any], message_type: MessageType = MessageType.NOTIFICATION):
        """Send a message to a specific agent"""
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=MessagePriority.NORMAL,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        return await self.bus.send_message(message)
    
    async def request(self, recipient_id: str, content: Dict[str, Any], timeout: float = 30.0) -> Optional[Message]:
        """Send a request and wait for response"""
        return await self.bus.send_request(self.agent_id, recipient_id, content, timeout)
    
    async def broadcast(self, content: Dict[str, Any]):
        """Broadcast a message to all agents"""
        await self.bus.broadcast(self.agent_id, content)
    
    async def publish(self, topic: str, content: Dict[str, Any]):
        """Publish to a topic"""
        await self.bus.publish(self.agent_id, topic, content)
    
    def subscribe(self, topic: str):
        """Subscribe to a topic"""
        self.bus.subscribe(self.agent_id, topic)
    
    def unsubscribe(self, topic: str):
        """Unsubscribe from a topic"""
        self.bus.unsubscribe(self.agent_id, topic)


# Global communication bus instance
_communication_bus = CommunicationBus()


def get_communication_bus() -> CommunicationBus:
    """Get the global communication bus"""
    return _communication_bus


async def start_communication_system():
    """Start the global communication system"""
    await _communication_bus.start()


async def stop_communication_system():
    """Stop the global communication system"""
    await _communication_bus.stop()


def create_communicator(agent_id: str) -> AgentCommunicator:
    """Create a communicator for an agent"""
    return AgentCommunicator(agent_id, _communication_bus)
