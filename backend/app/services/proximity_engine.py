import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import time

class ProximityAlert:
    def __init__(self, worker_id: int, vehicle_id: int, distance_meters: float, ttc_seconds: Optional[float], severity: int):
        self.worker_id = worker_id
        self.vehicle_id = vehicle_id
        self.distance_meters = distance_meters
        self.ttc_seconds = ttc_seconds
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "vehicle_id": self.vehicle_id,
            "distance_meters": round(self.distance_meters, 2),
            "ttc_seconds": round(self.ttc_seconds, 2) if self.ttc_seconds is not None else None,
            "severity": self.severity
        }

class ProximityEngine:
    def __init__(self, pixels_per_meter: float = 65.0, warning_distance_m: float = 3.5, critical_distance_m: float = 1.8):
        self.pixels_per_meter = pixels_per_meter
        self.warning_distance_m = warning_distance_m
        self.critical_distance_m = critical_distance_m
        # track_id -> [(timestamp, (x, y))]
        self.trajectory_history: Dict[int, List[Tuple[float, Tuple[float, float]]]] = {}

    def update_trajectory(self, track_id: int, pos: Tuple[float, float], timestamp: float):
        if track_id not in self.trajectory_history:
            self.trajectory_history[track_id] = []
        
        hist = self.trajectory_history[track_id]
        hist.append((timestamp, pos))
        if len(hist) > 15:
            hist.pop(0)

    def get_velocity_vector(self, track_id: int) -> Tuple[float, float]:
        hist = self.trajectory_history.get(track_id, [])
        if len(hist) < 2:
            return (0.0, 0.0)
        
        t0, (x0, y0) = hist[0]
        t1, (x1, y1) = hist[-1]
        dt = t1 - t0
        if dt <= 0.05:
            return (0.0, 0.0)
        
        return ((x1 - x0) / dt, (y1 - y0) / dt)

    def evaluate_proximity(
        self,
        workers: List[Dict[str, Any]],
        vehicles: List[Dict[str, Any]],
        current_time: Optional[float] = None
    ) -> List[ProximityAlert]:
        if current_time is None:
            current_time = time.time()

        alerts: List[ProximityAlert] = []

        # Update trajectories
        for w in workers:
            w_id = w.get("track_id", 0)
            w_pt = w.get("ground_pt", ((w["bbox"][0] + w["bbox"][2]) / 2, w["bbox"][3]))
            self.update_trajectory(w_id, w_pt, current_time)

        for v in vehicles:
            v_id = v.get("track_id", 0)
            v_pt = ((v["bbox"][0] + v["bbox"][2]) / 2, v["bbox"][3])
            self.update_trajectory(v_id, v_pt, current_time)

        for w in workers:
            w_id = w.get("track_id", 0)
            w_pt = w.get("ground_pt", ((w["bbox"][0] + w["bbox"][2]) / 2, w["bbox"][3]))

            for v in vehicles:
                v_id = v.get("track_id", 0)
                v_pt = ((v["bbox"][0] + v["bbox"][2]) / 2, v["bbox"][3])

                dx = (w_pt[0] - v_pt[0])
                dy = (w_pt[1] - v_pt[1])
                pixel_dist = np.sqrt(dx * dx + dy * dy)
                dist_m = pixel_dist / self.pixels_per_meter

                # Time-to-Collision (TTC) based on vehicle velocity towards worker
                v_vx, v_vy = self.get_velocity_vector(v_id)
                vehicle_speed = np.sqrt(v_vx * v_vx + v_vy * v_vy) / self.pixels_per_meter

                ttc: Optional[float] = None
                if vehicle_speed > 0.5:
                    # dot product of velocity with direction vector to worker
                    dir_x, dir_y = dx / max(1.0, pixel_dist), dy / max(1.0, pixel_dist)
                    relative_approach_speed = (v_vx * dir_x + v_vy * dir_y) / self.pixels_per_meter
                    if relative_approach_speed > 0.2:
                        ttc = dist_m / relative_approach_speed

                if dist_m <= self.critical_distance_m or (ttc is not None and ttc < 2.0):
                    alerts.append(ProximityAlert(
                        worker_id=w_id,
                        vehicle_id=v_id,
                        distance_meters=dist_m,
                        ttc_seconds=ttc,
                        severity=4 # CRITICAL
                    ))
                elif dist_m <= self.warning_distance_m:
                    alerts.append(ProximityAlert(
                        worker_id=w_id,
                        vehicle_id=v_id,
                        distance_meters=dist_m,
                        ttc_seconds=ttc,
                        severity=3 # HIGH
                    ))

        return alerts
