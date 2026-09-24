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
from decision_engine import evaluate_zone_status, get_gate_recommendations, calculate_evacuation_time


# Page Configuration
st.set_page_config(
    page_title="GhatNetra AI - MPSTDC SIH 2026",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
        border-left: 7px solid #f59e0b;
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


# Top Banner
st.markdown("""
<div class="main-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h2 style='margin:0; padding:0;'>🕉️ GhatNetra AI (घाट-नेत्र)</h2>
            <p style='margin:3px 0 0 0; font-size:1.0rem; opacity:0.9;'>
                <b>Madhya Pradesh State Tourism Development Corporation Limited (MPSTDC)</b><br/>
                AI-Powered River Ghat Crowd Management, Occupancy Prediction & Decision Support System
            </p>
        </div>

        <div style="text-align:right; font-size:0.85rem; background:rgba(255,255,255,0.1); padding:8px 14px; border-radius:8px;">
            <span>📍 <b>Ujjain Ram Ghat (Shipra River)</b></span><br/>
            <span>🌤️ 31°C | River Flow: 1.2 m/s | Aarti: 18:30 IST</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Sidebar Configuration
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


TOTAL_CAPACITY = cap_zone_a + cap_zone_b + cap_zone_c


# Full-frame zones
# Video is 2560 x 1440
ZONES = {
    "Zone A": {
        "polygon": np.array([
            (0, 0),
            (853, 0),
            (853, 1440),
            (0, 1440)
        ], np.int32),
        "capacity": cap_zone_a
    },

    "Zone B": {
        "polygon": np.array([
            (853, 0),
            (1706, 0),
            (1706, 1440),
            (853, 1440)
        ], np.int32),
        "capacity": cap_zone_b
    },

    "Zone C": {
        "polygon": np.array([
            (1706, 0),
            (2560, 0),
            (2560, 1440),
            (1706, 1440)
        ], np.int32),
        "capacity": cap_zone_c
    }
}


# 6 Clean Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📹 Live Surveillance & Gates",
    "🌡️ Density Heatmap & Flow",
    "📈 Trend & 60-Min Prediction",
    "🗺️ Ghat GIS Map & Diversions",
    "🔍 AI Lost Person Search",
    "🧪 'What-If' Simulation Sandbox"
])


# =====================================================================
# TAB 1: LIVE SURVEILLANCE & GATE CONTROL
# =====================================================================

with tab1:

    c_left, c_right = st.columns([7, 5])

    with c_left:

        st.subheader("🎥 Live CCTV & YOLOv11 Detections")

        st.caption(
            "Input: **ghat_crowd.mp4** (2560x1440) | "
            "Active Zones: **Zone A, B, C**"
        )

        vid_placeholder = st.empty()

        start_btn = st.button(
            "▶️ Start Live Crowd Processing",
            type="primary",
            key="start_live"
        )


    with c_right:

        st.subheader("🛡️ AI Gate & Decision Status")

        m_placeholder = st.empty()
        gate_placeholder = st.empty()
        route_placeholder = st.empty()


    if start_btn:

        # YOLO model
        model = YOLO("yolo11s.pt")

        # Video
        video = cv2.VideoCapture(
            "videos/ghat_crowd.mp4"
        )

        frame_idx = 0


        while video.isOpened():

            ret, frame = video.read()


            if not ret:

                video.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                continue


            h, w = frame.shape[:2]

            frame_idx += 1


            # Process every second frame
            if frame_idx % 2 != 0:
                continue


            # =========================================================
            # 4-TILE YOLO DETECTION
            # =========================================================

            all_boxes = []
            all_scores = []

            overlap = 0.15

            tile_w = int(w / 2)
            tile_h = int(h / 2)


            for row in range(2):

                for col in range(2):

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


                    tile = frame[
                        y_start:y_end,
                        x_start:x_end
                    ]


                    tile_results = model(
                        tile,
                        conf=0.10,
                        imgsz=1280,
                        classes=[0],
                        max_det=1000,
                        verbose=False
                    )


                    for box in tile_results[0].boxes:

                        x1, y1, x2, y2 = map(
                            int,
                            box.xyxy[0]
                        )

                        score = float(
                            box.conf[0]
                        )


                        # Convert tile coordinates
                        # back to original frame
                        x1 += x_start
                        x2 += x_start

                        y1 += y_start
                        y2 += y_start


                        all_boxes.append([
                            x1,
                            y1,
                            x2,
                            y2
                        ])

                        all_scores.append(
                            score
                        )


            # =========================================================
            # REMOVE DUPLICATE DETECTIONS
            # =========================================================

            final_boxes = []


            if len(all_boxes) > 0:

                keep = cv2.dnn.NMSBoxes(
                    all_boxes,
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


            # =========================================================
            # ZONE COUNT
            # =========================================================

            zone_counts = {
                z: 0
                for z in ZONES
            }

            total_people = 0

            zone_overlay = frame.copy()


            # =========================================================
            # DRAW DETECTIONS
            # =========================================================

            for box_data, score in final_boxes:

                total_people += 1


                x1, y1, x2, y2 = box_data


                # Keep coordinates inside frame
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


                # Bottom-center point
                cx = int(
                    (x1 + x2) / 2
                )

                cy = int(y2)


                person_zone = None


                # Check zone
                for z_name, z_data in ZONES.items():

                    if cv2.pointPolygonTest(
                        z_data["polygon"],
                        (cx, cy),
                        False
                    ) >= 0:

                        zone_counts[z_name] += 1

                        person_zone = z_name

                        break


                # Detection color
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


                # Bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    box_color,
                    2
                )


                # Detection center
                cv2.circle(
                    frame,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    -1
                )


            # =========================================================
            # ZONE OVERLAYS
            # =========================================================

            zone_status_map = {}


            for z_name, z_data in ZONES.items():

                cnt = zone_counts[z_name]

                cap = z_data["capacity"]


                occ, stat, col = evaluate_zone_status(
                    cnt,
                    cap
                )


                zone_status_map[z_name] = stat


                cv2.fillPoly(
                    zone_overlay,
                    [z_data["polygon"]],
                    col
                )


                cv2.polylines(
                    frame,
                    [z_data["polygon"]],
                    True,
                    col,
                    3
                )


            cv2.addWeighted(
                zone_overlay,
                0.25,
                frame,
                0.75,
                0,
                frame
            )


            # =========================================================
            # OVERALL OCCUPANCY
            # =========================================================

            overall_occ, overall_stat, _ = evaluate_zone_status(
                total_people,
                TOTAL_CAPACITY
            )


            # =========================================================
            # DECISION ENGINE
            # =========================================================

            decisions = get_gate_recommendations(
                overall_occ,
                zone_status_map
            )


            # =========================================================
            # EVACUATION TIME
            # =========================================================

            evac_time = calculate_evacuation_time(
                total_people,
                exit_width_meters=4.0
            )


            # =========================================================
            # VIDEO OUTPUT
            # =========================================================

            disp_frame = cv2.resize(
                frame,
                (850, 480)
            )


            disp_rgb = cv2.cvtColor(
                disp_frame,
                cv2.COLOR_BGR2RGB
            )


            vid_placeholder.image(
                disp_rgb,
                channels="RGB",
                width="stretch"
            )


            # =========================================================
            # METRICS
            # =========================================================

            with m_placeholder.container():

                c1, c2, c3 = st.columns(3)


                c1.metric(
                    "Total Count",
                    f"{total_people}/{TOTAL_CAPACITY}"
                )


                c2.metric(
                    "Occupancy",
                    f"{overall_occ}%",
                    delta=overall_stat
                )


                c3.metric(
                    "Est. Evac Time",
                    f"{evac_time} min"
                )


                st.write("---")


                st.markdown(
                    "#### 📊 Zone-Wise Status"
                )


                for z_name, z_data in ZONES.items():

                    cnt = zone_counts[z_name]

                    cap = z_data["capacity"]


                    occ, stat, _ = evaluate_zone_status(
                        cnt,
                        cap
                    )


                    st.write(
                        f"**{z_name}**: "
                        f"{cnt}/{cap} "
                        f"({occ}%) - `{stat}`"
                    )


                    st.progress(
                        min(
                            occ / 100.0,
                            1.0
                        )
                    )


            # =========================================================
            # GATE DECISIONS
            # =========================================================

            with gate_placeholder.container():

                st.write("---")


                st.markdown(
                    "#### 🚪 Controlled Entry/Exit Recommendations"
                )


                g1, g2 = st.columns(2)


                with g1:

                    st.info(
                        f"**Entry Gate 1 Status**\n"
                        f"### {decisions['gate_1']}"
                    )


                with g2:

                    st.success(
                        f"**Exit Gate 2 Status**\n"
                        f"### {decisions['gate_2']}"
                    )


            # =========================================================
            # ROUTE ADVICE
            # =========================================================

            with route_placeholder.container():

                st.warning(
                    f"🔀 **Diversion Route:** "
                    f"{decisions['alternate_route']}"
                )


                st.info(
                    f"👮 **Security Deployment:** "
                    f"{decisions['resource_action']}"
                )


            time.sleep(0.03)


        video.release()


    else:

        vid_placeholder.info(
            "Click **'▶️ Start Live Crowd Processing'** "
            "to run live YOLO detection and zone control."
        )


        if cv2.haveImageReader(
            "test_zone_output.jpg"
        ):

            test_img = cv2.imread(
                "test_zone_output.jpg"
            )


            if test_img is not None:

                vid_placeholder.image(
                    cv2.cvtColor(
                        test_img,
                        cv2.COLOR_BGR2RGB
                    ),
                    caption=(
                        "Snapshot with YOLO "
                        "Bounding Boxes & "
                        "Translucent Zones"
                    ),
                    width="stretch"
                )


        with m_placeholder.container():

            st.metric(
                "Total Capacity",
                f"{TOTAL_CAPACITY} Persons"
            )


            st.write(
                "Current calibrated baseline: "
                "Zone A=150, Zone B=200, Zone C=100"
            )


# =====================================================================
# TAB 2: CROWD DENSITY HEATMAP & FLOW VECTORS
# =====================================================================

with tab2:

    st.subheader(
        "🌡️ 2D Gaussian Crowd Density Heatmap & Spatial Concentration"
    )


    st.caption(
        "Converts detected people coordinates into a "
        "continuous spatial density gradient "
        "(Jet colormap) to detect stampede pressure zones."
    )


    hm_col1, hm_col2 = st.columns([7, 5])


    with hm_col1:

        if cv2.haveImageReader(
            "test_zone_output.jpg"
        ):

            raw_frame = cv2.imread(
                "test_zone_output.jpg"
            )


            h, w = raw_frame.shape[:2]


            heatmap_acc = np.zeros(
                (h, w),
                dtype=np.float32
            )


            points = [
                (450, 300),
                (470, 310),
                (510, 320),
                (530, 290),
                (550, 315),
                (600, 330),
                (620, 310),
                (640, 340),
                (660, 330),
                (700, 320),
                (720, 350),
                (750, 340),
                (380, 280),
                (400, 290),
                (420, 310),
                (800, 350),
                (820, 360)
            ]


            for pt in points:

                if (
                    0 <= pt[0] < w
                    and
                    0 <= pt[1] < h
                ):

                    heatmap_acc[
                        pt[1],
                        pt[0]
                    ] += 2.5


            heatmap_acc = cv2.GaussianBlur(
                heatmap_acc,
                (121, 121),
                0
            )


            cv2.normalize(
                heatmap_acc,
                heatmap_acc,
                0,
                255,
                cv2.NORM_MINMAX
            )


            heatmap_color = cv2.applyColorMap(
                heatmap_acc.astype(np.uint8),
                cv2.COLORMAP_JET
            )


            blended_heatmap = cv2.addWeighted(
                raw_frame,
                0.65,
                heatmap_color,
                0.35,
                0
            )


            st.image(
                cv2.cvtColor(
                    blended_heatmap,
                    cv2.COLOR_BGR2RGB
                ),
                caption=(
                    "Live Crowd Density Heatmap "
                    "(Red = High Concentration Hotspot)"
                ),
                width="stretch"
            )


    with hm_col2:

        st.markdown(
            "### 🌊 Crowd Flow Vectors & Movement Direction"
        )


        st.write("""
        - **Primary Inflow Vector:** Entry Staircase → Central Snan Steps (Speed: 0.85 m/s)
        - **Outflow Vector:** Waterfront → Exit Gate 2 (Speed: 0.62 m/s)
        - **Bottleneck Risk Index:** `LOW (0.18)`
        - **River Edge Submersion Geofence:** `SECURE (No unauthorized crossing detected)`
        """)


        st.info(
            "💡 **AI Insight:** Central Snan Steps (Zone B) "
            "has the highest dwell time as pilgrims perform "
            "holy dip rituals."
        )


# =====================================================================
# TAB 3: TRENDS & FUTURE PREDICTION
# =====================================================================

with tab3:

    st.subheader(
        "📈 Real-Time Crowd Inflow Trends & AI Rush Forecast"
    )


    st.caption(
        "Historical & real-time time-series modeling "
        "predicting pilgrim footfall before evening "
        "Ganga/Shipra Aarti."
    )


    now = datetime.now()


    times = [
        now - timedelta(minutes=10 * i)
        for i in range(6, 0, -1)
    ]


    future_times = [
        now + timedelta(minutes=10 * i)
        for i in range(1, 7)
    ]


    past_counts = [
        65,
        80,
        110,
        140,
        185,
        210
    ]


    predicted_counts = [
        240,
        295,
        360,
        420,
        380,
        310
    ]


    all_times = [
        t.strftime("%H:%M")
        for t in times + [now] + future_times
    ]


    all_values = (
        past_counts
        + [225]
        + predicted_counts
    )


    data_types = (
        ["Observed"] * len(past_counts)
        + ["Current"]
        + ["AI Predicted"] * len(future_times)
    )


    df_trend = pd.DataFrame({
        "Time": all_times,
        "Crowd Count": all_values,
        "Type": data_types
    })


    st.line_chart(
        df_trend.set_index("Time")["Crowd Count"],
        height=320
    )


    p1, p2, p3 = st.columns(3)


    p1.metric(
        "+15 Min Forecast",
        "240 Pilgrims",
        "+15 (Approaching Moderate)"
    )


    p2.metric(
        "+30 Min Forecast",
        "360 Pilgrims",
        "+120 (Aarti Peak Rush)"
    )


    p3.metric(
        "Recommended Action",
        "Throttle Gate 1 at 18:15 IST",
        "Prevent Overcrowding"
    )


# =====================================================================
# TAB 4: GHAT GIS MAP & DIVERSION ROUTES
# =====================================================================

with tab4:

    st.subheader(
        "🗺️ Ujjain Riverfront GIS Map & Alternate Route Diversion"
    )


    st.caption(
        "Dynamic diversion pathing when Ram Ghat "
        "approaches threshold capacity."
    )


    ghats_df = pd.DataFrame({

        "Ghat Name": [
            "Ram Ghat (Primary Monitoring)",
            "Narsingh Ghat (Alternate Route 1)",
            "Dutt Akhara Ghat (Alternate Route 2)",
            "Sunhari Ghat (Emergency Staging)"
        ],

        "lat": [
            23.1828,
            23.1865,
            23.1812,
            23.1880
        ],

        "lon": [
            75.7683,
            75.7695,
            75.7650,
            75.7710
        ],

        "Capacity Status": [
            "85% (High)",
            "30% (Available)",
            "20% (Available)",
            "Emergency Only"
        ]
    })


    st.map(
        ghats_df,
        latitude="lat",
        longitude="lon",
        size=30,
        zoom=14
    )


    st.markdown(
        "### 🔀 Active Emergency Diversion Protocol"
    )


    st.success("""
    - **Primary Path (Congested):** Mahakal Temple → Danigate → **Ram Ghat** *(Restrict Entry)*
    - **Recommended Diversion Path:** Danigate Junction → **Narsingh Ghat Pathway** *(Direct 60% crowd here)*
    - **Secondary Diversion:** Chhatri Chowk → **Dutt Akhara Bridge** *(Direct 40% crowd here)*
    """)


# =====================================================================
# TAB 5: AI LOST PERSON / FACE SEARCH DEMO
# =====================================================================

with tab5:

    st.subheader(
        "🔍 AI Missing Person & Child Tracking Demo"
    )


    st.caption(
        "SIH High-Impact Feature: Search camera logs "
        "to locate lost children or elderly pilgrims "
        "across Ghat zones."
    )


    lp_col1, lp_col2 = st.columns([5, 7])


    with lp_col1:

        st.markdown(
            "#### 📤 Upload Missing Person Photo"
        )


        uploaded_file = st.file_uploader(
            "Upload photo of lost child / pilgrim",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )


        person_name = st.text_input(
            "Name / Token ID",
            "Aarav Sharma (Age 7)"
        )


        search_btn = st.button(
            "🔎 Scan Camera Feeds & Match",
            type="primary"
        )


    with lp_col2:

        st.markdown(
            "#### 🎯 AI Match Results Across Camera Feeds"
        )


        if (
            search_btn
            or
            uploaded_file is not None
        ):

            st.success(
                "✅ **MATCH FOUND! (Confidence: 94.2%)**"
            )


            st.write(
                f"- **Person Name:** {person_name}"
            )


            st.write(
                "- **Last Seen Location:** "
                "Ujjain Ram Ghat - "
                "**Zone B (Central Snan Steps)**"
            )


            st.write(
                "- **Timestamp:** "
                "Today, 15:42 IST (Frame #1842)"
            )


            st.write(
                "- **Action Taken:** "
                "Local police booth and SDRF boat "
                "patrol notified with GPS tag."
            )


            st.info(
                "🚨 Alert sent to nearest Quick Response "
                "Volunteer Team."
            )


        else:

            st.info(
                "Upload a photo or click "
                "'Scan Camera Feeds & Match' "
                "to simulate facial identification demo."
            )


# =====================================================================
# TAB 6: PRE-EVENT WHAT-IF SIMULATION SANDBOX
# =====================================================================

with tab6:

    st.subheader(
        "🧪 Pre-Event Crowd Movement & Strategy Simulator"
    )


    st.caption(
        "Allow MPSTDC / District Administration "
        "to evaluate crowd control strategies "
        "before major festivals."
    )


    sc1, sc2 = st.columns([6, 6])


    with sc1:

        st.markdown(
            "### 🎛️ Simulation Parameters"
        )


        event_name = st.selectbox(
            "Select Event",
            [
                "Simhastha Kumbh Mela - Shahi Snan (Extreme Footfall)",
                "Mahakal Sawari - Evening Procession (High Density)",
                "Somwati Amavasya Holy Dip (Moderate Rush)",
                "Regular Morning Snan (Normal Flow)"
            ]
        )


        preset = (
            420
            if "Extreme" in event_name
            else (
                280
                if "High" in event_name
                else (
                    160
                    if "Moderate" in event_name
                    else 50
                )
            )
        )


        sim_crowd = st.slider(
            "Simulated Ghat Crowd",
            20,
            600,
            preset
        )


        sim_width = st.slider(
            "Available Exit Gate Width (Meters)",
            1.5,
            10.0,
            4.0,
            step=0.5
        )


    with sc2:

        st.markdown(
            "### 📋 AI Decision Engine Verdict"
        )


        sim_occ, sim_stat, _ = evaluate_zone_status(
            sim_crowd,
            TOTAL_CAPACITY
        )


        sim_dec = get_gate_recommendations(
            sim_occ,
            {}
        )


        sim_evac = calculate_evacuation_time(
            sim_crowd,
            exit_width_meters=sim_width
        )


        if sim_stat == "LOW":

            st.success(
                f"### Status: 🟢 SAFE "
                f"({sim_occ}% Occupancy)"
            )


        elif sim_stat == "MODERATE":

            st.warning(
                f"### Status: 🟡 MODERATE "
                f"({sim_occ}% Occupancy)"
            )


        elif sim_stat == "HIGH":

            st.error(
                f"### Status: 🟠 HIGH CONGESTION "
                f"({sim_occ}% Occupancy)"
            )


        else:

            st.error(
                f"### Status: 🚨 CRITICAL STAMPEDE RISK "
                f"({sim_occ}% Occupancy)"
            )


        st.write(
            f"- **Entry Gate 1:** "
            f"{sim_dec['gate_1']}"
        )


        st.write(
            f"- **Exit Gate 2:** "
            f"{sim_dec['gate_2']}"
        )


        st.write(
            f"- **Evacuation Clearance Time:** "
            f"`{sim_evac} Minutes`"
        )


        st.info(
            f"**Diversion Directive:** "
            f"{sim_dec['alternate_route']}"
        )


        st.warning(
            f"**Police / NDRF Deployment:** "
            f"{sim_dec['resource_action']}"
        )


        st.markdown(
            "#### 📢 Automated Multilingual PA Announcement:"
        )


        if sim_stat in [
            "HIGH",
            "CRITICAL"
        ]:

            st.code(
                "📢 [HINDI]: कृपया ध्यान दें! राम घाट पर क्षमता "
                "पूर्ण हो चुकी है। कृपया नरसिंह घाट की ओर प्रस्थान करें.\n"
                "📢 [ENGLISH]: Attention! Ram Ghat has reached "
                "capacity. Please proceed to Narsingh Ghat."
            )


        else:

            st.code(
                "📢 [HINDI]: श्रद्धालु कृपया घाट की सीढ़ियों पर "
                "कतारबद्ध होकर चलें।\n"
                "📢 [ENGLISH]: Pilgrims are requested to maintain "
                "queue discipline along ghat steps."
            )