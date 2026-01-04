"""
Human Observation & Behavior Analysis Engine.
LOCAL ONLY - All processing is local, no cloud APIs.
Runs in parallel with the interview without blocking it.
"""
import cv2
import numpy as np
import threading
import queue
import time
import pathlib
import sys
from typing import Dict, Optional, Callable
import logging

# Handle imports for both package and direct execution
try:
    from .face_analyzer import FaceAnalyzer
    from .emotion_analyzer import EmotionAnalyzer
    from .audio_analyzer import AudioAnalyzer
    from .observation_logger import ObservationLogger
except ImportError:
    sys.path.append(str(pathlib.Path(__file__).resolve().parent))
    from face_analyzer import FaceAnalyzer
    from emotion_analyzer import EmotionAnalyzer
    from audio_analyzer import AudioAnalyzer
    from observation_logger import ObservationLogger

logger = logging.getLogger(__name__)


class PaceController:
    """Controls interview pacing based on behavioral signals (non-intrusive)."""

    def __init__(self):
        self.stress_threshold = 0.6
        self.looking_away_threshold = 5  # seconds
        self.silence_threshold = 3  # seconds
        self.last_stress_adjustment = 0
        self.pressure_mode = "normal"

    def adjust_pace(self, observation: Dict) -> Dict:
        """Determine pace adjustments based on observation."""
        adjustments = {
            "delay_next_question": 0,  # seconds
            "reduce_pressure": False,
            "increase_pause_tolerance": False,
            "feedback": None
        }
        
        audio_data = observation.get("audio", {})
        face_data = observation.get("face", {})
        
        # High stress detected
        if audio_data.get("stress_level") == "high":
            adjustments["delay_next_question"] = 2
            adjustments["reduce_pressure"] = True
            adjustments["feedback"] = "Detected stress - allowing extra time to breathe"
            self.pressure_mode = "relaxed"
        
        # Looking away frequently
        elif face_data.get("looking_away"):
            adjustments["increase_pause_tolerance"] = True
            adjustments["delay_next_question"] = 1
            self.pressure_mode = "patient"
        
        # Long silence
        elif audio_data.get("silence_duration", 0) > self.silence_threshold:
            adjustments["increase_pause_tolerance"] = True
            adjustments["feedback"] = "Extended silence detected - more time for thinking"
        
        else:
            self.pressure_mode = "normal"
        
        return adjustments

    def reset(self):
        """Reset pace controller state."""
        self.pressure_mode = "normal"
        self.last_stress_adjustment = 0


