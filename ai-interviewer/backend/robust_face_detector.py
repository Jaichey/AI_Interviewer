"""
Robust face and person detection using YOLOv8.
Provides accurate multi-person detection with strict filtering to avoid false positives.
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
import os

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class RobustFaceDetector:
    """
    Detects faces and persons using YOLOv8.
    More reliable than Haar Cascade with strict filtering to prevent false positives.
    """
    
    def __init__(self, model_size: str = "s"):
        """
        Initialize YOLOv8 face detector.
        
        Args:
            model_size: Model size - 'n' (nano), 's' (small), 'm' (medium)
                       Small is recommended for balance between speed and accuracy
        """
        if not YOLO_AVAILABLE:
            raise RuntimeError(
                "YOLOv8 not available. Install with: pip install ultralytics"
            )
        
        # Use the appropriate model
        model_name = f"yolov8{model_size}.pt"
        self.model = YOLO(model_name)
        
        # Set model to evaluation mode
        self.model.to('cpu')  # Use CPU for consistency
        
        # STRICT THRESHOLDS to reduce false positives
        self.person_conf_threshold = 0.75  # Only count persons with >75% confidence (STRICT)
        self.min_person_area = 10000       # Minimum 100x100 pixels to avoid small false detections
        self.iou_threshold = 0.5           # IoU threshold for removing duplicate detections
        
        # Class IDs in COCO dataset
        self.PERSON_CLASS_ID = 0  # "person" class in COCO
        
        # Temporal smoothing for multi-person detection
        self.multi_person_frames = []      # Store recent detection results
        self.temporal_window = 5           # Require 5 frames to confirm
        
    def detect_persons(self, frame: np.ndarray) -> Tuple[int, List[Dict]]:
        """
        Detect persons in the frame using YOLOv8 with strict filtering.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            Tuple of (person_count, list of person detections with details)
        """
        if frame is None or frame.size == 0:
            return 0, []
        
        try:
            # Run YOLO inference with STRICT confidence threshold
            results = self.model(frame, verbose=False, conf=self.person_conf_threshold)
            
            if not results or len(results) == 0:
                return 0, []
            
            result = results[0]
            raw_persons = []
            
            # Extract detections with area filtering
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    # Check if this is a person detection
                    if int(box.cls) == self.PERSON_CLASS_ID:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(float, box.xyxy[0])
                        conf = float(box.conf)
                        
                        # Calculate area
                        width = int(x2 - x1)
                        height = int(y2 - y1)
                        area = width * height
                        
                        # Filter by area (remove tiny detections - likely false positives)
                        if area >= self.min_person_area:
                            raw_persons.append({
                                "bbox": (int(x1), int(y1), int(x2), int(y2)),
                                "confidence": conf,
                                "center": (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                                "width": width,
                                "height": height,
                                "area": area
                            })
            
            # Apply Non-Maximum Suppression (NMS) to remove duplicate/overlapping detections
            persons = self._apply_nms(raw_persons)
            
            return len(persons), persons
            
        except Exception as e:
            print(f"Error in person detection: {e}")
            return 0, []
    
    def is_multiple_persons(self, frame: np.ndarray) -> bool:
        """
        Check if multiple persons are detected in the frame.
        Uses temporal smoothing to avoid false positives from momentary detections.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            True if multiple persons detected consistently, False otherwise
        """
        person_count, _ = self.detect_persons(frame)
        
        # Add to temporal window
        self.multi_person_frames.append(person_count > 1)
        
        # Keep only recent frames
        if len(self.multi_person_frames) > self.temporal_window:
            self.multi_person_frames.pop(0)
        
        # Require at least 3 out of last 5 frames to confirm multiple persons
        # This prevents false positives from momentary detections
        if len(self.multi_person_frames) >= 3:
            multi_detections = sum(self.multi_person_frames)
            return multi_detections >= 3
        
        # Not enough frames yet, return False (conservative)
        return False
    
    def get_largest_person_bbox(self, frame: np.ndarray) -> Tuple[bool, Tuple[int, int, int, int]]:
        """
        Get the bounding box of the largest person in the frame.
        Useful for focusing analysis on the main subject.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            Tuple of (person_found, bbox) where bbox is (x1, y1, x2, y2)
        """
        person_count, persons = self.detect_persons(frame)
        
        if person_count == 0:
            return False, (0, 0, 0, 0)
        
        # Get the largest person by area
        largest = max(persons, key=lambda p: p["area"])
        return True, largest["bbox"]
    
    def is_face_centered(self, frame: np.ndarray) -> Tuple[bool, float]:
        """
        Check if a face/person is approximately centered in the frame.
        Returns confidence score for framing quality.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            Tuple of (is_centered, confidence_score)
        """
        found, bbox = self.get_largest_person_bbox(frame)
        
        if not found:
            return False, 0.0
        
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        
        # Calculate center of person
        person_center_x = (x1 + x2) / 2
        person_center_y = (y1 + y2) / 2
        
        # Frame center
        frame_center_x = w / 2
        frame_center_y = h / 2
        
        # Calculate deviation from center
        dx = abs(person_center_x - frame_center_x) / (w / 2)
        dy = abs(person_center_y - frame_center_y) / (h / 2)
        
        # Centering score: 1.0 = perfect center, 0.0 = far from center
        centering_score = max(0.0, 1.0 - (dx + dy) / 2.0)
        
        # Consider centered if within 30% of frame center
        is_centered = (dx + dy) / 2.0 < 0.3
        
        return is_centered, float(centering_score)
    
    def validate_single_person_frame(self, frame: np.ndarray) -> Dict[str, any]:
        """
        Validate that the frame contains exactly one person properly framed.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            Dictionary with validation results:
            - single_person: bool - exactly one person detected
            - person_count: int - number of persons detected
            - properly_centered: bool - person is centered
            - centering_score: float - 0-1 quality score
            - main_person_bbox: tuple - bounding box of main person
        """
        person_count, persons = self.detect_persons(frame)
        found, main_bbox = self.get_largest_person_bbox(frame)
        is_centered, centering_score = self.is_face_centered(frame)
        
        return {
            "single_person": person_count == 1,
            "person_count": person_count,
            "properly_centered": is_centered,
            "centering_score": centering_score,
            "main_person_bbox": main_bbox,
            "all_detections": persons
        }
    
    def _apply_nms(self, detections: List[Dict]) -> List[Dict]:
        """
        Apply Non-Maximum Suppression to remove duplicate/overlapping detections.
        
        Args:
            detections: List of detection dictionaries with bbox and confidence
            
        Returns:
            Filtered list of detections with duplicates removed
        """
        if len(detections) <= 1:
            return detections
        
        # Sort by confidence (highest first)
        detections = sorted(detections, key=lambda x: x["confidence"], reverse=True)
        
        keep = []
        while detections:
            # Keep the highest confidence detection
            best = detections.pop(0)
            keep.append(best)
            
            # Remove overlapping detections
            detections = [
                det for det in detections 
                if self._calculate_iou(best["bbox"], det["bbox"]) < self.iou_threshold
            ]
        
        return keep
    
    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bbox1: First bounding box (x1, y1, x2, y2)
            bbox2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            IoU value between 0 and 1
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection area
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union area
        bbox1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        bbox2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = bbox1_area + bbox2_area - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area


class HybridFaceAnalyzer:
    """
    Combines YOLOv8 person detection with MediaPipe detailed facial analysis.
    Uses YOLOv8 for robust multi-person detection, MediaPipe for eye/gaze details.
    """
    
    def __init__(self):
        """Initialize both detectors."""
        self.robust_detector = RobustFaceDetector(model_size="s")
        self.person_detected_cache = 0
        
    def check_multiple_persons(self, frame: np.ndarray) -> bool:
        """
        Robust check for multiple persons using YOLOv8.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            True if multiple persons detected, False otherwise
        """
        is_multiple = self.robust_detector.is_multiple_persons(frame)
        self.person_detected_cache = 1 if not is_multiple else 2
        return is_multiple
    
    def check_person_visible(self, frame: np.ndarray) -> Tuple[bool, Dict]:
        """
        Check if a single person is visible and properly framed.
        
        Args:
            frame: Input image (BGR format)
            
        Returns:
            Tuple of (single_person_visible, validation_dict)
        """
        validation = self.robust_detector.validate_single_person_frame(frame)
        return validation["single_person"], validation
