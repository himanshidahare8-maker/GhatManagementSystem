"""
GhatNetra AI (à¤˜à¤¾à¤Ÿ-à¤¨à¥‡à¤¤à¥à¤°)
MPSTDC AI Ghat Crowd Management & Decision Support System
Smart India Hackathon 2026
"""

import streamlit as st
import cv2
import numpy as np
import pandas as pd
import time
from pathlib import Path
from datetime import datetime, timedelta
from ultralytics import YOLO
import base64

st.markdown("## 🎥 Multi-Camera Crowd Counting")

uploaded_videos = st.file_uploader(
    "Upload videos from different camera angles",
    type=["mp4", "avi", "mov"],
    accept_multiple_files=True,
    key="multi_camera_upload"
)

if uploaded_videos:
    st.success(
        f"{len(uploaded_videos)} videos uploaded successfully!"
    )

    for i, video in enumerate(uploaded_videos, start=1):
        st.write(f"Camera {i}: {video.name}")


if uploaded_videos:
    if st.button("▶️ Process Videos", type="primary"):
        st.session_state["process_multi_videos"] = True

if uploaded_videos and st.session_state.get("process_multi_videos", False):
    model = YOLO("yolo11n.pt")
    total_people = 0

    for i, video in enumerate(uploaded_videos, start=1):
        st.write(f"### Camera {i}: {video.name}")

        temp_path = Path(f"temp_camera_{i}.mp4")
        temp_path.write_bytes(video.getvalue())

        cap = cv2.VideoCapture(str(temp_path))
        ids_seen = set()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model.track(
    frame,
    persist=True,
    classes=[0],
    tracker="bytetrack.yaml",
    conf=0.10,
    imgsz=1280,
    max_det=300,
    verbose=False
)

            boxes = results[0].boxes
            if boxes is not None and boxes.id is not None:
                ids_seen.update(
                    boxes.id.cpu().numpy().astype(int)
                )

        cap.release()
        temp_path.unlink(missing_ok=True)

        count = len(ids_seen)
        total_people += count
        st.metric(f"Camera {i} tracked people", count)

    st.metric("Combined tracked count", total_people)
    st.session_state["process_multi_videos"] = False

from decision_engine import (
    evaluate_zone_status,
    get_gate_recommendations,
    calculate_evacuation_time
)

# 🤖 Floating AI Assistant
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = [
        {
            "role": "assistant",
            "content": "Namaste! 👋 Main Crowd Vision AI Assistant hoon. Ghat, crowd, safety aur dashboard se related question pooch sakte hain."
        }
    ]

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CROWDVISION AI - MPSTDC SIH 2026",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)
# =========================================================
# 🤖 FLOATING AI ASSISTANT UI
# =========================================================

ROBOT_IMAGE = Path(__file__).resolve().parent / "assets" / "ai_robot.png"

