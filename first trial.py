import cv2
import time
import pyttsx3
import threading
from ultralytics import YOLO

# ----------------------------
# Load YOLOv8 Model
# ----------------------------
model = YOLO("yolov8n.pt")

# ----------------------------
# Text to Speech
# ----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak_warning():
    engine.say("Please drop the mobile phone and focus on driving.")
    engine.runAndWait()

def speak_warning_thread():
    threading.Thread(target=speak_warning, daemon=True).start()

# ----------------------------
# Camera
# ----------------------------
cap = cv2.VideoCapture(0)

# ----------------------------
# Variables
# ----------------------------
phone_detected = False
phone_hold_start = None
warning_given = False
phone_usage_count = 0

HOLD_THRESHOLD = 30      # 30 seconds (0.5 min)
GRACE_PERIOD = 2         # seconds allowed if detection is lost
last_seen_time = None

# ----------------------------
# Main Loop
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()

    # ---------------- YOLO Detection ----------------
    results = model(frame)
    detected_this_frame = False

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls.item())
            class_name = model.names[class_id]
            confidence = float(box.conf.item())

            # Only detect strong phone predictions
            if class_name == "cell phone" and confidence > 0.6:
                detected_this_frame = True
                last_seen_time = current_time

                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 0, 255), 2)

                cv2.putText(frame,
                            f"Phone {confidence:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2)

    # ---------------- Stable Timer Logic ----------------
    if detected_this_frame:
        if not phone_detected:
            phone_detected = True
            phone_hold_start = current_time
            warning_given = False
        else:
            duration = current_time - phone_hold_start

            cv2.putText(frame,
                        f"Holding Time: {int(duration)} sec",
                        (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 0, 255),
                        2)

            if duration >= HOLD_THRESHOLD and not warning_given:
                speak_warning_thread()
                warning_given = True

    else:
        # Allow small detection loss (grace period)
        if last_seen_time is not None and (current_time - last_seen_time) < GRACE_PERIOD:
            pass
        else:
            if phone_detected:
                phone_usage_count += 1
                print("Phone Usage Count:", phone_usage_count)

            phone_detected = False
            phone_hold_start = None
            warning_given = False

    # ---------------- Display Usage Count ----------------
    cv2.putText(frame,
                f"Total Phone Uses: {phone_usage_count}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2)

    cv2.imshow("Driver Phone Detection", frame)

    # Exit with ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# ----------------------------
# Save Count for Dashboard
# ----------------------------
with open("phone_usage.txt", "w") as f:
    f.write(str(phone_usage_count))

cap.release()
cv2.destroyAllWindows()