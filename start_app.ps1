# Start Backend (FastAPI)
Write-Host "Starting Backend..."
$backendProcess = Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "-m uvicorn api.index:app --reload --port 8001" -PassThru -NoNewWindow
Start-Sleep -Seconds 3 # Wait for backend to initialized on http://localhost:8001"

Write-Host "Starting Frontend..."
Start-Process -FilePath "cmd" -ArgumentList "/k cd frontend && npm run dev" -WorkingDirectory "."
Write-Host "Frontend started on http://localhost:5173"

Write-Host "App is running."
