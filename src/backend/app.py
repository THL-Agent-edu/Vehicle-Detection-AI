from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

import cv2
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "best.pt"
RUNS_DIR = ROOT / "runs" / "detect"
UPLOAD_DIR = ROOT / "uploads"
MAX_UPLOAD_SIZE_MB = 500
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

DEFAULT_SAMPLE_IMAGES = [
    ROOT / "test_images",
    ROOT / "data" / "valid" / "images",
]


class DetectionSettings(BaseModel):
    model: str = "best.pt"
    confidence: float = Field(default=0.25, ge=0.05, le=1.0)
    iou: float = Field(default=0.45, ge=0.05, le=1.0)
    imageSize: int = Field(default=640, ge=320, le=1280)
    mode: str = "Image"


class DetectionRequest(BaseModel):
    fileId: str | None = None
    mode: str = "Image"
    file: str | None = None
    settings: DetectionSettings | None = None


app = FastAPI(title="Vehicle Detection API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
        "http://localhost:4175",
        "http://127.0.0.1:4175",
        "http://localhost:4176",
        "http://127.0.0.1:4176",
        "http://localhost:4177",
        "http://127.0.0.1:4177",
        "http://localhost:4178",
        "http://127.0.0.1:4178",
        "http://localhost:4179",
        "http://127.0.0.1:4179",
        "http://localhost:5183",
        "http://127.0.0.1:5183",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RUNS_DIR.mkdir(parents=True, exist_ok=True)

model = YOLO(str(MODEL_PATH))
app.mount("/results", StaticFiles(directory=str(ROOT / "runs")), name="results")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def find_sample_image() -> Path:
    for directory in DEFAULT_SAMPLE_IMAGES:
        if not directory.exists():
            continue
        candidates = sorted(directory.glob("*"))
        for item in candidates:
            if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}:
                return item
    raise FileNotFoundError("No sample image found in test_images or data/valid/images")


def choose_source_path(file_id: str | None = None, explicit_path: str | None = None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        if path.exists():
            return path

    if file_id:
        upload_candidate = UPLOAD_DIR / file_id
        if upload_candidate.exists():
            return upload_candidate

    return find_sample_image()


def normalize_box(coords: list[float], image_width: int, image_height: int) -> dict[str, float | int]:
    x1, y1, x2, y2 = [float(value) for value in coords]
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    return {
        "x": round((x1 / max(image_width, 1)) * 100, 2),
        "y": round((y1 / max(image_height, 1)) * 100, 2),
        "width": round((width / max(image_width, 1)) * 100, 2),
        "height": round((height / max(image_height, 1)) * 100, 2),
    }


def infer_video_detection(source: Path, conf: float, iou: float, imgsz: int) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    run_id = f"api_{uuid.uuid4().hex[:8]}"
    result_dir = RUNS_DIR / run_id
    result_dir.mkdir(parents=True, exist_ok=True)

    video = cv2.VideoCapture(str(source))
    if not video.isOpened():
        raise ValueError(f"Unable to read video source: {source}")

    fps = video.get(cv2.CAP_PROP_FPS) or 30.0
    preview_frame: Any | None = None
    frame_entries: list[dict[str, Any]] = []
    frame_count = 0
    start_time = time.perf_counter()

    while True:
        ok, frame = video.read()
        if not ok:
            break
        if preview_frame is None:
            preview_frame = frame.copy()

        frame_index = frame_count
        timestamp = frame_index / max(1.0, fps)
        current_batch: list[dict[str, Any]] = []

        results = model(frame, conf=conf, iou=iou, imgsz=imgsz, verbose=False)
        if results and len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                image_width = int(result.orig_shape[1]) if getattr(result, 'orig_shape', None) else frame.shape[1]
                image_height = int(result.orig_shape[0]) if getattr(result, 'orig_shape', None) else frame.shape[0]
                for box in boxes:
                    if box.cls is None or box.conf is None or len(box.cls) == 0:
                        continue
                    cls_index = int(box.cls[0].item()) if hasattr(box.cls[0], 'item') else int(box.cls[0])
                    confidence = float(box.conf[0].item()) if hasattr(box.conf[0], 'item') else float(box.conf[0])
                    coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], 'tolist') else list(box.xyxy[0])
                    label = model.names.get(cls_index, str(cls_index))
                    entry = {
                        "className": label,
                        "confidence": round(confidence * 100, 1),
                        "boundingBox": normalize_box(coords, image_width, image_height),
                    }
                    current_batch.append(entry)
        frame_entries.append({"frame": frame_index, "timestamp": round(timestamp, 3), "detections": current_batch})
        frame_count += 1

    video.release()

    if preview_frame is not None:
        preview_path = result_dir / "preview.jpg"
        cv2.imwrite(str(preview_path), preview_frame)
    else:
        preview_path = None

    time_series = [
        {"frame": item["frame"], "timestamp": item["timestamp"], "detections": item["detections"]}
        for item in frame_entries
    ]

    current_detections = time_series[-1]["detections"] if time_series else []
    result_url = None
    if preview_path is not None and preview_path.exists():
        relative_path = preview_path.relative_to(ROOT / "runs")
        result_url = f"http://127.0.0.1:8000/results/{relative_path.as_posix()}"

    total_vehicles = len(current_detections)
    average_confidence = round(sum(item["confidence"] for item in current_detections) / total_vehicles, 1) if total_vehicles else 0.0

    return {
        "detectionId": f"det-{uuid.uuid4().hex[:10]}",
        "sourceFile": source.name,
        "totalVehicles": total_vehicles,
        "averageConfidence": average_confidence,
        "processingTime": round(time.perf_counter() - start_time, 3),
        "detections": current_detections,
        "resultUrl": result_url,
        "videoFrames": time_series,
    }


