"""
GhatNetra AI - Executive Modern Light-Theme Diagram Generator
Designed for SISTec Innovation Hackathon (SIH) 2026
Clean, minimalist, executive aesthetic (White/Slate background, Crisp Navy, Vibrant Blue/Amber/Emerald)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['figure.autolayout'] = True

def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(13.333, 6.2), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    # Header
    ax.text(6.5, 6.0, "SYSTEM ARCHITECTURE PIPELINE", fontsize=16, fontweight='bold', color='#0f172a', ha='center')
    ax.text(6.5, 5.65, "From Multi-Modal Input to AI Vision, Decision Engine & Command Dispatch", fontsize=10, color='#64748b', ha='center')

    layers = [
        {"num": "LAYER 01", "title": "Sensing & Data Ingestion", "border": "#3b82f6", "bg": "#eff6ff", "x": 0.5, "w": 2.6,
         "items": ["CCTV Feed (crowd.mp4)", "Ghat Topography & Steps", "Sacred Aarti Schedules", "Exit Gate Width Data"]},
        {"num": "LAYER 02", "title": "AI Computer Vision", "border": "#8b5cf6", "bg": "#f5f3ff", "x": 3.6, "w": 2.6,
         "items": ["Ultralytics YOLOv11 nano", "Ground Feet Points (cx, cy)", "cv2.pointPolygonTest", "Dynamic Zone A, B, C Counts"]},
        {"num": "LAYER 03", "title": "Decision Support Engine", "border": "#f59e0b", "bg": "#fffbeb", "x": 6.7, "w": 2.6,
         "items": ["Occupancy % vs Capacity", "Entry Flow Throttling", "Physics Evacuation Model", "Alternate Route Diversion"]},
        {"num": "LAYER 04", "title": "Command & Citizen Action", "border": "#10b981", "bg": "#f0fdf4", "x": 9.8, "w": 2.6,
         "items": ["Streamlit Command Center", "Gate 1 & 2 Live States", "Bilingual PA Audio Siren", "NDRF & Police Dispatch"]}
    ]

    for lay in layers:
        # Layer Container Card
        card = patches.FancyBboxPatch((lay["x"], 0.6), lay["w"], 4.6,
                                      boxstyle="round,pad=0.15",
                                      facecolor=lay["bg"], edgecolor=lay["border"], linewidth=2)
        ax.add_patch(card)

        # Layer Number Badge
        ax.text(lay["x"] + lay["w"]/2, 4.85, lay["num"], fontsize=8.5, fontweight='bold', color=lay["border"], ha='center')
        ax.text(lay["x"] + lay["w"]/2, 4.5, lay["title"], fontsize=11, fontweight='bold', color='#0f172a', ha='center')

        y_pos = 3.8
        for item in lay["items"]:
            ibox = patches.FancyBboxPatch((lay["x"] + 0.15, y_pos - 0.3), lay["w"] - 0.3, 0.58,
                                         boxstyle="round,pad=0.08",
                                         facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1)
            ax.add_patch(ibox)
            ax.text(lay["x"] + lay["w"]/2, y_pos, item, fontsize=8.5, fontweight='bold', color='#334155', ha='center', va='center')
            y_pos -= 0.85

    # Connecting Flow Arrows
    arrow_props = dict(facecolor='#3b82f6', edgecolor='#2563eb', width=3, headwidth=9, headlength=7)
    ax.annotate('', xy=(3.6, 2.8), xytext=(3.1, 2.8), arrowprops=arrow_props)
    ax.annotate('', xy=(6.7, 2.8), xytext=(6.2, 2.8), arrowprops=arrow_props)
    ax.annotate('', xy=(9.8, 2.8), xytext=(9.3, 2.8), arrowprops=arrow_props)

    plt.tight_layout()
    plt.savefig("system_architecture.png", dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print("[SUCCESS] Modern system_architecture.png generated.")

def generate_decision_flowchart():
    fig, ax = plt.subplots(figsize=(13.333, 6.2), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    ax.text(6.5, 6.0, "DECISION SUPPORT & GATE REGULATION LOGIC", fontsize=16, fontweight='bold', color='#0f172a', ha='center')
    ax.text(6.5, 5.65, "Automated Inflow Throttling & Pre-Emptive Stampede Prevention", fontsize=10, color='#64748b', ha='center')

    # Pipeline Steps on Left
    steps = [
        {"title": "1. Frame Ingestion", "desc": "Pre-recorded CCTV\n(crowd.mp4 2560x1440)", "x": 0.5, "w": 2.0, "color": "#2563eb"},
        {"title": "2. YOLO Detection", "desc": "Class 0 (Person)\nExtract Feet (cx, cy)", "x": 2.9, "w": 2.0, "color": "#7c3aed"},
        {"title": "3. Spatial Zoning", "desc": "cv2.pointPolygonTest\nZone A, B, C Counts", "x": 5.3, "w": 2.0, "color": "#059669"},
        {"title": "4. Occupancy Math", "desc": "Occ = (People/Cap)*100\nDynamic Status Check", "x": 7.7, "w": 2.0, "color": "#d97706"}
    ]

    for s in steps:
        box = patches.FancyBboxPatch((s["x"], 2.2), s["w"], 1.8,
                                     boxstyle="round,pad=0.1",
                                     facecolor='#f8fafc', edgecolor=s["color"], linewidth=2)
        ax.add_patch(box)
        ax.text(s["x"] + s["w"]/2, 3.5, s["title"], fontsize=9.5, fontweight='bold', color=s["color"], ha='center')
        ax.text(s["x"] + s["w"]/2, 2.8, s["desc"], fontsize=8, color='#334155', ha='center')

    # Horizontal arrows
    arrow_props = dict(facecolor='#64748b', edgecolor='#475569', width=2, headwidth=7, headlength=6)
    ax.annotate('', xy=(2.9, 3.1), xytext=(2.5, 3.1), arrowprops=arrow_props)
    ax.annotate('', xy=(5.3, 3.1), xytext=(4.9, 3.1), arrowprops=arrow_props)
    ax.annotate('', xy=(7.7, 3.1), xytext=(7.3, 3.1), arrowprops=arrow_props)

    # 4 Decision Branches on Right
    branches = [
        {"cond": "Occupancy < 60%", "gate": "Gate 1: OPEN (120/min)\nGate 2: Normal Exit\nRoute: Pathways Clear", "y": 4.6, "col": "#16a34a", "bg": "#f0fdf4"},
        {"cond": "60% <= Occ < 75%", "gate": "Gate 1: CONTROLLED (60/min)\nGate 2: Unrestricted Exit\nRoute: Queue Caution", "y": 3.3, "col": "#ca8a04", "bg": "#fefce8"},
        {"cond": "75% <= Occ < 90%", "gate": "Gate 1: RESTRICTED (20/min)\nGate 2: Priority Exit\nRoute: Divert to Narsingh Ghat", "y": 2.0, "col": "#ea580c", "bg": "#fff7ed"},
        {"cond": "Occupancy >= 90%", "gate": "Gate 1: CLOSED (Emergency)\nGate 2: Evacuation Mode\nRoute: Siren + NDRF Boats", "y": 0.7, "col": "#dc2626", "bg": "#fef2f2"}
    ]

    for br in branches:
        cbox = patches.FancyBboxPatch((10.1, br["y"]), 2.6, 1.05,
                                      boxstyle="round,pad=0.08",
                                      facecolor=br["bg"], edgecolor=br["col"], linewidth=1.8)
        ax.add_patch(cbox)
        ax.text(10.2, br["y"] + 0.8, f"[{br['cond']}]", fontsize=8.5, fontweight='bold', color=br["col"])
        ax.text(10.2, br["y"] + 0.38, br["gate"], fontsize=7.5, color='#1e293b')

        ax.annotate('', xy=(10.1, br["y"] + 0.52), xytext=(9.7, 3.1),
                    arrowprops=dict(facecolor=br["col"], edgecolor=br["col"], width=1.5, headwidth=6, headlength=5))

    plt.tight_layout()
    plt.savefig("decision_flowchart.png", dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print("[SUCCESS] Modern decision_flowchart.png generated.")

def generate_ghat_zones_layout():
    fig, ax = plt.subplots(figsize=(13.333, 6.2), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    ax.text(6.5, 6.0, "UJJAIN RAM GHAT (SHIPRA RIVER) - 3-ZONE SPATIAL MAPPING", fontsize=16, fontweight='bold', color='#0f172a', ha='center')
    ax.text(6.5, 5.65, "Functional Segmentation & River Danger Geofencing", fontsize=10, color='#64748b', ha='center')

    # Zone A
    rect_a = patches.FancyBboxPatch((0.8, 1.2), 3.4, 4.0, boxstyle="round,pad=0.1",
                                   facecolor='#ecfdf5', edgecolor='#10b981', linewidth=2)
    ax.add_patch(rect_a)
    ax.text(2.5, 4.6, "ZONE A (UPPER STEPS)", fontsize=11, fontweight='bold', color='#065f46', ha='center')
    ax.text(2.5, 4.25, "Entrance Channel & Queue Line", fontsize=8.5, color='#047857', ha='center')
    ax.text(2.5, 2.7, "• Main Inflow from Danigate\n• Gate 1 Throttling Point\n• Capacity: 150 Pilgrims\n• Queue Density Monitoring\n• Bottleneck Early Warning", fontsize=8.5, color='#1f2937', ha='center')

    # Zone B
    rect_b = patches.FancyBboxPatch((4.8, 1.2), 3.6, 4.0, boxstyle="round,pad=0.1",
                                   facecolor='#fffbeb', edgecolor='#f59e0b', linewidth=2)
    ax.add_patch(rect_b)
    ax.text(6.6, 4.6, "ZONE B (CENTRAL SNAN)", fontsize=11, fontweight='bold', color='#92400e', ha='center')
    ax.text(6.6, 4.25, "Holy Dip & Ritual Platforms", fontsize=8.5, color='#b45309', ha='center')
    ax.text(6.6, 2.7, "• Sacred Bathing Steps\n• Highest Visitor Dwell Time\n• Capacity: 200 Pilgrims\n• Crowd Pressure Hotspot\n• Automated Divert Trigger", fontsize=8.5, color='#1f2937', ha='center')

    # Zone C
    rect_c = patches.FancyBboxPatch((9.0, 1.2), 3.4, 4.0, boxstyle="round,pad=0.1",
                                   facecolor='#eff6ff', edgecolor='#3b82f6', linewidth=2)
    ax.add_patch(rect_c)
    ax.text(10.7, 4.6, "ZONE C (WATERFRONT EXIT)", fontsize=11, fontweight='bold', color='#1e40af', ha='center')
    ax.text(10.7, 4.25, "Exit Staircase & River Edge", fontsize=8.5, color='#1d4ed8', ha='center')
    ax.text(10.7, 2.7, "• Outflow to Exit Gate 2\n• Capacity: 100 Pilgrims\n• Emergency Evacuation Route\n• SDRF Rescue Boat Patrol\n• River Edge Drowning Guard", fontsize=8.5, color='#1f2937', ha='center')

    # Danger River Line
    ax.plot([0.5, 12.5], [0.85, 0.85], color='#dc2626', linestyle='--', linewidth=2.5)
    ax.text(6.5, 0.5, "⚠️ RIVER WATERLINE DANGER GEOFENCE (SHIPRA RIVER DEEP WATER CURRENT)", fontsize=9.5, fontweight='bold', color='#dc2626', ha='center')

    plt.tight_layout()
    plt.savefig("ghat_zones_layout.png", dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print("[SUCCESS] Modern ghat_zones_layout.png generated.")

if __name__ == "__main__":
    generate_system_architecture()
    generate_decision_flowchart()
    generate_ghat_zones_layout()
