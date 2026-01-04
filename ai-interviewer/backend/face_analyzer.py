"""
Face and gaze detection using MediaPipe with YOLOv8 for robust multi-person detection.
LOCAL ONLY - No cloud dependencies.
"""
import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import time

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Import YOLOv8 for robust person detection
try:
    from robust_face_detector import RobustFaceDetector
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class FaceAnalyzer:
    """Detects face presence, head direction, eye gaze, and blink rate."""

    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe not available. Install with: pip install mediapipe")
        
        # Initialize MediaPipe for detailed facial analysis
        try:
            from mediapipe.python.solutions import face_mesh as mp_face_mesh
            self.mp_face_mesh = mp_face_mesh
            # Enable iris landmarks for accurate eye tracking
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,  # Process only main face for detailed analysis
                refine_landmarks=True,  # Enable iris landmarks
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        except Exception:
            self.face_mesh = None
        
        # Initialize YOLOv8 for robust multi-person detection
        self.yolo_detector = None
        if YOLO_AVAILABLE:
            try:
                self.yolo_detector = RobustFaceDetector(model_size="s")
            except Exception as e:
                print(f"Warning: Could not initialize YOLOv8 detector: {e}")
                self.yolo_detector = None
        
        # Fallback Haar Cascade (only used if YOLOv8 fails)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Iris landmark indices (MediaPipe Face Mesh with iris)
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Eye landmark indices for aspect ratio
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # Face model points for 3D head pose
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)
        
        self.last_blink_time = time.time()
        self.blink_count = 0
        self.looking_away_start = None
        self.eye_aspect_ratio_threshold = 0.21

    def analyze(self, frame: np.ndarray) -> Dict:
        """Analyze frame for face, gaze, blink, and head direction."""
        if frame is None or frame.size == 0:
            return self._empty_result()

        h, w, _ = frame.shape
        
        # ROBUST MULTI-PERSON DETECTION: Use YOLOv8 first
        if self.yolo_detector is not None:
            try:
                # Check for multiple persons using YOLOv8 (more reliable)
                is_multiple = self.yolo_detector.is_multiple_persons(frame)
                
                if is_multiple:
                    return {
                        "face_detected": True,
                        "multiple_faces": True,
                        "face_count": 2,  # At least 2 detected
                        "violation": "MULTIPLE_PERSONS_DETECTED",
                        "head_yaw": 0.0,
                        "head_pitch": 0.0,
                        "gaze_direction": "violation",
                        "blink_detected": False,
                        "blink_count": self.blink_count,
                        "eye_aspect_ratio": 0.0,
                        "looking_away": True,
                        "looking_at_camera": False,
                        "eye_contact_confidence": 0.0
                    }
            except Exception as e:
                print(f"YOLOv8 detection warning: {e}")
                # Fall back to Haar Cascade if YOLOv8 fails
                pass
        
        # Fallback: Check for multiple faces using Haar Cascade (only if YOLOv8 unavailable)
        if self.yolo_detector is None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.3,  # Increased to reduce false positives
                minNeighbors=6,   # Increased to reduce false positives
                minSize=(80, 80)  # Larger minimum face size
            )
            
            if len(faces) > 1:
                return {
                    "face_detected": True,
                    "multiple_faces": True,
                    "face_count": len(faces),
                    "violation": "MULTIPLE_PERSONS_DETECTED",
                    "head_yaw": 0.0,
                    "head_pitch": 0.0,
                    "gaze_direction": "violation",
                    "blink_detected": False,
                    "blink_count": self.blink_count,
                    "eye_aspect_ratio": 0.0,
                    "looking_away": True,
                    "looking_at_camera": False,
                    "eye_contact_confidence": 0.0
                }
        
        # Use MediaPipe for detailed single-person analysis
        if self.face_mesh is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks and len(results.multi_face_landmarks) == 1:
                return self._analyze_with_mesh(frame, h, w, results)
        
        # Fallback: Use Haar Cascade for single face analysis if MediaPipe unavailable
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.3, 
            minNeighbors=6,
            minSize=(80, 80)
        )
        
        if len(faces) == 1:
            return self._analyze_with_cascade(frame, h, w)
        else:
            return self._empty_result()
    
    def _analyze_with_mesh(self, frame: np.ndarray, h: int, w: int, results) -> Dict:
        """Analyze using MediaPipe Face Mesh with iris tracking."""
        if not results.multi_face_landmarks:
            return self._empty_result()

        landmarks = results.multi_face_landmarks[0]
        
        # Extract eye landmarks
        left_eye = [landmarks.landmark[i] for i in self.LEFT_EYE]
        right_eye = [landmarks.landmark[i] for i in self.RIGHT_EYE]
        
        # Extract iris landmarks (center of each iris)
        left_iris_center = self._get_iris_center(landmarks, self.LEFT_IRIS)
        right_iris_center = self._get_iris_center(landmarks, self.RIGHT_IRIS)
        
        # Blink detection using eye aspect ratio
        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2
        
        blink_detected = ear < self.eye_aspect_ratio_threshold
        if blink_detected and time.time() - self.last_blink_time > 0.3:
            self.blink_count += 1
            self.last_blink_time = time.time()
        
        # Calculate 3D head pose using solvePnP
        yaw, pitch = self._calculate_3d_head_pose(landmarks, h, w)
        
        # Accurate gaze direction using iris position
        gaze_dir, gaze_offset = self._calculate_iris_gaze(left_iris_center, right_iris_center, left_eye, right_eye)
        
        # Eye contact detection combining head pose and iris gaze
        # More accurate: head facing forward AND irises centered
        head_facing_forward = abs(yaw) < 15 and abs(pitch) < 12
        iris_centered = abs(gaze_offset) < 0.15  # Iris within 15% of eye center
        
        looking_at_camera = head_facing_forward and iris_centered
        
        # Calculate eye contact confidence (0-1 scale)
        head_confidence = max(0.0, 1.0 - (abs(yaw) / 30.0 + abs(pitch) / 25.0) / 2.0)
        iris_confidence = max(0.0, 1.0 - abs(gaze_offset) / 0.3)
        eye_contact_confidence = (head_confidence * 0.6 + iris_confidence * 0.4)  # Weighted combination
        
        # Looking away detection (more strict)
        looking_away = abs(yaw) > 25 or abs(pitch) > 20 or abs(gaze_offset) > 0.25
        
        return {
            "face_detected": True,
            "multiple_faces": False,
            "face_count": 1,
            "head_yaw": float(yaw),
            "head_pitch": float(pitch),
            "gaze_direction": gaze_dir,
            "gaze_offset": float(gaze_offset),
            "blink_detected": blink_detected,
            "blink_count": self.blink_count,
            "eye_aspect_ratio": float(ear),
            "looking_away": looking_away,
            "looking_at_camera": looking_at_camera,
            "eye_contact_confidence": float(eye_contact_confidence),
            "eye_aspect_ratio_left": float(left_ear),
            "eye_aspect_ratio_right": float(right_ear),
            "iris_confidence": float(iris_confidence),
            "head_confidence": float(head_confidence),
        }
    
    def _analyze_with_cascade(self, frame: np.ndarray, h: int, w: int) -> Dict:
        """Analyze using Haar Cascade (fallback)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return self._empty_result()
        
        # Simple heuristic-based analysis
        x, y, fw, fh = faces[0]
        face_center_x = x + fw / 2
        face_center_y = y + fh / 2
        
        # Estimate head direction based on face position
        yaw = ((face_center_x / w) - 0.5) * 50  # -25 to +25 degrees
        pitch = ((face_center_y / h) - 0.5) * 40  # -20 to +20 degrees
        
        looking_away = abs(yaw) > 25 or abs(pitch) > 20
        
        looking_at_camera = abs(yaw) < 15 and abs(pitch) < 10
        eye_contact_confidence = max(0.0, 1.0 - (abs(yaw) / 30.0 + abs(pitch) / 25.0) / 2.0)
        
        return {
            "face_detected": True,
            "multiple_faces": False,
            "face_count": 1,
            "head_yaw": float(yaw),
            "head_pitch": float(pitch),
            "gaze_direction": "center",
            "blink_detected": False,
            "blink_count": self.blink_count,
            "eye_aspect_ratio": 0.3,
            "looking_away": looking_away,
            "looking_at_camera": looking_at_camera,
            "eye_contact_confidence": float(eye_contact_confidence),
            "eye_aspect_ratio_left": 0.3,
            "eye_aspect_ratio_right": 0.3,
        }

    def _empty_result(self) -> Dict:
        return {
            "face_detected": False,
            "head_yaw": 0.0,
            "head_pitch": 0.0,
            "gaze_direction": "unknown",
            "blink_detected": False,
            "blink_count": self.blink_count,
            "eye_aspect_ratio": 0.0,
            "looking_away": True,
            "eye_aspect_ratio_left": 0.0,
            "eye_aspect_ratio_right": 0.0,
        }

    @staticmethod
    def _eye_aspect_ratio(eye_landmarks) -> float:
        """Calculate eye aspect ratio from 6 landmarks."""
        if len(eye_landmarks) < 6:
            return 0.0
        
        p1, p2, p3, p4, p5, p6 = eye_landmarks
        
        dist_vertical_1 = np.sqrt((p2.x - p5.x) ** 2 + (p2.y - p5.y) ** 2)
        dist_vertical_2 = np.sqrt((p3.x - p4.x) ** 2 + (p3.y - p4.y) ** 2)
        dist_horizontal = np.sqrt((p1.x - p6.x) ** 2 + (p1.y - p6.y) ** 2)
        
        if dist_horizontal == 0:
            return 0.0
        
        return (dist_vertical_1 + dist_vertical_2) / (2.0 * dist_horizontal)

    def _calculate_3d_head_pose(self, landmarks, h: int, w: int) -> Tuple[float, float]:
        """Calculate accurate 3D head pose using solvePnP."""
        try:
            # Extract 2D image points from landmarks
            image_points = np.array([
                (landmarks.landmark[1].x * w, landmarks.landmark[1].y * h),      # Nose tip
                (landmarks.landmark[152].x * w, landmarks.landmark[152].y * h),   # Chin
                (landmarks.landmark[263].x * w, landmarks.landmark[263].y * h),   # Left eye left corner
                (landmarks.landmark[33].x * w, landmarks.landmark[33].y * h),     # Right eye right corner
                (landmarks.landmark[287].x * w, landmarks.landmark[287].y * h),   # Left mouth corner
                (landmarks.landmark[57].x * w, landmarks.landmark[57].y * h)      # Right mouth corner
            ], dtype=np.float64)
            
            # Camera internals (approximation)
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # Assume no lens distortion
            dist_coeffs = np.zeros((4, 1))
            
            # Solve PnP
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return 0.0, 0.0
            
            # Convert rotation vector to Euler angles
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Extract yaw and pitch from rotation matrix
            # Yaw (left/right rotation)
            yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            yaw_degrees = np.degrees(yaw)
            
            # Pitch (up/down rotation)
            pitch = np.arctan2(-rotation_matrix[2, 0], 
                               np.sqrt(rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))
            pitch_degrees = np.degrees(pitch)
            
            return float(np.clip(yaw_degrees, -45, 45)), float(np.clip(pitch_degrees, -35, 35))
            
        except Exception as e:
            # Fallback to simple estimation
            return 0.0, 0.0
    
    @staticmethod
    def _get_iris_center(landmarks, iris_indices) -> Tuple[float, float]:
        """Calculate center of iris from landmarks."""
        iris_x = sum(landmarks.landmark[i].x for i in iris_indices) / len(iris_indices)
        iris_y = sum(landmarks.landmark[i].y for i in iris_indices) / len(iris_indices)
        return iris_x, iris_y
    
    @staticmethod
    def _calculate_iris_gaze(left_iris, right_iris, left_eye, right_eye) -> Tuple[str, float]:
        """Calculate gaze direction from iris position relative to eye."""
        # Calculate iris position relative to eye boundaries
        # Left eye boundaries
        left_eye_left = left_eye[0].x
        left_eye_right = left_eye[3].x
        left_eye_width = abs(left_eye_right - left_eye_left)
        
        # Right eye boundaries
        right_eye_left = right_eye[0].x
        right_eye_right = right_eye[3].x
        right_eye_width = abs(right_eye_right - right_eye_left)
        
        if left_eye_width == 0 or right_eye_width == 0:
            return "center", 0.0
        
        # Calculate iris offset from eye center (-1 to 1, 0 is center)
        left_iris_offset = (left_iris[0] - (left_eye_left + left_eye_right) / 2) / (left_eye_width / 2)
        right_iris_offset = (right_iris[0] - (right_eye_left + right_eye_right) / 2) / (right_eye_width / 2)
        
        # Average offset
        avg_offset = (left_iris_offset + right_iris_offset) / 2
        
        # Determine gaze direction
        if avg_offset < -0.2:
            gaze_dir = "left"
        elif avg_offset > 0.2:
            gaze_dir = "right"
        else:
            gaze_dir = "center"
        
        return gaze_dir, float(avg_offset)

    @staticmethod
    def _estimate_gaze_direction(left_eye, right_eye) -> str:
        """Estimate gaze direction: center, left, right, up, down."""
        if len(left_eye) < 6 or len(right_eye) < 6:
            return "unknown"
        
        left_pupil_x = (left_eye[0].x + left_eye[3].x) / 2
        right_pupil_x = (right_eye[0].x + right_eye[3].x) / 2
        
        left_inner_x = left_eye[0].x
        left_outer_x = left_eye[3].x
        right_inner_x = right_eye[0].x
        right_outer_x = right_eye[3].x
        
        left_ratio = (left_pupil_x - left_inner_x) / (left_outer_x - left_inner_x + 1e-6)
        right_ratio = (right_pupil_x - right_inner_x) / (right_outer_x - right_inner_x + 1e-6)
        
        avg_ratio = (left_ratio + right_ratio) / 2
        
        if avg_ratio < 0.3:
            return "left"
        elif avg_ratio > 0.7:
            return "right"
        else:
            return "center"

    def reset(self):
        """Reset counters."""
        self.blink_count = 0
        self.looking_away_start = None
        self.last_blink_time = time.time()
