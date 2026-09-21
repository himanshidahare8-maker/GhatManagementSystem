import cv2

video_path = "../Videos\crowd.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Video open nahi ho rahi!")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Video finished.")
        break

    cv2.imshow("Ghat CCTV Video", frame)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()