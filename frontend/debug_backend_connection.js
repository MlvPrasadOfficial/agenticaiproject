// Debug script to test backend connectivity
const API_BASE_URL = 'http://localhost:8000';

async function testBackendEndpoints() {
  console.log('🔍 Testing backend endpoints...\n');
  
  const endpoints = [
    '/',
    '/health',
    '/api/v1/health',
    '/docs'
  ];
  
  for (const endpoint of endpoints) {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`Testing: ${url}`);
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      console.log(`  Status: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.text();
        console.log(`  Response: ${data.substring(0, 100)}${data.length > 100 ? '...' : ''}`);
      }
      
    } catch (error) {
      console.log(`  Error: ${error.message}`);
    }
    
    console.log('');
  }
}

// Test different health check approaches
async function testHealthChecks() {
  console.log('🏥 Testing health check methods...\n');
  
  const healthMethods = [
    { name: 'Current frontend method', url: `${API_BASE_URL}/health` },
    { name: 'Correct API method', url: `${API_BASE_URL}/api/v1/health` },
    { name: 'Root endpoint', url: `${API_BASE_URL}/` }
  ];
  
  for (const method of healthMethods) {
    console.log(`${method.name}: ${method.url}`);
    
    try {
      const response = await fetch(method.url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const isHealthy = response.ok;
      console.log(`  Healthy: ${isHealthy ? '✅ YES' : '❌ NO'} (Status: ${response.status})`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`  Data:`, data);
      }
      
    } catch (error) {
      console.log(`  Healthy: ❌ NO (Error: ${error.message})`);
    }
    
    console.log('');
  }
}

// Run tests
testBackendEndpoints().then(() => {
  console.log('='.repeat(50));
  return testHealthChecks();
}).then(() => {
  console.log('✅ Debug tests completed!');
}).catch(console.error);
