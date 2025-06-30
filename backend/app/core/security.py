"""
Security utilities for JWT authentication, rate limiting, and input validation
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Security, Request, FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import redis
from pydantic import BaseModel, validator
import re
import time
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# JWT Security
security = HTTPBearer()

# Redis for rate limiting (fallback to in-memory if Redis not available)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError, Exception):
    redis_client = None

# In-memory fallback for rate limiting
rate_limit_store = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# Rate limiting
class RateLimiter:
    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        current_time = int(time.time())
        window_start = current_time - (current_time % self.period)
        
        if redis_client:
            # Use Redis for distributed rate limiting
            pipe = redis_client.pipeline()
            pipe.incr(f"rate_limit:{key}:{window_start}")
            pipe.expire(f"rate_limit:{key}:{window_start}", self.period)
            results = pipe.execute()
            return results[0] <= self.calls
        else:
            # Fallback to in-memory
            if key not in rate_limit_store:
                rate_limit_store[key] = {}
            
            if window_start not in rate_limit_store[key]:
                rate_limit_store[key][window_start] = 0
            
            rate_limit_store[key][window_start] += 1
            
            # Clean old windows
            windows_to_remove = [w for w in rate_limit_store[key].keys() if w < window_start - self.period]
            for old_window in windows_to_remove:
                del rate_limit_store[key][old_window]
            
            return rate_limit_store[key][window_start] <= self.calls

# Create rate limiter instances
default_rate_limiter = RateLimiter(calls=100, period=60)  # 100 calls per minute
strict_rate_limiter = RateLimiter(calls=10, period=60)    # 10 calls per minute

def rate_limit(limiter: RateLimiter = default_rate_limiter):
    """Rate limiting decorator"""
    def decorator(request: Request):
        client_ip = request.client.host if request.client else "unknown"
        if not limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        return True
    return decorator

# Input validation
class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security"""
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for allowed characters
        pattern = r'^[a-zA-Z0-9._-]+$'
        return re.match(pattern, filename) is not None
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize input string"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>\"\'&]', '', text)
        
        # Limit length
        return text[:max_length]

# Middleware setup
def setup_security_middleware(app: FastAPI):
    """Configure security middleware for the FastAPI application"""
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.render.com"]
    )
    
    # Add session middleware with secure settings
    app.add_middleware(
        SessionMiddleware,
        secret_key=SECRET_KEY,
        https_only=True if os.getenv("ENVIRONMENT") == "production" else False,
        same_site="strict"
    )
    
    # Add security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
    
    # Add rate limiting middleware
    rate_limiter = RateLimiter(calls=100, period=60)
    
    @app.middleware("http")
    async def rate_limit_middleware(request, call_next):
        client_ip = request.client.host
        
        if not rate_limiter.is_allowed(client_ip):
            return HTTPException(
                status_code=429,
                detail="Too many requests"
            )
        
        response = await call_next(request)
        return response
