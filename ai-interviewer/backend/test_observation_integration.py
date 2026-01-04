"""
Integration Test for Human Observation Module
Run this to verify the observation engine works correctly.
"""

import sys
import pathlib

# Add backend to path
backend_path = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all modules can be imported."""
    print("\n=== Testing Module Imports ===")
    try:
        from face_analyzer import FaceAnalyzer
        print("✓ FaceAnalyzer imported")
    except Exception as e:
        print(f"✗ FaceAnalyzer failed: {e}")
        return False
    
    try:
        from emotion_analyzer import EmotionAnalyzer
        print("✓ EmotionAnalyzer imported")
    except Exception as e:
        print(f"✗ EmotionAnalyzer failed: {e}")
        return False
    
    try:
        from audio_analyzer import AudioAnalyzer
        print("✓ AudioAnalyzer imported")
    except Exception as e:
        print(f"✗ AudioAnalyzer failed: {e}")
        return False
    
    try:
        from observation_logger import ObservationLogger
        print("✓ ObservationLogger imported")
    except Exception as e:
        print(f"✗ ObservationLogger failed: {e}")
        return False
    
    try:
        from human_observation_engine import HumanObservationEngine
        print("✓ HumanObservationEngine imported")
    except Exception as e:
        print(f"✗ HumanObservationEngine failed: {e}")
        return False
    
    return True


def test_analyzer_initialization():
    """Test that analyzers can be initialized."""
    print("\n=== Testing Analyzer Initialization ===")
    try:
        from face_analyzer import FaceAnalyzer
        analyzer = FaceAnalyzer()
        print("✓ FaceAnalyzer initialized")
    except Exception as e:
        print(f"✗ FaceAnalyzer initialization failed: {e}")
        return False
    
    try:
        from emotion_analyzer import EmotionAnalyzer
        analyzer = EmotionAnalyzer()
        print("✓ EmotionAnalyzer initialized")
    except Exception as e:
        print(f"✗ EmotionAnalyzer initialization failed: {e}")
        return False
    
    try:
        from audio_analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer()
        print("✓ AudioAnalyzer initialized")
    except Exception as e:
        print(f"✗ AudioAnalyzer initialization failed: {e}")
        return False
    
    try:
        from observation_logger import ObservationLogger
        logger = ObservationLogger()
        print("✓ ObservationLogger initialized")
    except Exception as e:
        print(f"✗ ObservationLogger initialization failed: {e}")
        return False
    
    return True


def test_analyzer_methods():
    """Test that analyzers have required methods."""
    print("\n=== Testing Analyzer Methods ===")
    
    try:
        from face_analyzer import FaceAnalyzer
        import numpy as np
        analyzer = FaceAnalyzer()
        
        # Create dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = analyzer.analyze(dummy_frame)
        
        assert "face_detected" in result
        assert "head_yaw" in result
        assert "blink_count" in result
        print("✓ FaceAnalyzer.analyze() works")
    except Exception as e:
        print(f"✗ FaceAnalyzer.analyze() failed: {e}")
        return False
    
    try:
        from emotion_analyzer import EmotionAnalyzer
        import numpy as np
        analyzer = EmotionAnalyzer()
        
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = analyzer.analyze(dummy_frame)
        
        assert "emotion" in result
        assert "confidence" in result
        print("✓ EmotionAnalyzer.analyze() works")
    except Exception as e:
        print(f"✗ EmotionAnalyzer.analyze() failed: {e}")
        return False
    
    try:
        from audio_analyzer import AudioAnalyzer
        import numpy as np
        analyzer = AudioAnalyzer()
        
        dummy_audio = np.random.randn(2048).astype(np.float32)
        analyzer.add_audio_chunk(dummy_audio)
        result = analyzer.analyze()
        
        assert "pitch" in result
        assert "stress_level" in result
        print("✓ AudioAnalyzer.analyze() works")
    except Exception as e:
        print(f"✗ AudioAnalyzer.analyze() failed: {e}")
        return False
    
    try:
        from observation_logger import ObservationLogger
        logger = ObservationLogger()
        
        dummy_obs = {
            "face_detected": True,
            "looking_away": False,
            "face_data": {"looking_away": False},
            "audio": {"stress_level": "low"},
        }
        logger.log_observation(dummy_obs)
        report = logger.generate_report()
        
        assert "eye_contact_score" in report
        assert "stress_level" in report
        print("✓ ObservationLogger.generate_report() works")
    except Exception as e:
        print(f"✗ ObservationLogger.generate_report() failed: {e}")
        return False
    
    return True


def test_observation_engine():
    """Test HumanObservationEngine initialization."""
    print("\n=== Testing HumanObservationEngine ===")
    
    try:
        from human_observation_engine import HumanObservationEngine
        engine = HumanObservationEngine()
        
        assert hasattr(engine, 'start')
        assert hasattr(engine, 'stop')
        assert hasattr(engine, 'get_latest_observation')
        assert hasattr(engine, 'generate_report')
        print("✓ HumanObservationEngine has all required methods")
    except Exception as e:
        print(f"✗ HumanObservationEngine failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("OBSERVATION MODULE INTEGRATION TEST")
    print("="*60)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_analyzer_initialization()
    all_passed &= test_analyzer_methods()
    all_passed &= test_observation_engine()
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nObservation module is ready to use!")
        print("\nNext steps:")
        print("1. Start the backend: uvicorn main:app --reload --port 8000")
        print("2. Open the frontend: http://localhost:5500")
        print("3. Click camera button to view candidate feed")
        print("4. Start interview and observe behavioral metrics")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease check the errors above and ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
