from flask import Flask, jsonify
from flask_cors import CORS
import cv2
from ultralytics import YOLO

from decision_engine import (
    evaluate_zone_status,
    get_gate_recommendations,
    calculate_evacuation_time
)

app = Flask(__name__)
CORS(app)


# =========================================================
# YOLO MODEL
# =========================================================

model = YOLO("yolo11n.pt")


# =========================================================
# VIDEO
# =========================================================

VIDEO_PATH = "../Videos/crowd.mp4"

video = cv2.VideoCapture(VIDEO_PATH)

# Current video frame
current_frame = 0

# Number of frames to move on every API request
FRAME_STEP = 15


# =========================================================
# ZONE CAPACITIES
# =========================================================

ZONES = {
    "Zone A": 150,
    "Zone B": 200,
    "Zone C": 100
}

TOTAL_CAPACITY = sum(ZONES.values())


# =========================================================
# STATUS API
# =========================================================

@app.route("/api/status")
def get_status():

    global video
    global current_frame

    # -----------------------------------------------------
    # Check whether video is available
    # -----------------------------------------------------

    if not video.isOpened():

        video = cv2.VideoCapture(VIDEO_PATH)
        current_frame = 0

    # -----------------------------------------------------
    # Move forward in the video
    # -----------------------------------------------------

    ret = False
    frame = None

    for _ in range(FRAME_STEP):

        ret, frame = video.read()

        if not ret:
            break

    # -----------------------------------------------------
    # If video reached the end, restart
    # -----------------------------------------------------

    if not ret:

        video.release()

        video = cv2.VideoCapture(VIDEO_PATH)

        current_frame = 0

        # Read first frame after restart
        ret, frame = video.read()

    # -----------------------------------------------------
    # Check frame
    # -----------------------------------------------------

    if not ret:

        return jsonify({
            "success": False,
            "error": "Could not read video frame"
        }), 500

    # Update frame number
    current_frame += FRAME_STEP


    # =====================================================
    # YOLO DETECTION
    # =====================================================

    results = model(
        frame,
        verbose=False
    )

    total_people = 0

    for box in results[0].boxes:

        # Class 0 = person
        if int(box.cls[0]) == 0:

            total_people += 1


    # =====================================================
    # TEMPORARY ZONE DISTRIBUTION
    # =====================================================

    # NOTE:
    # This is currently a temporary distribution.
    # Exact polygon-based zone detection can be added later.

    zone_a = round(total_people * 0.20)

    zone_b = round(total_people * 0.60)

    zone_c = total_people - zone_a - zone_b


    zone_counts = {

        "Zone A": zone_a,

        "Zone B": zone_b,

        "Zone C": zone_c
    }


    # =====================================================
    # OVERALL OCCUPANCY
    # =====================================================

    occupancy, status, _ = evaluate_zone_status(

        total_people,

        TOTAL_CAPACITY
    )


    # =====================================================
    # ZONE STATUS
    # =====================================================

    zone_status = {}


    for zone, count in zone_counts.items():

        occ, stat, _ = evaluate_zone_status(

            count,

            ZONES[zone]
        )


        zone_status[zone] = {

            "count": count,

            "capacity": ZONES[zone],

            "occupancy": occ,

            "status": stat
        }


    # =====================================================
    # GATE DECISION
    # =====================================================

    decisions = get_gate_recommendations(

        occupancy,

        {
            zone: data["status"]

            for zone, data in zone_status.items()
        }
    )


    # =====================================================
    # EVACUATION TIME
    # =====================================================

    evacuation_time = calculate_evacuation_time(

        total_people,

        exit_width_meters=4.0
    )


    # =====================================================
    # API RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        # Video information
        "frame_number": current_frame,

        # Crowd
        "total_people": total_people,

        "total_capacity": TOTAL_CAPACITY,

        "occupancy": occupancy,

        "overall_status": status,

        # Gates
        "gate_1": decisions["gate_1"],

        "gate_2": decisions["gate_2"],

        # Safety
        "evacuation_time": evacuation_time,

        "alternate_route": decisions["alternate_route"],

        "resource_action": decisions["resource_action"],

        # Zones
        "zones": zone_status
    })


# =========================================================
# HOME API
# =========================================================

@app.route("/")
def home():

    return jsonify({

        "message": "GhatNetra AI Backend API is running",

        "status": "online",

        "video": "crowd.mp4",

        "frame_step": FRAME_STEP
    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )