"""
High-Fidelity Industrial CCTV Video Scenario Generator
Generates realistic, textured, professional CCTV footage for 4 industrial sectors:
1. CAM 01: Warehouse Logistics Corridor (Forklift & Pedestrian Proximity)
2. CAM 02: Shop Floor Assembly Walkway (PPE Compliance & Violation)
3. CAM 03: Robotic Fabrication Cell (Restricted Exclusion Zone Intrusion)
4. CAM 04: High-Rack Storage Aisle (Worker Fall & Prolonged Immobility)
"""

import cv2
import numpy as np
import os
import math
import time

def draw_cctv_hud(img, cam_id: int, cam_name: str, frame_idx: int, fps: float = 20.0):
    """Draws authentic high-end industrial CCTV camera on-screen display (OSD)."""
    h, w = img.shape[:2]
    
    # 1. Subtle Lens Vignette (darkened corners for realistic camera optics)
    X = cv2.getGaussianKernel(w, w * 0.75)
    Y = cv2.getGaussianKernel(h, h * 0.75)
    kernel = Y * X.T
    mask = kernel / kernel.max()
    vignette = np.dstack([mask] * 3)
    img[:] = np.clip(img * (0.65 + 0.35 * vignette), 0, 255).astype(np.uint8)

    # 2. Corner Crosshairs / Reticles
    c_len = 25
    c_color = (160, 160, 160)
    for cx, cy in [(30, 30), (w - 30, 30), (30, h - 30), (w - 30, h - 30)]:
        dx = 1 if cx < w / 2 else -1
        dy = 1 if cy < h / 2 else -1
        cv2.line(img, (cx, cy), (cx + dx * c_len, cy), c_color, 1)
        cv2.line(img, (cx, cy), (cx, cy + dy * c_len), c_color, 1)

    # 3. Top Banner: Camera Name, Red Recording Dot, and Live Timestamp
    rec_color = (0, 0, 230) if (frame_idx % 16 < 8) else (80, 80, 80)
    cv2.circle(img, (45, 45), 6, rec_color, -1)
    cv2.putText(img, "REC", (58, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

    cam_tag = f"CAM 0{cam_id}: {cam_name.upper()}"
    cv2.putText(img, cam_tag, (110, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 2)
    cv2.putText(img, cam_tag, (110, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 1)

    # Timestamp with running milliseconds
    t_seconds = 1789113600 + (frame_idx / fps)
    ms = int((frame_idx % int(fps)) * (1000 / fps))
    time_str = time.strftime("%Y-%m-%d  %H:%M:%S", time.gmtime(t_seconds)) + f".{ms:03d} UTC"
    cv2.putText(img, time_str, (w - 340, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 2)
    cv2.putText(img, time_str, (w - 340, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 1)

    # 4. Bottom Banner: Stream Telemetry & AI Status
    stat_str = "AI-SECURE  |  1080P/60FPS  |  H.265 4.8Mbps  |  EDGE-PROCESSED"
    cv2.putText(img, stat_str, (45, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

def draw_realistic_worker(img, wx: int, wy: int, has_helmet: bool = True, has_vest: bool = True, is_fallen: bool = False, frame_idx: int = 0):
    """Renders a detailed human industrial worker with realistic PPE apparel and shadows."""
    # Subtle walking bounce
    leg_offset = int(math.sin(frame_idx * 0.4) * 8) if not is_fallen else 0

    if not is_fallen:
        # Shadow on ground
        cv2.ellipse(img, (wx, wy + 62), (32, 10), 0, 0, 360, (25, 25, 25), -1)

        # Work Pants / Legs
        cv2.line(img, (wx - 10, wy), (wx - 12 + leg_offset, wy + 55), (35, 45, 60), 10) # Left leg denim
        cv2.line(img, (wx + 10, wy), (wx + 12 - leg_offset, wy + 55), (35, 45, 60), 10) # Right leg denim

        # Steel-Toe Boots
        cv2.rectangle(img, (wx - 18 + leg_offset, wy + 52), (wx - 6 + leg_offset, wy + 62), (20, 20, 20), -1)
        cv2.rectangle(img, (wx + 6 - leg_offset, wy + 52), (wx + 18 - leg_offset, wy + 62), (20, 20, 20), -1)
        cv2.rectangle(img, (wx - 22 + leg_offset, wy + 57), (wx - 6 + leg_offset, wy + 62), (40, 40, 40), -1) # Toe cap

        # Torso
        if has_vest:
            # Hi-Vis Fluorescent Green Body (ANSI Class 2)
            cv2.rectangle(img, (wx - 22, wy - 62), (wx + 22, wy), (0, 235, 110), -1)
            # Silver 3M Reflective Retroreflective Stripes
            cv2.rectangle(img, (wx - 22, wy - 35), (wx + 22, wy - 29), (225, 230, 235), -1) # Horizontal band
            cv2.line(img, (wx - 12, wy - 62), (wx - 12, wy), (225, 230, 235), 4) # Vertical suspender L
            cv2.line(img, (wx + 12, wy - 62), (wx + 12, wy), (225, 230, 235), 4) # Vertical suspender R
            # Dark Collar
            cv2.rectangle(img, (wx - 8, wy - 62), (wx + 8, wy - 55), (30, 30, 30), -1)
        else:
            # Dark Civilian / Non-compliant Clothing
            cv2.rectangle(img, (wx - 22, wy - 62), (wx + 22, wy), (65, 45, 35), -1)
            cv2.rectangle(img, (wx - 20, wy - 60), (wx + 20, wy - 2), (85, 55, 45), -1)

        # Arms
        arm_swing = int(math.sin(frame_idx * 0.4) * 6)
        cv2.line(img, (wx - 24, wy - 55), (wx - 26, wy - 20 + arm_swing), (0, 235, 110) if has_vest else (65, 45, 35), 8)
        cv2.line(img, (wx + 24, wy - 55), (wx + 26, wy - 20 - arm_swing), (0, 235, 110) if has_vest else (65, 45, 35), 8)
        # Hands / Gloves
        cv2.circle(img, (wx - 26, wy - 14 + arm_swing), 5, (220, 180, 50) if has_vest else (170, 190, 210), -1)
        cv2.circle(img, (wx + 26, wy - 14 - arm_swing), 5, (220, 180, 50) if has_vest else (170, 190, 210), -1)

        # Head / Neck
        cv2.rectangle(img, (wx - 6, wy - 68), (wx + 6, wy - 62), (170, 190, 210), -1)
        cv2.circle(img, (wx, wy - 80), 16, (170, 190, 210), -1) # Face

        # Headwear
        if has_helmet:
            # Industrial Yellow Hardhat with 3D Bevel & Safety Brim
            cv2.ellipse(img, (wx, wy - 85), (20, 13), 0, 180, 360, (0, 220, 255), -1)
            cv2.rectangle(img, (wx - 22, wy - 86), (wx + 22, wy - 82), (0, 180, 230), -1) # Front brim visor
            cv2.line(img, (wx - 16, wy - 85), (wx + 16, wy - 93), (80, 255, 255), 2) # Highlight sheen
        else:
            # Dark exposed hair, no protective helmet
            cv2.ellipse(img, (wx, wy - 86), (16, 12), 0, 180, 360, (30, 25, 20), -1)
    else:
        # Fallen / Recumbent Worker on Ground (Man-Down)
        # Shadow
        cv2.ellipse(img, (wx, wy + 15), (75, 16), 0, 0, 360, (20, 20, 20), -1)
        # Legs horizontal
        cv2.line(img, (wx + 25, wy), (wx + 75, wy + 6), (35, 45, 60), 10)
        cv2.rectangle(img, (wx + 72, wy + 2), (wx + 85, wy + 14), (20, 20, 20), -1) # Boots

        # Torso lying flat
        cv2.rectangle(img, (wx - 35, wy - 15), (wx + 25, wy + 18), (0, 235, 110), -1)
        cv2.line(img, (wx - 35, wy + 2), (wx + 25, wy + 2), (225, 230, 235), 5) # Reflective stripe
        cv2.line(img, (wx - 10, wy - 15), (wx - 10, wy + 18), (225, 230, 235), 4)

        # Head flat against concrete
        cv2.circle(img, (wx - 52, wy + 2), 15, (170, 190, 210), -1)
        # Dislodged Hardhat rolling nearby
        cv2.ellipse(img, (wx - 75, wy - 5), (16, 11), 35, 0, 360, (0, 220, 255), -1)

def draw_realistic_forklift(img, fx: int, fy: int, frame_idx: int):
    """Renders a detailed, realistic industrial forklift with 3D shading, cab, forks, and amber beacon."""
    # 1. Ground Shadow
    cv2.ellipse(img, (fx - 30, fy + 52), (110, 22), 0, 0, 360, (20, 20, 20), -1)

    # 2. Heavy Pneumatic Tires
    cv2.circle(img, (fx - 60, fy + 45), 24, (25, 25, 25), -1)
    cv2.circle(img, (fx - 60, fy + 45), 10, (140, 140, 140), -1) # Hub
    cv2.circle(img, (fx + 25, fy + 45), 24, (25, 25, 25), -1)
    cv2.circle(img, (fx + 25, fy + 45), 10, (140, 140, 140), -1)

    # 3. Main Chassis & Counterweight (Industrial Safety Yellow)
    cv2.rectangle(img, (fx - 85, fy - 65), (fx + 45, fy + 38), (0, 190, 240), -1)
    # Bevel shading
    cv2.rectangle(img, (fx - 85, fy - 65), (fx + 45, fy - 52), (0, 215, 255), -1)
    cv2.rectangle(img, (fx - 85, fy + 22), (fx + 45, fy + 38), (0, 140, 190), -1)
    # Caution Chevron Hazard Striping on Counterweight
    for cx in range(fx + 5, fx + 42, 14):
        cv2.line(img, (cx, fy - 15), (cx + 8, fy + 15), (20, 20, 20), 4)

    # 4. ROPS Overhead Safety Cab & Steel Protective Cage
    cv2.rectangle(img, (fx - 45, fy - 118), (fx + 22, fy - 65), (35, 35, 35), -1)
    # Safety Glass tint
    cv2.rectangle(img, (fx - 40, fy - 112), (fx + 18, fy - 68), (70, 95, 110), -1)
    # Steel Cage Bars
    cv2.line(img, (fx - 20, fy - 112), (fx - 20, fy - 68), (35, 35, 35), 3)
    cv2.line(img, (fx, fy - 112), (fx, fy - 68), (35, 35, 35), 3)

    # 5. Vertical Dual Mast & Hydraulic Ram
    cv2.rectangle(img, (fx - 92, fy - 130), (fx - 74, fy + 40), (45, 45, 50), -1)
    cv2.rectangle(img, (fx - 85, fy - 110), (fx - 81, fy + 25), (180, 180, 185), -1) # Chrome hydraulic ram

    # 6. Carriage and Steel Lifting Forks (Front)
    cv2.rectangle(img, (fx - 100, fy + 10), (fx - 90, fy + 38), (80, 80, 85), -1)
    cv2.rectangle(img, (fx - 150, fy + 30), (fx - 90, fy + 40), (160, 160, 165), -1) # Steel forks
    cv2.rectangle(img, (fx - 150, fy + 37), (fx - 90, fy + 40), (100, 100, 105), -1) # Bevel

    # 7. Rotating Flashing Amber Safety Beacon (Warning light on cab top)
    beacon_flash = (frame_idx % 6 < 3)
    beacon_col = (0, 195, 255) if beacon_flash else (0, 80, 180)
    cv2.circle(img, (fx - 12, fy - 126), 9, beacon_col, -1)
    cv2.circle(img, (fx - 12, fy - 126), 4, (255, 255, 255), -1)
    if beacon_flash:
        # Dynamic warning light glow on ground
        cv2.circle(img, (fx - 12, fy - 126), 24, (0, 165, 255), 1)

def create_scenario_videos():
    os.makedirs("data/sample_videos", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 1280, 720
    fps = 20.0
    num_frames = 200 # 10 seconds

    # =========================================================================
    # SCENARIO 1: Warehouse Loading Dock & Forklift Corridor
    # =========================================================================
    p1 = "data/sample_videos/warehouse_forklift_corridor.mp4"
    out1 = cv2.VideoWriter(p1, fourcc, fps, (width, height))
    print(f"[1/4] Generating photorealistic CCTV: {p1}...")

    # Realistic industrial concrete floor with expansion joints and textures
    np.random.seed(42)
    concrete_base = np.full((height, width, 3), (72, 75, 80), dtype=np.uint8)
    noise = np.random.normal(0, 5, (height, width, 3)).astype(np.int16)
    concrete_base = np.clip(concrete_base + noise, 0, 255).astype(np.uint8)

    # Architectural floor markings & safety lanes
    cv2.line(concrete_base, (0, 520), (width, 520), (55, 58, 62), 2)
    cv2.line(concrete_base, (220, 0), (220, height), (0, 210, 255), 6) # Yellow caution boundary
    cv2.line(concrete_base, (1080, 0), (1080, height), (0, 210, 255), 6)
    # Caution Chevron Striping in walkway
    for y in range(40, height, 60):
        cv2.line(concrete_base, (208, y), (232, y + 25), (0, 210, 255), 3)

    # Warehouse Wall & Loading Dock Roll-up Bay Door (Top)
    cv2.rectangle(concrete_base, (0, 0), (width, 140), (45, 48, 52), -1)
    for sl in range(15, 140, 12):
        cv2.line(concrete_base, (0, sl), (width, sl), (35, 38, 42), 1)
    cv2.rectangle(concrete_base, (480, 20), (800, 140), (25, 28, 32), -1) # Dock bay 4
    cv2.putText(concrete_base, "BAY 04 - LOADING CORRIDOR", (520, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 215, 255), 2)

    for f in range(num_frames):
        img = concrete_base.copy()

        # Moving Forklift (coming from right to left)
        fx = int(1050 - (f * 3.8))
        fy = 420
        draw_realistic_forklift(img, fx, fy, f)

        # Worker crossing corridor from top to bottom
        wx = 420
        wy = int(220 + (f * 1.5))
        draw_realistic_worker(img, wx, wy, has_helmet=True, has_vest=True, is_fallen=False, frame_idx=f)

        # Camera HUD
        draw_cctv_hud(img, 1, "Warehouse Logistics - Bay 04 Corridor", f, fps)
        out1.write(img)

    out1.release()

    # =========================================================================
    # SCENARIO 2: Shop Floor Assembly & PPE Enforcement Walkway
    # =========================================================================
    p2 = "data/sample_videos/shopfloor_ppe_compliance.mp4"
    out2 = cv2.VideoWriter(p2, fourcc, fps, (width, height))
    print(f"[2/4] Generating photorealistic CCTV: {p2}...")

    shop_base = np.full((height, width, 3), (62, 65, 70), dtype=np.uint8)
    shop_base = np.clip(shop_base + np.random.normal(0, 4, (height, width, 3)), 0, 255).astype(np.uint8)

    # Assembly Line Conveyors & Machinery (Left & Right)
    cv2.rectangle(shop_base, (120, 120), (360, 620), (45, 48, 55), -1)
    cv2.rectangle(shop_base, (920, 120), (1160, 620), (45, 48, 55), -1)
    # Conveyor rollers
    for ry in range(140, 600, 25):
        cv2.line(shop_base, (130, ry), (350, ry), (85, 90, 95), 3)
        cv2.line(shop_base, (930, ry), (1150, ry), (85, 90, 95), 3)

    # Pedestrian Walkway Markings (Center Green Safety Floor)
    cv2.rectangle(shop_base, (420, 60), (860, 680), (55, 70, 60), -1) # Epoxy green walkway
    cv2.line(shop_base, (420, 60), (420, 680), (0, 215, 255), 4)
    cv2.line(shop_base, (860, 60), (860, 680), (0, 215, 255), 4)
    cv2.putText(shop_base, "PPE MANDATORY ZONE - HARDHAT & VEST REQUIRED", (435, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 215, 255), 1)

    for f in range(num_frames):
        img = shop_base.copy()

        # Worker A (Fully Compliant: Yellow Hardhat + Fluorescent Vest) walking down
        wax = 510
        way = int(180 + (f * 1.8))
        draw_realistic_worker(img, wax, way, has_helmet=True, has_vest=True, is_fallen=False, frame_idx=f)

        # Worker B (NON-COMPLIANT: No Hardhat, Dark Clothing) walking up
        wbx = 730
        wby = int(580 - (f * 1.6))
        draw_realistic_worker(img, wbx, wby, has_helmet=False, has_vest=False, is_fallen=False, frame_idx=f)

        draw_cctv_hud(img, 2, "Shop Floor Assembly Walkway - PPE Compliance", f, fps)
        out2.write(img)

    out2.release()

    # =========================================================================
    # SCENARIO 3: Robotic Cell Geofence Intrusion (Restricted Exclusion Zone)
    # =========================================================================
    p3 = "data/sample_videos/robotic_cell_intrusion.mp4"
    out3 = cv2.VideoWriter(p3, fourcc, fps, (width, height))
    print(f"[3/4] Generating photorealistic CCTV: {p3}...")

    cell_base = np.full((height, width, 3), (58, 62, 68), dtype=np.uint8)
    cell_base = np.clip(cell_base + np.random.normal(0, 4, (height, width, 3)), 0, 255).astype(np.uint8)

    # Restricted Exclusion Zone Border (Red safety floor marking with hatched warning)
    cv2.rectangle(cell_base, (400, 230), (880, 630), (35, 35, 85), -1) # Danger zone floor
    cv2.rectangle(cell_base, (400, 230), (880, 630), (0, 0, 230), 4) # Red perimeter
    for hx in range(415, 875, 35):
        cv2.line(cell_base, (hx, 230), (hx + 20, 250), (0, 0, 230), 2)
    cv2.putText(cell_base, "DANGER: HIGH-VOLTAGE ROBOTIC EXCLUSION ZONE - ZERO TOLERANCE", (410, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 240), 2)

    for f in range(num_frames):
        img = cell_base.copy()

        # Multi-Axis Industrial Robotic Arm (Center of exclusion zone)
        cv2.circle(img, (640, 430), 45, (90, 95, 100), -1) # Base
        cv2.circle(img, (640, 430), 25, (40, 40, 45), -1)
        arm_ang = math.sin(f * 0.18) * 0.85
        ax = int(640 + 140 * math.cos(arm_ang - 1.57))
        ay = int(430 + 140 * math.sin(arm_ang - 1.57))
        cv2.line(img, (640, 430), (ax, ay), (0, 140, 235), 18) # Heavy industrial link
        cv2.circle(img, (ax, ay), 18, (40, 40, 45), -1)
        # End-effector / Welding tip with spark glow
        weld_x = int(ax + 50 * math.cos(arm_ang))
        weld_y = int(ay + 50 * math.sin(arm_ang))
        cv2.line(img, (ax, ay), (weld_x, weld_y), (140, 140, 145), 8)
        if f % 4 < 2:
            cv2.circle(img, (weld_x, weld_y), 10, (255, 255, 180), -1) # Welding spark glow

        # Worker walking in from left and penetrating the restricted perimeter
        if f < 40:
            wx = 280 + int(f * 3.5)
            wy = 440
        else:
            wx = int(430 + 25 * math.sin(f * 0.12))
            wy = int(440 + 18 * math.cos(f * 0.12))

        draw_realistic_worker(img, wx, wy, has_helmet=True, has_vest=True, is_fallen=False, frame_idx=f)
        draw_cctv_hud(img, 3, "Robotic Fabrication Cell 03 - Exclusion Zone", f, fps)
        out3.write(img)

    out3.release()

    # =========================================================================
    # SCENARIO 4: High-Rack Storage Aisle 03 (Fall & Man-Down)
    # =========================================================================
    p4 = "data/sample_videos/worker_fall_mandown.mp4"
    out4 = cv2.VideoWriter(p4, fourcc, fps, (width, height))
    print(f"[4/4] Generating photorealistic CCTV: {p4}...")

    aisle_base = np.full((height, width, 3), (65, 68, 72), dtype=np.uint8)
    aisle_base = np.clip(aisle_base + np.random.normal(0, 4, (height, width, 3)), 0, 255).astype(np.uint8)

    # Heavy Pallet Racking Shelving (Left & Right) with Cargo Pallets
    cv2.rectangle(aisle_base, (100, 80), (360, 680), (50, 52, 58), -1)
    cv2.rectangle(aisle_base, (920, 80), (1180, 680), (50, 52, 58), -1)
    # Steel rack uprights (Orange / Blue Industrial Standard)
    cv2.line(aisle_base, (110, 80), (110, 680), (0, 140, 235), 8)
    cv2.line(aisle_base, (350, 80), (350, 680), (0, 140, 235), 8)
    cv2.line(aisle_base, (930, 80), (930, 680), (0, 140, 235), 8)
    cv2.line(aisle_base, (1170, 80), (1170, 680), (0, 140, 235), 8)
    # Pallet shelves & shrinkwrapped boxes
    for sy in [180, 320, 460, 600]:
        cv2.line(aisle_base, (100, sy), (360, sy), (0, 140, 235), 6)
        cv2.line(aisle_base, (920, sy), (1180, sy), (0, 140, 235), 6)
        # Wooden pallets & cargo boxes
        cv2.rectangle(aisle_base, (130, sy - 90), (330, sy - 6), (90, 80, 65), -1) # Cargo box
        cv2.rectangle(aisle_base, (950, sy - 90), (1150, sy - 6), (90, 80, 65), -1)

    for f in range(num_frames):
        img = aisle_base.copy()

        # Worker walking upright (f < 50), falling (50 <= f < 70), recumbent man-down (f >= 70)
        if f < 50:
            wx = 640
            wy = int(320 + f * 1.5)
            draw_realistic_worker(img, wx, wy, has_helmet=True, has_vest=True, is_fallen=False, frame_idx=f)
        elif f < 70:
            prog = (f - 50) / 20.0
            wx = int(640 + prog * 45)
            wy = int(395 + prog * 65)
            draw_realistic_worker(img, wx, wy, has_helmet=True, has_vest=True, is_fallen=False, frame_idx=f)
        else:
            wx = 685
            wy = 460
            draw_realistic_worker(img, wx, wy, has_helmet=True, has_vest=True, is_fallen=True, frame_idx=f)

        draw_cctv_hud(img, 4, "High-Rack Storage Aisle 03 - Fall Monitoring", f, fps)
        out4.write(img)

    out4.release()
    print("[PASS] All 4 photorealistic industrial CCTV test videos generated successfully!")

if __name__ == "__main__":
    create_scenario_videos()
