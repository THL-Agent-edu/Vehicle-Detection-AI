from pathlib import Path
import shutil

import torch
import yaml
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parents[1]
DRIVE_DATASET_DIR = PROJECT_DIR / "dataset_v2_clean"
COLAB_DATASET_DIR = Path("/content/dataset_v2_clean")
COLAB_RUNS_DIR = Path("/content/runs/train")
RUN_NAME = "vehicle_v2_colab"


def main() -> None:
    if not Path("/content/drive/MyDrive").is_dir():
        raise RuntimeError("Mount Google Drive first: run drive.mount('/content/drive') in Colab.")

    if not torch.cuda.is_available():
        raise RuntimeError(
            "GPU not available. In Colab, select Runtime > Change runtime type > T4 GPU, "
            "then rerun the setup cells."
        )

    drive_yaml = DRIVE_DATASET_DIR / "data.yaml"
    if not drive_yaml.is_file():
        raise FileNotFoundError(f"Dataset config not found: {drive_yaml}")

    with drive_yaml.open("r", encoding="utf-8") as handle:
        dataset_config = yaml.safe_load(handle)

    for split in ("train", "val"):
        split_path = Path(str(dataset_config[split]))
        if not split_path.is_absolute():
            split_path = DRIVE_DATASET_DIR / split_path
        if not split_path.is_dir():
            raise FileNotFoundError(f"Dataset {split} images not found: {split_path}")

    shutil.copytree(DRIVE_DATASET_DIR, COLAB_DATASET_DIR, dirs_exist_ok=True)
    local_yaml = COLAB_DATASET_DIR / "data.yaml"
    if not local_yaml.is_file():
        raise FileNotFoundError(f"Copied dataset config not found: {local_yaml}")

    print(f"Training on GPU: {torch.cuda.get_device_name(0)}")
    model = YOLO("yolov8n.pt")
    model.train(
        data=str(local_yaml),
        epochs=50,
        imgsz=640,
        batch=-1,
        patience=10,
        device=0,
        project=str(COLAB_RUNS_DIR),
        name=RUN_NAME,
        exist_ok=True,
    )

    run_dir = Path(model.trainer.save_dir)
    best_model = Path(model.trainer.best)
    if not best_model.is_file():
        raise FileNotFoundError(f"Training did not produce a best.pt at {best_model}")

    drive_run_dir = PROJECT_DIR / "runs" / "train" / run_dir.name
    shutil.copytree(run_dir, drive_run_dir, dirs_exist_ok=True)

    drive_model = PROJECT_DIR / "models" / "best_v2.pt"
    drive_model.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_model, drive_model)
    print(f"Training artifacts saved to: {drive_run_dir}")
    print(f"Best model saved to: {drive_model}")


if __name__ == "__main__":
    main()