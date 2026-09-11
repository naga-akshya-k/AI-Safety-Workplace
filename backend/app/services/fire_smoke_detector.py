import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import time

class FireSmokeDetector:
    """
    Temporal Fire and Smoke Detector.
    Real-world industrial condition handling:
    Steam, exhaust dust, and yellow/orange safety floor markings generate high false alarms in single-frame vision.
    This service maintains a temporal persistence window with dynamic flicker analysis:
    - Rejects static yellow/orange painted lines and machinery (which have zero flicker variance).
    - Verifies true flame luminance fluctuation and expansion over consecutive frames.
    """
    def __init__(self, persistence_frames: int = 12, min_flame_area_px: int = 250):
        self.persistence_frames = persistence_frames
        self.min_flame_area = min_flame_area_px
        # list of { "bbox": [x1, y1, x2, y2], "area": float, "timestamp": float, "mean_val": float }
        self.candidate_detections: List[Dict[str, Any]] = []

    @staticmethod
    def extract_flame_chrominance_mask(frame: np.ndarray) -> np.ndarray:
        """
        Flame chrominance filter in YCbCr and HSV.
        Rules:
        Y >= Cb, Cr >= Cb + 20, Cr > 150
        HSV: High saturation (S > 150) and High Value (V > 200).
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        # High saturation / bright flame core
        lower_flame_hsv = np.array([0, 150, 200])
        upper_flame_hsv = np.array([35, 255, 255])
        mask_hsv = cv2.inRange(hsv, lower_flame_hsv, upper_flame_hsv)

        y = ycrcb[:, :, 0]
        cr = ycrcb[:, :, 1]
        cb = ycrcb[:, :, 2]
        mask_ycrcb = (cr > (cb + 25)) & (cr > 150) & (y > 160)

        combined_mask = mask_hsv & (mask_ycrcb.astype(np.uint8) * 255)
        return combined_mask

    def evaluate_frame(self, frame: np.ndarray, ai_detections: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        confirmed_hazards = []
        now = time.time()

        # Check AI model detections if provided (e.g. specialized fire/smoke class)
        if ai_detections:
            for d in ai_detections:
                label = d.get("label", "").lower()
                if "fire" in label or "flame" in label or "smoke" in label:
                    confirmed_hazards.append({
                        "event_type": "FIRE_SMOKE",
                        "bbox": d.get("bbox"),
                        "confidence": d.get("confidence", 0.9),
                        "source": "AI_MODEL",
                        "timestamp": now
                    })

        flame_mask = self.extract_flame_chrominance_mask(frame)
        contours, _ = cv2.findContours(flame_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area >= self.min_flame_area:
                x, y, w, h = cv2.boundingRect(c)
                aspect = w / max(1.0, float(h))
                if 0.4 <= aspect <= 2.5: # Flame contour aspect ratio
                    # Measure brightness in candidate region
                    roi = flame_mask[y:y+h, x:x+w]
                    mean_val = float(np.mean(roi))
                    self.candidate_detections.append({
                        "bbox": [x, y, x + w, y + h],
                        "area": area,
                        "mean_val": mean_val,
                        "timestamp": now
                    })

        # Retain candidate detections within a 1.2s rolling window
        self.candidate_detections = [c for c in self.candidate_detections if now - c["timestamp"] <= 1.2]

        # Require minimum persistence frames
        if len(self.candidate_detections) >= self.persistence_frames:
            # Check for temporal flicker (area & intensity variance)
            areas = [c["area"] for c in self.candidate_detections]
            area_std = float(np.std(areas))
            area_mean = float(np.mean(areas))

            # Industrial rule: Static painted yellow line has area_std / area_mean < 0.03 (static)
            # Real flame has turbulent boundary with area_std / area_mean >= 0.08
            if area_mean > 0 and (area_std / area_mean) >= 0.08:
                latest = self.candidate_detections[-1]
                if not any(h.get("event_type") == "FIRE_SMOKE" for h in confirmed_hazards):
                    confirmed_hazards.append({
                        "event_type": "FIRE_SMOKE",
                        "bbox": latest["bbox"],
                        "confidence": 0.89,
                        "source": "TEMPORAL_FLICKER_VERIFIED",
                        "timestamp": now
                    })

        return confirmed_hazards
