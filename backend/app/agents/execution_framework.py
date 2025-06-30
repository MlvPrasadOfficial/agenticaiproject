"""
Agent Execution Framework
Task 102: Create agent execution framework
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Type, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from contextlib import asynccontextmanager
import traceback
import uuid
from dataclasses import dataclass, field

from app.agents.base_agent import BaseAgent, AgentRegistry, get_agent_registry
from app.agents.io_models import AgentInputV2, AgentOutputV2, PerformanceMetrics
from app.agents.state_management import get_state_manager, StateType, StatePersistence
from app.agents.memory import get_memory_manager, MemoryType, MemoryImportance
from app.agents.communication import get_communication_bus, create_communicator

logger = logging.getLogger(__name__)


class ExecutionPriority(str, Enum):
    """Execution priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ExecutionMode(str, Enum):
    """Execution modes"""
    SYNC = "sync"        # Synchronous execution
    ASYNC = "async"      # Asynchronous execution
    PARALLEL = "parallel"  # Parallel execution
    SEQUENTIAL = "sequential"  # Sequential execution
    PIPELINE = "pipeline"  # Pipeline execution


class ResourceType(str, Enum):
    """Resource types for execution"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    NETWORK = "network"
    STORAGE = "storage"


@dataclass
class ResourceLimit:
    """Resource limit configuration"""
    resource_type: ResourceType
    limit: float
    unit: str
    soft_limit: Optional[float] = None


@dataclass
class ExecutionContext:
    """Context for agent execution"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    mode: ExecutionMode = ExecutionMode.ASYNC
    timeout: Optional[float] = None
    resource_limits: List[ResourceLimit] = field(default_factory=list)
    environment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult:
    """Result of agent execution"""
    
    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self.status = "pending"
        self.output: Optional[AgentOutputV2] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.metrics: Optional[PerformanceMetrics] = None
        self.resource_usage: Dict[str, float] = {}
        self.logs: List[Dict[str, Any]] = []
    
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if execution is complete"""
        return self.status in ["completed", "failed", "cancelled"]
    
    @property
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.status == "completed" and self.error is None
    
    def add_log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Add log entry"""
        self.logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        })


class ExecutionQueue:
    """Queue for managing agent execution requests"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        self.pending_executions: Dict[str, ExecutionResult] = {}
        self.completed_executions: Dict[str, ExecutionResult] = {}
        self.max_completed = 100  # Keep last 100 completed executions
    
    async def enqueue(
        self, 
        agent_input: AgentInputV2, 
        context: ExecutionContext
    ) -> str:
        """Enqueue execution request"""
        if self.queue.full():
            raise RuntimeError("Execution queue is full")
        
        # Create execution result
        result = ExecutionResult(context.execution_id)
        self.pending_executions[context.execution_id] = result
        
        # Priority mapping (lower number = higher priority)
        priority_map = {
            ExecutionPriority.URGENT: 0,
            ExecutionPriority.HIGH: 1,
            ExecutionPriority.NORMAL: 2,
            ExecutionPriority.LOW: 3
        }
        
        priority = priority_map.get(context.priority, 2)
        
        # Add to queue with priority and timestamp as tie-breaker
        item = (priority, context.created_at.timestamp(), agent_input, context)
        await self.queue.put(item)
        
        result.add_log("info", f"Execution {context.execution_id} enqueued with priority {context.priority}")
        return context.execution_id
    
    async def dequeue(self) -> Optional[tuple]:
        """Dequeue next execution request"""
        try:
            _, _, agent_input, context = await self.queue.get()
            return agent_input, context
        except asyncio.QueueEmpty:
            return None
    
    def get_result(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get execution result"""
        # Check pending first
        if execution_id in self.pending_executions:
            return self.pending_executions[execution_id]
        
        # Check completed
        return self.completed_executions.get(execution_id)
    
    def complete_execution(self, execution_id: str, result: ExecutionResult):
        """Mark execution as complete"""
        if execution_id in self.pending_executions:
            del self.pending_executions[execution_id]
        
        self.completed_executions[execution_id] = result
        
        # Trim completed executions if too many
        if len(self.completed_executions) > self.max_completed:
            oldest_id = min(
                self.completed_executions.keys(),
                key=lambda x: self.completed_executions[x].end_time or datetime.min.replace(tzinfo=timezone.utc)
            )
            del self.completed_executions[oldest_id]
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": self.queue.qsize(),
            "pending_executions": len(self.pending_executions),
            "completed_executions": len(self.completed_executions),
            "max_size": self.max_size
        }


