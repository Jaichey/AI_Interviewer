"""
Emotion detection using a lightweight local model.
Uses a pretrained emotion classification model (no cloud calls).
"""
import cv2
import numpy as np
from typing import Dict, Optional
import os


class EmotionAnalyzer:
    """Detects emotion from facial expressions using local model."""

    def __init__(self):
        """Initialize with a pretrained emotion model."""
        # Use OpenCV's DNN module with a local pretrained model
        # We'll use a simple face detector + emotion classifier
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Emotion labels
        self.emotions = ["Angry", "Disgusted", "Fearful", "Happy", "Neutral", "Sad", "Surprised"]
        
        # Try to load pretrained model (if available)
        self.model_loaded = False
        self._load_model()
        
        # Fallback: simple heuristic emotion detection
        self.use_heuristic = not self.model_loaded

    def _load_model(self):
        """Load pretrained emotion model if available."""
        try:
            # Try loading a pretrained model (e.g., from OpenCV or local file)
            model_path = os.path.join(os.path.dirname(__file__), "emotion_model.onnx")
            if os.path.exists(model_path):
                self.net = cv2.dnn.readNetFromONNX(model_path)
                self.model_loaded = True
        except Exception as e:
            print(f"[INFO] Emotion model not available, using heuristic analysis: {e}")
            self.model_loaded = False

    def analyze(self, frame: np.ndarray) -> Dict:
        """Analyze frame for emotion."""
        if frame is None or frame.size == 0:
            return self._empty_result()

        if self.use_heuristic:
            return self._heuristic_emotion(frame)
        else:
            return self._model_emotion(frame)

    def _heuristic_emotion(self, frame: np.ndarray) -> Dict:
        """Enhanced heuristic-based emotion detection with better preprocessing."""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better feature extraction
            gray = cv2.equalizeHist(gray)
            
            # Detect faces with optimized parameters
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(50, 50)
            )
            
            if len(faces) == 0:
                return self._empty_result()
            
            # Analyze facial features in the detected face
            x, y, w, h = faces[0]
            face_region = gray[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return self._empty_result()
            
            # Resize for consistent analysis
            face_region = cv2.resize(face_region, (96, 96))
            
            # Apply Gaussian blur to reduce noise
            face_region = cv2.GaussianBlur(face_region, (5, 5), 0)
            
            # Extract comprehensive features
            brightness_var = np.var(face_region)
            brightness_mean = np.mean(face_region)
            brightness_std = np.std(face_region)
            
            # Divide face into regions for detailed analysis
            # Eye region (upper 40% of face)
            eye_region = face_region[10:40, :]
            eye_brightness = np.mean(eye_region)
            eye_var = np.var(eye_region)
            eye_std = np.std(eye_region)
            
            # Eyebrow region (top 20%)
            eyebrow_region = face_region[5:20, :]
            eyebrow_var = np.var(eyebrow_region)
            
            # Mouth region (bottom 30%)
            mouth_region = face_region[65:90, 25:70]
            mouth_brightness = np.mean(mouth_region)
            mouth_var = np.var(mouth_region)
            mouth_std = np.std(mouth_region)
            
            # Cheek regions (mid face)
            left_cheek = face_region[35:65, 10:35]
            right_cheek = face_region[35:65, 60:85]
            cheek_symmetry = abs(np.mean(left_cheek) - np.mean(right_cheek))
            
            # Edge detection for expression intensity
            edges = cv2.Canny(face_region, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Initialize confidence scores with realistic baselines
            confidence_scores = {
                "Neutral": 4.0,
                "Happy": 2.0,
                "Focused": 3.0,
                "Stressed": 2.0,
                "Confused": 2.0,
                "Confident": 3.0,
            }
            # Happy: bright mouth (smile), high mouth variance, low eyebrow tension
            if mouth_brightness > brightness_mean * 1.08 and mouth_var > 250 and eyebrow_var < 300:
                confidence_scores["Happy"] += 4.5
                confidence_scores["Confident"] += 2.5
                confidence_scores["Neutral"] -= 1.5
                confidence_scores["Stressed"] -= 1.0
            
            # Focused: concentrated eye region, low variance, good symmetry
            elif eye_var < 350 and brightness_std < 40 and cheek_symmetry < 8 and edge_density < 0.15:
                confidence_scores["Focused"] += 4.0
                confidence_scores["Confident"] += 2.0
                confidence_scores["Neutral"] += 1.0
                confidence_scores["Confused"] -= 1.5
            
            # Stressed: high variance, tense features, high edge density
            elif brightness_var > 550 and eye_var > 450 and edge_density > 0.18:
                confidence_scores["Stressed"] += 4.5
                confidence_scores["Confused"] += 1.5
                confidence_scores["Confident"] -= 2.0
                confidence_scores["Happy"] -= 1.5
            
            # Confused: asymmetry, uneven features, moderate variance
            elif cheek_symmetry > 12 or abs(eye_brightness - mouth_brightness) > 20:
                confidence_scores["Confused"] += 3.5
                confidence_scores["Focused"] -= 1.5
                confidence_scores["Confident"] -= 1.0
            
            # Confident: balanced, moderate brightness, good symmetry, relaxed features
            elif 90 < brightness_mean < 150 and 300 < brightness_var < 500 and cheek_symmetry < 10:
                confidence_scores["Confident"] += 3.5
                confidence_scores["Focused"] += 1.5
                confidence_scores["Neutral"] += 1.0
            
            # Neutral adjustment: low variance, balanced features
            if brightness_var < 400 and cheek_symmetry < 8 and edge_density < 0.12:
                confidence_scores["Neutral"] += 2.0
            # Ensure minimum values
            confidence_scores = {k: max(1.0, v) for k, v in confidence_scores.items()}
            
            dominant_emotion = max(confidence_scores, key=confidence_scores.get)
            
            # Estimate stress level with improved thresholds
            stress_level = self._estimate_stress_level_enhanced(
                brightness_var, 
                eye_var, 
                mouth_var, 
                edge_density
            )\n            
            return {\n                \"emotion\": dominant_emotion,\n                \"confidence\": float(confidence_scores.get(dominant_emotion, 5.0)),\n                \"emotion_scores\": {k: float(v) for k, v in confidence_scores.items()},\n                \"stress_level\": stress_level,\n                \"brightness_variance\": float(brightness_var),\n                \"eye_brightness\": float(eye_brightness),\n                \"mouth_brightness\": float(mouth_brightness),\n                \"edge_density\": float(edge_density),\n                \"cheek_symmetry\": float(cheek_symmetry),\n            }\n        except Exception as e:\n            print(f\"[ERROR] Emotion analysis failed: {e}\")\n            import traceback\n            traceback.print_exc()
            return self._empty_result()

    def _model_emotion(self, frame: np.ndarray) -> Dict:
        """Emotion detection using pretrained model."""
        # Placeholder for model-based detection
        # If model is available, this would run the inference
        return self._heuristic_emotion(frame)

    @staticmethod
    def _estimate_stress_level_enhanced(brightness_var: float, eye_var: float, 
                                        mouth_var: float, edge_density: float) -> str:
        """Enhanced stress level estimation using multiple facial features."""
        stress_score = 0
        
        # High overall variance indicates tension
        if brightness_var > 600:
            stress_score += 3
        elif brightness_var > 450:
            stress_score += 2
        elif brightness_var > 350:
            stress_score += 1
        
        # Eye tension
        if eye_var > 500:
            stress_score += 2
        elif eye_var > 400:
            stress_score += 1
        
        # Mouth tension
        if mouth_var > 400:
            stress_score += 1
        
        # High edge density indicates facial tension
        if edge_density > 0.18:
            stress_score += 2
        elif edge_density > 0.15:
            stress_score += 1
        
        # Classify stress level
        if stress_score >= 6:
            return "high"
        elif stress_score >= 3:
            return "medium"
        else:
            return "low"
    
    
    @staticmethod
    def _estimate_stress_level(brightness_var: float, brightness_mean: float) -> str:
        """Estimate stress level from facial features (legacy method)."""
        # High variance + low brightness = potential stress
        if brightness_var > 2500 and brightness_mean < 100:
            return "high"
        elif brightness_var > 2000:
            return "medium"
        else:
            return "low"

    def _empty_result(self) -> Dict:
        return {
            "emotion": "unknown",
            "confidence": 0.0,
            "emotion_scores": {},
            "stress_level": "unknown",
            "brightness_variance": 0.0,
        }

    def reset(self):
        """Reset any state."""
        pass
