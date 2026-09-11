from typing import List, Dict, Tuple, Optional, Any
from shapely.geometry import Point, Polygon
import time

class ZoneViolation:
    def __init__(self, zone_id: int, zone_name: str, zone_type: str, severity: int, dwell_time: float, track_id: int):
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.zone_type = zone_type
        self.severity = severity
        self.dwell_time = dwell_time
        self.track_id = track_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "zone_type": self.zone_type,
            "severity": self.severity,
            "dwell_time": round(self.dwell_time, 2),
            "track_id": self.track_id
        }

class ZoneEngine:
    def __init__(self):
        # zone_id -> { "name": str, "type": str, "polygon": Polygon, "required_ppe": list, "severity": int, "dwell_threshold": float }
        self.zones: Dict[int, Dict[str, Any]] = {}
        # (track_id, zone_id) -> entry_timestamp
        self.track_zone_entry: Dict[Tuple[int, int], float] = {}

    def update_zones(self, zones_data: List[Dict[str, Any]]):
        """Update or register active zones for a camera frame."""
        self.zones.clear()
        for zd in zones_data:
            coords = zd.get("polygon_coords", [])
            if len(coords) >= 3:
                poly = Polygon(coords)
                self.zones[zd["id"]] = {
                    "name": zd.get("name", f"Zone {zd['id']}"),
                    "type": zd.get("zone_type", "EXCLUSION_ZONE"),
                    "polygon": poly,
                    "required_ppe": zd.get("required_ppe", []),
                    "severity": zd.get("severity_level", 3),
                    "dwell_threshold": float(zd.get("dwell_threshold_seconds", 3.0))
                }

    @staticmethod
    def get_ground_contact_point(bbox: List[float], keypoints: Optional[List[List[float]]] = None) -> Tuple[float, float]:
        """
        Calculates ground contact point (feet location).
        Industrial vision rule: never use bounding box center for ground geofences,
        as a worker leaning over a fence would produce false boundary breaches.
        """
        if keypoints and len(keypoints) >= 17:
            # COCO Keypoints: 15: left ankle, 16: right ankle
            left_ankle = keypoints[15]
            right_ankle = keypoints[16]
            if left_ankle[2] > 0.4 and right_ankle[2] > 0.4:
                return ((left_ankle[0] + right_ankle[0]) / 2.0, (left_ankle[1] + right_ankle[1]) / 2.0)
            elif left_ankle[2] > 0.4:
                return (left_ankle[0], left_ankle[1])
            elif right_ankle[2] > 0.4:
                return (right_ankle[0], right_ankle[1])
        
        # Fallback to bottom-center of bounding box
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, y2)

    def evaluate_track(self, track_id: int, ground_pt: Tuple[float, float], current_time: Optional[float] = None) -> List[ZoneViolation]:
        """
        Evaluates whether a worker track is inside any active zones,
        maintains dwell time persistence, and returns confirmed violations.
        """
        if current_time is None:
            current_time = time.time()

        pt = Point(ground_pt[0], ground_pt[1])
        active_violations: List[ZoneViolation] = []
        zones_present_in = set()

        for zone_id, zinfo in self.zones.items():
            poly: Polygon = zinfo["polygon"]
            if poly.contains(pt):
                zones_present_in.add(zone_id)
                key = (track_id, zone_id)
                if key not in self.track_zone_entry:
                    self.track_zone_entry[key] = current_time
                
                dwell = current_time - self.track_zone_entry[key]
                
                # Check dwell threshold
                if dwell >= zinfo["dwell_threshold"]:
                    active_violations.append(ZoneViolation(
                        zone_id=zone_id,
                        zone_name=zinfo["name"],
                        zone_type=zinfo["type"],
                        severity=zinfo["severity"],
                        dwell_time=dwell,
                        track_id=track_id
                    ))

        # Cleanup tracks that exited zones
        keys_to_remove = [k for k in self.track_zone_entry.keys() if k[0] == track_id and k[1] not in zones_present_in]
        for k in keys_to_remove:
            del self.track_zone_entry[k]

        return active_violations