class HumanObservationEngine:
    """
    Observes and analyzes human behavior during interview.
    Runs asynchronously in a separate thread.
    """

    def __init__(self, on_observation: Optional[Callable] = None):
        """
        Initialize observation engine.
        
        Args:
            on_observation: Callback function to receive observation updates
        """
        self.face_analyzer = FaceAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.logger = ObservationLogger()
        self.pace_controller = PaceController()
        
        self.on_observation = on_observation
        
        # Threading
        self.running = False
        self.observation_thread = None
        self.audio_thread = None
        
        # Queues for communication
        self.frame_queue = queue.Queue(maxsize=5)
        self.audio_queue = queue.Queue(maxsize=10)
        self.video_queue = queue.Queue(maxsize=10)  # Queue for video frames from frontend
        self.observation_queue = queue.Queue()
        
        # Video capture
        self.cap = None
        self.camera_ready = False
        
        # State
        self.observation_count = 0
        self.last_observation = None
        
        logger.info("[HumanObservationEngine] Initialized")

    def start(self) -> bool:
        """Start observation engine (camera + audio monitoring)."""
        if self.running:
            logger.warning("[HumanObservationEngine] Already running")
            return False
        
        try:
            # DISABLE camera - frontend handles video via WebRTC
            logger.info("[HumanObservationEngine] Starting without camera (frontend mode)")
            self.cap = None
            self.camera_ready = False
            
            self.running = True
            
            # Start observation thread
            self.observation_thread = threading.Thread(
                target=self._observation_loop,
                daemon=True
            )
            self.observation_thread.start()
            
            logger.info("[HumanObservationEngine] Started (camera disabled)")
            return True
        
        except Exception as e:
            logger.error(f"[HumanObservationEngine] Failed to start: {e}")
            self.running = False
            return False

    def stop(self):
        """Stop observation engine and generate final report."""
        if not self.running:
            return
        
        self.running = False
        
        if self.observation_thread:
            self.observation_thread.join(timeout=5)
        
        if self.cap:
            self.cap.release()
            self.camera_ready = False
        
        # Close the facial expression log file
        if hasattr(self.logger, 'close_log_file'):
            self.logger.close_log_file()
        
        logger.info("[HumanObservationEngine] Stopped")

    def add_audio_frame(self, audio_chunk: np.ndarray):
        """Add audio frame for analysis (called from speech recognition)."""
        if self.running and not self.audio_queue.full():
            self.audio_queue.put(audio_chunk)
    
    def add_video_frame(self, frame: np.ndarray):
        """Add video frame for analysis (called from frontend)."""
        if self.running and not self.video_queue.full():
            self.video_queue.put(frame)

    def get_latest_observation(self) -> Optional[Dict]:
        """Get the latest observation (non-blocking)."""
        try:
            while True:
                self.last_observation = self.observation_queue.get_nowait()
        except queue.Empty:
            pass
        
        return self.last_observation

    def get_observation_stream(self):
        """Generator that yields observations as they arrive."""
        while self.running:
            try:
                obs = self.observation_queue.get(timeout=1)
                yield obs
            except queue.Empty:
                continue

    def _observation_loop(self):
        """Main observation loop (runs in separate thread)."""
        while self.running:
            try:
                # Process video frames from queue (sent by frontend)
                frame = None
                while not self.video_queue.empty():
                    try:
                        frame = self.video_queue.get_nowait()
                    except queue.Empty:
                        break
                
                # Process audio from queue
                audio_data = self._process_audio_queue()
                
                # Analyze frame if available
                if frame is not None:
                    face_data = self.face_analyzer.analyze(frame)
                    emotion_data = self.emotion_analyzer.analyze(frame)
                else:
                    # No frame available - create minimal data
                    face_data = {"face_detected": False}
                    emotion_data = {"emotion": "unknown"}
                
                # Create observation
                observation = {
                    "timestamp": time.time(),
                    "face": face_data,
                    "emotion": emotion_data,
                    "audio": audio_data,
                    "pace_adjustment": {}
                }
                
                # Log observation
                self.logger.log_observation(observation)
                
                # Put in queue for retrieval
                if not self.observation_queue.full():
                    self.observation_queue.put(observation)
                
                # Sleep to control frequency
                time.sleep(0.1)  # 10 Hz
                
            except Exception as e:
                logger.error(f"[HumanObservationEngine] Error in loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.5)

    def _process_audio_queue(self) -> Dict:
        """Process accumulated audio chunks and analyze."""
        # Drain audio queue
        while not self.audio_queue.empty():
            try:
                audio_chunk = self.audio_queue.get_nowait()
                self.audio_analyzer.add_audio_chunk(audio_chunk)
            except queue.Empty:
                break
        
        # Analyze current audio
        return self.audio_analyzer.analyze()

    def get_frame(self) -> Optional[np.ndarray]:
        """Get current camera frame for display in UI."""
        if not self.running or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def generate_report(self) -> Dict:
        """Generate final behavioral analysis report."""
        return self.logger.generate_report()

    def reset(self):
        """Reset all analyzers and loggers for new interview."""
        self.face_analyzer.reset()
        self.emotion_analyzer.reset()
        self.audio_analyzer.reset()
        self.logger = ObservationLogger()
        self.pace_controller.reset()
        self.observation_count = 0
        logger.info("[HumanObservationEngine] Reset complete")
