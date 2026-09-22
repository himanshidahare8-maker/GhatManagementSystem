import cv2
import numpy as np
from ultralytics import YOLO
from decision_engine import evaluate_zone_status, get_gate_recommendations, calculate_evacuation_time

print("[1] Loading YOLO model...")
model = YOLO("yolo11n.pt")

print("[2] Opening video...")
video = cv2.VideoCapture("../Videos/crowd.mp4")
ret, frame = video.read()

if not ret:
    print("[ERROR] Could not read frame from ../Videos/crowd.mp4")
    exit(1)

print(f"[3] Frame read successfully. Dimensions: {frame.shape[1]}x{frame.shape[0]}")

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

print("[4] Running YOLO detection on frame...")
results = model(frame, verbose=False)

zone_counts = {z: 0 for z in ZONES}
total_people = 0

zone_overlay = frame.copy()

for box in results[0].boxes:
    if int(box.cls[0]) == 0:
        total_people += 1
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx = int((x1 + x2) / 2)
        cy = int(y2)

        person_zone = None
        for z_name, z_data in ZONES.items():
            if cv2.pointPolygonTest(z_data["polygon"], (cx, cy), False) >= 0:
                zone_counts[z_name] += 1
                person_zone = z_name
                break

        color = (0, 255, 0) if person_zone else (200, 200, 200)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

# Draw zones
zone_status_map = {}
for z_name, z_data in ZONES.items():
    cnt = zone_counts[z_name]
    cap = z_data["capacity"]
    occ, stat, col = evaluate_zone_status(cnt, cap)
    zone_status_map[z_name] = stat
    cv2.fillPoly(zone_overlay, [z_data["polygon"]], col)
    cv2.polylines(frame, [z_data["polygon"]], True, col, 3)

cv2.addWeighted(zone_overlay, 0.25, frame, 0.75, 0, frame)

total_cap = sum(z["capacity"] for z in ZONES.values())
overall_occ, overall_stat, _ = evaluate_zone_status(total_people, total_cap)
decisions = get_gate_recommendations(overall_occ, zone_status_map)
evac_time = calculate_evacuation_time(total_people)

# Draw info bar
cv2.rectangle(frame, (20, 20), (2540, 280), (30, 30, 30), -1)
cv2.putText(frame, f"GHATNETRA AI | People: {total_people} | Occ: {overall_occ}% ({overall_stat}) | Evac: {evac_time}m", (50, 80), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 255), 2)
cv2.putText(frame, f"Gate 1: {decisions['gate_1']} | Gate 2: {decisions['gate_2']}", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
cv2.putText(frame, f"Route: {decisions['alternate_route']}", (50, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)

out_resized = cv2.resize(frame, (1280, 720))
cv2.imwrite("test_zone_output.jpg", out_resized)
video.release()

print("\n=== PIPELINE SUCCESSFUL ===")
print(f"Total People Detected: {total_people}")
for z_name, count in zone_counts.items():
    print(f"  {z_name}: {count} people (Status: {zone_status_map[z_name]})")
print(f"Gate 1: {decisions['gate_1']}")
print(f"Gate 2: {decisions['gate_2']}")
print(f"Evacuation Time: {evac_time} minutes")
print("Saved annotated frame to test_zone_output.jpg")
