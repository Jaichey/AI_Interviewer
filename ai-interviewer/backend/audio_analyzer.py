"""
Voice stress and pitch analysis from microphone stream.
LOCAL ONLY - No cloud speech-to-text or APIs.
"""
import numpy as np
from typing import Dict, Optional
import threading
from collections import deque
import time


class AudioAnalyzer:
    """Analyzes audio for pitch, energy, stress, and speaking patterns."""

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 2048):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Audio buffer for analysis
        self.audio_buffer = deque(maxlen=sample_rate * 2)  # 2 seconds of audio
        self.lock = threading.Lock()
        
        # Baseline stats (will be calibrated during first few seconds)
        self.baseline_pitch = None
        self.baseline_energy = None
        self.calibrated = False
        
        # Stress tracking
        self.pitch_history = deque(maxlen=30)  # Last 30 frames
        self.energy_history = deque(maxlen=30)
        self.silence_start = None
        self.max_silence_duration = 0
        self.current_silence_duration = 0

    def add_audio_chunk(self, audio_chunk: np.ndarray):
        """Add audio chunk to buffer for analysis."""
        with self.lock:
            for sample in audio_chunk:
                self.audio_buffer.append(sample)

    def analyze(self) -> Dict:
        """Analyze current audio buffer for stress indicators."""
        with self.lock:
            if len(self.audio_buffer) < self.chunk_size:
                return self._empty_result()
            
            audio_data = np.array(list(self.audio_buffer))
        
        # Extract features
        pitch = self._estimate_pitch(audio_data)
        energy = self._calculate_energy(audio_data)
        speaking_rate = self._estimate_speaking_rate(audio_data)
        silence_detected = energy < np.mean(self.energy_history) * 0.3 if self.energy_history else False
        
        # Track baselines
        if not self.calibrated and len(self.pitch_history) > 10:
            self.baseline_pitch = np.median(list(self.pitch_history))
            self.baseline_energy = np.median(list(self.energy_history))
            self.calibrated = True
        
        # Update history
        self.pitch_history.append(pitch)
        self.energy_history.append(energy)
        
        # Detect silence
        if silence_detected:
            if self.silence_start is None:
                self.silence_start = time.time()
            self.current_silence_duration = time.time() - self.silence_start
            self.max_silence_duration = max(self.max_silence_duration, self.current_silence_duration)
        else:
            self.silence_start = None
            self.current_silence_duration = 0
        
        # Calculate stress indicators
        stress_indicators = self._calculate_stress(pitch, energy)
        
        return {
            "pitch": float(pitch),
            "energy": float(energy),
            "speaking_rate": float(speaking_rate),
            "silence_duration": float(self.current_silence_duration),
            "max_silence": float(self.max_silence_duration),
            "silence_detected": bool(silence_detected),
            "pitch_spike": stress_indicators["pitch_spike"],
            "energy_spike": stress_indicators["energy_spike"],
            "stress_level": stress_indicators["stress_level"],
            "voice_confidence": stress_indicators["confidence"],
            "baseline_pitch": float(self.baseline_pitch) if self.baseline_pitch else 0.0,
            "baseline_energy": float(self.baseline_energy) if self.baseline_energy else 0.0,
        }

    def _estimate_pitch(self, audio: np.ndarray) -> float:
        """Estimate fundamental frequency (pitch) using autocorrelation."""
        if len(audio) < self.chunk_size:
            return 0.0
        
        try:
            # Simple autocorrelation-based pitch detection
            audio = audio - np.mean(audio)
            
            # Window the signal
            window = np.hanning(len(audio))
            audio = audio * window
            
            # Autocorrelation
            corr = np.correlate(audio, audio, mode='full')
            corr = corr[len(corr) // 2:]
            
            # Find peak in expected pitch range (80-400 Hz)
            min_period = int(self.sample_rate / 400)
            max_period = int(self.sample_rate / 80)
            
            if max_period < len(corr):
                peak_idx = np.argmax(corr[min_period:max_period]) + min_period
                pitch = self.sample_rate / peak_idx
                return float(np.clip(pitch, 80, 400))
            else:
                return 0.0
        except Exception as e:
            return 0.0

    @staticmethod
    def _calculate_energy(audio: np.ndarray) -> float:
        """Calculate RMS energy of audio signal."""
        if len(audio) == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio ** 2)))

    @staticmethod
    def _estimate_speaking_rate(audio: np.ndarray) -> float:
        """Estimate speaking rate (rough approximation)."""
        # Zero crossings as proxy for speech activity
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / 2
        # Rough: speaking rate in words per minute (approximate)
        # Each word ~5-10 zero crossing groups
        return float(zero_crossings / 10)

    def _calculate_stress(self, current_pitch: float, current_energy: float) -> Dict:
        """Calculate stress indicators and voice confidence from pitch and energy."""
        # During calibration (first 10 frames)
        if not self.calibrated:
            return {
                "stress_level": "calibrating",
                "pitch_spike": False,
                "energy_spike": False,
                "confidence": 5.0,  # Neutral during calibration
            }
        
        stress_level = "low"
        pitch_spike = False
        energy_spike = False
        confidence = 5.0  # Default neutral
        
        # Check if currently speaking (non-zero pitch and sufficient energy)
        is_speaking = current_pitch > 0 and current_energy > 0.01
        
        if is_speaking and self.baseline_pitch and self.baseline_energy and self.baseline_pitch > 0:
            pitch_deviation = abs(current_pitch - self.baseline_pitch) / (self.baseline_pitch + 1e-6)
            energy_deviation = abs(current_energy - self.baseline_energy) / (self.baseline_energy + 1e-6)
            
            # Stress detection with improved thresholds
            if pitch_deviation > 0.35 or energy_deviation > 0.5:
                stress_level = "high"
                if pitch_deviation > 0.35:
                    pitch_spike = True
                if energy_deviation > 0.5:
                    energy_spike = True
            elif pitch_deviation > 0.18 or energy_deviation > 0.25:
                stress_level = "medium"
            
            # Voice confidence calculation (higher is better, 0-10 scale)
            # Factors: pitch stability, energy consistency, speaking rate
            pitch_stability = 1.0 - min(pitch_deviation, 1.0)
            energy_stability = 1.0 - min(energy_deviation, 1.0)
            
            # Combine factors (weighted)
            raw_confidence = (pitch_stability * 0.5 + energy_stability * 0.5)
            
            # Scale to 0-10, with baseline at 6.0 for normal speech
            confidence = 4.0 + (raw_confidence * 6.0)
            
            # Penalty for extreme deviations
            if stress_level == "high":
                confidence *= 0.7
            elif stress_level == "medium":
                confidence *= 0.85
            
            # Bonus for stable speech
            if pitch_deviation < 0.1 and energy_deviation < 0.15:
                confidence = min(10.0, confidence + 1.5)
            
        elif not is_speaking:
            # If not speaking, return neutral confidence (not 0)
            confidence = 5.0
            stress_level = "unknown"
        
        return {
            "stress_level": stress_level,
            "pitch_spike": pitch_spike,
            "energy_spike": energy_spike,
            "confidence": float(np.clip(confidence, 1.0, 10.0)),
        }

    def _empty_result(self) -> Dict:
        return {
            "pitch": 0.0,
            "energy": 0.0,
            "speaking_rate": 0.0,
            "silence_duration": 0.0,
            "max_silence": float(self.max_silence_duration),
            "silence_detected": False,
            "pitch_spike": False,
            "energy_spike": False,
            "stress_level": "unknown",
            "voice_confidence": 0.0,
            "baseline_pitch": float(self.baseline_pitch) if self.baseline_pitch else 0.0,
            "baseline_energy": float(self.baseline_energy) if self.baseline_energy else 0.0,
        }

    def reset(self):
        """Reset analyzer state."""
        self.audio_buffer.clear()
        self.pitch_history.clear()
        self.energy_history.clear()
        self.baseline_pitch = None
        self.baseline_energy = None
        self.calibrated = False
        self.silence_start = None
        self.max_silence_duration = 0
        self.current_silence_duration = 0