def infer_detection(source: Path, conf: float, iou: float, imgsz: int) -> dict[str, Any]:
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    if source.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv", ".webm"}:
        return infer_video_detection(source, conf, iou, imgsz)

    run_id = f"api_{uuid.uuid4().hex[:8]}"
    results = model(
        str(source),
        conf=conf,
        iou=iou,
        imgsz=imgsz,
        project=str(RUNS_DIR),
        name=run_id,
        exist_ok=True,
        verbose=False,
    )

    if not results or len(results) == 0:
        raise ValueError("No detection results were produced for the selected source.")

    first_result = results[0]
    boxes = first_result.boxes
    image_width = int(first_result.orig_shape[1]) if getattr(first_result, 'orig_shape', None) else 640
    image_height = int(first_result.orig_shape[0]) if getattr(first_result, 'orig_shape', None) else 640

    detections: list[dict[str, Any]] = []
    for i, box in enumerate(boxes):
        if box.cls is None or box.conf is None or len(box.cls) == 0:
            continue
        cls_index = int(box.cls[0].item()) if hasattr(box.cls[0], 'item') else int(box.cls[0])
        confidence = float(box.conf[0].item()) if hasattr(box.conf[0], 'item') else float(box.conf[0])
        coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], 'tolist') else list(box.xyxy[0])
        label = model.names.get(cls_index, str(cls_index))

        detections.append({
            "className": label,
            "confidence": round(confidence * 100, 1),
            "boundingBox": normalize_box(coords, image_width, image_height),
        })

    result_dir = RUNS_DIR / run_id
    rendered_files = sorted(result_dir.rglob("*.jpg")) + sorted(result_dir.rglob("*.jpeg")) + sorted(result_dir.rglob("*.png"))
    result_file = rendered_files[0] if rendered_files else None

    result_url = None
    if result_file is not None:
        relative_path = result_file.relative_to(ROOT / "runs")
        result_url = f"http://127.0.0.1:8000/results/{relative_path.as_posix()}"

    total_vehicles = len(detections)
    average_confidence = round(sum(item["confidence"] for item in detections) / total_vehicles, 1) if total_vehicles else 0.0

    return {
        "detectionId": f"det-{uuid.uuid4().hex[:10]}",
        "sourceFile": source.name,
        "totalVehicles": total_vehicles,
        "averageConfidence": average_confidence,
        "processingTime": round(time.perf_counter() * 1000) / 1000,
        "detections": detections,
        "resultUrl": result_url,
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "backend": "FastAPI", "model": str(MODEL_PATH.name)}


