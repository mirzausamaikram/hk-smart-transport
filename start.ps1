#!/usr/bin/env pwsh
# Start HK Smart Transport Backend with Hypercorn

$BackendPath = "$PSScriptRoot/backend"
$FrontendPath = "$PSScriptRoot/frontend"

Write-Host "Starting HK Smart Transport Application..." -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Start backend
Write-Host "Starting Backend (Hypercorn on port 8000)..." -ForegroundColor Green
Set-Location $BackendPath
Start-Process -WindowStyle Normal -NoNewWindow -FilePath "cmd" -ArgumentList "/c hypercorn main:app --bind 127.0.0.1:8000"

Start-Sleep -Seconds 3

# Start frontend (optional)
Write-Host "Backend started. To start frontend, run in another terminal:" -ForegroundColor Cyan
Write-Host "  cd frontend && npm run dev" -ForegroundColor Yellow
Write-Host "`nFrontend will be available at: http://localhost:5174/nearby-stations" -ForegroundColor Cyan

Write-Host "`nBackend API: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop"