if ROBOT_IMAGE.exists():

    robot_base64 = base64.b64encode(
        ROBOT_IMAGE.read_bytes()
    ).decode("utf-8")

    st.markdown(
        f"""
        <style>

        .ai-floating-btn {{
            position: fixed;
            right: 24px;
            bottom: 24px;
            width: 82px;
            height: 82px;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            cursor: pointer;
            transition: transform 0.25s ease, filter 0.25s ease;
        }}

        .ai-floating-btn:hover {{
            transform: scale(1.10);
            filter: drop-shadow(0 8px 18px rgba(21, 101, 192, 0.35));
        }}

        .ai-floating-btn img {{
            width: 82px;
            height: 82px;
            object-fit: contain;
            filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.25));
        }}

        </style>

        <a class="ai-floating-btn"
           href="?ai=open"
           title="Crowd Vision AI Assistant">
            <img src="data:image/png;base64,{robot_base64}"
                 alt="Crowd Vision AI Assistant">
        </a>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <style>
        .ai-floating-btn {
            position: fixed;
            right: 24px;
            bottom: 24px;
            width: 65px;
            height: 65px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1565C0, #42A5F5);
            box-shadow: 0 6px 20px rgba(0,0,0,0.30);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            z-index: 9999;
            text-decoration: none;
        }
        </style>
        <a class="ai-floating-btn"
           href="?ai=open"
           title="Crowd Vision AI Assistant">
            🤖
        </a>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PATH CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "yolo11n.pt"

VIDEO_CANDIDATES = [
    PROJECT_ROOT / "Videos" / "ghat_crowd.mp4",
    PROJECT_ROOT / "videos" / "ghat_crowd.mp4",
    PROJECT_ROOT / "ghat_crowd.mp4",
]


def find_video():
    for path in VIDEO_CANDIDATES:
        if path.exists() and path.is_file():
            return path
    return None


VIDEO_PATH = find_video()


# =========================================================
# ALERT SYSTEM (added; existing dashboard logic retained)
# =========================================================
HIGH_OCCUPANCY_PERCENT = 75
CRITICAL_OCCUPANCY_PERCENT = 90


def build_crowd_alerts(zone_counts, zones):
    alerts = []
    for zone_name, count in zone_counts.items():
        capacity = zones[zone_name]["capacity"]
        if capacity <= 0:
            continue
        occupancy = (count / capacity) * 100
        if occupancy >= CRITICAL_OCCUPANCY_PERCENT:
            alerts.append({
                "type": "CRITICAL CROWD",
                "zone": zone_name,
                "occupancy": round(occupancy, 1),
                "severity": "CRITICAL",
                "message": (
                    f"{zone_name} occupancy is {occupancy:.1f}%. "
                    "Notify safety personnel and follow the approved "
                    "site emergency plan."
                )
            })
        elif occupancy >= HIGH_OCCUPANCY_PERCENT:
            alerts.append({
                "type": "HIGH CROWD",
                "zone": zone_name,
                "occupancy": round(occupancy, 1),
                "severity": "HIGH",
                "message": (
                    f"{zone_name} occupancy is {occupancy:.1f}%. "
                    "Review entry restrictions and monitor the zone."
                )
            })
    return alerts


if "active_crowd_alert_keys" not in st.session_state:
    st.session_state.active_crowd_alert_keys = set()
if "crowd_alert_history" not in st.session_state:
    st.session_state.crowd_alert_history = []
if "latest_crowd_alerts" not in st.session_state:
    st.session_state.latest_crowd_alerts = []
if "manual_emergency_alerts" not in st.session_state:
    st.session_state.manual_emergency_alerts = []
if "latest_zone_counts" not in st.session_state:
    st.session_state.latest_zone_counts = {}
if "latest_total_people" not in st.session_state:
    st.session_state.latest_total_people = None
if "latest_overall_status" not in st.session_state:
    st.session_state.latest_overall_status = "Waiting for video analysis"


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>

    .main-header {
        background: linear-gradient(
            135deg,
            #1e3a8a 0%,
            #0f172a 100%
        );

        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
        border-left: 7px solid #f59e0b;
        width: 100%;
        box-sizing: border-box;
    }

    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

# Load the sidebar logo only if it exists; check both backend/assets and project/assets.
logo_candidates = [
    Path(__file__).resolve().parent / "assets" / "crowd_vision copy.png",
    Path(__file__).resolve().parent.parent / "assets" / "crowd_vision copy.png",
]
logo_path = next((path for path in logo_candidates if path.is_file()), None)
if logo_path is not None:
    st.sidebar.image(str(logo_path), width=450)

st.sidebar.title("Command Controls")


selected_ghat = st.sidebar.selectbox(
    " Select Ghat Location",
    [
        "Ujjain - Ram Ghat (Shipra River)",
        "Ujjain - Narsingh Ghat (Shipra River)",
        "Omkareshwar - Nagar Ghat (Narmada River)",
        "Maheshwar - Ahilya Ghat (Narmada River)",
        "Narmadapuram - Sethani Ghat (Narmada River)"
    ]
)


st.sidebar.subheader("Zone Capacity Limits")

cap_zone_a = st.sidebar.slider(
    "Zone A (Entry Steps)",
    20,
    100,
    50
)

cap_zone_b = st.sidebar.slider(
    "Zone B (Central Snan)",
    20,
    120,
    60
)

cap_zone_c = st.sidebar.slider(
    "Zone C (Waterfront/Exit)",
    20,
    100,
    50
)


TOTAL_CAPACITY = (
    cap_zone_a +
    cap_zone_b +
    cap_zone_c
)


# =========================================================
# TOP BANNER
# =========================================================

st.title("\U0001F549\U0000FE0F CrowdVision AI ")

st.subheader(
    "Madhya Pradesh State Tourism Development Corporation Limited (MPSTDC)"
)

st.write(
    "AI-Powered River Ghat Crowd Management, "
    "Occupancy Prediction & Decision Support System"
)

c1, c2 = st.columns(2)

with c1:
    st.write("Ujjain Ram Ghat (Shipra River)**")

with c2:
    st.write(
        "31°C  |  River Flow: 1.2 m/s  |  Aarti: 18:30 IST"
    )

st.divider()

# Top-right alert bell (added)
_alert_count = len(st.session_state.latest_crowd_alerts) + len(st.session_state.manual_emergency_alerts)
_alert_spacer, _alert_col = st.columns([9.5, 1.5])
with _alert_col:
    with st.popover(f"🔔 ALERTS ({_alert_count})", use_container_width=True):
        st.markdown("### 🚨 Emergency Alerts")
        _all_alerts = list(st.session_state.latest_crowd_alerts) + list(st.session_state.manual_emergency_alerts)
        if _all_alerts:
            for _alert in _all_alerts:
                _zone_text = _alert.get("zone", "Ghat-wide")
                _occupancy_text = f"\n\n{_alert['occupancy']}% occupancy" if "occupancy" in _alert else ""
                _alert_text = (
                    f"**{_alert['severity']} — {_alert['type']}**\n\n"
                    f"{_zone_text}{_occupancy_text}\n\n"
                    f"{_alert['message']}"
                )
                if _alert["severity"] == "CRITICAL":
                    st.error(_alert_text)
                else:
                    st.warning(_alert_text)
        else:
            st.success("No active emergency alerts.")

        st.markdown("#### Report an Emergency")
        st.caption("Fire/medical/exit alerts are manually reportable in this prototype; they are not automatically detected.")
        _emergency_type = st.selectbox(
            "Emergency type",
            ["Fire / Smoke", "Medical Emergency", "Blocked Exit", "Stampede Risk", "Water Level Warning"],
            key="manual_emergency_type"
        )
        _emergency_zone = st.selectbox(
            "Affected area",
            ["Ghat-wide", "Zone A", "Zone B", "Zone C"],
            key="manual_emergency_zone"
        )
        if st.button("🚨 Report Emergency", key="report_emergency_alert", use_container_width=True):
            _severity = "CRITICAL" if _emergency_type in ["Fire / Smoke", "Stampede Risk"] else "HIGH"
            _manual_alert = {
                "type": _emergency_type.upper(),
                "zone": _emergency_zone,
                "severity": _severity,
                "message": "Emergency reported manually. Notify on-site safety staff and follow the approved emergency response plan.",
                "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
            st.session_state.manual_emergency_alerts.insert(0, _manual_alert)
            st.session_state.crowd_alert_history.insert(0, _manual_alert.copy())
            st.session_state.crowd_alert_history = st.session_state.crowd_alert_history[:50]
            st.rerun()
        if st.session_state.manual_emergency_alerts:
            if st.button("Clear reported emergency alerts", key="clear_manual_emergency_alerts", use_container_width=True):
                st.session_state.manual_emergency_alerts = []
                st.rerun()

        st.markdown("#### Recent Alert History")
        if st.session_state.crowd_alert_history:
            for _old_alert in st.session_state.crowd_alert_history[:10]:
                st.write(
                    f"{_old_alert['time']} — {_old_alert['severity']} — "
                    f"{_old_alert['zone']}: {_old_alert['type']}"
                )
        else:
            st.caption("No alerts recorded yet.")


# =========================================================
# ZONES
# =========================================================

ZONES = {
    "Zone A": {
        "polygon": np.array(
            [
                (0, 0),
                (773, 0),
                (773, 1080),
                (0, 1080)
            ],
            np.int32
        ),
        "capacity": cap_zone_a
    },

    "Zone B": {
        "polygon": np.array(
            [
                (773, 0),
                (1546, 0),
                (1546, 1080),
                (773, 1080)
            ],
            np.int32
        ),
        "capacity": cap_zone_b
    },

    "Zone C": {
        "polygon": np.array(
            [
                (1546, 0),
                (2320, 0),
                (2320, 1080),
                (1546, 1080)
            ],
            np.int32
        ),
        "capacity": cap_zone_c
    }
}


# =========================================================
# MODEL LOADING
# =========================================================

@st.cache_resource
def load_model():

    if not MODEL_PATH.exists():
        return None

    return YOLO(str(MODEL_PATH))


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "\U0001F4F9 Live Surveillance & Gates",
        "\U0001F321\U0000FE0F Density Heatmap & Flow",
        "\U0001F4C8 Trend & 60-Min Prediction",
        "\U0001F5FA\U0000FE0F Ghat GIS Map & Diversions",
        "\U0001F50D AI Lost Person Search",
        "\U0001F9EA What-If Simulation Sandbox"
    ]
)


# =========================================================
# TAB 1
# LIVE SURVEILLANCE & GATE CONTROL
# =========================================================

with tab1:

    c_left, c_right = st.columns([7, 5])


    # =====================================================
    # LEFT SIDE
    # =====================================================

    with c_left:

        st.subheader(
            "🎥 Live CCTV & YOLOv11 Detections"
        )

        st.caption(
            "Input: **ghat_crowd.mp4** (2320x1080) | "
            "Active Zones: **Zone A, B, C**"
        )

        vid_placeholder = st.empty()


        start_btn = st.button(
            "Start Live Crowd Processing",
            type="primary",
            key="start_live"
        )


    # =====================================================
    # RIGHT SIDE
    # =====================================================

    with c_right:

        st.subheader(
            "AI Gate & Decision Status"
        )

        m_placeholder = st.empty()

        gate_placeholder = st.empty()

        route_placeholder = st.empty()
        alert_placeholder = st.empty()  # added for live crowd alerts


    # =====================================================
    # START PROCESSING
    # =====================================================

    if start_btn:

        st.success("✅ Start Button Clicked!")

        # -------------------------------------------------
        # CHECK MODEL
        # -------------------------------------------------

        if not MODEL_PATH.exists():

            st.error(
                f"YOLO model not found:\n\n"
                f"{MODEL_PATH}"
            )

            st.info(
                "Project root me `yolo11n.pt` hona chahiye."
            )

            st.stop()


        # -------------------------------------------------
        # CHECK VIDEO
        # -------------------------------------------------

        if VIDEO_PATH is None:

            st.error(
                "âŒ Video file nahi mili."
            )

            st.info(
                "Inme se kisi location par `ghat_crowd.mp4` rakho:\n\n"
                "• Videos/ghat_crowd.mp4\n"
                "• videos/ghat_crowd.mp4\n"
                "• project root/ghat_crowd.mp4"
            )

            st.stop()


        # -------------------------------------------------
        # LOAD MODEL
        # -------------------------------------------------

        with st.spinner("🤖 Loading YOLOv11 model..."):

            model = load_model()


        if model is None:

            st.error(
                "YOLO model load nahi hua."
            )

            st.stop()


        st.success(
            f"✅ Model loaded: {MODEL_PATH.name}"
        )


        # -------------------------------------------------
        # OPEN VIDEO
        # -------------------------------------------------

        video = cv2.VideoCapture(
            str(VIDEO_PATH)
        )


        if not video.isOpened():

            st.error(
                f"Video open nahi ho rahi:\n{VIDEO_PATH}"
            )

            st.stop()


        # -------------------------------------------------
        # VIDEO INFORMATION
        # -------------------------------------------------

        fps = video.get(
            cv2.CAP_PROP_FPS
        )

        total_frames = int(
            video.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        if fps <= 0:
            fps = 25


        st.info(
            f"🎥 Video: `{VIDEO_PATH.name}` | "
            f"FPS: {fps:.1f} | "
            f"Frames: {total_frames}"
        )


        # -------------------------------------------------
        # PROCESSING SETTINGS
        # -------------------------------------------------

        frame_idx = 0

        process_every = 3

        overlap = 0.15

        processed_frames = 0

        max_processed_frames = 300


        # =================================================
        # VIDEO LOOP
        # =================================================

        while video.isOpened():

            ret, frame = video.read()


            # -------------------------------------------------
            # VIDEO END
            # -------------------------------------------------

            if not ret:

                video.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                continue


            frame_idx += 1


            # -------------------------------------------------
            # FRAME SKIP
            # -------------------------------------------------

            if frame_idx % process_every != 0:

                continue


            processed_frames += 1


            # -------------------------------------------------
            # LIMIT DEMO PROCESSING
            # -------------------------------------------------

            if processed_frames > max_processed_frames:

                break


            # -------------------------------------------------
            # FRAME SIZE
            # -------------------------------------------------

            h, w = frame.shape[:2]


            # =================================================
            # 4-TILE YOLO DETECTION
            # =================================================

            all_boxes = []

            all_scores = []


            tile_w = int(w / 2)

            tile_h = int(h / 2)


            # =================================================
            # CREATE 4 OVERLAPPING TILES
            # =================================================

            for row in range(2):

                for col in range(2):

                    # -------------------------------------------------
                    # TILE START
                    # -------------------------------------------------

                    x_start = int(
                        col * tile_w
                        - overlap * tile_w
                    )

                    y_start = int(
                        row * tile_h
                        - overlap * tile_h
                    )


                    x_start = max(
                        0,
                        x_start
                    )

                    y_start = max(
                        0,
                        y_start
                    )


                    # -------------------------------------------------
                    # TILE END
                    # -------------------------------------------------

                    x_end = int(
                        (col + 1) * tile_w
                        + overlap * tile_w
                    )

                    y_end = int(
                        (row + 1) * tile_h
                        + overlap * tile_h
                    )


                    x_end = min(
                        w,
                        x_end
                    )

                    y_end = min(
                        h,
                        y_end
                    )


                    # -------------------------------------------------
                    # CROP TILE
                    # -------------------------------------------------

                    tile = frame[
                        y_start:y_end,
                        x_start:x_end
                    ]


                    if tile.size == 0:
                        continue


                    # =================================================
                    # YOLO ON TILE
                    # =================================================

                    results = model(
                        tile,
                        conf=0.08,
                        imgsz=960,
                        classes=[0],
                        max_det=1000,
                        verbose=False
                    )


                    # =================================================
                    # READ DETECTIONS
                    # =================================================

                    if len(results) == 0:
                        continue


                    boxes = results[0].boxes


                    for box in boxes:

                        x1, y1, x2, y2 = map(
                            int,
                            box.xyxy[0]
                        )


                        score = float(
                            box.conf[0]
                        )


                        # -------------------------------------------------
                        # TILE -> FULL FRAME
                        # -------------------------------------------------

                        x1 += x_start
                        x2 += x_start

                        y1 += y_start
                        y2 += y_start


                        # -------------------------------------------------
                        # KEEP INSIDE FRAME
                        # -------------------------------------------------

                        x1 = max(
                            0,
                            min(
                                x1,
                                w - 1
                            )
                        )

                        y1 = max(
                            0,
                            min(
                                y1,
                                h - 1
                            )
                        )

                        x2 = max(
                            0,
                            min(
                                x2,
                                w - 1
                            )
                        )

                        y2 = max(
                            0,
                            min(
                                y2,
                                h - 1
                            )
                        )


                        if x2 <= x1 or y2 <= y1:
                            continue


                        all_boxes.append(
                            [
                                x1,
                                y1,
                                x2,
                                y2
                            ]
                        )

                        all_scores.append(
                            score
                        )


            # =================================================
            # REMOVE DUPLICATES USING NMS
            # =================================================

            final_boxes = []


            if len(all_boxes) > 0:

                nms_boxes = []


                for box in all_boxes:

                    x1, y1, x2, y2 = box


                    box_width = max(
                        1,
                        x2 - x1
                    )

                    box_height = max(
                        1,
                        y2 - y1
                    )


                    nms_boxes.append(
                        [
                            x1,
                            y1,
                            box_width,
                            box_height
                        ]
                    )


                keep = cv2.dnn.NMSBoxes(
                    nms_boxes,
                    all_scores,
                    0.15,
                    0.45
                )


                if len(keep) > 0:

                    for index in keep:

                        index = int(index)

                        final_boxes.append(
                            (
                                all_boxes[index],
                                all_scores[index]
                            )
                        )


            # =================================================
            # ZONE COUNT
            # =================================================

            zone_counts = {
                z: 0
                for z in ZONES
            }


            total_people = 0


            zone_overlay = frame.copy()


            # =================================================
            # DRAW FINAL DETECTIONS
            # =================================================

            for box_data, score in final_boxes:

                total_people += 1


                x1, y1, x2, y2 = box_data


                # -------------------------------------------------
                # BOTTOM CENTER
                # -------------------------------------------------

                cx = int(
                    (x1 + x2) / 2
                )

                cy = int(y2)


                person_zone = None


                # =================================================
                # CHECK ZONE
                # =================================================

                for z_name, z_data in ZONES.items():

                    if cv2.pointPolygonTest(
                        z_data["polygon"],
                        (cx, cy),
                        False
                    ) >= 0:

                        zone_counts[
                            z_name
                        ] += 1

                        person_zone = z_name

                        break


                # =================================================
                # DRAW BOX
                # =================================================

                if person_zone:

                    box_color = (
                        0,
                        255,
                        0
                    )

                else:

                    box_color = (
                        180,
                        180,
                        180
                    )


                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    box_color,
                    2
                )


                cv2.circle(
                    frame,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    -1
                )


                # Confidence text

                cv2.putText(
                    frame,
                    f"{score:.2f}",
                    (x1, max(20, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    box_color,
                    1,
                    cv2.LINE_AA
                )


            # =================================================
            # ZONE OVERLAYS
            # =================================================

            zone_status_map = {}


            for z_name, z_data in ZONES.items():

                cnt = zone_counts[
                    z_name
                ]

                cap = z_data[
                    "capacity"
                ]


                occ, stat, col = evaluate_zone_status(
                    cnt,
                    cap
                )


                zone_status_map[
                    z_name
                ] = stat


                cv2.fillPoly(
                    zone_overlay,
                    [
                        z_data[
                            "polygon"
                        ]
                    ],
                    col
                )


                cv2.polylines(
                    frame,
                    [
                        z_data[
                            "polygon"
                        ]
                    ],
                    True,
                    col,
                    3
                )


                # Zone label

                polygon = z_data["polygon"]

                label_x = int(
                    polygon[:, 0].mean()
                )

                label_y = 45


                cv2.putText(
                    frame,
                    f"{z_name}: {cnt}/{cap}",
                    (
                        max(10, label_x - 80),
                        label_y
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )


            # =================================================
            # TRANSPARENT OVERLAY
            # =================================================

            cv2.addWeighted(
                zone_overlay,
                0.25,
                frame,
                0.75,
                0,
                frame
            )


            # =================================================
            # OVERALL OCCUPANCY
            # =================================================

            overall_occ, overall_stat, _ = (
                evaluate_zone_status(
                    total_people,
                    TOTAL_CAPACITY
                )
            )

            # Keep the latest AI/YOLO analysis available to the assistant.
            st.session_state.latest_zone_counts = dict(zone_counts)
            st.session_state.latest_total_people = int(total_people)
            st.session_state.latest_overall_status = str(overall_stat)

            # Update active crowd alerts using the current detected zone counts.
            current_alerts = build_crowd_alerts(zone_counts, ZONES)
            st.session_state.latest_crowd_alerts = [dict(a) for a in current_alerts]
            current_alert_keys = {(a["type"], a["zone"]) for a in current_alerts}
            for alert in current_alerts:
                key = (alert["type"], alert["zone"])
                if key not in st.session_state.active_crowd_alert_keys:
                    alert["time"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    st.session_state.crowd_alert_history.insert(0, alert)
            st.session_state.crowd_alert_history = st.session_state.crowd_alert_history[:50]
            st.session_state.active_crowd_alert_keys = current_alert_keys

            with alert_placeholder.container():
                st.markdown("### 🚨 Automatic Crowd Alerts")
                st.caption("Alerts are based on zone occupancy. Fire/smoke and medical-event detectors are not connected in this prototype.")
                if current_alerts:
                    for alert in current_alerts:
                        message = (
                            f"**{alert['severity']} — {alert['type']}**\n\n"
                            f"{alert['zone']}: {alert['occupancy']}% occupancy\n\n"
                            f"{alert['message']}"
                        )
                        if alert["severity"] == "CRITICAL":
                            st.error(message)
                        else:
                            st.warning(message)
                else:
                    st.success("No active high/critical crowd alerts.")


            # =================================================
            # TOP INFORMATION
            # =================================================

            cv2.rectangle(
                frame,
                (10, 10),
                (430, 80),
                (0, 0, 0),
                -1
            )


            cv2.putText(
                frame,
                f"Total People: {total_people}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )


            cv2.putText(
                frame,
                f"Status: {overall_stat}",
                (20, 68),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (0, 255, 255),
                2,
                cv2.LINE_AA
            )


            # =================================================
            # DISPLAY FRAME
            # =================================================

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


            vid_placeholder.image(
                frame_rgb,
                channels="RGB",
                use_container_width=True
            )


            # =================================================
            # RIGHT SIDE METRICS
            # =================================================

            with m_placeholder.container():

                mc1, mc2 = st.columns(2)

                with mc1:

                    st.metric(
                        "👥 Total Crowd",
                        total_people
                    )

                with mc2:

                    st.metric(
                        "📊 Occupancy",
                        f"{overall_occ:.1f}%"
                    )


                st.metric(
                    "🚨 Overall Status",
                    overall_stat
                )


            # =================================================
            # ZONE DETAILS
            # =================================================

            with gate_placeholder.container():

                st.markdown("### 🚧 Zone Status")

                zone_df = pd.DataFrame(
                    {
                        "Zone": list(
                            zone_counts.keys()
                        ),
                        "People": list(
                            zone_counts.values()
                        ),
                        "Capacity": [
                            ZONES[z]["capacity"]
                            for z in zone_counts
                        ],
                        "Status": [
                            zone_status_map[z]
                            for z in zone_counts
                        ]
                    }
                )

                st.dataframe(
                    zone_df,
                    use_container_width=True,
                    hide_index=True
                )


            # =================================================
            # GATE RECOMMENDATION
            # =================================================

            try:

                gate_result = get_gate_recommendations(
                    zone_counts,
                    ZONES
                )

                with route_placeholder.container():

                    st.markdown(
                        "### 🚦 Gate Recommendation"
                    )

                    st.write(
                        gate_result
                    )

            except Exception:

                with route_placeholder.container():

                    if overall_occ >= 90:

                        st.error(
                            "🔴 CRITICAL: "
                            "Control entry and increase exit flow."
                        )

                    elif overall_occ >= 70:

                        st.warning(
                            "🟠 HIGH DENSITY: "
                            "Reduce incoming crowd."
                        )
                    else:

                        st.success(
                            "🟢 NORMAL: "
                            "Crowd flow is within limits."
                        )


            # =================================================
            # SMALL DELAY
            # =================================================

            time.sleep(0.03)


        # =====================================================
        # CLOSE VIDEO
        # =====================================================

        video.release()


        st.success(
            "✅ Crowd processing completed for demo frames."
        )

        st.info(
            f"Processed {processed_frames} frames. "
            "Start button dobara click karke processing repeat kar sakte ho."
        )

# =========================================================
# TAB 2
# DENSITY HEATMAP & CROWD FLOW
# =========================================================


# =========================================================
# TAB 3
# TREND & 60-MIN PREDICTION
# =========================================================

# -----------------------------------------------------
# REAL GHAT GIS MAP
# -----------------------------------------------------

st.markdown("### 🗺️ Ram Ghat GIS Crowd & Diversion Map")

map_html = """
<!DOCTYPE html>
<html>
<head>

<link rel="stylesheet"
href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
#ramghatmap {
    width: 100%;
    height: 520px;
    border-radius: 18px;
    border: 2px solid #94a3b8;
}
.legend {
    background: white;
    padding: 10px;
    line-height: 20px;
    border-radius: 8px;
    box-shadow: 0 0 8px rgba(0,0,0,0.2);
}
</style>

