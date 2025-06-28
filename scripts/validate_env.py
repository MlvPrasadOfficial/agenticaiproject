#!/usr/bin/env python3
"""
Environment validation script for Enterprise Insights Copilot.
Validates that all required environment variables are set and have valid values.
"""

import os
import sys
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse


class EnvironmentValidator:
    """Validates environment configuration."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate(self) -> bool:
        """Validate all environment variables."""
        print("🔍 Validating environment configuration...")
        
        # Core environment settings
        self._validate_core_settings()
        
        # API and service URLs
        self._validate_urls()
        
        # Security settings
        self._validate_security()
        
        # AI/ML configuration
        self._validate_ai_ml()
        
        # File upload configuration
        self._validate_file_upload()
        
        # Report results
        self._report_results()
        
        return len(self.errors) == 0
    
    def _validate_core_settings(self):
        """Validate core environment settings."""
        required_vars = {
            'ENVIRONMENT': ['development', 'staging', 'production'],
            'NODE_ENV': ['development', 'production'],
            'LOG_LEVEL': ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        }
        
        for var, allowed_values in required_vars.items():
            value = os.getenv(var)
            if not value:
                self.errors.append(f"❌ {var} is required")
            elif value not in allowed_values:
                self.errors.append(f"❌ {var} must be one of: {', '.join(allowed_values)}")
    
    def _validate_urls(self):
        """Validate URL configurations."""
        url_vars = [
            'BACKEND_URL',
            'API_BASE_URL',
            'NEXT_PUBLIC_API_URL'
        ]
        
        for var in url_vars:
            value = os.getenv(var)
            if not value:
                self.errors.append(f"❌ {var} is required")
                continue
                
            try:
                parsed = urlparse(value)
                if not parsed.scheme or not parsed.netloc:
                    self.errors.append(f"❌ {var} must be a valid URL")
            except Exception:
                self.errors.append(f"❌ {var} is not a valid URL")
    
    def _validate_security(self):
        """Validate security configuration."""
        jwt_secret = os.getenv('JWT_SECRET')
        if not jwt_secret:
            self.errors.append("❌ JWT_SECRET is required")
        elif len(jwt_secret) < 32:
            self.warnings.append("⚠️  JWT_SECRET should be at least 32 characters long")
        
        rate_limit = os.getenv('RATE_LIMIT_PER_MINUTE')
        if rate_limit:
            try:
                rate_limit_int = int(rate_limit)
                if rate_limit_int <= 0:
                    self.errors.append("❌ RATE_LIMIT_PER_MINUTE must be positive")
            except ValueError:
                self.errors.append("❌ RATE_LIMIT_PER_MINUTE must be a number")
    
    def _validate_ai_ml(self):
        """Validate AI/ML service configuration."""
        ollama_url = os.getenv('OLLAMA_URL')
        if ollama_url:
            try:
                parsed = urlparse(ollama_url)
                if not parsed.scheme or not parsed.netloc:
                    self.warnings.append("⚠️  OLLAMA_URL should be a valid URL")
            except Exception:
                self.warnings.append("⚠️  OLLAMA_URL is not a valid URL")
        
        # Pinecone configuration (optional but recommended)
        pinecone_key = os.getenv('PINECONE_API_KEY')
        pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
        
        if not pinecone_key or pinecone_key == 'your_pinecone_api_key_here':
            self.warnings.append("⚠️  PINECONE_API_KEY not configured (vector storage disabled)")
        
        if not pinecone_env or pinecone_env == 'your_pinecone_environment_here':
            self.warnings.append("⚠️  PINECONE_ENVIRONMENT not configured")
    
    def _validate_file_upload(self):
        """Validate file upload configuration."""
        max_size = os.getenv('MAX_FILE_SIZE_MB')
        if max_size:
            try:
                max_size_int = int(max_size)
                if max_size_int <= 0:
                    self.errors.append("❌ MAX_FILE_SIZE_MB must be positive")
                elif max_size_int > 100:
                    self.warnings.append("⚠️  MAX_FILE_SIZE_MB is quite large (>100MB)")
            except ValueError:
                self.errors.append("❌ MAX_FILE_SIZE_MB must be a number")
        
        allowed_types = os.getenv('ALLOWED_FILE_TYPES')
        if allowed_types:
            types = [t.strip() for t in allowed_types.split(',')]
            valid_types = ['csv', 'xlsx', 'json', 'txt', 'xml']
            invalid_types = [t for t in types if t not in valid_types]
            if invalid_types:
                self.warnings.append(f"⚠️  Unknown file types: {', '.join(invalid_types)}")
    
    def _report_results(self):
        """Report validation results."""
        print("\n" + "="*60)
        print("ENVIRONMENT VALIDATION RESULTS")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All environment variables are properly configured!")
        elif not self.errors:
            print(f"\n✅ Configuration is valid (with {len(self.warnings)} warnings)")
        else:
            print(f"\n❌ Configuration has {len(self.errors)} errors that must be fixed")
        
        print("\n" + "="*60)


def load_env_file(env_file: str = '.env'):
    """Load environment variables from file."""
    if os.path.exists(env_file):
        print(f"📁 Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"⚠️  Environment file {env_file} not found")


def main():
    """Main validation function."""
    print("🚀 Enterprise Insights Copilot - Environment Validation")
    print("="*60)
    
    # Load environment files
    env_files = ['.env', '.env.local', '.env.development']
    for env_file in env_files:
        load_env_file(env_file)
    
    # Validate configuration
    validator = EnvironmentValidator()
    is_valid = validator.validate()
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
