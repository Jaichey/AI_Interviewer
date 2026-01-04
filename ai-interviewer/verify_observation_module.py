#!/usr/bin/env python3
"""
Verification Script for Human Observation & Behavior Analysis Module

This script verifies that all new files are in place and working correctly.
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_file_exists(path):
    """Check if a file exists."""
    if os.path.isfile(path):
        return True
    return False

def check_directory_exists(path):
    """Check if a directory exists."""
    if os.path.isdir(path):
        return True
    return False

def main():
    print_header("OBSERVATION MODULE VERIFICATION")
    
    # Get project root
    script_dir = Path(__file__).resolve().parent
    backend_dir = script_dir / "backend"
    frontend_dir = script_dir / "frontend"
    
    print(f"Project Root: {script_dir}")
    print(f"Backend Dir: {backend_dir}")
    print(f"Frontend Dir: {frontend_dir}\n")
    
    all_good = True
    
    # ========== BACKEND FILES ==========
    print_header("Backend Files")
    
    backend_files = [
        ("face_analyzer.py", "Face & gaze detection"),
        ("emotion_analyzer.py", "Emotion classification"),
        ("audio_analyzer.py", "Voice stress detection"),
        ("observation_logger.py", "Logging & reporting"),
        ("human_observation_engine.py", "Main orchestration"),
        ("observation_config.py", "Configuration"),
        ("test_observation_integration.py", "Integration tests"),
    ]
    
    for filename, description in backend_files:
        filepath = backend_dir / filename
        if check_file_exists(filepath):
            print_success(f"{filename:40} - {description}")
        else:
            print_error(f"{filename:40} - MISSING!")
            all_good = False
    
    # ========== FRONTEND FILES ==========
    print_header("Frontend Files")
    
    frontend_files = [
        ("observation_client.js", "Backend API client"),
        ("app.js", "Updated with observation integration"),
        ("index.html", "Updated with camera panel"),
        ("styles.css", "Updated with camera styles"),
    ]
    
    for filename, description in frontend_files:
        filepath = frontend_dir / filename
        if check_file_exists(filepath):
            print_success(f"{filename:40} - {description}")
        else:
            print_error(f"{filename:40} - MISSING!")
            all_good = False
    
    # ========== DOCUMENTATION FILES ==========
    print_header("Documentation Files")
    
    doc_files = [
        ("OBSERVATION_EXTENSION.md", "Overview of new feature"),
        ("OBSERVATION_QUICKSTART.md", "Quick start guide"),
        ("OBSERVATION_MODULE.md", "Technical documentation"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation details"),
        ("DEPLOYMENT_CHECKLIST.md", "Deployment verification"),
    ]
    
    for filename, description in doc_files:
        filepath = script_dir / filename
        if check_file_exists(filepath):
            print_success(f"{filename:40} - {description}")
        else:
            print_error(f"{filename:40} - MISSING!")
            all_good = False
    
    # ========== REQUIREMENTS CHECK ==========
    print_header("Dependencies")
    
    requirements_path = backend_dir / "requirements.txt"
    
    required_packages = {
        "opencv-python": "Camera capture",
        "mediapipe": "Face detection",
        "numpy": "Numerical computation",
    }
    
    if check_file_exists(requirements_path):
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        for package, description in required_packages.items():
            if package in content:
                print_success(f"{package:40} - {description}")
            else:
                print_error(f"{package:40} - NOT in requirements.txt!")
                all_good = False
    else:
        print_error("requirements.txt not found!")
        all_good = False
    
    # ========== CODE INTEGRATION CHECK ==========
    print_header("Code Integration")
    
    integration_checks = [
        (backend_dir / "main.py", "from human_observation_engine import", "Observation import in main.py"),
        (backend_dir / "main.py", "@app.post(\"/observation/start\")", "Observation endpoints in main.py"),
        (frontend_dir / "app.js", "import { ObservationClient }", "ObservationClient import"),
        (frontend_dir / "index.html", "id=\"camera-panel\"", "Camera panel in HTML"),
        (frontend_dir / "styles.css", ".camera-panel {", "Camera panel styles"),
    ]
    
    for filepath, search_string, description in integration_checks:
        if check_file_exists(filepath):
            with open(filepath, 'r') as f:
                if search_string in f.read():
                    print_success(f"{description:45} ✓")
                else:
                    print_error(f"{description:45} - String not found!")
                    all_good = False
        else:
            print_error(f"{description:45} - File not found!")
            all_good = False
    
    # ========== SUMMARY ==========
    print_header("Summary")
    
    if all_good:
        print_success("All files present and integrated correctly!")
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print(f"\n1. Install dependencies:")
        print(f"   cd {backend_dir}")
        print(f"   pip install -r requirements.txt\n")
        
        print(f"2. Run integration tests:")
        print(f"   python {backend_dir}/test_observation_integration.py\n")
        
        print(f"3. Start backend:")
        print(f"   uvicorn main:app --reload --port 8000\n")
        
        print(f"4. Start frontend:")
        print(f"   cd {frontend_dir}")
        print(f"   python -m http.server 5500\n")
        
        print(f"5. Open browser:")
        print(f"   http://localhost:5500\n")
        
        print("="*70)
        print(f"{'All systems go! 🚀':^70}")
        print("="*70)
        return 0
    else:
        print_error("Some files are missing or not integrated!")
        print("\nPlease check the errors above and ensure all files are in place.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