@app.get("/system-info")
async def system_info() -> dict[str, str]:
    return {
        "system": "Vehicle Detection AI",
        "description": "YOLOv8 vehicle detection system",
        "aiModel": "best.pt",
        "backend": "FastAPI",
        "frontend": "React + TypeScript + Vite",
        "computerVision": "OpenCV + Ultralytics",
        "deepLearning": "PyTorch",
        "framework": "YOLOv8",
        "version": "1.0.0",
    }


@app.get("/settings")
async def settings() -> dict[str, Any]:
    return {
        "model": "best.pt",
        "confidenceThreshold": 0.25,
        "iouThreshold": 0.45,
        "inputResolution": "640",
        "detectionMode": "Image",
        "maxFileSize": "500 MB",
        "supportedFormats": ".jpg, .png, .mp4",
    }


@app.get("/files")
async def list_files() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in sorted(UPLOAD_DIR.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True):
        if not item.is_file():
            continue
        file_type = "file"
        suffix = item.name.lower()
        if suffix.endswith((".jpg", ".jpeg", ".png")):
            file_type = "image"
        elif suffix.endswith(".mp4"):
            file_type = "video"

        display_name = item.name.split("_", 1)[1] if "_" in item.name else item.name

        entries.append({
            "id": item.name,
            "fileName": display_name,
            "fileType": file_type,
            "fileSize": item.stat().st_size,
            "uploadedAt": __import__("datetime").datetime.fromtimestamp(item.stat().st_mtime, tz=__import__("datetime").timezone.utc).isoformat(),
            "status": "ready",
        })
    return entries


@app.get("/data-management")
async def data_management() -> dict[str, Any]:
    files = await list_files()
    total_files = len(files)
    total_images = sum(1 for item in files if item["fileType"] == "image")
    total_videos = sum(1 for item in files if item["fileType"] == "video")
    ready = sum(1 for item in files if item["status"] in {"ready", "processed"})
    return {
        "summary": {
            "total_files": total_files,
            "processed": ready,
            "processing": 0,
            "failed": 0,
        },
        "recent_sources": [
            {
                "name": item["fileName"],
                "size": f"{max(1, item['fileSize'] // 1024)} KB",
                "time": item["uploadedAt"],
                "status": "Processed" if item["status"] == "ready" else "Processing",
            }
            for item in files[:5]
        ],
        "metrics": [
            {"label": "Total files", "value": str(total_files), "delta": "+0%"},
            {"label": "Images", "value": str(total_images), "delta": "+0%"},
            {"label": "Videos", "value": str(total_videos), "delta": "+0%"},
            {"label": "Ready for detection", "value": str(ready), "delta": "+0%"},
        ],
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    file_id = f"{uuid.uuid4().hex}_{file.filename}"
    destination = UPLOAD_DIR / file_id
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds the {MAX_UPLOAD_SIZE_MB} MB limit.")
    with destination.open("wb") as buffer:
        buffer.write(file_bytes)
    return {
        "id": file_id,
        "fileName": file.filename,
        "fileType": "image" if file.filename.lower().endswith((".jpg", ".jpeg", ".png")) else "video" if file.filename.lower().endswith(".mp4") else "file",
        "fileSize": len(file_bytes),
        "uploadedAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "status": "ready",
        "path": str(destination),
    }


@app.post("/detect")
async def detect(payload: DetectionRequest) -> dict[str, Any]:
    try:
        source = choose_source_path(payload.fileId, payload.file)
        settings = payload.settings or DetectionSettings()
        mode = (payload.mode or settings.mode or "Image").strip()
        if mode.lower() not in {"image", "video", "camera"}:
            mode = "Image"

        result = infer_detection(
            source=source,
            conf=float(settings.confidence),
            iou=float(settings.iou),
            imgsz=int(settings.imageSize),
        )

        result["sourceFile"] = source.name
        result["processingTime"] = round(result["processingTime"], 2)
        result["averageConfidence"] = round(float(result["averageConfidence"]), 1)
        result["detections"] = result["detections"]
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.backend.app:app", host="0.0.0.0", port=8000, reload=False)
