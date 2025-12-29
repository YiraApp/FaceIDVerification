# Installation Guide for Face ID Verification API on Windows

Write-Host "=== Face ID Verification API - Windows Installation ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python version
Write-Host "Step 1: Checking Python version..." -ForegroundColor Yellow
python --version
Write-Host ""

# Step 2: Upgrade pip
Write-Host "Step 2: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host ""

# Step 3: Install Microsoft C++ Build Tools (if needed)
Write-Host "Step 3: Checking for C++ Build Tools..." -ForegroundColor Yellow
Write-Host "If InsightFace fails to install, you may need Microsoft C++ Build Tools." -ForegroundColor Red
Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
Write-Host "Or install Visual Studio with 'Desktop development with C++' workload" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to continue with installation..." -ForegroundColor Green
Read-Host

# Step 4: Create virtual environment
Write-Host "Step 4: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Gray
}
else {
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}
Write-Host ""

# Step 5: Activate virtual environment
Write-Host "Step 5: Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\activate.ps1"
Write-Host ""

# Step 6: Install dependencies in stages
Write-Host "Step 6: Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  [1/4] Installing core dependencies..." -ForegroundColor Cyan
pip install numpy==1.26.4 packaging wheel setuptools

Write-Host "  [2/4] Installing FastAPI and web framework..." -ForegroundColor Cyan
pip install fastapi uvicorn[standard] python-multipart pydantic pydantic-settings

Write-Host "  [3/4] Installing computer vision libraries..." -ForegroundColor Cyan
pip install opencv-python onnxruntime PyMuPDF Pillow

Write-Host "  [4/4] Installing InsightFace (this may take a while)..." -ForegroundColor Cyan
pip install insightface

Write-Host ""
Write-Host "Step 7: Installing remaining utilities..." -ForegroundColor Yellow
pip install python-dotenv tqdm coloredlogs scikit-image scipy

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy .env.example to .env (optional)" -ForegroundColor White
Write-Host "  2. Run: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "  3. Open: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