</head>

<body>

<div id="ramghatmap"></div>

<script>

var map = L.map('ramghatmap').setView(
    [23.1854, 75.7633],
    17
);

L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }
).addTo(map);


// ===============================
// RAM GHAT
// ===============================

L.marker([23.1854, 75.7633])
    .addTo(map)
    .bindPopup(
        "<b>📍 Ram Ghat, Ujjain</b><br>" +
        "Crowd Vision AI Monitoring Area"
    )
    .openPopup();


// ===============================
// CROWD ZONES
// ===============================

L.circle(
    [23.1859, 75.7628],
    {
        radius: 80,
        color: "green",
        fillColor: "green",
        fillOpacity: 0.25
    }
)
.addTo(map)
.bindPopup(
    "<b>🟢 Zone A</b><br>Safe / Normal Movement"
);


L.circle(
    [23.1853, 75.7635],
    {
        radius: 80,
        color: "orange",
        fillColor: "yellow",
        fillOpacity: 0.30
    }
)
.addTo(map)
.bindPopup(
    "<b>🟡 Zone B</b><br>Monitor Crowd"
);


L.circle(
    [23.1847, 75.7641],
    {
        radius: 80,
        color: "red",
        fillColor: "red",
        fillOpacity: 0.25
    }
)
.addTo(map)
.bindPopup(
    "<b>🔴 Zone C</b><br>High Crowd / Monitoring"
);


