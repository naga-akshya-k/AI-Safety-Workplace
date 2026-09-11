import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import time

class FallDetectionState:
    UPRIGHT = "UPRIGHT"
    CROUCHING = "CROUCHING"
    FALLING = "FALLING"
    RECUMBENT = "RECUMBENT"
    CRITICAL_MAN_DOWN = "CRITICAL_MAN_DOWN"

class FallDetector:
    def __init__(self, immobility_threshold_seconds: float = 3.5):
        self.immobility_threshold = immobility_threshold_seconds
        # track_id -> { "state": str, "recumbent_since": float, "history": list, "last_keypoints": np.array }
        self.track_states: Dict[int, Dict[str, Any]] = {}

    @staticmethod
    def calculate_spine_angle(keypoints: np.ndarray) -> float:
        """
        Calculates angle of spine with respect to horizontal ground plane.
        Keypoint indices in COCO:
        5: left shoulder, 6: right shoulder
        11: left hip, 12: right hip
        """
        if len(keypoints) < 13:
            return 90.0 # Default upright

        l_sh, r_sh = keypoints[5], keypoints[6]
        l_hip, r_hip = keypoints[11], keypoints[12]

        # Check visibility confidence
        if (l_sh[2] < 0.25 and r_sh[2] < 0.25) or (l_hip[2] < 0.25 and r_hip[2] < 0.25):
            return 90.0

        mid_sh = np.array([(l_sh[0] + r_sh[0]) / 2.0, (l_sh[1] + r_sh[1]) / 2.0])
        mid_hip = np.array([(l_hip[0] + r_hip[0]) / 2.0, (l_hip[1] + r_hip[1]) / 2.0])

        dx = mid_sh[0] - mid_hip[0]
        dy = mid_sh[1] - mid_hip[1]

        # dy is negative when shoulder is above hip in image coordinates (y increases downward)
        angle_rad = np.arctan2(abs(dy), abs(dx))
        angle_deg = np.degrees(angle_rad)
        return float(angle_deg)

    @staticmethod
    def calculate_bounding_box_aspect_ratio(bbox: List[float]) -> float:
        x1, y1, x2, y2 = bbox
        width = max(1.0, x2 - x1)
        height = max(1.0, y2 - y1)
        return width / height

    def evaluate_track(
        self,
        track_id: int,
        bbox: List[float],
        keypoints: Optional[List[List[float]]],
        current_time: Optional[float] = None
    ) -> Dict[str, Any]:
        if current_time is None:
            current_time = time.time()

        if track_id not in self.track_states:
            self.track_states[track_id] = {
                "state": FallDetectionState.UPRIGHT,
                "recumbent_since": 0.0,
                "history": [],
                "last_keypoints": None
            }

        t_data = self.track_states[track_id]
        aspect_ratio = self.calculate_bounding_box_aspect_ratio(bbox)
        
        spine_angle = 90.0
        if keypoints and len(keypoints) >= 13:
            kps = np.array(keypoints)
            spine_angle = self.calculate_spine_angle(kps)
        else:
            # Fallback heuristic if keypoints temporarily occluded
            if aspect_ratio > 1.35:
                spine_angle = 20.0
            else:
                spine_angle = 80.0

        is_recumbent = spine_angle < 35.0 or (aspect_ratio > 1.4 and spine_angle < 45.0)

        if is_recumbent:
            if t_data["state"] not in [FallDetectionState.RECUMBENT, FallDetectionState.CRITICAL_MAN_DOWN]:
                t_data["state"] = FallDetectionState.RECUMBENT
                t_data["recumbent_since"] = current_time
            
            elapsed = current_time - t_data["recumbent_since"]
            if elapsed >= self.immobility_threshold:
                t_data["state"] = FallDetectionState.CRITICAL_MAN_DOWN

            return {
                "track_id": track_id,
                "state": t_data["state"],
                "spine_angle": round(spine_angle, 1),
                "aspect_ratio": round(aspect_ratio, 2),
                "immobility_seconds": round(elapsed, 2),
                "is_hazard": t_data["state"] == FallDetectionState.CRITICAL_MAN_DOWN
            }
        else:
            # Reset to upright
            t_data["state"] = FallDetectionState.UPRIGHT
            t_data["recumbent_since"] = 0.0
            return {
                "track_id": track_id,
                "state": FallDetectionState.UPRIGHT,
                "spine_angle": round(spine_angle, 1),
                "aspect_ratio": round(aspect_ratio, 2),
                "immobility_seconds": 0.0,
                "is_hazard": False
            }
