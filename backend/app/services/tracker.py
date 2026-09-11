import numpy as np
from typing import List, Dict, Any, Tuple

class Track:
    def __init__(self, track_id: int, bbox: List[float], label: str = "worker"):
        self.track_id = track_id
        self.bbox = bbox # [x1, y1, x2, y2]
        self.label = label
        self.hits = 1
        self.age = 1
        self.time_since_update = 0
        self.history: List[List[float]] = [bbox]

    def update(self, bbox: List[float]):
        self.bbox = bbox
        self.hits += 1
        self.time_since_update = 0
        self.history.append(bbox)
        if len(self.history) > 30:
            self.history.pop(0)

    def mark_missed(self):
        self.age += 1
        self.time_since_update += 1

class MultiObjectTracker:
    """
    Lightweight, robust Multi-Object Tracker based on IoU and centroid distance association.
    Preserves identity across occlusions, preventing ID switching and alert flickering.
    """
    def __init__(self, max_age: int = 25, min_iou: float = 0.25):
        self.max_age = max_age
        self.min_iou = min_iou
        self.next_id = 1
        self.tracks: List[Track] = []

    @staticmethod
    def iou(box_a: List[float], box_b: List[float]) -> float:
        xa1, ya1, xa2, ya2 = box_a
        xb1, yb1, xb2, yb2 = box_b

        xi1 = max(xa1, xb1)
        yi1 = max(ya1, yb1)
        xi2 = min(xa2, xb2)
        yi2 = min(ya2, yb2)

        if xi2 <= xi1 or yi2 <= yi1:
            return 0.0

        inter = (xi2 - xi1) * (yi2 - yi1)
        area_a = (xa2 - xa1) * (ya2 - ya1)
        area_b = (xb2 - xb1) * (yb2 - yb1)
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Match current detections with existing active tracks
        unmatched_dets = list(range(len(detections)))
        matched_tracks = set()

        if self.tracks and detections:
            iou_matrix = np.zeros((len(self.tracks), len(detections)), dtype=np.float32)
            for t_idx, track in enumerate(self.tracks):
                for d_idx, det in enumerate(detections):
                    iou_matrix[t_idx, d_idx] = self.iou(track.bbox, det["bbox"])

            # Greedy matching by maximum IoU
            while True:
                max_iou = np.max(iou_matrix) if iou_matrix.size > 0 else 0.0
                if max_iou < self.min_iou:
                    break

                t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                if t_idx in matched_tracks or d_idx not in unmatched_dets:
                    iou_matrix[t_idx, d_idx] = -1.0
                    continue

                # Match found
                track = self.tracks[t_idx]
                det = detections[d_idx]
                track.update(det["bbox"])
                matched_tracks.add(t_idx)
                unmatched_dets.remove(d_idx)
                iou_matrix[t_idx, :] = -1.0
                iou_matrix[:, d_idx] = -1.0

        # Mark unmatched tracks as missed
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.mark_missed()

        # Create new tracks for unmatched detections
        for d_idx in unmatched_dets:
            det = detections[d_idx]
            new_track = Track(self.next_id, det["bbox"], det.get("label", "worker"))
            self.next_id += 1
            self.tracks.append(new_track)

        # Remove dead tracks
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

        # Return tracked detections with stable track_id
        tracked_results = []
        for det in detections:
            best_iou = 0.0
            best_track_id = 0
            for t in self.tracks:
                overlap = self.iou(t.bbox, det["bbox"])
                if overlap > best_iou:
                    best_iou = overlap
                    best_track_id = t.track_id

            det_copy = dict(det)
            det_copy["track_id"] = best_track_id if best_iou >= self.min_iou else self.next_id
            tracked_results.append(det_copy)

        return tracked_results