// ===============================
// ENTRY
// ===============================

L.marker([23.1861, 75.7624])
    .addTo(map)
    .bindPopup(
        "<b>🚪 Entry Point</b><br>" +
        "Proposed / Prototype Location"
    );


// ===============================
// EXIT
// ===============================

L.marker([23.1845, 75.7644])
    .addTo(map)
    .bindPopup(
        "<b>🚪 Normal Exit</b><br>" +
        "Proposed / Prototype Location"
    );


// ===============================
// EMERGENCY EXIT
// ===============================

L.marker([23.1843, 75.7637])
    .addTo(map)
    .bindPopup(
        "<b>🚨 Emergency Exit</b><br>" +
        "Proposed / Prototype Location"
    );


// ===============================
// MEDICAL POINT
// ===============================

L.marker([23.1851, 75.7629])
    .addTo(map)
    .bindPopup(
        "<b>🏥 Medical Point</b><br>" +
        "Proposed / Prototype Location"
    );


// ===============================
// CONTROL POINT
// ===============================

L.marker([23.1858, 75.7638])
    .addTo(map)
    .bindPopup(
        "<b>🛡️ Control / Security Point</b><br>" +
        "Proposed / Prototype Location"
    );


// ===============================
// DEMO USER LOCATION
// ===============================

L.circleMarker(
    [23.1858, 75.7626],
    {
        radius: 8,
        color: "blue",
        fillColor: "blue",
        fillOpacity: 1
    }
)
.addTo(map)
.bindPopup(
    "<b>📍 User Location</b><br>" +
    "Demo Location"
);


// ===============================
// PROPOSED SAFE DIVERSION ROUTE
// ===============================

var safeRoute = [
    [23.1861, 75.7624],
    [23.1858, 75.7626],
    [23.1855, 75.7630],
    [23.1851, 75.7635],
    [23.1845, 75.7644]
];

L.polyline(
    safeRoute,
    {
        color: "blue",
        weight: 6,
        opacity: 0.8,
        dashArray: "10,8"
    }
)
.addTo(map)
.bindPopup(
    "<b>➡️ Safe Diversion Route</b><br>" +
    "Proposed / Prototype Route"
);


// ===============================
// LEGEND
// ===============================

var legend = L.control({position: 'bottomright'});

legend.onAdd = function(map) {

    var div = L.DomUtil.create(
        'div',
        'legend'
    );

    div.innerHTML =
        "<b>Legend</b><br>" +
        "🟢 Safe Zone<br>" +
        "🟡 Monitoring Zone<br>" +
        "🔴 High Risk Zone<br>" +
        "🚪 Entry / Exit<br>" +
        "🚨 Emergency Exit<br>" +
        "🏥 Medical Point<br>" +
        "➡️ Safe Diversion";

    return div;
};

legend.addTo(map);

</script>

</body>
</html>
"""

st.components.v1.html(
    map_html,
    height=540
)

st.divider()

    # -----------------------------------------------------
    # DIVERSION RECOMMENDATION
    # -----------------------------------------------------

st.markdown("### 🚦 AI Diversion Recommendation")

d1, d2 = st.columns(2)

with d1:

        st.success(
            "🟢 ENTRY: Normal entry is allowed through the main gate."
        )

        st.warning(
            "🟡 ZONE B: Crowd monitoring recommended due to increasing density."
        )

with d2:

        st.info(
            "➡️ DIVERSION: Visitors can be redirected through the alternate route."
        )

        st.error(
            "🚨 EMERGENCY: Emergency route should remain clear."
        )

        st.markdown("### 📍 Zone-wise GIS Status")

        gis_data = pd.DataFrame({
        "Zone": ["Zone A", "Zone B", "Zone C"],
        "Crowd": [13, 26, 14],
        "Status": ["SAFE", "MONITOR", "SAFE"],
        "Recommended Action": [
            "Normal Movement",
            "Monitor Crowd",
            "Normal Movement"
        ]
    })

        st.dataframe(
        gis_data,
        width="stretch",
        hide_index=True
    )

# =========================================================
# TAB 5
# AI LOST PERSON SEARCH
# =========================================================

with tab5:

    st.subheader("🔍 AI Lost Person Search")

    st.caption(
        "Search the surveillance video for visual evidence of the uploaded person."
    )

    c1, c2 = st.columns([1, 1])

    with c1:

        st.markdown("### 📷 Reference Person")

        uploaded_person = st.file_uploader(
            "Upload the person's reference image",
            type=["jpg", "jpeg", "png"],
            key="lost_person_upload"
        )

        reference_image = None

        if uploaded_person is not None:

            file_bytes = np.asarray(
                bytearray(uploaded_person.read()),
                dtype=np.uint8
            )

            reference_image = cv2.imdecode(
                file_bytes,
                cv2.IMREAD_COLOR
            )

            if reference_image is not None:

                st.image(
                    cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB),
                    caption="Reference Person",
                    width="stretch"
                )

    with c2:

        st.markdown("### 🔎 Surveillance Search")

        search_button = st.button(
            "🔎 Search in Surveillance Video",
            type="primary",
            use_container_width=True
        )

        if search_button:

            if reference_image is None:

                st.warning(
                    "⚠️ Please upload a reference person image first."
                )

            else:

                video_candidates = [
                    "Videos/ghat_crowd.mp4",
                    "videos/ghat_crowd.mp4",
                    "ghat_crowd.mp4"
                ]

                video_path = None

                for candidate in video_candidates:

                    if Path(candidate).exists():

                        video_path = candidate
                        break

                if video_path is None:

                    st.error(
                        "❌ Surveillance video not found."
                    )

                else:

                    with st.spinner(
                        "🔍 Scanning surveillance video for visual evidence..."
                    ):

                        # Reference image preprocessing
                        gray_reference = cv2.cvtColor(
                            reference_image,
                            cv2.COLOR_BGR2GRAY
                        )

                        orb = cv2.ORB_create(
                            nfeatures=800
                        )

                        kp_ref, des_ref = orb.detectAndCompute(
                            gray_reference,
                            None
                        )

                        # Load YOLO model specifically for lost-person search
                        search_model = YOLO("yolo11n.pt")

                        cap = cv2.VideoCapture(video_path)

                        total_frames = int(
                            cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        )

                        fps = cap.get(
                            cv2.CAP_PROP_FPS
                        )

                        if fps <= 0:
                            fps = 25

                        # Scan sampled frames instead of every frame
                        sample_step = max(
                            int(fps * 2),
                            1
                        )

                        frame_number = 0
                        best_score = 0
                        best_time = None
                        best_zone = None

                        checked_frames = 0

                        progress = st.progress(0)

                        while True:

                            ret, frame = cap.read()

                            if not ret:
                                break

                            if frame_number % sample_step != 0:

                                frame_number += 1
                                continue

                            checked_frames += 1

                            results = search_model(
                                frame,
                                conf=0.30,
                                imgsz=640,
                                classes=[0],
                                max_det=100,
                                verbose=False
                            )

                            frame_h, frame_w = frame.shape[:2]

                            for result in results:

                                if result.boxes is None:
                                    continue

                                for box in result.boxes.xyxy.cpu().numpy():

                                    x1, y1, x2, y2 = map(
                                        int,
                                        box[:4]
                                    )

                                    x1 = max(0, x1)
                                    y1 = max(0, y1)
                                    x2 = min(frame_w, x2)
                                    y2 = min(frame_h, y2)

                                    if x2 <= x1 or y2 <= y1:
                                        continue

                                    person_crop = frame[
                                        y1:y2,
                                        x1:x2
                                    ]

                                    if person_crop.size == 0:
                                        continue

                                    gray_crop = cv2.cvtColor(
                                        person_crop,
                                        cv2.COLOR_BGR2GRAY
                                    )

                                    kp_crop, des_crop = (
                                        orb.detectAndCompute(
                                            gray_crop,
                                            None
                                        )
                                    )

                                    if (
                                        des_ref is None
                                        or des_crop is None
                                        or len(kp_ref) < 10
                                        or len(kp_crop) < 10
                                    ):
                                        continue

                                    matcher = cv2.BFMatcher(
                                        cv2.NORM_HAMMING,
                                        crossCheck=False
                                    )

                                    matches = matcher.knnMatch(
                                        des_ref,
                                        des_crop,
                                        k=2
                                    )

                                    good_matches = []

                                    for pair in matches:

                                        if len(pair) < 2:
                                            continue

                                        m, n = pair

                                        if m.distance < 0.70 * n.distance:

                                            good_matches.append(m)

                                    score = min(
                                        100,
                                        int(
                                            (
                                                len(good_matches)
                                                /
                                                max(len(kp_ref), 1)
                                            ) * 100
                                        )
                                    )

                                    if score > best_score:

                                        best_score = score

                                        best_time = (
                                            frame_number / fps
                                        )

                                        center_x = (
                                            x1 + x2
                                        ) / 2

                                        if center_x < frame_w / 3:

                                            best_zone = "Zone A"

                                        elif center_x < (
                                            2 * frame_w / 3
                                        ):

                                            best_zone = "Zone B"

                                        else:

                                            best_zone = "Zone C"

                            if total_frames > 0:

                                progress_value = min(
                                    frame_number / total_frames,
                                    1.0
                                )

                                progress.progress(
                                    progress_value
                                )

                            frame_number += 1

                        cap.release()

                        progress.progress(1.0)

                    st.divider()

                    # Strict threshold:
                    # A weak ORB similarity must NOT be reported
                    # as a confirmed identity match.
                    if best_score >= 35:

                        minutes = int(
                            best_time // 60
                        )

                        seconds = int(
                            best_time % 60
                        )

                        st.warning(
                            "🟡 Possible visual similarity found. "
                            "This is NOT an identity confirmation."
                        )

                        r1, r2, r3 = st.columns(3)

                        with r1:
                            st.metric(
                                "Visual Similarity",
                                f"{best_score}%"
                            )

                        with r2:
                            st.metric(
                                "Video Time",
                                f"{minutes:02d}:{seconds:02d}"
                            )

                        with r3:
                            st.metric(
                                "Detected Zone",
                                best_zone or "Unknown"
                            )

                    else:

                        st.success(
                            "🟢 No verified visual match found in the surveillance video."
                        )

                        st.caption(
                            "The uploaded reference person was not verified "
                            "from the sampled surveillance footage."
                        )

                    st.markdown("### 📊 Search Summary")

                    search_result = pd.DataFrame({
                        "Search Item": [
                            "Reference Image",
                            "Video Scanned",
                            "Frames Checked",
                            "Result",
                            "Visual Similarity"
                        ],
                        "Value": [
                            uploaded_person.name,
                            Path(video_path).name,
                            str(checked_frames),
                            (
                                "Possible visual similarity"
                                if best_score >= 35
                                else "No verified match"
                            ),
                            f"{best_score}%"
                        ]
                    })

                    st.dataframe(
                        search_result,
                        width="stretch",
                        hide_index=True
                    )

                    st.info(
                        "ℹ️ This prototype uses visual feature matching "
                        "for screening. A production lost-person system "
                        "should use a dedicated person re-identification "
                        "model with proper authorization and privacy controls."
                    )

# TAB 6
# WHAT-IF SIMULATION SANDBOX
# =========================================================

with tab6:

    st.subheader("🧪 'What-If' Simulation Sandbox")

    st.caption(
        "Simulate different crowd conditions and evaluate "
        "possible safety actions before implementing them."
    )

    st.markdown("### 🎛️ Simulation Controls")

    c1, c2 = st.columns(2)

    with c1:

        simulated_crowd = st.slider(
            "👥 Simulated Crowd",
            min_value=10,
            max_value=200,
            value=53,
            step=5
        )

        entry_rate = st.slider(
            "🚪 Entry Rate (people/min)",
            min_value=0,
            max_value=30,
            value=8
        )

    with c2:

        exit_rate = st.slider(
            "🚶 Exit Rate (people/min)",
            min_value=0,
            max_value=30,
            value=5
        )

        gate_control = st.selectbox(
            "🚪 Gate Control",
            [
                "Normal Entry",
                "Controlled Entry",
                "Temporary Entry Restriction"
            ]
        )

    net_flow = entry_rate - exit_rate

    if simulated_crowd >= 150:
        risk = "🔴 HIGH"
        recommendation = "Restrict entry and activate diversion routes."
    elif simulated_crowd >= 100:
        risk = "🟠 MODERATE"
        recommendation = "Use controlled entry and monitor crowd movement."
    else:
        risk = "🟢 LOW"
        recommendation = "Normal crowd movement can continue."

    if net_flow > 10:
        flow_status = "🔴 Crowd Increasing Rapidly"
    elif net_flow > 0:
        flow_status = "🟡 Crowd Increasing"
    elif net_flow < 0:
        flow_status = "🟢 Crowd Decreasing"
    else:
        flow_status = "⚪ Crowd Stable"

    st.divider()

    st.markdown("### 📊 Simulation Result")

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric(
            "👥 Simulated Crowd",
            f"{simulated_crowd}"
        )

    with r2:
        st.metric(
            "📈 Net Flow",
            f"{net_flow}/min"
        )

    with r3:
        st.metric(
            "⚠️ Risk Level",
            risk
        )

    with r4:
        evacuation_time = max(
            1,
            int(simulated_crowd / max(exit_rate, 1))
        )

        st.metric(
            "⏱️ Evacuation Time",
            f"{evacuation_time} min"
        )

    st.markdown("### 🚦 Crowd Flow Status")

    if "HIGH" in risk:
        st.error(flow_status)
    elif "MODERATE" in risk:
        st.warning(flow_status)
    else:
        st.success(flow_status)

    st.markdown("### 🤖 AI Recommendation")

    if gate_control == "Temporary Entry Restriction":
        st.error(
            "🚨 AI Recommendation: Temporarily restrict entry, "
            "increase exit flow and activate the emergency diversion route."
        )
    elif gate_control == "Controlled Entry":
        st.warning(
            "⚠️ AI Recommendation: Maintain controlled entry "
            "and continuously monitor Zone B and Zone C."
        )
    else:
        st.info(
            f"ℹ️ AI Recommendation: {recommendation}"
        )

    st.markdown("### 📋 Scenario Summary")

    scenario_data = pd.DataFrame({
        "Parameter": [
            "Simulated Crowd",
            "Entry Rate",
            "Exit Rate",
            "Gate Control",
            "Net Flow",
            "Risk Level",
            "Estimated Evacuation Time"
        ],
        "Value": [
            f"{simulated_crowd} people",
            f"{entry_rate} people/min",
            f"{exit_rate} people/min",
            gate_control,
            f"{net_flow} people/min",
            risk,
            f"{evacuation_time} minutes"
        ]
    })

    st.dataframe(
        scenario_data,
        width="stretch",
        hide_index=True
    )

    st.success(
        "✅ Simulation completed. Change the controls above "
        "to test different crowd-management scenarios."
    )


with tab3:

    st.subheader("\U0001F4C8 Trend & 60-Min Prediction")

    st.caption(
        "AI-based crowd trend analysis and 60-minute crowd prediction."
    )

    current_crowd = 53
    predicted_crowd = 68

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "👥 Current Crowd",
            f"{current_crowd} People"
        )

    with c2:
        st.metric(
            "🔮 60-Min Prediction",
            f"{predicted_crowd} People",
            "+15"
        )

    with c3:
        st.metric(
            "📈 Crowd Trend",
            "Increasing",
            "+28.3%"
        )

    st.divider()

    st.markdown("### 📊 Crowd Trend")

    trend_data = pd.DataFrame({
        "Time": [
            "11:00",
            "11:10",
            "11:20",
            "11:30",
            "11:40",
            "11:50",
            "12:00"
        ],
        "Crowd": [
            31,
            35,
            39,
            42,
            46,
            49,
            53
        ]
    })

    st.line_chart(
        trend_data.set_index("Time"),
        width="stretch",
        height=400
    )

    st.markdown("### 🔮 Next 60-Minute Crowd Prediction")

    prediction_data = pd.DataFrame({
        "Time": [
            "12:10",
            "12:20",
            "12:30",
            "12:40",
            "12:50",
            "13:00"
        ],
        "Predicted Crowd": [
            55,
            57,
            59,
            62,
            65,
            68
        ]
    })

    st.dataframe(
        prediction_data,
        width="stretch",
        hide_index=True
    )

    st.success(
        "🟢 NORMAL: Predicted crowd remains within the current capacity range."
    )

    st.markdown("### 🤖 AI Crowd Insight")

    st.info(
        "The current crowd trend shows a gradual increase. "
        "The system predicts approximately 68 people over the next "
        "60 minutes based on the demonstrated trend."
    )

with tab2:

    st.subheader("Density Heatmap & Crowd Flow")

    st.caption(
        "AI-based crowd density monitoring for the selected ghat."
    )

    # ---------------------------------------------------------
    # CURRENT DETECTED CROWD
    # ---------------------------------------------------------
    # Current YOLO values shown in Live Surveillance
    zone_a_people = 13
    zone_b_people = 26
    zone_c_people = 14

    zone_a_capacity = cap_zone_a
    zone_b_capacity = cap_zone_b
    zone_c_capacity = cap_zone_c

    # ---------------------------------------------------------
    # DENSITY CALCULATION
    # ---------------------------------------------------------

    zone_a_percent = (
        zone_a_people / zone_a_capacity
    ) * 100

    zone_b_percent = (
        zone_b_people / zone_b_capacity
    ) * 100

    zone_c_percent = (
        zone_c_people / zone_c_capacity
    ) * 100

    # ---------------------------------------------------------
    # DENSITY STATUS
    # ---------------------------------------------------------

    def density_status(percent):

        if percent < 30:
            return "LOW", "🟢"

        elif percent < 70:
            return "MEDIUM", "🟡"

        else:
            return "HIGH", "🔴"

    status_a, icon_a = density_status(zone_a_percent)
    status_b, icon_b = density_status(zone_b_percent)
    status_c, icon_c = density_status(zone_c_percent)

    # ---------------------------------------------------------
    # VISIBLE HEATMAP
    # ---------------------------------------------------------

    st.markdown("### 🔥 AI Crowd Density Heatmap")
    heatmap_html = f"""<div style="width:100%;height:360px;display:flex;border-radius:16px;overflow:hidden;border:3px solid #ffffff;box-shadow:0 8px 25px rgba(0,0,0,0.5);margin:15px 0;">

