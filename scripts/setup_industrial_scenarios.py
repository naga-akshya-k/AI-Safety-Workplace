import cv2
import numpy as np
import os
import math

def create_scenario_videos():
    os.makedirs("data/sample_videos", exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 1280, 720
    fps = 20.0
    num_frames = 200 # 10 seconds per scenario

    # =========================================================================
    # SCENARIO 1: Warehouse Forklift Corridor (Vehicle-Worker Proximity & TTC)
    # =========================================================================
    p1 = "data/sample_videos/warehouse_forklift_corridor.mp4"
    out1 = cv2.VideoWriter(p1, fourcc, fps, (width, height))
    print(f"[1/4] Generating {p1}...")

    for f in range(num_frames):
        t = f / fps
        img = np.full((height, width, 3), (60, 65, 70), dtype=np.uint8) # Concrete

        # Floor markings (Walkway & Drive Lane)
        cv2.line(img, (200, 50), (200, 680), (0, 215, 255), 4)
        cv2.line(img, (1080, 50), (1080, 680), (0, 215, 255), 4)
        for y in range(80, 680, 80):
            cv2.line(img, (190, y), (210, y + 20), (0, 215, 255), 3) # Caution dashes

        # Moving Forklift (coming from right to left, accelerating)
        # Forklift position: x moves from 1050 down to 400
        fx = int(1050 - (f * 3.8))
        fy = 420
        # Forklift Body (Industrial Yellow)
        cv2.rectangle(img, (fx - 80, fy - 60), (fx + 40, fy + 40), (0, 190, 240), -1)
        # Overhead Guard / Cab
        cv2.rectangle(img, (fx - 40, fy - 110), (fx + 20, fy - 60), (40, 40, 40), -1)
        # Forks (front)
        cv2.rectangle(img, (fx - 130, fy + 25), (fx - 80, fy + 38), (120, 120, 120), -1)
        # Mast (vertical)
        cv2.rectangle(img, (fx - 85, fy - 120), (fx - 70, fy + 40), (50, 50, 50), -1)
        # Wheels
        cv2.circle(img, (fx - 50, fy + 45), 22, (20, 20, 20), -1)
        cv2.circle(img, (fx + 20, fy + 45), 22, (20, 20, 20), -1)
        # Flashing Amber Beacon on cab
        beacon_color = (0, 165, 255) if (f % 6 < 3) else (0, 80, 180)
        cv2.circle(img, (fx - 10, fy - 120), 8, beacon_color, -1)

        # Worker crossing the corridor from top to bottom
        wx = 420
        wy = int(220 + (f * 1.5))
        # Head
        cv2.circle(img, (wx, wy - 80), 16, (170, 190, 210), -1)
        # Hardhat (yellow)
        cv2.ellipse(img, (wx, wy - 85), (18, 9), 0, 180, 360, (0, 240, 255), -1)
        # Torso (Hi-vis vest)
        cv2.rectangle(img, (wx - 20, wy - 60), (wx + 20, wy), (0, 230, 110), -1)
        # Legs
        cv2.line(img, (wx - 10, wy), (wx - 10, wy + 50), (40, 50, 70), 8)
        cv2.line(img, (wx + 10, wy), (wx + 10, wy + 50), (40, 50, 70), 8)

        # Label
        cv2.putText(img, "CAM 01: WAREHOUSE FORKLIFT & LOADING CORRIDOR", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)
        out1.write(img)

    out1.release()

    # =========================================================================
    # SCENARIO 2: Shop Floor PPE Compliance (Hardhat & Vest Validation)
    # =========================================================================
    p2 = "data/sample_videos/shopfloor_ppe_compliance.mp4"
    out2 = cv2.VideoWriter(p2, fourcc, fps, (width, height))
    print(f"[2/4] Generating {p2}...")

    for f in range(num_frames):
        img = np.full((height, width, 3), (50, 55, 60), dtype=np.uint8)

        # Machinery and walkways
        cv2.rectangle(img, (150, 150), (350, 550), (80, 85, 95), -1)
        cv2.rectangle(img, (900, 150), (1100, 550), (80, 85, 95), -1)
        # Yellow walkway boundary
        cv2.line(img, (400, 80), (400, 650), (0, 215, 255), 3)
        cv2.line(img, (850, 80), (850, 650), (0, 215, 255), 3)

        # Worker A (Fully Compliant: Yellow Hardhat + Green Vest) walking down
        wax = 500
        way = int(180 + (f * 1.8))
        cv2.circle(img, (wax, way - 80), 16, (170, 190, 210), -1)
        cv2.ellipse(img, (wax, way - 85), (18, 9), 0, 180, 360, (0, 240, 255), -1) # Hardhat
        cv2.rectangle(img, (wax - 20, way - 60), (wax + 20, way), (0, 230, 110), -1) # Vest
        cv2.line(img, (wax - 10, way), (wax - 10, way + 45), (40, 50, 70), 7)
        cv2.line(img, (wax + 10, way), (wax + 10, way + 45), (40, 50, 70), 7)

        # Worker B (NON-COMPLIANT: No Hardhat, Dark Jacket) walking up
        wbx = 720
        wby = int(580 - (f * 1.6))
        # Head (bare dark hair, no hardhat)
        cv2.circle(img, (wbx, wby - 80), 16, (170, 190, 210), -1)
        cv2.circle(img, (wbx, wby - 86), 14, (30, 25, 20), -1) # Hair, no helmet
        # Torso (ordinary dark blue clothing, no hi-vis vest)
        cv2.rectangle(img, (wbx - 20, wby - 60), (wbx + 20, wby), (100, 60, 40), -1)
        cv2.line(img, (wbx - 10, wby), (wbx - 10, wby + 45), (40, 40, 50), 7)
        cv2.line(img, (wbx + 10, wby), (wbx + 10, wby + 45), (40, 40, 50), 7)

        cv2.putText(img, "CAM 02: SHOPFLOOR ASSEMBLY & PPE ENFORCEMENT WALKWAY", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)
        out2.write(img)

    out2.release()

    # =========================================================================
    # SCENARIO 3: Robotic Cell Geofence Intrusion (Restricted Exclusion Zone)
    # =========================================================================
    p3 = "data/sample_videos/robotic_cell_intrusion.mp4"
    out3 = cv2.VideoWriter(p3, fourcc, fps, (width, height))
    print(f"[3/4] Generating {p3}...")

    for f in range(num_frames):
        img = np.full((height, width, 3), (55, 60, 65), dtype=np.uint8)

        # Restricted Exclusion Zone Geofence (400, 250) to (880, 620)
        cv2.rectangle(img, (400, 250), (880, 620), (0, 0, 220), 3) # Danger Red
        for d in range(410, 870, 30):
            cv2.line(img, (d, 250), (d + 20, 270), (0, 0, 220), 2)

        # Industrial Robot Arm inside zone
        cv2.circle(img, (640, 430), 40, (120, 120, 130), -1)
        arm_angle = math.sin(f * 0.15) * 0.8
        ax = int(640 + 130 * math.cos(arm_angle - 1.57))
        ay = int(430 + 130 * math.sin(arm_angle - 1.57))
        cv2.line(img, (640, 430), (ax, ay), (0, 165, 255), 14) # Arm link
        cv2.circle(img, (ax, ay), 16, (0, 0, 255), -1)

        # Worker approaches from outside and steps into the restricted zone at f=40
        if f < 40:
            wx = 280 + int(f * 3.5)
            wy = 440
        else:
            # Worker dwells inside restricted zone!
            wx = int(430 + 30 * math.sin(f * 0.1))
            wy = int(440 + 20 * math.cos(f * 0.1))

        cv2.circle(img, (wx, wy - 80), 16, (170, 190, 210), -1)
        cv2.ellipse(img, (wx, wy - 85), (18, 9), 0, 180, 360, (0, 240, 255), -1)
        cv2.rectangle(img, (wx - 20, wy - 60), (wx + 20, wy), (0, 230, 110), -1)
        cv2.line(img, (wx - 10, wy), (wx - 10, wy + 45), (40, 50, 70), 7)
        cv2.line(img, (wx + 10, wy), (wx + 10, wy + 45), (40, 50, 70), 7)

        cv2.putText(img, "CAM 03: ROBOTIC ARM ASSEMBLY CELL [RESTRICTED ZONE]", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)
        out3.write(img)

    out3.release()

    # =========================================================================
    # SCENARIO 4: Worker Fall & Incapacitation (Man-Down Detection)
    # =========================================================================
    p4 = "data/sample_videos/worker_fall_mandown.mp4"
    out4 = cv2.VideoWriter(p4, fourcc, fps, (width, height))
    print(f"[4/4] Generating {p4}...")

    for f in range(num_frames):
        img = np.full((height, width, 3), (65, 70, 75), dtype=np.uint8)

        # Storage shelving
        cv2.rectangle(img, (100, 100), (350, 650), (100, 105, 115), -1)
        cv2.rectangle(img, (930, 100), (1180, 650), (100, 105, 115), -1)

        # Worker walking upright from f=0 to f=50, then falling from f=50 to f=70, then lying recumbent/still from f=70 to 200
        if f < 50:
            wx = 640
            wy = 380
            cv2.circle(img, (wx, wy - 80), 16, (170, 190, 210), -1)
            cv2.ellipse(img, (wx, wy - 85), (18, 9), 0, 180, 360, (0, 240, 255), -1)
            cv2.rectangle(img, (wx - 20, wy - 60), (wx + 20, wy), (0, 230, 110), -1)
            cv2.line(img, (wx - 10, wy), (wx - 10, wy + 45), (40, 50, 70), 7)
            cv2.line(img, (wx + 10, wy), (wx + 10, wy + 45), (40, 50, 70), 7)
        elif f < 70:
            # Falling transition (collapsing downward and tilting)
            progress = (f - 50) / 20.0
            wx = int(640 + progress * 50)
            wy = int(380 + progress * 80)
            # Tilted body
            cv2.circle(img, (wx - 30, wy - 10), 16, (170, 190, 210), -1) # Head close to floor
            cv2.ellipse(img, (wx - 35, wy - 12), (18, 9), 45, 180, 360, (0, 240, 255), -1)
            cv2.rectangle(img, (wx - 20, wy - 20), (wx + 40, wy + 15), (0, 230, 110), -1) # Horizontal torso
        else:
            # Recumbent on floor / Man-down sustained immobility (> 4 seconds)
            wx = 690
            wy = 460
            # Head flat on floor
            cv2.circle(img, (wx - 55, wy + 5), 16, (170, 190, 210), -1)
            cv2.ellipse(img, (wx - 60, wy + 3), (18, 9), 90, 180, 360, (0, 240, 255), -1)
            # Body lying flat horizontally: width >> height!
            cv2.rectangle(img, (wx - 40, wy - 12), (wx + 45, wy + 18), (0, 230, 110), -1)
            cv2.line(img, (wx + 45, wy), (wx + 90, wy + 5), (40, 50, 70), 8)

        cv2.putText(img, "CAM 04: STORAGE AISLE 3 — FALL & MAN-DOWN MONITORING", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 220, 220), 2)
        out4.write(img)

    out4.release()
    print("Successfully generated all 4 industrial test video scenarios!")

if __name__ == "__main__":
    create_scenario_videos()
