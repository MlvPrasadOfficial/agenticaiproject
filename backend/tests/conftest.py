# Test configuration
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "INFO"
