# Base Agent Class - Foundation for all agents

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
from datetime import datetime

import httpx
from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.ollama_client = None
        self.execution_history = []
    
    async def get_ollama_client(self) -> httpx.AsyncClient:
        """Get or create Ollama HTTP client"""
        if not self.ollama_client:
            self.ollama_client = httpx.AsyncClient(
                base_url=settings.OLLAMA_BASE_URL,
                timeout=30.0
            )
        return self.ollama_client
    
    async def call_ollama(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Call Ollama LLM with prompt"""
        try:
            client = await self.get_ollama_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.post("/api/chat", json={
                "model": model or settings.OLLAMA_MODEL,
                "messages": messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                "stream": False
            })
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error calling Ollama in {self.agent_name}: {str(e)}")
            return f"Error: {str(e)}"
    
    async def execute_with_retry(
        self,
        state: Dict[str, Any],
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ) -> Dict[str, Any]:
        """Execute agent with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                result = await self.execute(state)
                execution_time = time.time() - start_time
                
                # Log successful execution
                self.execution_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "execution_time": execution_time,
                    "attempt": attempt + 1
                })
                
                return result
            
            except Exception as e:
                last_error = e
                wait_time = backoff_factor ** attempt
                
                print(f"⚠️ {self.agent_name} attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    # Log failed execution
                    self.execution_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error": str(e),
                        "attempts": max_retries
                    })
        
        # Return error result if all retries failed
        return {
            "error": f"Failed after {max_retries} attempts: {str(last_error)}",
            "agent": self.agent_name,
            "status": "failed"
        }
    
    def validate_input(self, state: Dict[str, Any]) -> bool:
        """Validate input state for agent execution"""
        required_fields = self.get_required_fields()
        
        for field in required_fields:
            if field not in state or state[field] is None:
                print(f"❌ Missing required field '{field}' for {self.agent_name}")
                return False
        
        return True
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        successful = [h for h in self.execution_history if h.get("success", False)]
        failed = [h for h in self.execution_history if not h.get("success", True)]
        
        avg_time = 0
        if successful:
            avg_time = sum(h.get("execution_time", 0) for h in successful) / len(successful)
        
        return {
            "total_executions": len(self.execution_history),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.execution_history) if self.execution_history else 0,
            "average_execution_time": avg_time
        }
    
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main logic"""
        pass
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Get list of required fields in state"""
        pass
    
    def get_agent_prompt(self, task_description: str, context: str = "") -> str:
        """Generate agent-specific prompt"""
        return f"""
You are the {self.agent_name} in an enterprise business intelligence system.

Task: {task_description}

Context: {context}

Please provide a detailed, actionable response based on your specialized role.
Focus on accuracy, business relevance, and clear communication.
"""
    
    def __del__(self):
        """Cleanup on agent destruction"""
        if self.ollama_client:
            asyncio.create_task(self.ollama_client.aclose())
