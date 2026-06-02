from fastapi import APIRouter, UploadFile, File
import shutil
import cv2
import os
from ultralytics import YOLO

router = APIRouter()

# Load YOLO model once
model = YOLO("yolov8n.pt")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

    # -----------------------------
    # 1. SAVE IMAGE
    # -----------------------------
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -----------------------------
    # 2. READ IMAGE
    # -----------------------------
    image = cv2.imread(file_path)

    if image is None:
        return {"error": "Image not found or corrupted"}

    height, width, _ = image.shape

    # -----------------------------
    # 3. YOLO DETECTION
    # -----------------------------
    results = model(image, verbose=False)

    detected_objects = []

    # -----------------------------
    # 4. PROCESS DETECTIONS
    # -----------------------------
    for result in results:
        for box in result.boxes:

            # Bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Class + confidence
            cls_id = int(box.cls[0])
            confidence = float(box.conf[0])
            label = model.names[cls_id]

            # Filter weak detections
            if confidence < 0.5:
                continue

            # -----------------------------
            # DRONE INTELLIGENCE LOGIC
            # -----------------------------

            # center position
            center_x = (x1 + x2) / 2
            frame_center_x = width / 2

            # direction logic
            if center_x < frame_center_x - 100:
                direction = "MOVE RIGHT"
            elif center_x > frame_center_x + 100:
                direction = "MOVE LEFT"
            else:
                direction = "STOP / AVOID"

            # risk calculation
            area = (x2 - x1) * (y2 - y1)

            if confidence > 0.7 and area > 50000:
                risk_level = "DANGER"
                action = "STOP"
            elif confidence > 0.4:
                risk_level = "WARNING"
                action = "SLOW DOWN"
            else:
                risk_level = "SAFE"
                action = "MOVE FORWARD"

            # -----------------------------
            # STORE RESULT
            # -----------------------------
            detected_objects.append({
                "object": label,
                "confidence": round(confidence, 2),

                "coordinates": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                },

                "center_x": int(center_x),
                "direction": direction,
                "risk_level": risk_level,
                "action": action
            })

            # -----------------------------
            # DRAW BOX ON IMAGE
            # -----------------------------
            color = (0, 255, 0)  # green default

            if risk_level == "WARNING":
                color = (0, 255, 255)  # yellow
            elif risk_level == "DANGER":
                color = (0, 0, 255)  # red

            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            cv2.putText(
                image,
                f"{label} {confidence:.2f} {risk_level}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

    # -----------------------------
    # 5. SAVE PROCESSED IMAGE
    # -----------------------------
    output_path = os.path.join(UPLOAD_DIR, f"output_{file.filename}")
    cv2.imwrite(output_path, image)

    # -----------------------------
    # 6. RESPONSE (SWAGGER SAFE)
    # -----------------------------
    return {
        "filename": file.filename,
        "width": width,
        "height": height,
        "detections": detected_objects,
        "processed_image": output_path,
        "message": "AI Drone Vision System Active"
    }