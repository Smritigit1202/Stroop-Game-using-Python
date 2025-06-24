import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not detected by OpenCV.")
else:
    print("✅ Camera opened successfully. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame from camera.")
            break

        cv2.imshow("Camera Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
