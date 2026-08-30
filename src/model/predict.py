import argparse
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = ROOT / "models" / "best.pt"
VALID_IMAGES_DIR = ROOT / "data" / "valid" / "images"


def detect(source: str | Path, weights: str | Path = DEFAULT_WEIGHTS, conf: float = 0.25, imgsz: int = 640) -> Path:
    weights_path = Path(weights)
    if not weights_path.exists():
        raise FileNotFoundError(f"Model weights not found: {weights_path}")

    source_path = Path(source)
    if not source_path.exists():
        raise FileNotFoundError(f"Input source not found: {source_path}")

    model = YOLO(str(weights_path))
    model(source, conf=conf, imgsz=imgsz, project=str(ROOT / "runs" / "detect"), name="predict", exist_ok=True)

    output_dir = ROOT / "runs" / "detect" / "predict"
    print(f"Detection output saved to: {output_dir}")
    return output_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run vehicle detection inference using trained YOLOv8 model.")
    parser.add_argument("--weights", type=str, default=str(DEFAULT_WEIGHTS), help="Path to best.pt weights file.")
    parser.add_argument("--source", type=str, default=str(next(iter(VALID_IMAGES_DIR.glob("*.jpg")), VALID_IMAGES_DIR)), help="Image or directory to detect.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for inference.")
    args = parser.parse_args()

    detect(source=args.source, weights=args.weights, conf=args.conf, imgsz=args.imgsz)
