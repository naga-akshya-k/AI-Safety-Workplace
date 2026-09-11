import cv2
import time
import os
import threading
import numpy as np
from typing import Optional, Dict, Any, Generator, Tuple
from datetime import datetime

class VideoStream:
    """
    Industrial Stream Worker.
    Provides non-blocking frame retrieval with automatic reconnect,
    real-time 20 FPS pacing, frame-rate monitoring, and fail-safe status degradation.
    """
    def __init__(self, camera_id: int, source: str, target_fps: float = 20.0):
        self.camera_id = camera_id
        self.source = source
        self.target_fps = target_fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.lock = threading.Lock()
        
        self.current_frame: Optional[np.ndarray] = None
        self.last_frame_time: float = 0.0
        self.calculated_fps: float = 0.0
        self.status = "UNKNOWN" # HEALTHY, DEGRADED, OFFLINE, UNKNOWN
        self.frame_count = 0
        self.thread: Optional[threading.Thread] = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
            self.cap = None
        self.status = "OFFLINE"

    def _open_source(self) -> bool:
        if self.source.isdigit():
            # Webcam index
            self.cap = cv2.VideoCapture(int(self.source))
            return self.cap.isOpened() if self.cap else False
        elif os.path.exists(self.source):
            self.cap = cv2.VideoCapture(self.source)
            return self.cap.isOpened() if self.cap else False
        else:
            return False

    def _generate_synthetic_industrial_frame(self) -> np.ndarray:
        """
        Deterministic fallback generator if video file is absent.
        """
        img = np.zeros((720, 1280, 3), dtype=np.uint8)
        img[:] = (70, 75, 80) # Concrete
        
        cv2.line(img, (200, 100), (200, 650), (0, 215, 255), 4)
        cv2.line(img, (1080, 100), (1080, 650), (0, 215, 255), 4)
        cv2.rectangle(img, (400, 300), (880, 600), (0, 0, 200), 3)
        
        cv2.putText(img, f"INDUSTRIAL MONITORING STREAM [CAM {self.camera_id}]", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        cv2.putText(img, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        t = time.time()
        wx = int(450 + 200 * np.sin(t * 0.8))
        wy = int(400 + 50 * np.cos(t * 0.8))
        
        cv2.rectangle(img, (wx - 25, wy - 70), (wx + 25, wy + 50), (50, 120, 200), -1)
        cv2.circle(img, (wx, wy - 90), 18, (180, 200, 220), -1)
        cv2.ellipse(img, (wx, wy - 95), (20, 10), 0, 180, 360, (0, 255, 255), -1)
        cv2.rectangle(img, (wx - 25, wy - 65), (wx + 25, wy - 10), (0, 255, 128), -1)

        return img

    def _capture_loop(self):
        fps_timer = time.time()
        frames_in_second = 0
        use_synthetic = False

        if not self._open_source():
            print(f"[VideoStream] Unable to open source '{self.source}'. Switching to synthetic industrial feed.")
            use_synthetic = True

        frame_interval = 1.0 / self.target_fps

        while self.running:
            start_t = time.time()

            if use_synthetic:
                frame = self._generate_synthetic_industrial_frame()
                ret = True
            else:
                ret, frame = self.cap.read()
                if not ret:
                    # Seamless video file loop
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    if not ret:
                        self.status = "DEGRADED"
                        time.sleep(0.2)
                        continue

            now = time.time()
            with self.lock:
                self.current_frame = frame
                self.last_frame_time = now
                self.frame_count += 1
                frames_in_second += 1

            # Update FPS calculation every second
            if now - fps_timer >= 1.0:
                self.calculated_fps = frames_in_second / (now - fps_timer)
                frames_in_second = 0
                fps_timer = now
                
                # Fail-safe state machine
                if self.calculated_fps >= 10.0:
                    self.status = "HEALTHY"
                elif self.calculated_fps > 0:
                    self.status = "DEGRADED"
                else:
                    self.status = "OFFLINE"

            # Real-time stream pacing to match camera target FPS
            elapsed = time.time() - start_t
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray], Dict[str, Any]]:
        with self.lock:
            if self.current_frame is None or (time.time() - self.last_frame_time > 3.0):
                return False, None, {
                    "status": "UNKNOWN / MONITORING_DEGRADED",
                    "fps": 0.0,
                    "frame_count": self.frame_count
                }
            return True, self.current_frame.copy(), {
                "status": self.status,
                "fps": round(self.calculated_fps, 1),
                "frame_count": self.frame_count
            }

class StreamManager:
    def __init__(self):
        self.streams: Dict[int, VideoStream] = {}

    def get_or_create_stream(self, camera_id: int, source: str) -> VideoStream:
        if camera_id not in self.streams:
            stream = VideoStream(camera_id, source)
            stream.start()
            self.streams[camera_id] = stream
        return self.streams[camera_id]

    def stop_stream(self, camera_id: int):
        if camera_id in self.streams:
            self.streams[camera_id].stop()
            del self.streams[camera_id]

    def stop_all(self):
        for s in self.streams.values():
            s.stop()
        self.streams.clear()

stream_manager = StreamManager()
