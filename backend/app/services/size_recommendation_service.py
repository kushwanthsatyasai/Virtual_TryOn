"""
Size Recommendation Service
===========================
AI-powered size recommendations based on body measurements
"""
from typing import Dict, Optional
import numpy as np
from PIL import Image

MEDIAPIPE_AVAILABLE = False
_mp = None

try:
    import mediapipe as _mp
    import cv2
    # On some platforms (e.g. Render, Python 3.13) mediapipe installs but .solutions is missing
    if getattr(_mp, "solutions", None) is not None and getattr(_mp.solutions, "pose", None) is not None:
        MEDIAPIPE_AVAILABLE = True
except (ImportError, AttributeError):
    pass


def _create_pose_detector():
    """Create pose detector if available; otherwise None. Avoids crash when mediapipe.solutions is missing."""
    if not MEDIAPIPE_AVAILABLE or _mp is None:
        return None
    try:
        return _mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            min_detection_confidence=0.5,
        )
    except (AttributeError, Exception):
        return None


class SizeRecommendationService:
    """Recommend clothing sizes based on measurements"""
    
    def __init__(self):
        try:
            self.pose_detector = _create_pose_detector()
        except (AttributeError, Exception):
            # Render / Python 3.13: mediapipe may install but .solutions missing
            self.pose_detector = None
    
    def estimate_measurements_from_image(
        self,
        image_path: str,
        user_height_cm: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Estimate body measurements from image
        
        Args:
            image_path: Path to person image
            user_height_cm: User's actual height for calibration (optional)
        
        Returns:
            Dictionary with estimated measurements
        """
        if not MEDIAPIPE_AVAILABLE or not self.pose_detector:
            return self._default_measurements()
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return self._default_measurements()
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect pose
        results = self.pose_detector.process(image_rgb)
        
        if not results.pose_landmarks:
            return self._default_measurements()
        
        landmarks = results.pose_landmarks.landmark
        h, w, _ = image.shape
        
        # Get key landmarks (normalized 0-1); use _mp when pose is available
        pose_lm = _mp.solutions.pose.PoseLandmark
        left_shoulder = landmarks[pose_lm.LEFT_SHOULDER]
        right_shoulder = landmarks[pose_lm.RIGHT_SHOULDER]
        left_hip = landmarks[pose_lm.LEFT_HIP]
        right_hip = landmarks[pose_lm.RIGHT_HIP]
        
        # Calculate pixel distances
        shoulder_width_px = np.sqrt(
            ((left_shoulder.x - right_shoulder.x) * w) ** 2 +
            ((left_shoulder.y - right_shoulder.y) * h) ** 2
        )
        
        hip_width_px = np.sqrt(
            ((left_hip.x - right_hip.x) * w) ** 2 +
            ((left_hip.y - right_hip.y) * h) ** 2
        )
        
        torso_length_px = np.sqrt(
            ((left_shoulder.x - left_hip.x) * w) ** 2 +
            ((left_shoulder.y - left_hip.y) * h) ** 2
        )
        
        # Estimate height from landmarks if not provided
        if user_height_cm is None:
            # Rough estimate: torso is about 40% of height
            estimated_height_cm = 170  # Default
        else:
            estimated_height_cm = user_height_cm
        
        # Calibration factor (pixels per cm)
        # Assuming torso is ~40% of height
        expected_torso_cm = estimated_height_cm * 0.4
        px_per_cm = torso_length_px / expected_torso_cm
        
        # Convert to cm
        shoulder_width_cm = shoulder_width_px / px_per_cm
        hip_width_cm = hip_width_px / px_per_cm
        
        # Estimate other measurements (rough approximations)
        chest_cm = shoulder_width_cm * 2.2  # Chest is wider than shoulders
        waist_cm = hip_width_cm * 1.8
        
        return {
            "height_cm": estimated_height_cm,
            "shoulder_width_cm": round(shoulder_width_cm, 1),
            "chest_cm": round(chest_cm, 1),
            "waist_cm": round(waist_cm, 1),
            "hip_cm": round(hip_width_cm * 2, 1),  # Hip circumference
        }
    
    def recommend_size(
        self,
        measurements: Dict[str, float],
        garment_type: str = "shirt",
        gender: str = "unisex"
    ) -> Dict[str, any]:
        """
        Recommend size based on measurements
        
        Args:
            measurements: Body measurements dict
            garment_type: shirt, pants, dress, etc.
            gender: male, female, unisex
        
        Returns:
            Recommended size and confidence
        """
        chest = measurements.get("chest_cm", 90)
        waist = measurements.get("waist_cm", 75)
        hip = measurements.get("hip_cm", 95)
        
        # Size charts (approximate)
        if garment_type in ["shirt", "top", "jacket"]:
            size_chart = self._get_shirt_size_chart(gender)
            ref_measurement = chest
        elif garment_type in ["pants", "jeans", "skirt"]:
            size_chart = self._get_pants_size_chart(gender)
            ref_measurement = waist
        elif garment_type in ["dress"]:
            size_chart = self._get_dress_size_chart(gender)
            ref_measurement = (chest + waist + hip) / 3  # Average
        else:
            # Default to shirt
            size_chart = self._get_shirt_size_chart(gender)
            ref_measurement = chest
        
        # Find best fit
        best_size = "M"
        min_diff = float('inf')
        
        for size, range_cm in size_chart.items():
            mid_point = (range_cm[0] + range_cm[1]) / 2
            diff = abs(ref_measurement - mid_point)
            
            if diff < min_diff:
                min_diff = diff
                best_size = size
        
        # Calculate confidence (closer = higher confidence)
        confidence = max(0, 1 - (min_diff / 20))  # 0-1 scale
        
        # Recommendations
        recommendations = [best_size]
        
        # Suggest adjacent sizes if on border
        if confidence < 0.8:
            size_order = list(size_chart.keys())
            idx = size_order.index(best_size)
            
            if min_diff > 0 and idx < len(size_order) - 1:
                recommendations.append(size_order[idx + 1])
            elif min_diff < 0 and idx > 0:
                recommendations.insert(0, size_order[idx - 1])
        
        return {
            "recommended_size": best_size,
            "alternative_sizes": recommendations,
            "confidence": round(confidence, 2),
            "measurements_used": {
                "chest_cm": chest,
                "waist_cm": waist,
                "hip_cm": hip
            },
            "fit_notes": self._get_fit_notes(ref_measurement, size_chart[best_size])
        }
    
    def _get_shirt_size_chart(self, gender: str) -> Dict[str, tuple]:
        """Get shirt size chart"""
        if gender == "male":
            return {
                "XS": (81, 86),
                "S": (86, 91),
                "M": (91, 97),
                "L": (97, 102),
                "XL": (102, 107),
                "XXL": (107, 112)
            }
        elif gender == "female":
            return {
                "XS": (76, 81),
                "S": (81, 86),
                "M": (86, 91),
                "L": (91, 97),
                "XL": (97, 102),
                "XXL": (102, 107)
            }
        else:  # unisex
            return {
                "XS": (76, 86),
                "S": (86, 91),
                "M": (91, 97),
                "L": (97, 102),
                "XL": (102, 107),
                "XXL": (107, 112)
            }
    
    def _get_pants_size_chart(self, gender: str) -> Dict[str, tuple]:
        """Get pants size chart (waist)"""
        return {
            "XS": (66, 71),
            "S": (71, 76),
            "M": (76, 81),
            "L": (81, 86),
            "XL": (86, 91),
            "XXL": (91, 97)
        }
    
    def _get_dress_size_chart(self, gender: str) -> Dict[str, tuple]:
        """Get dress size chart"""
        return {
            "XS": (81, 86),
            "S": (86, 91),
            "M": (91, 94),
            "L": (94, 99),
            "XL": (99, 104),
            "XXL": (104, 109)
        }
    
    def _get_fit_notes(self, measurement: float, size_range: tuple) -> str:
        """Generate fit notes"""
        mid = (size_range[0] + size_range[1]) / 2
        
        if measurement < size_range[0]:
            return "May be slightly loose"
        elif measurement > size_range[1]:
            return "May be slightly tight"
        elif abs(measurement - mid) < 2:
            return "Perfect fit"
        elif measurement < mid:
            return "Comfortable fit with room"
        else:
            return "Fitted style"
    
    def _default_measurements(self) -> Dict[str, float]:
        """Default measurements if detection fails"""
        return {
            "height_cm": 170,
            "shoulder_width_cm": 42,
            "chest_cm": 90,
            "waist_cm": 75,
            "hip_cm": 95
        }
