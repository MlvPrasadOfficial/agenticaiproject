"""
Ollama LLM Configuration and Setup
Task 95: Implement Ollama local LLM integration (Llama 3.1 8b setup and configuration)
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field
import httpx
import asyncio

logger = logging.getLogger(__name__)


class OllamaConfig(BaseSettings):
    """Configuration for Ollama LLM integration"""
    
    # Ollama server configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=300, env="OLLAMA_TIMEOUT")  # 5 minutes
    
    # Model parameters
    temperature: float = Field(default=0.7, env="OLLAMA_TEMPERATURE")
    max_tokens: int = Field(default=2048, env="OLLAMA_MAX_TOKENS")
    top_p: float = Field(default=0.9, env="OLLAMA_TOP_P")
    top_k: int = Field(default=40, env="OLLAMA_TOP_K")
    
    # Performance settings
    num_predict: int = Field(default=-1, env="OLLAMA_NUM_PREDICT")  # -1 for no limit
    num_ctx: int = Field(default=4096, env="OLLAMA_NUM_CTX")  # Context window
    repeat_penalty: float = Field(default=1.1, env="OLLAMA_REPEAT_PENALTY")
    
    # Health check settings
    health_check_interval: int = Field(default=30, env="OLLAMA_HEALTH_CHECK_INTERVAL")
    max_retries: int = Field(default=3, env="OLLAMA_MAX_RETRIES")
    
    class Config:
        env_prefix = "OLLAMA_"
        case_sensitive = False


class OllamaManager:
    """Manager for Ollama LLM operations"""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.ollama_base_url,
            timeout=httpx.Timeout(self.config.ollama_timeout)
        )
        self._is_initialized = False
        self._model_loaded = False
    
    async def initialize(self) -> bool:
        """Initialize Ollama connection and load model"""
        try:
            # Check if Ollama server is running
            if not await self.health_check():
                logger.error("Ollama server is not accessible")
                return False
            
            # Pull/load the model if not available
            if not await self.is_model_available():
                logger.info(f"Pulling model {self.config.ollama_model}...")
                await self.pull_model()
            
            self._is_initialized = True
            self._model_loaded = True
            logger.info(f"Ollama initialized successfully with model {self.config.ollama_model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama server is healthy"""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def is_model_available(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return any(model.get("name", "").startswith(self.config.ollama_model) for model in models)
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    async def pull_model(self) -> bool:
        """Pull the specified model"""
        try:
            payload = {"name": self.config.ollama_model}
            response = await self.client.post("/api/pull", json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        try:
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Ollama"""
        if not self._is_initialized:
            raise RuntimeError("Ollama not initialized. Call initialize() first.")
        
        try:
            # Prepare the payload
            payload = {
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                    "top_k": kwargs.get("top_k", self.config.top_k),
                    "num_predict": kwargs.get("num_predict", self.config.num_predict),
                    "num_ctx": kwargs.get("num_ctx", self.config.num_ctx),
                    "repeat_penalty": kwargs.get("repeat_penalty", self.config.repeat_penalty),
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            # Make the request
            response = await self.client.post("/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "prompt_eval_duration": result.get("prompt_eval_duration", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                }
            else:
                return {
                    "success": False,
                    "error": f"Request failed with status {response.status_code}",
                    "response": ""
                }
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with Ollama using conversation format"""
        if not self._is_initialized:
            raise RuntimeError("Ollama not initialized. Call initialize() first.")
        
        try:
            payload = {
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", self.config.top_p),
                    "top_k": kwargs.get("top_k", self.config.top_k),
                    "num_predict": kwargs.get("num_predict", self.config.num_predict),
                    "num_ctx": kwargs.get("num_ctx", self.config.num_ctx),
                    "repeat_penalty": kwargs.get("repeat_penalty", self.config.repeat_penalty),
                }
            }
            
            response = await self.client.post("/api/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": result.get("message", {}),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "prompt_eval_duration": result.get("prompt_eval_duration", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                }
            else:
                return {
                    "success": False,
                    "error": f"Request failed with status {response.status_code}",
                    "message": {}
                }
                
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": {}
            }
    
    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
    
    def is_ready(self) -> bool:
        """Check if Ollama is ready for use"""
        return self._is_initialized and self._model_loaded


# Global instance
_ollama_manager: Optional[OllamaManager] = None


async def get_ollama_manager() -> OllamaManager:
    """Get the global Ollama manager instance"""
    global _ollama_manager
    
    if _ollama_manager is None:
        _ollama_manager = OllamaManager()
        await _ollama_manager.initialize()
    
    return _ollama_manager


async def shutdown_ollama_manager():
    """Shutdown the global Ollama manager"""
    global _ollama_manager
    
    if _ollama_manager:
        await _ollama_manager.close()
        _ollama_manager = None
