#!/bin/bash

# HireSense AI - Model Setup Script for Linux/Mac
# Automatically downloads and installs all required models and dependencies

echo "============================================="
echo "  HireSense AI - Model Setup (Linux/Mac)    "
echo "============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${YELLOW}[1/6] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}  ✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}  ✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
else
    echo -e "${RED}  ✗ Python not found! Please install Python 3.8+${NC}"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
elif command -v pip &> /dev/null; then
    PIP_CMD=pip
else
    echo -e "${RED}  ✗ pip not found! Please install pip${NC}"
    exit 1
fi

# Install Python requirements
echo -e "${YELLOW}[2/6] Installing Python requirements...${NC}"
echo -e "${CYAN}  Installing core dependencies...${NC}"
$PIP_CMD install --upgrade pip
$PIP_CMD install -r backend/requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Python requirements installed successfully${NC}"
else
    echo -e "${RED}  ✗ Failed to install requirements${NC}"
    exit 1
fi

# Download YOLOv8 model
echo -e "${YELLOW}[3/6] Downloading YOLOv8 model...${NC}"
YOLO_PATH="backend/yolov8s.pt"

if [ -f "$YOLO_PATH" ]; then
    echo -e "${CYAN}  YOLOv8 model already exists at $YOLO_PATH${NC}"
else
    echo -e "${CYAN}  Downloading yolov8s.pt...${NC}"
    $PIP_CMD install ultralytics
    $PYTHON_CMD -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt'); print('YOLOv8 downloaded successfully')"
    
    # Move to backend directory
    if [ -f "yolov8s.pt" ]; then
        mv yolov8s.pt backend/yolov8s.pt
    fi
    
    if [ -f "$YOLO_PATH" ]; then
        echo -e "${GREEN}  ✓ YOLOv8 model downloaded successfully${NC}"
    else
        echo -e "${RED}  ✗ Failed to download YOLOv8 model${NC}"
        echo -e "${YELLOW}  Please manually download from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt${NC}"
    fi
fi

# Install MediaPipe
echo -e "${YELLOW}[4/6] Installing MediaPipe for face analysis...${NC}"
$PIP_CMD install mediapipe opencv-python
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ MediaPipe installed successfully${NC}"
else
    echo -e "${RED}  ✗ MediaPipe installation failed${NC}"
fi

# Install DeepFace for emotion detection
echo -e "${YELLOW}[5/6] Installing DeepFace for emotion analysis...${NC}"
$PIP_CMD install deepface tf-keras
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ DeepFace installed successfully${NC}"
else
    echo -e "${RED}  ✗ DeepFace installation failed${NC}"
fi

# Optional: Install Ollama for local LLM (if not using cloud APIs)
echo -e "${YELLOW}[6/6] Checking Ollama installation (optional)...${NC}"
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version)
    echo -e "${GREEN}  ✓ Ollama is already installed: $OLLAMA_VERSION${NC}"
else
    echo -e "${YELLOW}  Ollama not found. To use local LLMs:${NC}"
    echo -e "${CYAN}    Linux:   curl -fsSL https://ollama.ai/install.sh | sh${NC}"
    echo -e "${CYAN}    Mac:     brew install ollama${NC}"
    echo -e "${CYAN}    Then run: ollama pull mistral${NC}"
    echo -e "${CYAN}              ollama pull llama3${NC}"
fi

# Generate synthetic dataset
echo ""
echo -e "${CYAN}=============================================${NC}"
echo -e "${CYAN}  Generating Synthetic Dataset              ${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""

echo -e "${YELLOW}Generating 100 synthetic interview sessions...${NC}"
$PYTHON_CMD backend/synthetic_data_generator.py --num-sessions 100

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Synthetic dataset generated successfully${NC}"
else
    echo -e "${RED}  ✗ Failed to generate synthetic dataset${NC}"
fi

# Final summary
echo ""
echo -e "${CYAN}=============================================${NC}"
echo -e "${CYAN}  Setup Complete!                           ${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""
echo -e "${GREEN}HireSense AI is ready to run!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${CYAN}  1. Start backend:  cd backend && uvicorn main:app --reload${NC}"
echo -e "${CYAN}  2. Open frontend:  Open frontend/index.html in browser${NC}"
echo -e "${CYAN}  3. Start interview!${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo -e "${CYAN}  - Edit config.json to switch between synthetic/real data mode${NC}"
echo -e "${CYAN}  - Current mode: Check config.json 'DATA_MODE' field${NC}"
echo ""
