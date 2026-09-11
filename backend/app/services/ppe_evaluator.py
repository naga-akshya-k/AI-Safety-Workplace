from typing import List, Dict, Tuple, Any

class PPEEvaluationResult:
    def __init__(self, track_id: int, compliant: bool, missing_items: List[str], detected_items: List[str], details: Dict[str, Any]):
        self.track_id = track_id
        self.compliant = compliant
        self.missing_items = missing_items
        self.detected_items = detected_items
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "compliant": self.compliant,
            "missing_items": self.missing_items,
            "detected_items": self.detected_items,
            "details": self.details
        }

class PPEEvaluator:
    @staticmethod
    def calculate_box_overlap(box_a: List[float], box_b: List[float]) -> float:
        """Calculates area of intersection divided by area of box_b."""
        xa1, ya1, xa2, ya2 = box_a
        xb1, yb1, xb2, yb2 = box_b

        xi1 = max(xa1, xb1)
        yi1 = max(ya1, yb1)
        xi2 = min(xa2, xb2)
        yi2 = min(ya2, yb2)

        if xi2 <= xi1 or yi2 <= yi1:
            return 0.0

        inter_area = (xi2 - xi1) * (yi2 - yi1)
        b_area = (xb2 - xb1) * (yb2 - yb1)
        return inter_area / b_area if b_area > 0 else 0.0

    @classmethod
    def evaluate_worker_ppe(
        cls,
        track_id: int,
        worker_bbox: List[float],
        detected_ppe_items: List[Dict[str, Any]],
        required_ppe: List[str]
    ) -> PPEEvaluationResult:
        """
        Hierarchical Anatomical PPE Evaluator.
        Verifies that:
        1. Hardhat is located in the HEAD sub-region (top 22% of worker body).
           If a worker is carrying a hardhat in hand, overlap with head is near 0.
        2. High-vis vest is located in the TORSO sub-region (15% to 75% of worker body).
        """
        x1, y1, x2, y2 = worker_bbox
        w_height = y2 - y1

        head_region = [x1, y1, x2, y1 + 0.25 * w_height]
        torso_region = [x1, y1 + 0.15 * w_height, x2, y1 + 0.75 * w_height]

        detected_worn_items = []
        details = {}

        for item in detected_ppe_items:
            label = item.get("label", "").lower()
            box = item.get("bbox", [])
            conf = item.get("confidence", 0.0)

            if "hardhat" in label or "helmet" in label:
                overlap = cls.calculate_box_overlap(head_region, box)
                if overlap > 0.35:
                    detected_worn_items.append("hardhat")
                    details["hardhat"] = {"confidence": conf, "head_overlap": round(overlap, 2)}
            
            elif "vest" in label or "hi_vis" in label or "high_vis" in label:
                overlap = cls.calculate_box_overlap(torso_region, box)
                if overlap > 0.35:
                    detected_worn_items.append("vest")
                    details["vest"] = {"confidence": conf, "torso_overlap": round(overlap, 2)}

        missing = [item for item in required_ppe if item.lower() not in detected_worn_items]
        compliant = len(missing) == 0

        return PPEEvaluationResult(
            track_id=track_id,
            compliant=compliant,
            missing_items=missing,
            detected_items=detected_worn_items,
            details=details
        )
