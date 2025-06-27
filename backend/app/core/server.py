"""
Enterprise Insights Copilot - Uvicorn Server Configuration
MAANG-level production-ready server setup
"""

import uvicorn
from app.core.config import settings
from app.core.logging import get_logger
from app.core.environment import env_config

logger = get_logger(__name__)


def create_uvicorn_config():
    """Create uvicorn configuration based on environment"""
    
    # Base configuration
    config = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": env_config.get('reload', False),
        "log_level": env_config.get('log_level', 'info').lower(),
        "access_log": True,
        "use_colors": env_config.get('debug', False),
        "loop": "auto",  # Use best available event loop
        "http": "auto",  # Use best available HTTP implementation
    }
    
    # Environment-specific configurations
    if settings.is_production:
        config.update({
            "workers": 4,  # Multiple workers for production
            "log_config": None,  # Use our custom logging
            "access_log": False,  # Reduce log verbosity
            "server_header": False,  # Don't expose server info
            "date_header": False,  # Don't expose date header
        })
    
    elif settings.is_staging:
        config.update({
            "workers": 2,  # Fewer workers for staging
            "reload": False,
            "debug": False,
        })
    
    else:  # Development
        config.update({
            "reload": True,
            "reload_dirs": ["app"],
            "reload_delay": 0.25,
            "debug": True,
        })
    
    # SSL configuration for production
    if settings.is_production and hasattr(settings, 'SSL_CERT_PATH'):
        config.update({
            "ssl_keyfile": getattr(settings, 'SSL_KEY_PATH', None),
            "ssl_certfile": getattr(settings, 'SSL_CERT_PATH', None),
        })
    
    return config


def run_server():
    """Run the uvicorn server with proper configuration"""
    
    config = create_uvicorn_config()
    
    logger.info(
        "Starting uvicorn server",
        host=config["host"],
        port=config["port"],
        environment=settings.ENVIRONMENT,
        workers=config.get("workers", 1),
        reload=config["reload"]
    )
    
    try:
        uvicorn.run(**config)
    except Exception as e:
        logger.error("Failed to start server", error=str(e), exc_info=True)
        raise


if __name__ == "__main__":
    run_server()
