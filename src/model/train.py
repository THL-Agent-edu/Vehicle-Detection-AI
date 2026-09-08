import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "data" / "data.yaml"
MODELS_DIR = ROOT / "models"


def train_model(epochs: int = 10, imgsz: int = 640, batch: int = 8, model_name: str = "yolov8n.pt") -> Path:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset config not found: {DATASET_PATH}")

    model = YOLO(model_name)
    model.train(
        data=str(DATASET_PATH),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=str(ROOT / "runs" / "train"),
        name="vehicle_detection",
        exist_ok=True,
        pretrained=True,
        device="cpu",
    )

    best_source = None
    ckpt_path = getattr(model, "ckpt_path", None)
    if ckpt_path:
        best_source = Path(ckpt_path)

    candidate_paths = [
        best_source,
        ROOT / "runs" / "train" / "vehicle_detection" / "weights" / "best.pt",
        ROOT / "runs" / "train" / "exp" / "weights" / "best.pt",
    ]
    for candidate in candidate_paths:
        if candidate is not None and candidate.exists():
            best_source = candidate
            break

    if best_source is None or not best_source.exists():
        raise FileNotFoundError("Model weights not found after training. Please check the training output directory.")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_target = MODELS_DIR / "best.pt"
    shutil.copy2(best_source, best_target)

    print(f"Training completed. Best model saved to: {best_target}")
    return best_target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 vehicle detection model.")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size.")
    parser.add_argument("--batch", type=int, default=8, help="Batch size.")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base YOLO weights to start from.")
    args = parser.parse_args()

    train_model(epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, model_name=args.model)
