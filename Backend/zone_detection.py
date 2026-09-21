"""
GhatNetra AI - Zone-Wise Crowd Detection & Decision Support Prototype
SIH 2026 - MPSTDC Problem Statement
Location Context: Ujjain Ram Ghat (Shipra River)
"""

import cv2
import numpy as np
from ultralytics import YOLO
from decision_engine import evaluate_zone_status, get_gate_recommendations, calculate_evacuation_time

# 1. Model & Video setup
print("[INFO] Loading YOLO11 model...")
model = YOLO("yolo11n.pt")

video_path = "../videos/crowd.mp4"
video = cv2.VideoCapture(video_path)

if not video.isOpened():
    print(f"[ERROR] Could not open video from {video_path}")
    exit()

# 2. Ghat Zones Definition (2560x1440 Resolution Coordinates)
# Capacity is calibrated for demonstration
ZONES = {
    "Zone A (Upper Entry)": {
        "polygon": np.array([(0, 550), (850, 500), (850, 1440), (0, 1440)], np.int32),
        "capacity": 150
    },
    "Zone B (Central Snan)": {
        "polygon": np.array([(850, 500), (1700, 520), (1700, 1440), (850, 1440)], np.int32),
        "capacity": 200
    },
    "Zone C (Waterfront/Exit)": {
        "polygon": np.array([(1700, 520), (2560, 500), (2560, 1440), (1700, 1440)], np.int32),
        "capacity": 100
    }
}

TOTAL_CAPACITY = sum(z["capacity"] for z in ZONES.values())

print("[INFO] Starting Crowd Video Stream. Press 'q' to quit.")

while video.isOpened():
    ret, frame = video.read()
    if not ret:
        # Loop video for continuous demonstration
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # YOLO Person Detection (verbose=False keeps terminal clean)
    results = model(frame, verbose=False)

    # Initialize count dictionaries for this frame
    zone_counts = {zone: 0 for zone in ZONES}
    total_detected = 0

    # Overlay copy for semi-transparent zone filling
    zone_overlay = frame.copy()

    # Step A: Process each detected bounding box
    for box in results[0].boxes:
        class_id = int(box.cls[0])

        if class_id == 0:  # 0 = Person
            total_detected += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Bottom-Center point (represents feet of the person on ghat steps)
            cx = int((x1 + x2) / 2)
            cy = int(y2)

            # Check which zone this person belongs to
            person_zone = None
            for zone_name, zone_data in ZONES.items():
                # pointPolygonTest >= 0 means point is inside or on the boundary
                if cv2.pointPolygonTest(zone_data["polygon"], (cx, cy), False) >= 0:
                    zone_counts[zone_name] += 1
                    person_zone = zone_name
                    break

            # Draw clear bounding box on the person
            box_color = (0, 255, 0) if person_zone else (180, 180, 180)
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            # Draw feet point
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

    # Step B: Draw Colored Translucent Zones based on real-time occupancy
    zone_status_map = {}
    for zone_name, zone_data in ZONES.items():
        count = zone_counts[zone_name]
        cap = zone_data["capacity"]
        occ, status, color_bgr = evaluate_zone_status(count, cap)
        zone_status_map[zone_name] = status

        # Fill zone polygon with its status color (semi-transparent)
        cv2.fillPoly(zone_overlay, [zone_data["polygon"]], color_bgr)
        # Draw solid boundary line
        cv2.polylines(frame, [zone_data["polygon"]], isClosed=True, color=color_bgr, thickness=3)

    # Blend overlay with 25% opacity
    cv2.addWeighted(zone_overlay, 0.25, frame, 0.75, 0, frame)

    # Step C: Evaluate Overall Decision Support Metrics
    overall_occupancy, overall_status, overall_color = evaluate_zone_status(total_detected, TOTAL_CAPACITY)
    decisions = get_gate_recommendations(overall_occupancy, zone_status_map)
    evac_time = calculate_evacuation_time(total_detected, exit_width_meters=4.0)

    # Step D: Draw High-Tech Command Center HUD (Top Information Bar)
    # HUD Background Rectangle (Dark Translucent Bar)
    hud_overlay = frame.copy()
    cv2.rectangle(hud_overlay, (20, 20), (2540, 320), (20, 20, 20), -1)
    cv2.addWeighted(hud_overlay, 0.85, frame, 0.15, 0, frame)
    cv2.rectangle(frame, (20, 20), (2540, 320), (100, 100, 100), 2)

    # Header Title
    cv2.putText(frame, "GHATNETRA AI - MPSTDC DECISION SUPPORT SYSTEM (UJJAIN RAM GHAT)",
                (40, 70), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 255), 3)

    # Row 1: Overall Metrics
    cv2.putText(frame, f"Total Crowd: {total_detected}/{TOTAL_CAPACITY}",
                (40, 125), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
    cv2.putText(frame, f"Occupancy: {overall_occupancy}% [{overall_status}]",
                (550, 125), cv2.FONT_HERSHEY_SIMPLEX, 1.1, overall_color, 3)
    cv2.putText(frame, f"Est. Evac Time: {evac_time} min",
                (1200, 125), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 2)

    # Row 2: Zone-Wise Breakdown
    zone_x = 40
    for z_name, z_data in ZONES.items():
        z_count = zone_counts[z_name]
        z_cap = z_data["capacity"]
        z_occ, z_stat, z_col = evaluate_zone_status(z_count, z_cap)
        cv2.putText(frame, f"{z_name}: {z_count}/{z_cap} ({z_occ}%) - {z_stat}",
                    (zone_x, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.9, z_col, 2)
        zone_x += 820

    # Row 3: Live Gate Control & AI Decision Recommendation
    gate_color = (0, 255, 0) if decisions["gate_1_state"] == "OPEN" else (
        (0, 255, 255) if decisions["gate_1_state"] == "CONTROLLED" else (0, 0, 255)
    )
    cv2.putText(frame, f"ENTRY GATE 1: {decisions['gate_1']}",
                (40, 245), cv2.FONT_HERSHEY_SIMPLEX, 1.0, gate_color, 2)
    cv2.putText(frame, f"EXIT GATE 2: {decisions['gate_2']}",
                (1300, 245), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # Row 4: Route Guidance / Resource Deployment
    cv2.putText(frame, f"Action: {decisions['alternate_route']} | {decisions['resource_action']}",
                (40, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (220, 220, 220), 2)

    # Step E: Resize for Display (2560x1440 -> 1280x720) so it fits on any standard screen
    display_frame = cv2.resize(frame, (1280, 720))
    cv2.imshow("GhatNetra AI - SIH 2026 Prototype", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
print("[INFO] Application closed successfully.")