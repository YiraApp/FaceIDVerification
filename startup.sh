# # Quick Start Script for Face ID Verification API
# # Run this script to start the FastAPI server

# Write-Host "Starting Face ID Verification API..." -ForegroundColor Green
# Write-Host ""

# # Check if virtual environment exists
# if (Test-Path "venv\Scripts\activate.ps1") {
#     Write-Host "Activating virtual environment..." -ForegroundColor Yellow
#     & "venv\Scripts\activate.ps1"
# } else {
#     Write-Host "Warning: Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
# }

# # Start the server
# Write-Host "Starting Uvicorn server..." -ForegroundColor Yellow
# Write-Host ""
# Write-Host "API will be available at:" -ForegroundColor Cyan
# Write-Host "  - API: http://localhost:8000" -ForegroundColor White
# Write-Host "  - Swagger UI: http://localhost:8000/docs" -ForegroundColor White
# Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor White
# Write-Host ""

# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

#!/bin/bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005
