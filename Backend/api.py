from pathlib import Path
from collections import deque

import cv2
from flask import Flask, jsonify
from flask_cors import CORS
from ultralytics import YOLO

from decision_engine import (
    evaluate_zone_status,
    get_gate_recommendations,
    calculate_evacuation_time,
)


# =========================================================
# APP SETUP
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

MODEL_PATH = BASE_DIR / "yolo11n.pt"

# NEW CROWD VIDEO
VIDEO_NAME = "ghat_crowd.mp4"
VIDEO_PATH = PROJECT_DIR / "Videos" / VIDEO_NAME


# =========================================================
# YOLO CONFIGURATION
# =========================================================

model = YOLO(str(MODEL_PATH))

# YOLO class 0 = person
PERSON_CLASS = 0

# Minimum confidence for person detection
CONFIDENCE_THRESHOLD = 0.50


# =========================================================
# VIDEO CONFIGURATION
# =========================================================

video = cv2.VideoCapture(str(VIDEO_PATH))

current_frame = 0

# Analyze every 15 frames
FRAME_STEP = 15


# =========================================================
# GHAT ZONE CAPACITY
# =========================================================

ZONES = {
    "Zone A": 150,
    "Zone B": 200,
    "Zone C": 100,
}

TOTAL_CAPACITY = sum(ZONES.values())


# =========================================================
# CROWD HISTORY
# =========================================================

crowd_history = deque(maxlen=60)


# =========================================================
# VIDEO FUNCTIONS
# =========================================================

def open_video():
    """Open or reopen the crowd video."""

    global video

    if video.isOpened():
        return True

    video.release()
    video = cv2.VideoCapture(str(VIDEO_PATH))

    return video.isOpened()


def get_next_frame():
    """Move video forward and return the current frame."""

    global video
    global current_frame

    if not open_video():
        return None

    for _ in range(FRAME_STEP):

        ret, frame = video.read()

        if ret:
            current_frame += 1
            continue

        # Restart video when it reaches the end
        video.release()
        video = cv2.VideoCapture(str(VIDEO_PATH))
        current_frame = 0

        ret, frame = video.read()

        if not ret:
            return None

        current_frame = 1

    return frame


def get_video_time():
    """Return current video time in seconds."""

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    return current_frame / fps


# =========================================================
# YOLO DETECTION
# =========================================================

def detect_people(frame):
    """Detect people in the given frame."""

    results = model(
        frame,
        classes=[PERSON_CLASS],
        conf=CONFIDENCE_THRESHOLD,
        verbose=False,
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

    return total_people


# =========================================================
# ZONE CALCULATION
# =========================================================

def calculate_zone_counts(total_people):
    """
    Temporary zone distribution.

    Zone A = 20%
    Zone B = 60%
    Zone C = remaining people

    Later this can be replaced with
    actual polygon-based zone detection.
    """

    zone_a = round(total_people * 0.20)
    zone_b = round(total_people * 0.60)
    zone_c = total_people - zone_a - zone_b

    return {
        "Zone A": zone_a,
        "Zone B": zone_b,
        "Zone C": zone_c,
    }


# =========================================================
# CROWD PREDICTION
# =========================================================

def predict_zone(zone_name, capacity):
    """
    Predict approximately when a zone may reach
    80% of its capacity.
    """

    if len(crowd_history) < 2:
        return {
            "growth_per_min": 0,
            "high_crowd_in_min": None,
            "prediction_status": "Collecting data",
        }

    first = crowd_history[0]
    last = crowd_history[-1]

    time_diff = last["video_time"] - first["video_time"]

    if time_diff <= 0:
        return {
            "growth_per_min": 0,
            "high_crowd_in_min": None,
            "prediction_status": "Collecting data",
        }

    people_change = last[zone_name] - first[zone_name]

    # People growth per minute
    growth_per_min = (people_change / time_diff) * 60

    current_people = last[zone_name]

    # 80% capacity = HIGH crowd threshold
    high_threshold = capacity * 0.80

    people_remaining = high_threshold - current_people

    if current_people >= high_threshold:

        minutes = 0
        prediction_status = "HIGH"

    elif growth_per_min > 0 and people_remaining > 0:

        minutes = people_remaining / growth_per_min
        prediction_status = "Rising"

    elif growth_per_min > 0:

        minutes = 0
        prediction_status = "HIGH"

    else:

        minutes = None
        prediction_status = "Stable"

    return {
        "growth_per_min": round(growth_per_min, 2),
        "high_crowd_in_min": (
            round(minutes, 1)
            if minutes is not None
            else None
        ),
        "prediction_status": prediction_status,
    }


def build_prediction():
    """Create prediction data for all zones."""

    return {
        zone_name: predict_zone(
            zone_name,
            capacity,
        )
        for zone_name, capacity in ZONES.items()
    }


# =========================================================
# ZONE STATUS
# =========================================================

def build_zone_status(zone_counts):
    """Calculate occupancy and status for each zone."""

    zone_status = {}

    for zone_name, capacity in ZONES.items():

        count = zone_counts[zone_name]

        occupancy = (count / capacity) * 100

        status = evaluate_zone_status(
            count,
            capacity,
        )

        # decision_engine may return a tuple
        if isinstance(status, tuple):
            status = status[0]

        zone_status[zone_name] = {
            "count": count,
            "capacity": capacity,
            "occupancy": round(occupancy, 1),
            "status": status,
        }

    return zone_status


# =========================================================
# HOME API
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "project": "GhatNetra AI",
        "status": "Backend running",
        "model": "YOLO11n",
        "detection_class": "person",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "video": VIDEO_NAME,
        "prediction_history_points": len(crowd_history),
    })


