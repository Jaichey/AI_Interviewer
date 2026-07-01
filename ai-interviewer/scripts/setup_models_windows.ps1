# HireSense AI - Model Setup Script for Windows
# Automatically downloads and installs all required models and dependencies

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  HireSense AI - Model Setup (Windows)      " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Install Python requirements
Write-Host "[2/6] Installing Python requirements..." -ForegroundColor Yellow
Write-Host "  Installing core dependencies..." -ForegroundColor Gray
pip install --upgrade pip
pip install -r backend/requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python requirements installed successfully" -ForegroundColor Green

# Download YOLOv8 model
Write-Host "[3/6] Downloading YOLOv8 model..." -ForegroundColor Yellow
$yoloPath = "backend/yolov8s.pt"

if (Test-Path $yoloPath) {
    Write-Host "  YOLOv8 model already exists at $yoloPath" -ForegroundColor Gray
} else {
    Write-Host "  Downloading yolov8s.pt..." -ForegroundColor Gray
    pip install ultralytics
    python -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt'); print('YOLOv8 downloaded successfully')"
    
    # Move to backend directory
    if (Test-Path "yolov8s.pt") {
        Move-Item "yolov8s.pt" "backend/yolov8s.pt" -Force
    }
    
    if (Test-Path $yoloPath) {
        Write-Host "  ✓ YOLOv8 model downloaded successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to download YOLOv8 model" -ForegroundColor Red
        Write-Host "  Please manually download from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt" -ForegroundColor Yellow
    }
}

# Install MediaPipe
Write-Host "[4/6] Installing MediaPipe for face analysis..." -ForegroundColor Yellow
pip install mediapipe opencv-python
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ MediaPipe installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ MediaPipe installation failed" -ForegroundColor Red
}

# Install DeepFace for emotion detection
Write-Host "[5/6] Installing DeepFace for emotion analysis..." -ForegroundColor Yellow
pip install deepface tf-keras
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ DeepFace installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ DeepFace installation failed" -ForegroundColor Red
}

# Optional: Install Ollama for local LLM (if not using cloud APIs)
Write-Host "[6/6] Checking Ollama installation (optional)..." -ForegroundColor Yellow
try {
    $ollamaCheck = ollama --version 2>&1
    Write-Host "  ✓ Ollama is already installed: $ollamaCheck" -ForegroundColor Green
} catch {
    Write-Host "  Ollama not found. To use local LLMs:" -ForegroundColor Yellow
    Write-Host "    1. Download from: https://ollama.ai/download/windows" -ForegroundColor Gray
    Write-Host "    2. Install Ollama" -ForegroundColor Gray
    Write-Host "    3. Run: ollama pull mistral" -ForegroundColor Gray
    Write-Host "    4. Run: ollama pull llama3" -ForegroundColor Gray
}

# Generate synthetic dataset
Write-Host "" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Generating Synthetic Dataset              " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Generating 100 synthetic interview sessions..." -ForegroundColor Yellow
python backend/synthetic_data_generator.py --num-sessions 100

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Synthetic dataset generated successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to generate synthetic dataset" -ForegroundColor Red
}

# Final summary
Write-Host "" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                           " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "HireSense AI is ready to run!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start backend:  cd backend; uvicorn main:app --reload" -ForegroundColor Gray
Write-Host "  2. Open frontend:  Open frontend/index.html in browser" -ForegroundColor Gray
Write-Host "  3. Start interview!" -ForegroundColor Gray
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - Edit config.json to switch between synthetic/real data mode" -ForegroundColor Gray
Write-Host "  - Current mode: Check config.json 'DATA_MODE' field" -ForegroundColor Gray
Write-Host ""
