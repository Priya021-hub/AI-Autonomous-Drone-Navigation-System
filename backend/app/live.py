
import cv2
import time
import os

from ultralytics import YOLO

from app.services.path_planning import PathPlanner

# -----------------------------------
# REDUCE YOLO LOGS
# -----------------------------------

os.environ["YOLO_VERBOSE"] = "False"

# -----------------------------------
# LOAD YOLO MODEL
# -----------------------------------

model = YOLO("yolov8n.pt")

# -----------------------------------
# OPEN WEBCAM
# -----------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Camera not detected")
    exit()

# -----------------------------------
# FPS TIMER
# -----------------------------------

prev_time = 0

# -----------------------------------
# MAIN LOOP
# -----------------------------------

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # FRAME SIZE

    h, w, _ = frame.shape

    # GRID CELL SIZE

    cell_width = w // 10
    cell_height = h // 10

    # RUN YOLO

    results = model(frame, verbose=False)

    detected_objects = []

    # -----------------------------------
    # PRIORITY VARIABLES
    # -----------------------------------

    highest_area = 0

    priority_object = "NONE"

    priority_direction = "SAFE"

    priority_action = "MOVE FORWARD"

    priority_danger = "LOW"

    # -----------------------------------
    # PROCESS DETECTIONS
    # -----------------------------------

    for r in results:

        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cls = int(box.cls[0])

            conf = float(box.conf[0])

            # CONFIDENCE FILTER

            if conf < 0.5:
                continue

            label = model.names[cls]

            # SAVE DETECTIONS

            detected_objects.append({

                "object": label,

                "confidence": round(conf, 2),

                "coordinates": {

                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            })

            # -----------------------------------
            # CENTER POINT
            # -----------------------------------

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # OBJECT AREA

            area = (x2 - x1) * (y2 - y1)

            # -----------------------------------
            # DIRECTION SYSTEM
            # -----------------------------------

            if cx < w / 3:

                direction = "LEFT"

                action = "MOVE RIGHT"

            elif cx > 2 * w / 3:

                direction = "RIGHT"

                action = "MOVE LEFT"

            else:

                direction = "CENTER"

                action = "STOP"

            # -----------------------------------
            # DANGER LEVEL
            # -----------------------------------

            danger = "LOW"

            if area > 150000:

                danger = "HIGH"

            elif area > 70000:

                danger = "MEDIUM"

            # -----------------------------------
            # PRIORITY OBJECT
            # -----------------------------------

            if area > highest_area:

                highest_area = area

                priority_object = label

                priority_direction = direction

                priority_action = action

                priority_danger = danger

            # -----------------------------------
            # DRAW YOLO BOX
            # -----------------------------------

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # LABEL

            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # CENTER POINT

            cv2.circle(
                frame,
                (cx, cy),
                5,
                (0, 0, 255),
                -1
            )

    # -----------------------------------
    # PATH PLANNING
    # -----------------------------------

    planner = PathPlanner()

    path_result = planner.generate_path(
        detected_objects,
        w,
        h
    )

    path = path_result["path"]

    grid = path_result["grid"]

    print("SAFE PATH:", path)

    # -----------------------------------
    # DRAW NAVIGATION GRID
    # -----------------------------------

    for row in range(10):

        for col in range(10):

            x_start = col * cell_width
            y_start = row * cell_height

            x_end = x_start + cell_width
            y_end = y_start + cell_height

            # -----------------------------------
            # OBSTACLE CELL
            # -----------------------------------

            if grid[row][col] == 1:

                cv2.rectangle(
                    frame,
                    (x_start, y_start),
                    (x_end, y_end),
                    (0, 0, 255),
                    -1
                )

            # -----------------------------------
            # SAFE PATH CELL
            # -----------------------------------

            if (col, row) in path:

                cv2.rectangle(
                    frame,
                    (x_start, y_start),
                    (x_end, y_end),
                    (0, 255, 0),
                    -1
                )

            # -----------------------------------
            # GRID BORDER
            # -----------------------------------

            cv2.rectangle(
                frame,
                (x_start, y_start),
                (x_end, y_end),
                (255, 255, 255),
                1
            )

    # -----------------------------------
    # FPS
    # -----------------------------------

    curr_time = time.time()

    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0

    prev_time = curr_time

    # -----------------------------------
    # SHOW TEXT INFO
    # -----------------------------------

    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    cv2.putText(
        frame,
        f"OBJECT: {priority_object}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"DIRECTION: {priority_direction}",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"DANGER: {priority_danger}",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"ACTION: {priority_action}",
        (20, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # -----------------------------------
    # SHOW WINDOW
    # -----------------------------------

    cv2.imshow(
        "AUTONOMOUS DRONE NAVIGATION SYSTEM",
        frame
    )

    # -----------------------------------
    # EXIT KEY
    # -----------------------------------

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break

# -----------------------------------
# CLEANUP
# -----------------------------------

cap.release()

cv2.destroyAllWindows()
