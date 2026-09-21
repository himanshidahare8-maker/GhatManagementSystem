"""
GhatNetra AI - Decision Support & Recommendation Engine
Developed for SIH 2026 - MPSTDC Problem Statement
"""

def evaluate_zone_status(people_count, capacity):
    """
    Zone ke people count aur capacity ke hisab se occupancy aur status calculate karta hai.
    """
    if capacity <= 0:
        return 0.0, "UNKNOWN", (200, 200, 200)

    occupancy = (people_count / capacity) * 100

    if occupancy < 50:
        status = "LOW"
        color_bgr = (0, 255, 0)       # Green (Safe)
    elif occupancy < 75:
        status = "MODERATE"
        color_bgr = (0, 255, 255)     # Yellow (Caution)
    elif occupancy < 90:
        status = "HIGH"
        color_bgr = (0, 140, 255)     # Orange (Warning)
    else:
        status = "CRITICAL"
        color_bgr = (0, 0, 255)       # Red (Danger / Stampede Risk)

    return round(occupancy, 1), status, color_bgr


def get_gate_recommendations(overall_occupancy, zone_statuses):
    """
    Occupancy ke hisab se entry/exit gate recommendations generate karta hai.
    """
    if overall_occupancy < 60:
        gate_1 = "OPEN (Normal Entry: 120/min)"
        gate_1_state = "OPEN"
        gate_2 = "OPEN (Normal Exit)"
        alternate_route = "No diversion needed. All pathways clear."
        resource_action = "Routine patrolling by local volunteers."
    elif overall_occupancy < 75:
        gate_1 = "CONTROLLED (Regulated Entry: 60/min)"
        gate_1_state = "CONTROLLED"
        gate_2 = "OPEN (Unrestricted Exit)"
        alternate_route = "Advise incoming pilgrims to proceed to Narsingh Ghat."
        resource_action = "Deploy 2 additional police officers at Entry Gate 1."
    elif overall_occupancy < 90:
        gate_1 = "RESTRICTED (Staggered Entry: 20/min)"
        gate_1_state = "RESTRICTED"
        gate_2 = "OPEN (Priority Exit Channel Active)"
        alternate_route = "Divert incoming crowd towards Dutt Akhara Ghat."
        resource_action = "Place movable barricades at Alleyway B. Alert SDRF boat team."
    else:
        gate_1 = "CLOSED (Emergency Restriction)"
        gate_1_state = "CLOSED"
        gate_2 = "WIDE OPEN (Emergency Phased Evacuation)"
        alternate_route = "CRITICAL: Direct all foot traffic away from Ram Ghat to Narsingh Ghat."
        resource_action = "Sound PA siren. Deploy quick response NDRF team and SDRF divers."

    return {
        "gate_1": gate_1,
        "gate_1_state": gate_1_state,
        "gate_2": gate_2,
        "alternate_route": alternate_route,
        "resource_action": resource_action
    }


def calculate_evacuation_time(total_people, exit_width_meters=4.0, flow_rate_per_meter=1.3):
    """
    Physics-based Evacuation Clearance Time Model:
    Formula: Time (minutes) = Total People / (Exit Width in meters * Flow Rate persons/meter/sec * 60)
    Standard safety flow rate on stairs/slopes = 1.3 persons per meter width per second.
    """
    if exit_width_meters <= 0:
        return 0
    throughput_per_sec = exit_width_meters * flow_rate_per_meter
    throughput_per_min = throughput_per_sec * 60
    evac_minutes = total_people / throughput_per_min
    return round(evac_minutes, 1)