class ResourceMonitor:
    """Monitor resource usage during execution"""
    
    def __init__(self):
        self.monitors: Dict[ResourceType, Callable] = {}
        self._setup_default_monitors()
    
    def _setup_default_monitors(self):
        """Setup default resource monitors"""
        import psutil
        
        def cpu_usage():
            return psutil.cpu_percent(interval=0.1)
        
        def memory_usage():
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        
        self.monitors[ResourceType.CPU] = cpu_usage
        self.monitors[ResourceType.MEMORY] = memory_usage
    
    def add_monitor(self, resource_type: ResourceType, monitor_func: Callable):
        """Add custom resource monitor"""
        self.monitors[resource_type] = monitor_func
    
    def get_usage(self, resource_type: ResourceType) -> Optional[float]:
        """Get current resource usage"""
        monitor = self.monitors.get(resource_type)
        if monitor:
            try:
                return monitor()
            except Exception as e:
                logger.error(f"Error monitoring {resource_type}: {e}")
        return None
    
    def get_all_usage(self) -> Dict[str, float]:
        """Get usage for all monitored resources"""
        usage = {}
        for resource_type in self.monitors:
            value = self.get_usage(resource_type)
            if value is not None:
                usage[resource_type.value] = value
        return usage
    
    def check_limits(self, limits: List[ResourceLimit]) -> List[str]:
        """Check if any resource limits are exceeded"""
        violations = []
        
        for limit in limits:
            current_usage = self.get_usage(limit.resource_type)
            if current_usage is not None:
                if current_usage > limit.limit:
                    violations.append(
                        f"{limit.resource_type.value} usage {current_usage:.2f}{limit.unit} "
                        f"exceeds limit {limit.limit}{limit.unit}"
                    )
                elif limit.soft_limit and current_usage > limit.soft_limit:
                    logger.warning(
                        f"{limit.resource_type.value} usage {current_usage:.2f}{limit.unit} "
                        f"exceeds soft limit {limit.soft_limit}{limit.unit}"
                    )
        
        return violations


class ExecutionEngine:
    """Core execution engine for agents"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.queue = ExecutionQueue()
        self.resource_monitor = ResourceMonitor()
        self.agent_registry = get_agent_registry()
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_hooks: Dict[str, List[Callable]] = {
            "pre_execution": [],
            "post_execution": [],
            "on_error": [],
            "on_timeout": []
        }
        self.running = False
        self._worker_tasks: List[asyncio.Task] = []
    
    def add_hook(self, hook_type: str, hook_func: Callable):
        """Add execution hook"""
        if hook_type in self.execution_hooks:
            self.execution_hooks[hook_type].append(hook_func)
    
    async def execute(
        self, 
        agent_input: AgentInputV2, 
        agent_id: Optional[str] = None,
        context: Optional[ExecutionContext] = None
    ) -> str:
        """Submit execution request and return execution ID"""
        
        # Create context if not provided
        if context is None:
            context = ExecutionContext(agent_id=agent_id or "default")
        
        # Validate agent exists or can be created
        if agent_id and not self.agent_registry.get_agent(agent_id):
            # Try to create agent if not exists
            try:
                await self.agent_registry.create_agent("conversation", agent_id)
            except Exception as e:
                raise RuntimeError(f"Failed to create agent {agent_id}: {e}")
        
        # Enqueue execution
        execution_id = await self.queue.enqueue(agent_input, context)
        
        # Start processing if not running
        if not self.running:
            await self.start()
        
        return execution_id
    
    async def get_result(self, execution_id: str, timeout: Optional[float] = None) -> ExecutionResult:
        """Get execution result, optionally waiting for completion"""
        result = self.queue.get_result(execution_id)
        if not result:
            raise ValueError(f"Execution {execution_id} not found")
        
        if timeout and not result.is_complete:
            # Wait for completion with timeout
            start_time = datetime.now(timezone.utc)
            while not result.is_complete:
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                if elapsed >= timeout:
                    break
                await asyncio.sleep(0.1)
        
        return result
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel pending or active execution"""
        # Check if it's an active execution
        if execution_id in self.active_executions:
            task = self.active_executions[execution_id]
            task.cancel()
            del self.active_executions[execution_id]
            
            # Update result
            result = self.queue.get_result(execution_id)
            if result:
                result.status = "cancelled"
                result.end_time = datetime.now(timezone.utc)
                self.queue.complete_execution(execution_id, result)
            
            return True
        
        # Check if it's pending
        result = self.queue.get_result(execution_id)
        if result and not result.is_complete:
            result.status = "cancelled"
            result.end_time = datetime.now(timezone.utc)
            self.queue.complete_execution(execution_id, result)
            return True
        
        return False
    
    async def start(self):
        """Start the execution engine"""
        if self.running:
            return
        
        self.running = True
        
        # Start worker tasks
        for i in range(self.max_concurrent):
            task = asyncio.create_task(self._worker_loop())
            self._worker_tasks.append(task)
        
        logger.info(f"Execution engine started with {self.max_concurrent} workers")
    
    async def stop(self):
        """Stop the execution engine"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel all worker tasks
        for task in self._worker_tasks:
            task.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()
        
        # Cancel active executions
        for task in self.active_executions.values():
            task.cancel()
        self.active_executions.clear()
        
        logger.info("Execution engine stopped")
    
    async def _worker_loop(self):
        """Main worker loop for processing executions"""
        while self.running:
            try:
                # Get next execution from queue
                item = await self.queue.dequeue()
                if not item:
                    await asyncio.sleep(0.1)
                    continue
                
                agent_input, context = item
                
                # Execute asynchronously
                task = asyncio.create_task(
                    self._execute_agent(agent_input, context)
                )
                self.active_executions[context.execution_id] = task
                
                # Wait for completion and cleanup
                try:
                    await task
                finally:
                    self.active_executions.pop(context.execution_id, None)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_agent(self, agent_input: AgentInputV2, context: ExecutionContext):
        """Execute agent with full lifecycle management"""
        result = self.queue.get_result(context.execution_id)
        if not result:
            return
        
        try:
            result.status = "running"
            result.start_time = datetime.now(timezone.utc)
            result.add_log("info", f"Starting execution for agent {context.agent_id}")
            
            # Run pre-execution hooks
            await self._run_hooks("pre_execution", agent_input, context, result)
            
            # Get or create agent
            agent = await self._get_or_create_agent(context.agent_id)
            if not agent:
                raise RuntimeError(f"Failed to get agent {context.agent_id}")
            
            # Setup execution environment
            await self._setup_execution_environment(agent, context, result)
            
            # Monitor resources during execution
            resource_violations = self.resource_monitor.check_limits(context.resource_limits)
            if resource_violations:
                raise RuntimeError(f"Resource limit violations: {', '.join(resource_violations)}")
            
            # Execute agent with timeout
            if context.timeout:
                output = await asyncio.wait_for(
                    agent.execute(self._convert_input(agent_input)),
                    timeout=context.timeout
                )
            else:
                output = await agent.execute(self._convert_input(agent_input))
            
            # Process output
            result.output = self._convert_output(output, context)
            result.status = "completed"
            result.add_log("info", "Execution completed successfully")
            
            # Run post-execution hooks
            await self._run_hooks("post_execution", agent_input, context, result)
            
        except asyncio.TimeoutError:
            result.status = "failed"
            result.error = TimeoutError(f"Execution timed out after {context.timeout} seconds")
            result.add_log("error", f"Execution timed out after {context.timeout} seconds")
            await self._run_hooks("on_timeout", agent_input, context, result)
            
        except Exception as e:
            result.status = "failed"
            result.error = e
            result.add_log("error", f"Execution failed: {str(e)}")
            result.add_log("debug", traceback.format_exc())
            await self._run_hooks("on_error", agent_input, context, result)
            
        finally:
            result.end_time = datetime.now(timezone.utc)
            result.resource_usage = self.resource_monitor.get_all_usage()
            
            # Create performance metrics
            result.metrics = PerformanceMetrics(
                execution_time=result.duration or 0.0,
                token_usage=getattr(result.output, 'metrics', {}).get('token_usage', {}),
                memory_usage=int(result.resource_usage.get('memory', 0) * 1024 * 1024),  # Convert MB to bytes
                api_calls=1,  # At least one call to the agent
                cache_hits=0,  # Would be tracked by caching system
                cache_misses=0
            )
            
            # Complete execution
            self.queue.complete_execution(context.execution_id, result)
            result.add_log("info", f"Execution completed in {result.duration:.2f} seconds")
    
    async def _get_or_create_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get existing agent or create new one"""
        agent = self.agent_registry.get_agent(agent_id)
        if not agent:
            # Try to create default conversation agent
            try:
                await self.agent_registry.create_agent("conversation", agent_id)
                agent = self.agent_registry.get_agent(agent_id)
            except Exception as e:
                logger.error(f"Failed to create agent {agent_id}: {e}")
        return agent
    
    async def _setup_execution_environment(self, agent: BaseAgent, context: ExecutionContext, result: ExecutionResult):
        """Setup execution environment for agent"""
        try:
            # Setup state management
            state_manager = get_state_manager(context.agent_id)
            if context.session_id:
                state_manager.set_variable("session_id", context.session_id, StateType.SESSION, StatePersistence.SESSION)
            
            # Setup memory management
            memory_manager = get_memory_manager(context.agent_id)
            
            # Setup communication
            communicator = create_communicator(context.agent_id)
            
            result.add_log("info", "Execution environment setup completed")
            
        except Exception as e:
            result.add_log("warning", f"Failed to setup execution environment: {e}")
    
    def _convert_input(self, agent_input: AgentInputV2):
        """Convert enhanced input to base agent input"""
        from app.agents.base_agent import AgentInput
        
        return AgentInput(
            message=agent_input.message,
            context=agent_input.context.model_dump() if hasattr(agent_input.context, 'model_dump') else {},
            session_id=agent_input.context.session_id,
            user_id=agent_input.context.user_id,
            metadata={"request_id": agent_input.request_id, "priority": agent_input.priority}
        )
    
    def _convert_output(self, agent_output, context: ExecutionContext) -> AgentOutputV2:
        """Convert base agent output to enhanced output"""
        from app.agents.io_models import PerformanceMetrics
        
        return AgentOutputV2(
            response=agent_output.response,
            status=agent_output.status,
            agent_id=context.agent_id,
            request_id=context.execution_id,
            confidence=None,  # Would be populated if agent provides confidence
            reasoning=None,   # Would be populated if agent provides reasoning
            suggestions=agent_output.suggestions,
            metrics=PerformanceMetrics(
                execution_time=agent_output.execution_time,
                token_usage=agent_output.token_usage
            ),
            content_length=len(agent_output.response),
            metadata=agent_output.metadata
        )
    
    async def _run_hooks(self, hook_type: str, agent_input: AgentInputV2, context: ExecutionContext, result: ExecutionResult):
        """Run execution hooks"""
        hooks = self.execution_hooks.get(hook_type, [])
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(agent_input, context, result)
                else:
                    hook(agent_input, context, result)
            except Exception as e:
                logger.error(f"Hook {hook_type} failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution engine statistics"""
        return {
            "running": self.running,
            "max_concurrent": self.max_concurrent,
            "active_executions": len(self.active_executions),
            "worker_tasks": len(self._worker_tasks),
            "queue_stats": self.queue.get_queue_stats(),
            "resource_usage": self.resource_monitor.get_all_usage()
        }


# Global execution engine instance
_execution_engine: Optional[ExecutionEngine] = None


def get_execution_engine() -> ExecutionEngine:
    """Get the global execution engine"""
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine


async def start_execution_system():
    """Start the global execution system"""
    engine = get_execution_engine()
    await engine.start()


async def stop_execution_system():
    """Stop the global execution system"""
    engine = get_execution_engine()
    await engine.stop()


# Convenience functions


async def execute_agent(
    message: str,
    agent_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None
) -> ExecutionResult:
    """High-level function to execute an agent"""
    from app.agents.io_models import AgentInputV2, ContextData
    
    # Create input
    agent_input = AgentInputV2(
        message=message,
        context=ContextData(**(context or {}))
    )
    
    # Create execution context
    execution_context = ExecutionContext(
        agent_id=agent_id or "default",
        timeout=timeout
    )
    
    # Execute
    engine = get_execution_engine()
    execution_id = await engine.execute(agent_input, agent_id, execution_context)
    
    # Wait for result
    return await engine.get_result(execution_id, timeout)


async def execute_agent_async(
    message: str,
    agent_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Execute agent asynchronously and return execution ID"""
    from app.agents.io_models import AgentInputV2, ContextData
    
    agent_input = AgentInputV2(
        message=message,
        context=ContextData(**(context or {}))
    )
    
    execution_context = ExecutionContext(agent_id=agent_id or "default")
    
    engine = get_execution_engine()
    return await engine.execute(agent_input, agent_id, execution_context)
