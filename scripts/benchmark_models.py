import time
import json
import os
import cv2
import torch
import numpy as np

def create_synthetic_industrial_frame() -> np.ndarray:
    """Creates a realistic synthetic 720p industrial camera frame."""
    frame = np.full((720, 1280, 3), (75, 80, 85), dtype=np.uint8)
    # Markings
    cv2.rectangle(frame, (100, 100), (400, 600), (0, 140, 255), 2)
    cv2.rectangle(frame, (500, 300), (900, 650), (0, 0, 200), 2)
    # Simulated worker
    cv2.rectangle(frame, (200, 200), (280, 450), (40, 40, 180), -1) # body
    cv2.circle(frame, (240, 170), 25, (160, 180, 200), -1) # head
    cv2.ellipse(frame, (240, 160), (25, 12), 0, 180, 360, (0, 255, 255), -1) # hardhat
    cv2.rectangle(frame, (210, 210), (270, 320), (0, 255, 128), -1) # vest
    return frame

def run_benchmark():
    print("=" * 60)
    print("INDUSTRIAL AI SAFETY PLATFORM — MODEL BENCHMARK HARNESS")
    print("=" * 60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Active Compute Device: {device}")
    if device == "cuda":
        print(f"GPU Model: {torch.cuda.get_device_name(0)}")
        print(f"VRAM Available: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")

    from ultralytics import YOLO

    test_frame = create_synthetic_industrial_frame()

    # 1. Benchmark YOLOv8n Base Detector
    print("\n[1/3] Benchmarking Person & Machinery Detector (YOLOv8n FP16)...")
    base_model = YOLO("yolov8n.pt")
    
    # Warmup
    for _ in range(5):
        base_model(test_frame, device=device, half=(device=="cuda"), verbose=False)

    latencies_base = []
    for _ in range(25):
        t0 = time.perf_counter()
        base_model(test_frame, device=device, half=(device=="cuda"), verbose=False)
        latencies_base.append((time.perf_counter() - t0) * 1000)

    avg_base = np.mean(latencies_base)
    p95_base = np.percentile(latencies_base, 95)
    fps_base = 1000.0 / avg_base
    print(f"  -> Average Latency: {avg_base:.2f} ms")
    print(f"  -> 95th Percentile: {p95_base:.2f} ms")
    print(f"  -> Maximum Throughput: {fps_base:.1f} FPS")

    # 2. Benchmark YOLOv8n-pose Keypoint Estimator
    print("\n[2/3] Benchmarking Fall & Pose Kinematic Estimator (YOLOv8n-pose FP16)...")
    pose_model = YOLO("yolov8n-pose.pt")
    
    # Warmup
    for _ in range(5):
        pose_model(test_frame, device=device, half=(device=="cuda"), verbose=False)

    latencies_pose = []
    for _ in range(25):
        t0 = time.perf_counter()
        pose_model(test_frame, device=device, half=(device=="cuda"), verbose=False)
        latencies_pose.append((time.perf_counter() - t0) * 1000)

    avg_pose = np.mean(latencies_pose)
    p95_pose = np.percentile(latencies_pose, 95)
    fps_pose = 1000.0 / avg_pose
    print(f"  -> Average Latency: {avg_pose:.2f} ms")
    print(f"  -> 95th Percentile: {p95_pose:.2f} ms")
    print(f"  -> Maximum Throughput: {fps_pose:.1f} FPS")

    # 3. Benchmark End-to-End Pipeline
    from app.services.ai_pipeline import SafetyPerceptionPipeline
    from app.services.detector import VisionDetector
    print("\n[3/3] Benchmarking Unified End-to-End Pipeline (Inference + MOT + Geofence + Kinematics + Risk Engine)...")
    
    det = VisionDetector(device=device)
    pipeline = SafetyPerceptionPipeline(detector=det)
    
    pipeline.update_zones([{
        "id": 1,
        "name": "Robotic Perimeter",
        "zone_type": "EXCLUSION_ZONE",
        "polygon_coords": [[300, 200], [800, 200], [800, 600], [300, 600]],
        "severity_level": 4,
        "dwell_threshold_seconds": 3.0
    }])

    import asyncio
    async def run_pipeline_benchmark():
        # Warmup
        for _ in range(3):
            await pipeline.process_frame(test_frame, camera_id=1)

        latencies_pipeline = []
        for _ in range(25):
            t0 = time.perf_counter()
            await pipeline.process_frame(test_frame, camera_id=1)
            latencies_pipeline.append((time.perf_counter() - t0) * 1000)
        return latencies_pipeline

    latencies_e2e = asyncio.run(run_pipeline_benchmark())
    avg_e2e = np.mean(latencies_e2e)
    p95_e2e = np.percentile(latencies_e2e, 95)
    fps_e2e = 1000.0 / avg_e2e
    print(f"  -> End-to-End Latency: {avg_e2e:.2f} ms")
    print(f"  -> 95th Percentile: {p95_e2e:.2f} ms")
    print(f"  -> Real-Time Streaming FPS: {fps_e2e:.1f} FPS")

    results = {
        "device": device,
        "gpu_model": torch.cuda.get_device_name(0) if device == "cuda" else "CPU",
        "base_detector_ms": round(float(avg_base), 2),
        "base_detector_fps": round(float(fps_base), 1),
        "pose_detector_ms": round(float(avg_pose), 2),
        "pose_detector_fps": round(float(fps_pose), 1),
        "pipeline_e2e_ms": round(float(avg_e2e), 2),
        "pipeline_e2e_fps": round(float(fps_e2e), 1),
        "status": "PASS: Ultra Real-Time Industrial Performance (<45ms)" if avg_e2e < 45 else "PASS: Real-Time Industrial Performance (<65ms)" if avg_e2e < 65 else "ADVISORY"
    }

    os.makedirs("data", exist_ok=True)
    with open("data/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nBenchmark results successfully exported to data/benchmark_results.json")
    print(f"Status: {results['status']}")

if __name__ == "__main__":
    run_benchmark()
