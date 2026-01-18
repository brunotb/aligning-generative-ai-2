# Start Voice Form Assistant - Full Stack
# Starts both backend API and frontend

Write-Host "=== Voice Form Assistant Startup ===" -ForegroundColor Cyan
Write-Host ""

# Load .env file if it exists
if (Test-Path .env) {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Gray
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Check if GOOGLE_API_KEY is set
if (-not $env:GOOGLE_API_KEY) {
    Write-Host "ERROR: GOOGLE_API_KEY environment variable not set!" -ForegroundColor Red
    Write-Host "Please set it with: `$env:GOOGLE_API_KEY = 'your-api-key'" -ForegroundColor Yellow
    exit 1
}

# Start Backend (FastAPI)
Write-Host "[1/3] Starting Backend API Server..." -ForegroundColor Green
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn voice_api.api.server:app --host 0.0.0.0 --port 8001 --reload" -PassThru
Start-Sleep -Seconds 3

Write-Host "[2/3] Backend API started on http://localhost:8001" -ForegroundColor Green
Write-Host ""

# Start Frontend (Vite)
Write-Host "[3/3] Starting Frontend Development Server..." -ForegroundColor Green
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru
Start-Sleep -Seconds 3

Write-Host "[3/3] Frontend started on http://localhost:5173" -ForegroundColor Green
Write-Host ""

Write-Host "=== Application is Running ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "Backend:   http://localhost:8001" -ForegroundColor White
Write-Host "API Docs:  http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
Write-Host ""

# Note: Voice pipeline starts automatically when user clicks "Start Conversation"
Write-Host "NOTE: Voice pipeline will start when you click 'Start Conversation' in the UI" -ForegroundColor Cyan
Write-Host "      Make sure your microphone is connected and permissions are granted" -ForegroundColor Cyan