# =========================================================
# STATUS API
# =========================================================

@app.route("/api/status")
def get_status():

    # -----------------------------------------------------
    # GET VIDEO FRAME
    # -----------------------------------------------------

    frame = get_next_frame()

    if frame is None:

        return jsonify({
            "success": False,
            "error": (
                f"Could not open or read video: "
                f"{VIDEO_PATH}"
            ),
        }), 500

    # -----------------------------------------------------
    # YOLO PERSON DETECTION
    # -----------------------------------------------------

    total_people = detect_people(frame)

    # -----------------------------------------------------
    # ZONE COUNTS
    # -----------------------------------------------------

    zone_counts = calculate_zone_counts(
        total_people
    )

    # -----------------------------------------------------
    # VIDEO TIME
    # -----------------------------------------------------

    video_time = get_video_time()

    # -----------------------------------------------------
    # SAVE CROWD HISTORY
    # -----------------------------------------------------

    observation = {
        "video_time": round(video_time, 2),
        "frame": current_frame,
        "Zone A": zone_counts["Zone A"],
        "Zone B": zone_counts["Zone B"],
        "Zone C": zone_counts["Zone C"],
        "total": total_people,
    }

    crowd_history.append(observation)

    # -----------------------------------------------------
    # PREDICTION
    # -----------------------------------------------------

    prediction = build_prediction()

    # -----------------------------------------------------
    # OVERALL OCCUPANCY
    # -----------------------------------------------------

    overall_occupancy = (
        total_people / TOTAL_CAPACITY
    ) * 100

    # -----------------------------------------------------
    # ZONE STATUS
    # -----------------------------------------------------

    zone_status = build_zone_status(
        zone_counts
    )

    # -----------------------------------------------------
    # GATE DECISION
    # -----------------------------------------------------

    decisions = get_gate_recommendations(
        overall_occupancy,
        zone_status,
    )

    # -----------------------------------------------------
    # EVACUATION TIME
    # -----------------------------------------------------

    evacuation_time = calculate_evacuation_time(
        total_people,
        exit_width_meters=4.0,
    )

    # =====================================================
    # API RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "frame_number": current_frame,

        "video_time": round(
            video_time,
            2,
        ),

        # Crowd
        "total_people": total_people,

        "total_capacity": TOTAL_CAPACITY,

        "occupancy": round(
            overall_occupancy,
            1,
        ),

        # Zones
        "zones": zone_status,

        # Prediction
        "prediction": prediction,

        # Gates
        "gate_1": decisions.get(
            "gate_1",
            "OPEN",
        ),

        "gate_2": decisions.get(
            "gate_2",
            "OPEN",
        ),

        # Alternate route
        "alternate_route": decisions.get(
            "alternate_route",
            "No diversion needed. All pathways clear.",
        ),

        # Resource action
        "resource_action": decisions.get(
            "resource_action",
            "Routine patrolling by local volunteers.",
        ),

        # Evacuation
        "evacuation_time": round(
            evacuation_time,
            1,
        ),

        # History
        "history": {
            "points": len(crowd_history),
            "recent": list(crowd_history)[-10:],
        },

        # Detection
        "detection": {
            "model": "YOLO11n",
            "class": "person",
            "confidence_threshold": CONFIDENCE_THRESHOLD,
        },
    })


# =========================================================
# CROWD HISTORY API
# =========================================================

@app.route("/api/history")
def get_history():

    return jsonify({
        "success": True,
        "points": len(crowd_history),
        "history": list(crowd_history),
    })


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("GhatNetra AI Backend")
    print("=" * 50)
    print(f"Video : {VIDEO_PATH}")
    print(f"Model : {MODEL_PATH}")
    print("Server: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )