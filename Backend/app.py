"""
GhatNetra AI (घाट-नेत्र)
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

from decision_engine import (
    evaluate_zone_status,
    get_gate_recommendations,
    calculate_evacuation_time
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GhatNetra AI - MPSTDC SIH 2026",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
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

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Emblem_of_Madhya_Pradesh.svg/200px-Emblem_of_Madhya_Pradesh.svg.png",
    width=80
)

st.sidebar.title("🎛️ Command Controls")


selected_ghat = st.sidebar.selectbox(
    "📍 Select Ghat Location",
    [
        "Ujjain - Ram Ghat (Shipra River)",
        "Ujjain - Narsingh Ghat (Shipra River)",
        "Omkareshwar - Nagar Ghat (Narmada River)",
        "Maheshwar - Ahilya Ghat (Narmada River)",
        "Narmadapuram - Sethani Ghat (Narmada River)"
    ]
)


st.sidebar.subheader("📐 Zone Capacity Limits")

cap_zone_a = st.sidebar.slider(
    "Zone A (Entry Steps)",
    50,
    300,
    150
)

cap_zone_b = st.sidebar.slider(
    "Zone B (Central Snan)",
    50,
    400,
    200
)

cap_zone_c = st.sidebar.slider(
    "Zone C (Waterfront/Exit)",
    50,
    200,
    100
)


TOTAL_CAPACITY = (
    cap_zone_a +
    cap_zone_b +
    cap_zone_c
)


# =========================================================
# TOP BANNER
# =========================================================

st.title("🕉️ GhatNetra AI (घाट-नेत्र)")

st.subheader(
    "Madhya Pradesh State Tourism Development Corporation Limited (MPSTDC)"
)

st.write(
    "AI-Powered River Ghat Crowd Management, "
    "Occupancy Prediction & Decision Support System"
)

c1, c2 = st.columns(2)

with c1:
    st.write("📍 **Ujjain Ram Ghat (Shipra River)**")

with c2:
    st.write(
        "🌤️ 31°C  |  River Flow: 1.2 m/s  |  Aarti: 18:30 IST"
    )

st.divider()


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
        "📹 Live Surveillance & Gates",
        "🌡️ Density Heatmap & Flow",
        "📈 Trend & 60-Min Prediction",
        "🗺️ Ghat GIS Map & Diversions",
        "🔍 AI Lost Person Search",
        "🧪 'What-If' Simulation Sandbox"
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
            "▶️ Start Live Crowd Processing",
            type="primary",
            key="start_live"
        )


    # =====================================================
    # RIGHT SIDE
    # =====================================================

    with c_right:

        st.subheader(
            "🛡️ AI Gate & Decision Status"
        )

        m_placeholder = st.empty()

        gate_placeholder = st.empty()

        route_placeholder = st.empty()


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
                f"❌ YOLO model not found:\n\n"
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
                "❌ Video file nahi mili."
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
                "❌ YOLO model load nahi hua."
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
                f"❌ Video open nahi ho rahi:\n{VIDEO_PATH}"
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
                        conf=0.15,
                        imgsz=640,
                        classes=[0],
                        max_det=500,
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
# DENSITY HEATMAP & FLOW
# =========================================================

with tab2:

    st.subheader(
        "🌡️ Density Heatmap & Crowd Flow"
    )

    st.write(
        "AI-based crowd density monitoring for the selected ghat."
    )

    heatmap_data = np.random.randint(
        10,
        100,
        (10, 15)
    )

    st.image(
        heatmap_data,
        caption="Simulated Crowd Density Heatmap",
        use_container_width=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🔵 Low Density Zones",
            "15"
        )

    with c2:
        st.metric(
            "🟡 Medium Density Zones",
            "20"
        )

    with c3:
        st.metric(
            "🔴 High Density Zones",
            "15"
        )


# =========================================================
# TAB 3
# TREND & 60-MIN PREDICTION
# =========================================================

with tab3:

    st.subheader(
        "📈 Crowd Trend & 60-Min Prediction"
    )

    current_time = datetime.now()

    times = [
        current_time + timedelta(minutes=i)
        for i in range(0, 61, 5)
    ]

    base_crowd = 120

    predicted = [
        base_crowd + int(
            i * 3 +
            10 * np.sin(i / 3)
        )
        for i in range(len(times))
    ]

    trend_df = pd.DataFrame(
        {
            "Time": times,
            "Predicted Crowd": predicted
        }
    )

    st.line_chart(
        trend_df.set_index("Time")
    )

    st.info(
        "Prediction is a prototype visualization for the SIH demonstration."
    )


# =========================================================
# TAB 4
# GIS MAP & DIVERSIONS
# =========================================================

with tab4:

    st.subheader(
        "🗺️ Ghat GIS Map & Diversions"
    )

    st.write(
        f"Selected Location: **{selected_ghat}**"
    )

    map_df = pd.DataFrame(
        {
            "lat": [
                23.1765,
                23.1770,
                23.1760,
                23.1775
            ],
            "lon": [
                75.7885,
                75.7890,
                75.7878,
                75.7895
            ]
        }
    )

    st.map(
        map_df,
        latitude="lat",
        longitude="lon",
        size=80
    )

    st.markdown("### 🚧 Diversion Recommendations")

    st.success(
        "🟢 Route 1: Normal flow"
    )

    st.warning(
        "🟡 Route 2: Monitor crowd density"
    )

    st.info(
        "🔵 Emergency evacuation route available"
    )


# =========================================================
# TAB 5
# AI LOST PERSON SEARCH
# =========================================================

with tab5:

    st.subheader(
        "🔍 AI Lost Person Search"
    )

    st.write(
        "Upload a reference image for the prototype lost-person search workflow."
    )

    uploaded_image = st.file_uploader(
        "Upload Person Image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if uploaded_image is not None:

        st.image(
            uploaded_image,
            caption="Uploaded Reference Image",
            use_container_width=False
        )

        st.success(
            "✅ Reference image received."
        )

        st.info(
            "AI matching module can be connected to CCTV embeddings "
            "or a face/person re-identification model."
        )


# =========================================================
# TAB 6
# WHAT-IF SIMULATION
# =========================================================

with tab6:

    st.subheader(
        "🧪 'What-If' Simulation Sandbox"
    )

    st.write(
        "Adjust crowd parameters to simulate different scenarios."
    )

    sim_crowd = st.slider(
        "👥 Simulated Crowd",
        0,
        1000,
        300
    )

    sim_capacity = st.slider(
        "📐 Total Capacity",
        100,
        1500,
        TOTAL_CAPACITY
    )

    sim_water = st.slider(
        "🌊 River Flow",
        0.1,
        5.0,
        1.2
    )

    simulated_occupancy = (
        sim_crowd / sim_capacity
    ) * 100


    st.markdown("### 📊 Simulation Result")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Simulated Crowd",
            sim_crowd
        )

    with c2:

        st.metric(
            "Occupancy",
            f"{simulated_occupancy:.1f}%"
        )

    with c3:

        st.metric(
            "River Flow",
            f"{sim_water:.1f} m/s"
        )


    if simulated_occupancy >= 90:

        st.error(
            "🔴 CRITICAL: Controlled entry and emergency preparedness required."
        )

    elif simulated_occupancy >= 70:

        st.warning(
            "🟠 HIGH: Reduce incoming crowd and monitor gates."
        )

    elif simulated_occupancy >= 40:

        st.info(
            "🟡 MODERATE: Continue active monitoring."
        )

    else:

        st.success(
            "🟢 LOW: Normal crowd conditions."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "GhatNetra AI (घाट-नेत्र) | "
    "MPSTDC | Smart India Hackathon 2026 | "
    "AI-Powered Ghat Crowd Management Prototype"
)