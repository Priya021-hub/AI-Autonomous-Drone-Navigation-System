from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ultralytics import YOLO

from app.services.path_planning import PathPlanner

import cv2
import shutil
import os

app = FastAPI()

# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# UPLOAD FOLDER
# =====================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# =====================================
# LOAD YOLO MODEL
# =====================================

model = YOLO("yolov8n.pt")

# =====================================
# PATH PLANNER
# =====================================

planner = PathPlanner()

# =====================================
# LIVE DATA
# =====================================

live_data = {

    "message": "ARecon backend running",

    "object": "None",

    "danger": "LOW",

    "direction": "SAFE",

    "action": "MOVE FORWARD",

    "path": []
}

# =====================================
# HOME ROUTE
# =====================================

@app.get("/")
async def home():

    return live_data

# =====================================
# VIDEO STREAM FUNCTION
# =====================================

def generate_frames():

    global live_data

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:

        success, frame = cap.read()

        if not success:

            print("Camera frame not received")
            continue

        h, w, _ = frame.shape

        results = model(frame, verbose=False)

        detected_objects = []

        highest_area = 0

        priority_object = "None"
        priority_direction = "SAFE"
        priority_action = "MOVE FORWARD"
        priority_danger = "LOW"

        # =====================================
        # YOLO DETECTION
        # =====================================

        for r in results:

            for box in r.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                cls = int(box.cls[0])

                conf = float(box.conf[0])

                if conf < 0.5:
                    continue

                label = model.names[cls]

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

                # CENTER

                cx = (x1 + x2) // 2

                # AREA

                area = (x2 - x1) * (y2 - y1)

                # DIRECTION

                if cx < w / 3:

                    direction = "LEFT"
                    action = "MOVE RIGHT"

                elif cx > 2 * w / 3:

                    direction = "RIGHT"
                    action = "MOVE LEFT"

                else:

                    direction = "CENTER"
                    action = "STOP"

                # DANGER

                danger = "LOW"

                if area > 150000:

                    danger = "HIGH"

                elif area > 70000:

                    danger = "MEDIUM"

                # PRIORITY OBJECT

                if area > highest_area:

                    highest_area = area

                    priority_object = label
                    priority_direction = direction
                    priority_action = action
                    priority_danger = danger

                # DRAW BOX

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

        # =====================================
        # A* PATH PLANNING
        # =====================================

        path_result = planner.generate_path(
            detected_objects,
            w,
            h
        )

        path = path_result["path"]

        grid = path_result["grid"]

        print("SAFE PATH:", path)

        obstacle_count = len(detected_objects)

        # =====================================
        # UPDATE LIVE DATA
        # =====================================

        live_data = {

            "message": "YOLO Detection Active",

            "object": priority_object,

            "danger": priority_danger,

            "direction": priority_direction,

            "action": priority_action,

            "obstacle_count": obstacle_count,

            "path": path,
     
            "grid": grid
        }

        # =====================================
        # GRID SETTINGS
        # =====================================

        cell_w = w // 20
        cell_h = h // 20

        # =====================================
        # DRAW GRID
        # =====================================

        for i in range(21):

            cv2.line(
                frame,
                (i * cell_w, 0),
                (i * cell_w, h),
                (60, 60, 60),
                1
            )

            cv2.line(
                frame,
                (0, i * cell_h),
                (w, i * cell_h),
                (60, 60, 60),
                1
            )

        # =====================================
        # DRAW BLOCKED CELLS
        # =====================================

        grid = path_result["grid"]

        for y in range(20):

            for x in range(20):

                if grid[y][x] == 1:

                    start_x = x * cell_w
                    start_y = y * cell_h

                    end_x = start_x + cell_w
                    end_y = start_y + cell_h

                    overlay = frame.copy()

                    cv2.rectangle(
                        overlay,
                        (start_x, start_y),
                        (end_x, end_y),
                        (0, 0, 255),
                        -1
                    )

                    cv2.addWeighted(
                        overlay,
                        0.45,
                        frame,
                        0.55,
                        0,
                        frame
                    )

        # =====================================
        # PATH POINTS
        # =====================================

        path_points = []

        for point in path:

            px, py = point

            center_x = px * cell_w + cell_w // 2
            center_y = py * cell_h + cell_h // 2

            path_points.append(
                (center_x, center_y)
            )

        # =====================================
        # DRAW SAFE PATH
        # =====================================

        for i in range(len(path_points) - 1):

            pt1 = path_points[i]
            pt2 = path_points[i + 1]

            cv2.line(
                frame,
                pt1,
                pt2,
                (255, 0, 0),
                5
            )

            cv2.line(
                frame,
                pt1,
                pt2,
                (255, 255, 0),
                2
            )

            cv2.arrowedLine(
                frame,
                pt1,
                pt2,
                (0, 255, 255),
                2,
                tipLength=0.25
            )

        # =====================================
        # DRAW PATH NODES
        # =====================================

        for point in path_points:

            cv2.circle(
                frame,
                point,
                7,
                (0, 255, 255),
                -1
            )

        # =====================================
        # START POINT
        # =====================================

        cv2.circle(
            frame,
            (
                cell_w // 2,
                cell_h // 2
            ),
            12,
            (0, 255, 0),
            -1
        )

        cv2.putText(
            frame,
            "START",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # =====================================
        # GOAL POINT
        # =====================================

        goal_x = w - cell_w // 2
        goal_y = h - cell_h // 2

        cv2.circle(
            frame,
            (
                goal_x,
                goal_y
            ),
            12,
            (255, 255, 255),
            -1
        )

        cv2.putText(
            frame,
            "GOAL",
            (goal_x - 40, goal_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # =====================================
        # STATUS PANEL
        # =====================================

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (10, 10),
            (420, 190),
            (0, 0, 0),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.4,
            frame,
            0.6,
            0,
            frame
        )

        cv2.putText(
            frame,
            f"OBJECT: {priority_object}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"DANGER: {priority_danger}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
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
            f"ACTION: {priority_action}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # =====================================
        # ENCODE FRAME
        # =====================================

        _, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

# =====================================
# VIDEO ROUTE
# =====================================

@app.get("/video")
def video():

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# =====================================
# IMAGE UPLOAD
# =====================================

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    image = cv2.imread(file_path)

    results = model(image)

    detections = []

    for r in results:

        for box in r.boxes:

            cls_id = int(box.cls[0])

            conf = float(box.conf[0])

            object_name = model.names[cls_id]

            detections.append({

                "object": object_name,

                "confidence": round(conf, 2)
            })

    return {

        "message": "Image Uploaded Successfully",

        "filename": file.filename,

        "detections": detections
    }

# =====================================
# VIDEO UPLOAD
# =====================================

@app.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...)
):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {

        "message": "Video Uploaded Successfully",

        "filename": file.filename
    }