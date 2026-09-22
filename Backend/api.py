from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import time
from collections import deque
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

# Only YOLO class 0 = person
PERSON_CLASS = 0

# Ignore very low-confidence detections
CONFIDENCE_THRESHOLD = 0.50


# =========================================================
# VIDEO
# =========================================================

VIDEO_PATH = "../Videos/crowd.mp4"

video = cv2.VideoCapture(VIDEO_PATH)

current_frame = 0

# Analyze every 15 frames
FRAME_STEP = 15


# =========================================================
# GHAT ZONE CAPACITY
# =========================================================

ZONES = {
    "Zone A": 150,
    "Zone B": 200,
    "Zone C": 100
}

TOTAL_CAPACITY = sum(ZONES.values())


# =========================================================
# CROWD HISTORY
# =========================================================
# We will keep recent crowd observations.
#
# Example:
#
# {
#   "video_time": 1.2,
#   "Zone A": 3,
#   "Zone B": 8,
#   "Zone C": 2
# }
#
# This data will later be used for prediction.

crowd_history = deque(maxlen=60)

history_start_time = time.time()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "project": "GhatNetra AI",
        "status": "Backend running",
        "model": "YOLO11n",
        "detection_class": "person",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "prediction_history_points": len(crowd_history)
    })


# =========================================================
# STATUS API
# =========================================================

@app.route("/api/status")
def get_status():

    global video
    global current_frame

    # -----------------------------------------------------
    # Check video
    # -----------------------------------------------------

    if not video.isOpened():

        video = cv2.VideoCapture(VIDEO_PATH)

        if not video.isOpened():

            return jsonify({
                "success": False,
                "error": "Could not open crowd video."
            }), 500


    # -----------------------------------------------------
    # Move video forward
    # -----------------------------------------------------

    for _ in range(FRAME_STEP):

        ret, frame = video.read()

        if not ret:

            # Restart video when it reaches the end
            video.release()
            video = cv2.VideoCapture(VIDEO_PATH)

            current_frame = 0

            ret, frame = video.read()

            if not ret:

                return jsonify({
                    "success": False,
                    "error": "Could not read video frame."
                }), 500

            break

        current_frame += 1


    # -----------------------------------------------------
    # YOLO PERSON DETECTION
    # -----------------------------------------------------

    results = model(
        frame,
        classes=[PERSON_CLASS],
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )


    total_people = 0

    for box in results[0].boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        if (
            class_id == PERSON_CLASS
            and confidence >= CONFIDENCE_THRESHOLD
        ):
            total_people += 1


    # -----------------------------------------------------
    # TEMPORARY ZONE DISTRIBUTION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # This is still temporary.
    #
    # Next step we will replace this with the actual
    # polygon-based Zone A/B/C detection.
    #

    zone_a = round(total_people * 0.20)

    zone_b = round(total_people * 0.60)

    zone_c = total_people - zone_a - zone_b


    # -----------------------------------------------------
    # CURRENT VIDEO TIME
    # -----------------------------------------------------

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    video_time = current_frame / fps


    # -----------------------------------------------------
    # SAVE CROWD HISTORY
    # -----------------------------------------------------

    observation = {
        "video_time": round(video_time, 2),
        "frame": current_frame,
        "Zone A": zone_a,
        "Zone B": zone_b,
        "Zone C": zone_c,
        "total": total_people
    }

    crowd_history.append(observation)


    # -----------------------------------------------------
    # OCCUPANCY
    # -----------------------------------------------------

    overall_occupancy = (
        total_people / TOTAL_CAPACITY
    ) * 100


    # -----------------------------------------------------
    # ZONE STATUS
    # -----------------------------------------------------

    zone_counts = {
        "Zone A": zone_a,
        "Zone B": zone_b,
        "Zone C": zone_c
    }

    zone_status = {}

    for zone_name, capacity in ZONES.items():

        count = zone_counts[zone_name]

        occupancy = (count / capacity) * 100

        status = evaluate_zone_status(
            count,
            capacity
        )

        zone_status[zone_name] = {
            "count": count,
            "capacity": capacity,
            "occupancy": round(occupancy, 1),
            "status": status[0] if isinstance(status, tuple) else status
        }


    # -----------------------------------------------------
    # GATE DECISION
    # -----------------------------------------------------

    decisions = get_gate_recommendations(
        overall_occupancy,
        zone_status
    )


    # -----------------------------------------------------
    # EVACUATION TIME
    # -----------------------------------------------------

    evacuation_time = calculate_evacuation_time(
        total_people,
        exit_width_meters=4.0
    )


    # -----------------------------------------------------
    # RETURN RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "frame_number": current_frame,

        "video_time": round(video_time, 2),

        "total_people": total_people,

        "total_capacity": TOTAL_CAPACITY,

        "occupancy": round(
            overall_occupancy,
            1
        ),

        "zones": zone_status,

        "gate_1": decisions.get(
            "gate_1",
            "OPEN"
        ),

        "gate_2": decisions.get(
            "gate_2",
            "OPEN"
        ),

        "alternate_route": decisions.get(
            "alternate_route",
            "No diversion needed. All pathways clear."
        ),

        "resource_action": decisions.get(
            "resource_action",
            "Routine patrolling by local volunteers."
        ),

        "evacuation_time": round(
            evacuation_time,
            1
        ),

        # ---------------------------------------------
        # HISTORY INFORMATION
        # ---------------------------------------------

        "history": {
            "points": len(crowd_history),
            "recent": list(crowd_history)[-10:]
        },

        # ---------------------------------------------
        # DETECTION INFORMATION
        # ---------------------------------------------

        "detection": {

            "model": "YOLO11n",

            "class": "person",

            "confidence_threshold":
                CONFIDENCE_THRESHOLD
        }

    })


# =========================================================
# CROWD HISTORY API
# =========================================================

@app.route("/api/history")
def get_history():

    return jsonify({

        "success": True,

        "points": len(crowd_history),

        "history": list(crowd_history)

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