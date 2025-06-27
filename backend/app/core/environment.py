"""
Enterprise Insights Copilot - Multi-Environment Support
MAANG-level environment configuration management
"""

from typing import Dict, Any
from app.core.config import settings, Environment
from app.core.logging import get_logger

logger = get_logger(__name__)


class EnvironmentConfig:
    """Environment-specific configuration manager"""
    
    def __init__(self):
        self.current_env = settings.ENVIRONMENT
        self.config = self._load_environment_config()
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        
        base_config = {
            "database": {
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "echo": False,
            },
            "security": {
                "access_token_expire": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_expire": settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            },
            "performance": {
                "cache_ttl": settings.CACHE_TTL,
                "request_timeout": settings.REQUEST_TIMEOUT,
            },
            "features": {
                "file_upload": settings.ENABLE_FILE_UPLOAD,
                "data_preview": settings.ENABLE_DATA_PREVIEW,
                "ai_agents": settings.ENABLE_AI_AGENTS,
                "rag": settings.ENABLE_RAG,
            }
        }
        
        # Environment-specific overrides
        if self.current_env == Environment.DEVELOPMENT:
            return {**base_config, **self._development_config()}
        elif self.current_env == Environment.STAGING:
            return {**base_config, **self._staging_config()}
        elif self.current_env == Environment.PRODUCTION:
            return {**base_config, **self._production_config()}
        else:
            logger.warning(f"Unknown environment: {self.current_env}, using development config")
            return {**base_config, **self._development_config()}
    
    def _development_config(self) -> Dict[str, Any]:
        """Development environment configuration"""
        return {
            "debug": True,
            "reload": True,
            "log_level": "DEBUG",
            "database": {
                "echo": True,  # SQL query logging
                "pool_size": 5,
                "max_overflow": 10,
            },
            "security": {
                "access_token_expire": 60,  # 1 hour for development
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            },
            "performance": {
                "cache_ttl": 300,  # 5 minutes for quick testing
                "request_timeout": 60,  # Longer timeout for debugging
            },
            "agents": {
                "timeout": 600,  # 10 minutes for debugging
                "temperature": 0.2,  # More predictable responses
                "max_retries": 1,  # Fewer retries for faster iteration
            },
            "monitoring": {
                "enable_metrics": True,
                "enable_tracing": True,
                "detailed_logs": True,
            }
        }
    
    def _staging_config(self) -> Dict[str, Any]:
        """Staging environment configuration"""
        return {
            "debug": False,
            "reload": False,
            "log_level": "INFO",
            "database": {
                "echo": False,
                "pool_size": 10,
                "max_overflow": 20,
            },
            "security": {
                "access_token_expire": 30,  # 30 minutes
                "cors_origins": ["https://staging.your-domain.com"],
            },
            "performance": {
                "cache_ttl": 1800,  # 30 minutes
                "request_timeout": 30,
            },
            "agents": {
                "timeout": 300,  # 5 minutes
                "temperature": 0.1,
                "max_retries": 2,
            },
            "monitoring": {
                "enable_metrics": True,
                "enable_tracing": True,
                "detailed_logs": True,
            }
        }
    
    def _production_config(self) -> Dict[str, Any]:
        """Production environment configuration"""
        return {
            "debug": False,
            "reload": False,
            "log_level": "INFO",
            "database": {
                "echo": False,
                "pool_size": 20,
                "max_overflow": 40,
            },
            "security": {
                "access_token_expire": 15,  # 15 minutes for security
                "cors_origins": ["https://your-domain.com"],
            },
            "performance": {
                "cache_ttl": 3600,  # 1 hour
                "request_timeout": 30,
            },
            "agents": {
                "timeout": 300,  # 5 minutes
                "temperature": 0.1,
                "max_retries": 3,
            },
            "monitoring": {
                "enable_metrics": True,
                "enable_tracing": True,
                "detailed_logs": False,  # Reduce log verbosity
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for current environment"""
        return self.get('database', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration for current environment"""
        return self.get('security', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration for current environment"""
        return self.get('performance', {})
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration for current environment"""
        return self.get('agents', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration for current environment"""
        return self.get('monitoring', {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled in current environment"""
        return self.get(f'features.{feature}', False)
    
    def log_configuration(self) -> None:
        """Log current configuration (excluding sensitive data)"""
        safe_config = {
            "environment": self.current_env,
            "debug": self.get('debug'),
            "log_level": self.get('log_level'),
            "database_pool_size": self.get('database.pool_size'),
            "cache_ttl": self.get('performance.cache_ttl'),
            "features": self.get('features', {}),
            "monitoring": self.get('monitoring', {}),
        }
        
        logger.info("Environment configuration loaded", config=safe_config)


def get_environment_config() -> EnvironmentConfig:
    """Get environment configuration instance"""
    return EnvironmentConfig()


# Global environment configuration
env_config = get_environment_config()

# Log configuration on import
env_config.log_configuration()
