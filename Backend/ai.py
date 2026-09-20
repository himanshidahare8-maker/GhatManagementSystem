from ultralytics import YOLO
import cv2

# YOLO model load
model = YOLO("yolo11n.pt")

# Video path
video_path = "../Videos/ghat_video.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Video open nahi ho rahi!")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Video finished.")
        break

    # YOLO detection
    results = model(frame)

    # Detected objects ke around boxes draw
    annotated_frame = results[0].plot()

    cv2.imshow("Ghat AI - Person Detection", annotated_frame)

    # Q press karke video close
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()