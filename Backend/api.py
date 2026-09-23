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

# YOLO class 0 = person
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

# Recent crowd observations
crowd_history = deque(maxlen=60)

history_start_time = time.time()


# =========================================================
# PREDICTION FUNCTION
# =========================================================

def predict_zone(zone_name, capacity):
    """
    Predict when a zone may reach 80% capacity.

    Prediction is based on recent crowd observations
    from the recorded video.
    """

    # Need at least 2 observations
    if len(crowd_history) < 2:
        return {
            "growth_per_min": 0,
            "high_crowd_in_min": None,
            "prediction_status": "Collecting data"
        }

    first = crowd_history[0]
    last = crowd_history[-1]

    # Time difference in seconds
    time_diff = last["video_time"] - first["video_time"]

    if time_diff <= 0:
        return {
            "growth_per_min": 0,
            "high_crowd_in_min": None,
            "prediction_status": "Collecting data"
        }

    # Change in number of people
    people_change = (
        last[zone_name] -
        first[zone_name]
    )

    # Convert growth to people/minute
    growth_per_min = (
        people_change / time_diff
    ) * 60

    current_people = last[zone_name]

    # 80% capacity = High Crowd threshold
    high_threshold = capacity * 0.80

    people_remaining = (
        high_threshold -
        current_people
    )

    # -----------------------------------------------------
    # Predict future crowd
    # -----------------------------------------------------

    if current_people >= high_threshold:

        minutes = 0

        prediction_status = "HIGH"

    elif growth_per_min > 0 and people_remaining > 0:

        minutes = (
            people_remaining /
            growth_per_min
        )

        prediction_status = "Rising"

    elif growth_per_min > 0:

        minutes = 0

        prediction_status = "HIGH"

    else:

        minutes = None

        prediction_status = "Stable"

    return {
        "growth_per_min": round(
            growth_per_min,
            2
        ),

        "high_crowd_in_min": (
            round(minutes, 1)
            if minutes is not None
            else None
        ),

        "prediction_status":
            prediction_status
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({

        "project":
            "GhatNetra AI",

        "status":
            "Backend running",

        "model":
            "YOLO11n",

        "detection_class":
            "person",

        "confidence_threshold":
            CONFIDENCE_THRESHOLD,

        "prediction_history_points":
            len(crowd_history)
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

        video = cv2.VideoCapture(
            VIDEO_PATH
        )

        if not video.isOpened():

            return jsonify({

                "success": False,

                "error":
                    "Could not open crowd video."

            }), 500


    # -----------------------------------------------------
    # Move video forward
    # -----------------------------------------------------

    for _ in range(FRAME_STEP):

        ret, frame = video.read()

        if not ret:

            # Restart video
            video.release()

            video = cv2.VideoCapture(
                VIDEO_PATH
            )

            current_frame = 0

            ret, frame = video.read()

            if not ret:

                return jsonify({

                    "success": False,

                    "error":
                        "Could not read video frame."

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

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        if (
            class_id == PERSON_CLASS
            and
            confidence >= CONFIDENCE_THRESHOLD
        ):

            total_people += 1


    # -----------------------------------------------------
    # TEMPORARY ZONE DISTRIBUTION
    # -----------------------------------------------------

    # NOTE:
    # This is temporary.
    # Later this can be replaced by actual
    # polygon-based zone detection.

    zone_a = round(
        total_people * 0.20
    )

    zone_b = round(
        total_people * 0.60
    )

    zone_c = (
        total_people
        - zone_a
        - zone_b
    )


    # -----------------------------------------------------
    # CURRENT VIDEO TIME
    # -----------------------------------------------------

    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        fps = 30

    video_time = (
        current_frame /
        fps
    )


    # -----------------------------------------------------
    # SAVE CROWD HISTORY
    # -----------------------------------------------------

    observation = {

        "video_time":
            round(video_time, 2),

        "frame":
            current_frame,

        "Zone A":
            zone_a,

        "Zone B":
            zone_b,

        "Zone C":
            zone_c,

        "total":
            total_people
    }

    crowd_history.append(
        observation
    )


    # =====================================================
    # PREDICTION
    # =====================================================

    prediction = {

        "Zone A":
            predict_zone(
                "Zone A",
                ZONES["Zone A"]
            ),

        "Zone B":
            predict_zone(
                "Zone B",
                ZONES["Zone B"]
            ),

        "Zone C":
            predict_zone(
                "Zone C",
                ZONES["Zone C"]
            )
    }


    # -----------------------------------------------------
    # OCCUPANCY
    # -----------------------------------------------------

    overall_occupancy = (
        total_people /
        TOTAL_CAPACITY
    ) * 100


    # -----------------------------------------------------
    # ZONE STATUS
    # -----------------------------------------------------

    zone_counts = {

        "Zone A":
            zone_a,

        "Zone B":
            zone_b,

        "Zone C":
            zone_c
    }

    zone_status = {}

    for zone_name, capacity in ZONES.items():

        count = zone_counts[
            zone_name
        ]

        occupancy = (
            count /
            capacity
        ) * 100

        status = evaluate_zone_status(
            count,
            capacity
        )

        zone_status[
            zone_name
        ] = {

            "count":
                count,

            "capacity":
                capacity,

            "occupancy":
                round(
                    occupancy,
                    1
                ),

            "status":
                (
                    status[0]
                    if isinstance(
                        status,
                        tuple
                    )
                    else status
                )
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

    evacuation_time = (
        calculate_evacuation_time(
            total_people,
            exit_width_meters=4.0
        )
    )


    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return jsonify({

        "success":
            True,

        "frame_number":
            current_frame,

        "video_time":
            round(
                video_time,
                2
            ),

        "total_people":
            total_people,

        "total_capacity":
            TOTAL_CAPACITY,

        "occupancy":
            round(
                overall_occupancy,
                1
            ),

        # -------------------------------------------------
        # ZONE DATA
        # -------------------------------------------------

        "zones":
            zone_status,

        # -------------------------------------------------
        # PREDICTION DATA
        # -------------------------------------------------

        "prediction":
            prediction,

        # -------------------------------------------------
        # GATE DATA
        # -------------------------------------------------

        "gate_1":
            decisions.get(
                "gate_1",
                "OPEN"
            ),

        "gate_2":
            decisions.get(
                "gate_2",
                "OPEN"
            ),

        # -------------------------------------------------
        # ROUTE
        # -------------------------------------------------

        "alternate_route":
            decisions.get(
                "alternate_route",
                "No diversion needed. All pathways clear."
            ),

        # -------------------------------------------------
        # RESOURCE ACTION
        # -------------------------------------------------

        "resource_action":
            decisions.get(
                "resource_action",
                "Routine patrolling by local volunteers."
            ),

        # -------------------------------------------------
        # EVACUATION
        # -------------------------------------------------

        "evacuation_time":
            round(
                evacuation_time,
                1
            ),

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        "history": {

            "points":
                len(crowd_history),

            "recent":
                list(
                    crowd_history
                )[-10:]
        },

        # -------------------------------------------------
        # DETECTION
        # -------------------------------------------------

        "detection": {

            "model":
                "YOLO11n",

            "class":
                "person",

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

        "success":
            True,

        "points":
            len(crowd_history),

        "history":
            list(crowd_history)

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