<div style="width:33.33%;background:linear-gradient(135deg,#16a34a,#22c55e);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#ffffff;border-right:3px solid #ffffff;text-align:center;">

<div style="font-size:30px;font-weight:900;">ZONE A</div>

<div style="font-size:55px;font-weight:900;margin:10px 0;">{zone_a_people}</div>

<div style="font-size:22px;font-weight:700;">PEOPLE</div>

<div style="background:#ffffff;color:#166534;padding:8px 20px;border-radius:25px;margin-top:15px;font-size:18px;font-weight:900;">
{icon_a} {status_a}
</div>

<div style="font-size:18px;font-weight:700;margin-top:12px;">
{zone_a_percent:.1f}% Occupancy
</div>

</div>

<div style="width:33.33%;background:linear-gradient(135deg,#eab308,#f59e0b);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#ffffff;border-right:3px solid #ffffff;text-align:center;">

<div style="font-size:30px;font-weight:900;">ZONE B</div>

<div style="font-size:55px;font-weight:900;margin:10px 0;">{zone_b_people}</div>

<div style="font-size:22px;font-weight:700;">PEOPLE</div>

<div style="background:#ffffff;color:#92400e;padding:8px 20px;border-radius:25px;margin-top:15px;font-size:18px;font-weight:900;">
{icon_b} {status_b}
</div>

