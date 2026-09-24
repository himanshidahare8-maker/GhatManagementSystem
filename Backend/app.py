"""
GhatNetra AI (घाट-नेत्र) - MPSTDC AI Ghat Crowd Management & Decision Support System
Smart India Hackathon 2026 - Comprehensive 22-Feature Prototype
Author: SIH Team
"""

import streamlit as st
import cv2
import numpy as np
import time
import pandas as pd
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
# CUSTOM STYLING
# =========================================================

st.markdown("""
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

.main-header h1,
.main-header h2,
.main-header p {
    word-break: normal !important;
    overflow-wrap: normal !important;
    white-space: normal !important;
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
""", unsafe_allow_html=True)



# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Emblem_of_Madhya_Pradesh.svg/200px-Emblem_of_Madhya_Pradesh.svg.png",
    width=80
)# =========================================================
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
    cap_zone_a
    + cap_zone_b
    + cap_zone_c
)


# =========================================================
# FULL FRAME ZONES
# VIDEO SIZE = 2320 x 1080
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

    c_left, c_right = st.columns(
        [7, 5]
    )


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

        st.success("Start Button Clicked!")
        st.write("Crowd processing start ho rhi hai...")

        # -------------------------------------------------
        # LOAD YOLO MODEL
        # -------------------------------------------------

        model = YOLO(
            "yolo11s.pt"
        )


        # -------------------------------------------------
        # OPEN VIDEO
        # -------------------------------------------------

        video = cv2.VideoCapture(
            "videos/ghat_crowd.mp4"
        )


        # Check video
        if not video.isOpened():

            st.error(
                "❌ Video file open nahi ho rahi. "
                "Check karo: videos/ghat_crowd.mp4"
            )

            st.stop()


        frame_idx = 0


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


            # -------------------------------------------------
            # FRAME SIZE
            # -------------------------------------------------

            h, w = frame.shape[:2]


            frame_idx += 1


            # =================================================
            # 4-TILE YOLO DETECTION
            # =================================================

            all_boxes = []

            all_scores = []


            # 15% overlap
            overlap = 0.15


            # Divide frame into 2 x 2
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


                    # =================================================
                    # YOLO ON TILE
                    # =================================================

                    tile_results = model(
                        tile,

                        conf=0.10,

                        imgsz=1280,

                        classes=[0],

                        max_det=1000,

                        verbose=False
                    )


                    # =================================================
                    # READ DETECTIONS
                    # =================================================

                    for box in tile_results[0].boxes:

                        x1, y1, x2, y2 = map(
                            int,
                            box.xyxy[0]
                        )


                        score = float(
                            box.conf[0]
                        )


                        # -------------------------------------------------
                        # CONVERT TILE COORDINATES
                        # TO FULL FRAME COORDINATES
                        # -------------------------------------------------

                        x1 += x_start
                        x2 += x_start

                        y1 += y_start
                        y2 += y_start


                        # -------------------------------------------------
                        # KEEP BOX INSIDE FRAME
                        # -------------------------------------------------

                        x1 = max(
                            0,
                            min(x1, w - 1)
                        )

                        y1 = max(
                            0,
                            min(y1, h - 1)
                        )

                        x2 = max(
                            0,
                            min(x2, w - 1)
                        )

                        y2 = max(
                            0,
                            min(y2, h - 1)
                        )


                        # -------------------------------------------------
                        # SAVE BOX
                        # -------------------------------------------------

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
            # REMOVE DUPLICATE DETECTIONS
            # =================================================

            final_boxes = []


            if len(all_boxes) > 0:

                # -------------------------------------------------
                # IMPORTANT:
                # NMSBoxes expects:
                # [x, y, width, height]
                # NOT [x1, y1, x2, y2]
                # -------------------------------------------------

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


                # -------------------------------------------------
                # NMS
                # -------------------------------------------------

                keep = cv2.dnn.NMSBoxes(
                    nms_boxes,
                    all_scores,
                    0.10,
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
                # BOTTOM CENTER POINT
                # -------------------------------------------------

                cx = int(
                    (x1 + x2) / 2
                )


                cy = int(
                    y2
                )


                person_zone = None


                # =================================================
                # CHECK WHICH ZONE
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
                # BOX COLOR
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


                # =================================================
                # DRAW BOUNDING BOX
                # =================================================

                cv2.rectangle(
                    frame,

                    (x1, y1),

                    (x2, y2),

                    box_color,

                    2
                )


                # =================================================
                # DRAW CENTER POINT
                # =================================================

                cv2.circle(
                    frame,

                    (cx, cy),

                    5,

                    (0, 0, 255),

                    -1
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


                # -------------------------------------------------
                # EVALUATE ZONE
                # -------------------------------------------------

                occ, stat, col = evaluate_zone_status(
                    cnt,
                    cap
                )


                zone_status_map[
                    z_name
                ] = stat


                # -------------------------------------------------
                # FILL ZONE
                # -------------------------------------------------

                cv2.fillPoly(
                    zone_overlay,

                    [
                        z_data[
                            "polygon"
                        ]
                    ],

                    col
                )


                # -------------------------------------------------
                # ZONE BORDER
                # -------------------------------------------------

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


            # =================================================
            # APPLY TRANSPARENT ZONE OVERLAY
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
            # DECISION ENG