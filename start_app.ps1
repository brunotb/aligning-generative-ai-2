Write-Host "Starting Backend..."
Start-Process -FilePath "cmd" -ArgumentList "/k cd backend && .\venv\Scripts\activate && uvicorn main:app --reload --port 8001" -WorkingDirectory "."
Write-Host "Backend started on http://localhost:8001"

Write-Host "Starting Frontend..."
Start-Process -FilePath "cmd" -ArgumentList "/k cd frontend && npm run dev" -WorkingDirectory "."
Write-Host "Frontend started on http://localhost:5173"

Write-Host "App is running."
