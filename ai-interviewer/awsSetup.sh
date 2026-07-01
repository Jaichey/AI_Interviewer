#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="$PROJECT_ROOT/logs"

BACKEND_VENV="$BACKEND_DIR/.venv"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-5500}"

START_SERVICES="${START_SERVICES:-1}"
GENERATE_DATASET="${GENERATE_DATASET:-auto}"

mkdir -p "$LOG_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
  printf "%b\n" "$*"
}

step() {
  log "${YELLOW}$1${NC}"
}

success() {
  log "${GREEN}$1${NC}"
}

warn() {
  log "${CYAN}$1${NC}"
}

fail() {
  log "${RED}$1${NC}"
  exit 1
}

if [[ ! -d "$BACKEND_DIR" || ! -d "$FRONTEND_DIR" ]]; then
  fail "Run this script from the project root containing backend/ and frontend/."
fi

if [[ $EUID -eq 0 ]]; then
  SUDO=""
elif command -v sudo >/dev/null 2>&1; then
  SUDO="sudo"
else
  fail "Please run as root or install sudo."
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

if [[ "$PYTHON_VERSION" != "3.10" && "$PYTHON_VERSION" != "3.11" ]]; then
  warn "Python $PYTHON_VERSION detected. Python 3.10 or 3.11 is recommended."
fi

install_system_packages() {
  if command -v apt-get >/dev/null 2>&1; then
    step "[1/6] Installing system packages..."

    $SUDO apt-get update -y

    $SUDO apt-get install -y \
      python3 \
      python3-pip \
      python3-venv \
      python3-dev \
      git \
      curl \
      build-essential \
      libgl1 \
      libglib2.0-0 \
      nodejs \
      npm

  elif command -v dnf >/dev/null 2>&1; then
    step "[1/6] Installing system packages..."

    $SUDO dnf install -y \
      python3 \
      python3-pip \
      python3-devel \
      git \
      curl \
      gcc \
      gcc-c++ \
      make \
      glib2 \
      nodejs \
      npm

  else
    fail "Unsupported Linux distribution."
  fi
}

create_python_environment() {
  step "[2/6] Creating virtual environment..."

  if [[ ! -d "$BACKEND_VENV" ]]; then
    python3 -m venv "$BACKEND_VENV"
  fi

  source "$BACKEND_VENV/bin/activate"

  python -m pip install --upgrade pip setuptools wheel

  success "✓ Virtual environment ready"
}

install_backend_dependencies() {
  step "[3/6] Installing backend dependencies..."

  source "$BACKEND_VENV/bin/activate"

  [[ -f "$BACKEND_DIR/requirements.txt" ]] || \
    fail "backend/requirements.txt not found."

  python -m pip install -r "$BACKEND_DIR/requirements.txt"

  python -m pip install ultralytics

  success "✓ Backend dependencies installed"
}

install_frontend_dependencies() {
  step "[4/6] Installing frontend dependencies..."

  if ! command -v npm >/dev/null 2>&1; then
    fail "npm not installed."
  fi

  pushd "$FRONTEND_DIR" >/dev/null

  if [[ -f package.json ]]; then
    npm install
  else
    warn "No package.json found. Skipping npm install."
  fi

  popd >/dev/null

  success "✓ Frontend dependencies installed"
}

download_yolo_model() {
  step "[5/6] Downloading YOLOv8n..."

  if [[ -f "$BACKEND_DIR/yolov8n.pt" ]]; then
    success "✓ YOLO model already exists"
    return
  fi

  source "$BACKEND_VENV/bin/activate"

  pushd "$BACKEND_DIR" >/dev/null

  python - <<'PY'
from ultralytics import YOLO

YOLO("yolov8n.pt")

print("YOLOv8n downloaded successfully")
PY

  popd >/dev/null

  if [[ -f "$BACKEND_DIR/yolov8n.pt" ]]; then
    success "✓ YOLOv8n downloaded"
  else
    warn "⚠ Could not verify YOLO model."
  fi
}

generate_synthetic_dataset() {
  step "[6/6] Preparing dataset..."

  if [[ "$GENERATE_DATASET" == "0" ]]; then
    warn "Dataset generation skipped."
    return
  fi

  if [[ "$GENERATE_DATASET" == "auto" &&
        -f "$PROJECT_ROOT/dataset/synthetic/index.json" ]]; then
    success "✓ Dataset already exists"
    return
  fi

  source "$BACKEND_VENV/bin/activate"

  if [[ -f "$BACKEND_DIR/synthetic_data_generator.py" ]]; then
    python "$BACKEND_DIR/synthetic_data_generator.py" --num-sessions 100
    success "✓ Dataset generated"
  else
    warn "Synthetic data generator not found."
  fi
}

start_services() {
  if [[ "$START_SERVICES" != "1" ]]; then
    warn "START_SERVICES=0, skipping startup."
    return
  fi

  warn "Starting services..."

  if ! pgrep -f "uvicorn" >/dev/null; then
    nohup bash -lc "
      cd '$BACKEND_DIR' &&
      source '$BACKEND_VENV/bin/activate' &&
      python -m uvicorn main:app \
      --host '$BACKEND_HOST' \
      --port '$BACKEND_PORT'
    " > "$LOG_DIR/backend.log" 2>&1 &
  else
    warn "Backend already running."
  fi

  if ! pgrep -f "http.server $FRONTEND_PORT" >/dev/null; then
    nohup bash -lc "
      cd '$FRONTEND_DIR' &&
      python3 -m http.server \
      '$FRONTEND_PORT' \
      --bind '$FRONTEND_HOST'
    " > "$LOG_DIR/frontend.log" 2>&1 &
  else
    warn "Frontend already running."
  fi

  sleep 5

  if curl -fsS "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null 2>&1; then
    success "✓ Backend health check passed"
  else
    warn "Backend health endpoint not responding."
  fi

  success "✓ Services started"
}

print_next_steps() {
  log ""
  log "======================================="
  log "       HireSense AI Setup Complete"
  log "======================================="
  log ""

  success "Backend:"
  log "http://<EC2-IP>:$BACKEND_PORT/health"

  success "Frontend:"
  log "http://<EC2-IP>:$FRONTEND_PORT"

  log ""
  warn "Open these ports in AWS Security Group:"
  log "22, 8000, 5500"

  log ""
  warn "Camera and microphone require HTTPS."

  log ""
  log "Logs:"
  log "Backend : $LOG_DIR/backend.log"
  log "Frontend: $LOG_DIR/frontend.log"
}

main() {
  log "====================================="
  log "       HireSense AI AWS Setup"
  log "====================================="
  log ""

  install_system_packages
  create_python_environment
  install_backend_dependencies
  install_frontend_dependencies
  download_yolo_model
  generate_synthetic_dataset
  start_services
  print_next_steps
}

main "$@"