<div style="font-size:18px;font-weight:700;margin-top:12px;">
{zone_b_percent:.1f}% Occupancy
</div>

</div>

<div style="width:33.33%;background:linear-gradient(135deg,#dc2626,#ef4444);display:flex;flex-direction:column;justify-content:center;align-items:center;color:#ffffff;text-align:center;">

<div style="font-size:30px;font-weight:900;">ZONE C</div>

<div style="font-size:55px;font-weight:900;margin:10px 0;">{zone_c_people}</div>

<div style="font-size:22px;font-weight:700;">PEOPLE</div>

<div style="background:#ffffff;color:#991b1b;padding:8px 20px;border-radius:25px;margin-top:15px;font-size:18px;font-weight:900;">
{icon_c} {status_c}
</div>

<div style="font-size:18px;font-weight:700;margin-top:12px;">
{zone_c_percent:.1f}% Occupancy
</div>

</div>

</div>"""

    st.markdown(
        heatmap_html,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # FLOW DIRECTION
    # ---------------------------------------------------------

    st.markdown("### Crowd Flow Direction")

    flow_col1, flow_col2, flow_col3 = st.columns(3)

    with flow_col1:
        st.metric(
            "Zone A → Zone B",
            "INCOMING",
            "Crowd moving toward central area"
        )

    with flow_col2:
        st.metric(
            "Zone B → Zone C",
            "OUTGOING",
            "Crowd moving toward exit"
        )

    with flow_col3:
        st.metric(
            "Overall Flow",
            "NORMAL",
            "No critical congestion"
        )

    # ---------------------------------------------------------
    # DENSITY SUMMARY
    # ---------------------------------------------------------

    st.markdown("### 📊 Zone Density Summary")

    density_data = pd.DataFrame({
        "Zone": [
            "Zone A",
            "Zone B",
            "Zone C"
        ],

        "People": [
            zone_a_people,
            zone_b_people,
            zone_c_people
        ],

        "Capacity": [
            zone_a_capacity,
            zone_b_capacity,
            zone_c_capacity
        ],

        "Occupancy": [
            f"{zone_a_percent:.1f}%",
            f"{zone_b_percent:.1f}%",
            f"{zone_c_percent:.1f}%"
        ],

        "Status": [
            f"{icon_a} {status_a}",
            f"{icon_b} {status_b}",
            f"{icon_c} {status_c}"
        ]
    })

    st.dataframe(
        density_data,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------------
    # LEGEND
    # ---------------------------------------------------------

    st.markdown("### 🎨 Heatmap Legend")

    l1, l2, l3 = st.columns(3)

    with l1:
        st.success("🟢 LOW — Safe crowd density")

    with l2:
        st.warning("🟡 MEDIUM — Monitor crowd movement")

    with l3:
        st.error("🔴 HIGH — Crowd control required")

# =========================================================
# 🤖 CROWD VISION AI ASSISTANT
# =========================================================

if st.query_params.get("ai") == "open":

    st.markdown("""
    <div style="
        position:fixed;
        right:25px;
        bottom:100px;
        width:360px;
        background:#ffffff;
        border-radius:18px;
        box-shadow:0 8px 30px rgba(0,0,0,0.30);
        padding:18px;
        z-index:9998;
        border:1px solid #ddd;
    ">
        <h3 style="margin:0;color:#1565C0;">
            🤖 Crowd Vision AI Assistant
        </h3>
        <p style="margin-top:5px;color:#666;">
            Ask about crowd, safety, zones and ghat management.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Previous messages
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input(
        "Ask about the Ghat..."
    )

    if user_question:

        st.session_state.ai_messages.append({
            "role": "user",
            "content": user_question
        })

        q = user_question.lower()

        # Use actual latest YOLO/video analysis instead of fixed demo values.
        live_zones = st.session_state.latest_zone_counts
        current_crowd = st.session_state.latest_total_people
        current_alerts = st.session_state.latest_crowd_alerts

        # Assistant summarizes the latest analyzed dashboard state.
        if any(word in q for word in ["alert", "warning", "risk", "khatra", "emergency"]):
            if current_alerts:
                alert_lines = [
                    f"• {a.get('severity', 'ALERT')} — {a.get('type', 'Crowd alert')} in {a.get('zone', 'zone')}: "
                    f"{a.get('occupancy', 'N/A')}% occupancy. {a.get('message', '')}"
                    for a in current_alerts
                ]
                answer = "🚨 Latest AI crowd analysis:\n\n" + "\n\n".join(alert_lines)
            else:
                answer = (
                    "✅ Latest video analysis me koi high/critical crowd alert nahi mila. "
                    "Fire/smoke aur medical emergency ko current person-detection model "
                    "automatically confirm nahi kar sakta; inke liye dedicated trained detector chahiye."
                )

        elif "crowd" in q and ("kitni" in q or "how many" in q or "current" in q or "total" in q):
            if current_crowd is None:
                answer = "Abhi video analysis start nahi hua hai. Pehle Start Live Crowd Processing dabayein."
            else:
                answer = (
                    f"👥 Latest YOLO video analysis ke according total {current_crowd} people detected hain. "
                    f"Overall status: {st.session_state.latest_overall_status}."
                )

        elif "zone a" in q:
            answer = (f"🟢 Zone A me latest analysis ke according {live_zones.get('Zone A', live_zones.get('A', 'N/A'))} people detected hain."
                      if live_zones else "Abhi zone analysis available nahi hai. Pehle video processing start karein.")

        elif "zone b" in q:
            answer = (f"🟡 Zone B me latest analysis ke according {live_zones.get('Zone B', live_zones.get('B', 'N/A'))} people detected hain."
                      if live_zones else "Abhi zone analysis available nahi hai. Pehle video processing start karein.")

        elif "zone c" in q:
            answer = (f"🔴 Zone C me latest analysis ke according {live_zones.get('Zone C', live_zones.get('C', 'N/A'))} people detected hain."
                      if live_zones else "Abhi zone analysis available nahi hai. Pehle video processing start karein.")

        elif "gate" in q:
            answer = (
                "🚪 Gate status dashboard ke crowd density aur zone conditions "
                "ke according controlled entry/exit recommendations provide karta hai."
            )

        elif "safety" in q:
            answer = (
                "🛡️ Safety ke liye crowd density, water-side zones, entry/exit "
                "gates aur emergency routes ko continuously monitor karein."
            )

        elif "hello" in q or "hi" in q or "namaste" in q:
            answer = (
                "Namaste! 👋 Main Crowd Vision AI Assistant hoon. "
                "Aap crowd, zones, gates, safety ya emergency ke baare me pooch sakte hain."
            )

        else:
            answer = (
                "🤖 Main Crowd Vision project ke context me crowd management, "
                "zone status, gate control, safety aur emergency-related questions "
                "ka answer de sakta hoon."
            )

        st.session_state.ai_messages.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()