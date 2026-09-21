from ultralytics import YOLO
import cv2

# YOLO model load
model = YOLO("yolo11n.pt")

# Crowd video open
video = cv2.VideoCapture("videos/crowd.mp4")

# Demo capacity
capacity = 500

while video.isOpened():

    ret, frame = video.read()

    if not ret:
        break

    # YOLO detection
    results = model(frame, verbose=False)

    # People count
    person_count = 0

    for box in results[0].boxes:

        class_id = int(box.cls[0])

        # Class 0 = person
        if class_id == 0:
            person_count += 1

    # Draw detection boxes
    output = results[0].plot()

    # Calculate occupancy
    occupancy = (person_count / capacity) * 100

    # Crowd status + recommendation
    if occupancy < 50:
        status = "LOW"
        recommendation = "Normal monitoring"

    elif occupancy < 75:
        status = "MODERATE"
        recommendation = "Continue monitoring crowd movement"

    elif occupancy < 90:
        status = "HIGH"
        recommendation = "Reduce entry rate and monitor exits"

    else:
        status = "CRITICAL"
        recommendation = "Restrict entry and redirect visitors"

    # People count
    cv2.putText(
        output,
        f"People Detected: {person_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Occupancy
    cv2.putText(
        output,
        f"Occupancy: {occupancy:.1f}%",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Status
    cv2.putText(
        output,
        f"Status: {status}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Recommendation
    cv2.putText(
        output,
        f"Action: {recommendation}",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    # Show video
    cv2.imshow("Crowd Detection", output)

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()