"""
Test Configuration and Utilities
================================
Common test configuration, fixtures, and utility functions
"""

import os
import sys
import requests
import pandas as pd
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data"
SAMPLE_CSV = PROJECT_ROOT / "sample_sales_data.csv"

class TestConfig:
    """Test configuration constants"""
    BACKEND_URL = BACKEND_URL
    FRONTEND_URL = FRONTEND_URL
    TIMEOUT = 30
    RETRY_COUNT = 3

def check_servers_running():
    """Check if both backend and frontend servers are running"""
    try:
        backend_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        backend_ok = backend_response.status_code == 200
    except requests.exceptions.RequestException:
        backend_ok = False
    
    return {
        "backend": backend_ok,
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL
    }

def create_test_csv(filename="test_data.csv", rows=100):
    """Create a test CSV file with sample data"""
    import numpy as np
    
    # Use modern numpy random generator
    rng = np.random.default_rng(42)  # For reproducible results
    
    categories = ["Electronics", "Clothing", "Books", "Sports", "Home"]
    regions = ["North", "South", "East", "West", "Central"]
    
    data = {
        "id": range(1, rows + 1),
        "category": rng.choice(categories, rows),
        "region": rng.choice(regions, rows),
        "sales_amount": rng.uniform(100, 5000, rows).round(2),
        "quantity": rng.integers(1, 50, rows),
        "customer_segment": rng.choice(["Premium", "Standard", "Basic"], rows),
        "date": pd.date_range("2023-01-01", periods=rows, freq="D").strftime("%Y-%m-%d")
    }
    
    df = pd.DataFrame(data)
    filepath = TEST_DATA_DIR / filename
    
    # Create data directory if it doesn't exist
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    df.to_csv(filepath, index=False)
    return filepath

def upload_test_file(filepath):
    """Upload a test file and return file_id"""
    with open(filepath, 'rb') as file:
        files = {'file': (filepath.name, file, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
    
    if response.status_code == 200:
        return response.json()['file_id']
    else:
        raise RuntimeError(f"Upload failed: {response.text}")

def query_backend(file_id, query):
    """Send a query to the backend"""
    payload = {"query": query, "file_id": file_id}
    response = requests.post(f"{BACKEND_URL}/query", json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Query failed: {response.text}")

def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_test_result(success, message):
    """Print a formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
