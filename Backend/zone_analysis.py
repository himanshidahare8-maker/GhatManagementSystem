zones = {
    "Zone A": 150,
    "Zone B": 200,
    "Zone C": 100
}

zone_people = {
    "Zone A": 90,
    "Zone B": 185,
    "Zone C": 70
}

for zone in zones:

    capacity = zones[zone]
    people = zone_people[zone]

    occupancy = (people / capacity) * 100

    if occupancy < 50:
        status = "LOW"
    elif occupancy < 75:
        status = "MODERATE"
    elif occupancy < 90:
        status = "HIGH"
    else:
        status = "CRITICAL"

    print("----------------------------")
    print(zone)
    print("Capacity:", capacity)
    print("People:", people)
    print("Occupancy:", round(occupancy, 1), "%")
    print("Status:", status)