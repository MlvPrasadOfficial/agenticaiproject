# PowerShell script to test frontend-backend connection
Write-Host "🔍 Testing Frontend-Backend Connection" -ForegroundColor Cyan
Write-Host ("=" * 50)

# Test backend endpoints
$baseUrl = "http://localhost:8000"
$endpoints = @(
    @{ Name = "Root Endpoint"; Url = "$baseUrl/" }
    @{ Name = "Wrong Health Check (old)"; Url = "$baseUrl/health" }
    @{ Name = "Correct Health Check (new)"; Url = "$baseUrl/api/v1/health" }
    @{ Name = "API Documentation"; Url = "$baseUrl/docs" }
)

foreach ($endpoint in $endpoints) {
    Write-Host "`n🔗 Testing: $($endpoint.Name)" -ForegroundColor Yellow
    Write-Host "   URL: $($endpoint.Url)"
    
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -Method GET -UseBasicParsing -TimeoutSec 5
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
            
            # Show first 100 characters of response
            $content = $response.Content
            if ($content.Length -gt 100) {
                $content = $content.Substring(0, 100) + "..."
            }
            Write-Host "   Response: $content" -ForegroundColor Gray
        } else {
            Write-Host "   ⚠️  UNEXPECTED - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n" + "=" * 50
Write-Host "🎯 SUMMARY:" -ForegroundColor Cyan

# Test the specific health check that frontend uses
Write-Host "`n🏥 Testing Frontend Health Check Logic..." -ForegroundColor Magenta
try {
    $healthResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/health" -Method GET -UseBasicParsing -TimeoutSec 5
    $isHealthy = $healthResponse.StatusCode -eq 200
    
    if ($isHealthy) {
        Write-Host "✅ BACKEND CONNECTED - Frontend should show LIVE MODE" -ForegroundColor Green
        Write-Host "   - Header: '🟢 Backend Connected'" -ForegroundColor Gray
        Write-Host "   - Data Preview: 'LIVE DATA' badge" -ForegroundColor Gray
        Write-Host "   - Agent Logs: 'LIVE LOGS' badge" -ForegroundColor Gray
    } else {
        Write-Host "❌ BACKEND OFFLINE - Frontend will show DEMO MODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ BACKEND OFFLINE - Frontend will show DEMO MODE" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host "`n🚀 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. If backend is connected, start frontend with:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host "2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "3. The frontend should automatically detect backend and switch to LIVE mode" -ForegroundColor White

Write-Host "`n✅ Test completed!" -ForegroundColor Green
