Write-Host "🌐 Starting Ethos AI Tunnel..." -ForegroundColor Green
Write-Host ""

# Check if npx is available
try {
    $null = Get-Command npx -ErrorAction Stop
    Write-Host "✅ npx found" -ForegroundColor Green
} catch {
    Write-Host "❌ npx not found. Please install Node.js first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Ollama is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama not running. Please start Ollama first." -ForegroundColor Red
    Write-Host "Run: ollama serve" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Starting tunnel..." -ForegroundColor Green
Write-Host ""

# Start localtunnel
try {
    npx localtunnel --port 11434 --subdomain ethos-ollama
} catch {
    Write-Host "❌ Failed to start tunnel" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "If successful, your tunnel URL will be: https://ethos-ollama.loca.lt" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
