"""Evaluate a YOLO detector and persist precision, recall, and F1 metrics."""

import argparse
import json
from pathlib import Path
from typing import Any

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEIGHTS = ROOT / "models" / "best_v2.pt"
DEFAULT_DATASET = ROOT / "dataset_v2_clean" / "data.yaml"
DEFAULT_OUTPUT = ROOT / "runs" / "metrics" / "f1_score.json"


def _metric_values(values: Any) -> list[float]:
    if values is None:
        return []
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [float(value) for value in values]


def evaluate_model(
    weights: str | Path = DEFAULT_WEIGHTS,
    dataset: str | Path = DEFAULT_DATASET,
    output: str | Path = DEFAULT_OUTPUT,
    confidence: float = 0.25,
) -> dict[str, Any]:
    model = YOLO(str(weights))
    metrics = model.val(
        data=str(dataset),
        split="val",
        conf=confidence,
        plots=True,
        project=str(ROOT / "runs" / "val"),
        name="vehicle_metrics",
        exist_ok=True,
    )
    box = metrics.box
    precision = _metric_values(getattr(box, "p", None))
    recall = _metric_values(getattr(box, "r", None))
    f1 = _metric_values(getattr(box, "f1", None))
    names = model.names

    per_class = []
    for index, f1_value in enumerate(f1):
        class_id = int(box.ap_class_index[index]) if index < len(box.ap_class_index) else index
        class_name = names.get(class_id, str(class_id)) if isinstance(names, dict) else names[class_id]
        per_class.append({
            "class": class_name,
            "precision": round(precision[index], 6) if index < len(precision) else 0.0,
            "recall": round(recall[index], 6) if index < len(recall) else 0.0,
            "f1": round(f1_value, 6),
        })

    result = {
        "model": str(Path(weights).name),
        "dataset": str(dataset),
        "confidence": confidence,
        "precision": round(float(getattr(box, "mp", 0.0)), 6),
        "recall": round(float(getattr(box, "mr", 0.0)), 6),
        "f1": round(float(sum(f1) / len(f1)) if f1 else 0.0, 6),
        "map50": round(float(getattr(box, "map50", 0.0)), 6),
        "map50_95": round(float(getattr(box, "map", 0.0)), 6),
        "per_class": per_class,
    }

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a YOLO model with F1 score.")
    parser.add_argument("--weights", default=str(DEFAULT_WEIGHTS))
    parser.add_argument("--data", default=str(DEFAULT_DATASET))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    report = evaluate_model(args.weights, args.data, args.output, args.conf)
    print(json.dumps(report, indent=2))