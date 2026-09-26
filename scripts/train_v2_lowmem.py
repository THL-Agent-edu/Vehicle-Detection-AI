from pathlib import Path
import shutil

from ultralytics import YOLO

root = Path(r"E:\Vehicle-Detection-AI")
train_dir = root / "dataset_v2_clean"
model_path = root / "models" / "best_v2.pt"
project_dir = root / "runs" / "train"

# CPU-only training with conservative settings to fit memory constraints.
model = YOLO("yolov8n.pt")
model.train(
    data=str(train_dir / "data.yaml"),
    epochs=10,
    imgsz=320,
    batch=2,
    patience=5,
    project=str(project_dir),
    name="vehicle_v2_lowmem",
    device="cpu",
    workers=0,
    amp=False,
    exist_ok=True,
)

best_model = Path("runs/train/vehicle_v2_lowmem/weights/best.pt")
print(f"BEST_MODEL_PATH={best_model}")
print(f"BEST_MODEL_EXISTS={best_model.exists()}")
if best_model.exists():
    shutil.copy2(best_model, model_path)
    print(f"COPIED_TO={model_path}")
else:
    raise FileNotFoundError(f"Training did not produce a best.pt at {best_model}")
