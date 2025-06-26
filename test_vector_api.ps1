# Test Vector Count in Agent Status API
# PowerShell script to test vector count logging

Write-Host "🧪 Testing Vector Count in Agent Status API" -ForegroundColor Cyan
Write-Host "============================================================"

# Test 1: Health Check
Write-Host "`n📊 Testing Backend Health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ Backend is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend health check failed: $($healthResponse.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Cannot connect to backend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the backend is running" -ForegroundColor Yellow
    exit 1
}

# Test 2: Query Status Endpoint (should include vector count)
Write-Host "`n📊 Testing Query Status Endpoint..." -ForegroundColor Yellow
try {
    $queryResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agents/query-status/test123" -Method GET -TimeoutSec 10
    
    if ($queryResponse.StatusCode -eq 200) {
        Write-Host "✅ Query status endpoint accessible" -ForegroundColor Green
        
        $data = $queryResponse.Content | ConvertFrom-Json
        $retrievalOutputs = $data.agents.'retrieval-agent'.outputs
        
        Write-Host "`n📊 Retrieval Agent Query Outputs:" -ForegroundColor Cyan
        foreach ($output in $retrievalOutputs) {
            Write-Host "  - $output" -ForegroundColor White
            if ($output -match "vector|pinecone" -or $output -match "Vector|Pinecone") {
                Write-Host "    ✅ Contains vector count information!" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "❌ Query status failed: $($queryResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing query status: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Upload Status Endpoint (with dummy file)
Write-Host "`n📊 Testing Upload Status Endpoint..." -ForegroundColor Yellow
try {
    $statusResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agents/status/dummy123" -Method GET -TimeoutSec 10
    
    if ($statusResponse.StatusCode -eq 404) {
        Write-Host "ℹ️ File not found (expected for dummy file_id)" -ForegroundColor Yellow
    } elseif ($statusResponse.StatusCode -eq 200) {
        Write-Host "✅ Status endpoint accessible" -ForegroundColor Green
        
        $data = $statusResponse.Content | ConvertFrom-Json
        $retrievalOutputs = $data.agents.'retrieval-agent'.outputs
        
        Write-Host "`n📊 Retrieval Agent Upload Outputs:" -ForegroundColor Cyan
        foreach ($output in $retrievalOutputs) {
            Write-Host "  - $output" -ForegroundColor White
            if ($output -match "vector|pinecone" -or $output -match "Vector|Pinecone") {
                Write-Host "    ✅ Contains vector count information!" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "❌ Unexpected status code: $($statusResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing upload status: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Vector count API test completed!" -ForegroundColor Green
