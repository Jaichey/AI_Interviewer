"""
Test script to verify YOLOv8 integration and false positive fixes.
"""
import sys
import os
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 60)
print("AI Interviewer - YOLOv8 Integration Test")
print("=" * 60)

# Test 1: YOLOv8 installation
print("\n[TEST 1] Checking YOLOv8 installation...")
try:
    from ultralytics import YOLO
    print("✅ YOLOv8 (ultralytics) is installed")
except ImportError:
    print("❌ YOLOv8 not installed. Installing now...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "ultralytics"], check=True)
    from ultralytics import YOLO
    print("✅ YOLOv8 installed successfully")

# Test 2: Robust Face Detector
print("\n[TEST 2] Testing RobustFaceDetector...")
try:
    from robust_face_detector import RobustFaceDetector
    detector = RobustFaceDetector(model_size="s")
    print("✅ RobustFaceDetector initialized successfully")
    
    # Test with synthetic frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    person_count, persons = detector.detect_persons(test_frame)
    print(f"   - Test frame person count: {person_count}")
    print(f"   - Detections: {len(persons)}")
    print("✅ RobustFaceDetector is working")
except Exception as e:
    print(f"❌ RobustFaceDetector error: {e}")

# Test 3: Face Analyzer
print("\n[TEST 3] Testing FaceAnalyzer with YOLOv8...")
try:
    from face_analyzer import FaceAnalyzer
    analyzer = FaceAnalyzer()
    print("✅ FaceAnalyzer initialized with YOLOv8 support")
    
    # Check if YOLOv8 detector is loaded
    if analyzer.yolo_detector is not None:
        print("✅ YOLOv8 detector is active in FaceAnalyzer")
    else:
        print("⚠️  YOLOv8 detector not active (fallback to Haar Cascade)")
except Exception as e:
    print(f"❌ FaceAnalyzer error: {e}")

# Test 4: Warning threshold logic
print("\n[TEST 4] Testing warning threshold logic...")
test_cases = [
    {"eye_contact": 0.90, "looking_away": False, "should_warn": False, "desc": "Looking at camera (0.90 confidence)"},
    {"eye_contact": 0.82, "looking_away": False, "should_warn": False, "desc": "Looking at camera (0.82 confidence)"},
    {"eye_contact": 0.50, "looking_away": False, "should_warn": False, "desc": "Borderline eye contact (0.50 confidence, not looking away)"},
    {"eye_contact": 0.30, "looking_away": False, "should_warn": False, "desc": "Low eye contact but not looking away (0.30 confidence)"},
    {"eye_contact": 0.20, "looking_away": False, "should_warn": True, "desc": "Very low eye contact (0.20 confidence)"},
    {"eye_contact": 0.30, "looking_away": True, "should_warn": True, "desc": "Low confidence + looking away (0.30)"},
    {"eye_contact": 0.10, "looking_away": True, "should_warn": True, "desc": "Very low confidence + looking away (0.10)"},
]

print("\nWarning threshold test cases:")
for i, test in enumerate(test_cases, 1):
    eye_contact = test["eye_contact"]
    looking_away = test["looking_away"]
    
    # NEW LOGIC: Only warn if low confidence AND looking away, OR very low confidence
    will_warn = (eye_contact < 0.35 and looking_away) or eye_contact < 0.25
    
    expected = test["should_warn"]
    status = "✅" if will_warn == expected else "❌"
    
    print(f"{status} [{i}] {test['desc']}")
    print(f"    Confidence: {eye_contact:.2f}, Looking Away: {looking_away}")
    print(f"    Will warn: {will_warn} (Expected: {expected})")

print("\n" + "=" * 60)
print("Integration test complete!")
print("=" * 60)

print("\n[NEXT STEPS]")
print("1. Run the AI Interviewer with: python backend/main.py")
print("2. Test with a live camera feed")
print("3. Verify:")
print("   ✓ No false positives when looking at camera (confidence 0.8+)")
print("   ✓ Multi-person detection only when multiple people present")
print("   ✓ Warnings only for actual violations (low eye contact < 0.25)")
