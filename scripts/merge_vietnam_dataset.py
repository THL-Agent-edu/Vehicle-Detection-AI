from __future__ import annotations

import shutil
from collections import Counter, defaultdict
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parents[1]
OLD_DATASET = ROOT / "data"
VIETNAM_DATASET = ROOT / "dataset_vietnam_raw"
OUTPUT_DIR = ROOT / "dataset_v2"

OLD_CLASSES = {0: "bus", 1: "car", 2: "motorbike", 3: "threewheel", 4: "truck", 5: "van"}
VIETNAM_REMAP = {11: 0, 12: 1, 13: 2, 14: 4}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}
ERRORS = defaultdict(list)


def add_error(kind: str, file_name: str, detail: str = "") -> None:
    ERRORS[kind].append((file_name, detail))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def unique_name(original_name: str, used_names: set[str], prefix: str = "") -> str:
    stem = Path(original_name).stem
    suffix = Path(original_name).suffix.lower()
    candidate = f"{prefix}{stem}{suffix}"
    if candidate not in used_names:
        used_names.add(candidate)
        return candidate

    index = 1
    while True:
        candidate = f"{prefix}{stem}_{index}{suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        index += 1


def is_valid_image(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        return False
    if Image is None:
        return True
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def copy_old_dataset(dst_root: Path) -> tuple[int, int, set[str]]:
    used_names: set[str] = set()
    train_count = 0
    valid_count = 0

    for split_name, split_folder in (("train", OLD_DATASET / "train"), ("valid", OLD_DATASET / "valid")):
        src_img = split_folder / "images"
        src_lbl = split_folder / "labels"
        dst_img = dst_root / split_name / "images"
        dst_lbl = dst_root / split_name / "labels"
        ensure_dir(dst_img)
        ensure_dir(dst_lbl)

        image_files = sorted(p for p in src_img.iterdir() if p.is_file()) if src_img.exists() else []
        for image_path in image_files:
            if not is_valid_image(image_path):
                add_error("invalid_image_file", image_path.name, f"{split_name} source image invalid")
            dest_img_path = dst_img / image_path.name
            shutil.copy2(image_path, dest_img_path)
            used_names.add(image_path.name)

            label_path = src_lbl / f"{image_path.stem}.txt"
            if label_path.exists():
                shutil.copy2(label_path, dst_lbl / label_path.name)
            else:
                add_error("image_missing_label", image_path.name, f"{split_name} image has no label")

            if split_name == "train":
                train_count += 1
            else:
                valid_count += 1

    return train_count, valid_count, used_names


def parse_label_file(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    result: list[tuple[int, float, float, float, float]] = []
    if not label_path.exists():
        add_error("image_missing_label", label_path.name)
        return result

    with open(label_path, "r", encoding="utf-8", errors="replace") as handle:
        lines = [line.strip() for line in handle if line.strip()]

    if not lines:
        add_error("empty_annotation", label_path.name, "Label file has no rows")
        return result

    for index, raw_line in enumerate(lines, start=1):
        parts = raw_line.split()
        if len(parts) != 5:
            add_error("label_sai_format", label_path.name, f"line {index}: expected 5 values, got {len(parts)}")
            continue
        try:
            cls_id, x_center, y_center, width, height = [float(value) for value in parts]
        except ValueError:
            add_error("label_sai_format", label_path.name, f"line {index}: non-numeric YOLO values")
            continue

        class_id = int(cls_id)
        if class_id < 0 or class_id > 14:
            add_error("class_id_out_of_range", label_path.name, f"line {index}: class {class_id} is outside 0..14")
            continue

        if not (0.0 <= x_center <= 1.0 and 0.0 <= y_center <= 1.0 and 0.0 <= width <= 1.0 and 0.0 <= height <= 1.0):
            add_error("invalid_yolo_coordinates", label_path.name, f"line {index}: normalized coords out of range")
            continue

        if width <= 0 or height <= 0:
            add_error("invalid_yolo_coordinates", label_path.name, f"line {index}: width/height must be > 0")
            continue

        x_min = x_center - width / 2.0
        y_min = y_center - height / 2.0
        x_max = x_center + width / 2.0
        y_max = y_center + height / 2.0
        if x_min < 0 or y_min < 0 or x_max > 1 or y_max > 1:
            add_error("invalid_yolo_coordinates", label_path.name, f"line {index}: box exceeds normalized canvas")
            continue

        result.append((class_id, x_center, y_center, width, height))

    return result


def write_label_file(path: Path, annotations: list[tuple[int, float, float, float, float]]) -> None:
    lines = [f"{cls_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}" for cls_id, x_center, y_center, width, height in annotations]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def process_vietnam_dataset(dst_root: Path, used_names: set[str]) -> tuple[int, int, Counter]:
    kept_train = 0
    kept_valid = 0
    annotation_counts: Counter = Counter()

    for split_name in ("train", "valid"):
        src_img_dir = VIETNAM_DATASET / split_name / "images"
        src_label_dir = VIETNAM_DATASET / split_name / "labels"
        dst_img_dir = dst_root / split_name / "images"
        dst_label_dir = dst_root / split_name / "labels"
        ensure_dir(dst_img_dir)
        ensure_dir(dst_label_dir)

        if not src_img_dir.exists() or not src_label_dir.exists():
            continue

        image_files = sorted(p for p in src_img_dir.iterdir() if p.is_file())
        label_files = {p.stem: p for p in src_label_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"}

        for image_path in image_files:
            if not is_valid_image(image_path):
                add_error("invalid_image_file", image_path.name, f"{split_name} Vietnam image invalid")
                continue

            label_path = label_files.get(image_path.stem)
            if label_path is None:
                add_error("image_missing_label", image_path.name, f"{split_name} Vietnam image has no matching label")
                continue

            annotations = parse_label_file(label_path)
            filtered = []
            for cls_id, x_center, y_center, width, height in annotations:
                if cls_id in VIETNAM_REMAP:
                    filtered.append((VIETNAM_REMAP[cls_id], x_center, y_center, width, height))

            if not filtered:
                add_error("empty_annotation", label_path.name, f"{split_name} Vietnam label has no valid vehicle classes after filtering")
                continue

            output_name = unique_name(image_path.name, used_names, prefix="vn_")
            output_stem = Path(output_name).stem
            shutil.copy2(image_path, dst_img_dir / output_name)
            write_label_file(dst_label_dir / f"{output_stem}.txt", filtered)

            for cls_id, _, _, _, _ in filtered:
                annotation_counts[cls_id] += 1

            if split_name == "train":
                kept_train += 1
            else:
                kept_valid += 1

    return kept_train, kept_valid, annotation_counts


def copy_vietnam_test_split(dst_root: Path, used_names: set[str]) -> None:
    src_img_dir = VIETNAM_DATASET / "test" / "images"
    src_label_dir = VIETNAM_DATASET / "test" / "labels"
    dst_img_dir = dst_root / "test_vietnam" / "images"
    dst_label_dir = dst_root / "test_vietnam" / "labels"
    ensure_dir(dst_img_dir)
    ensure_dir(dst_label_dir)

    if not src_img_dir.exists() or not src_label_dir.exists():
        return

    image_files = sorted(p for p in src_img_dir.iterdir() if p.is_file())
    label_files = {p.stem: p for p in src_label_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"}

    for image_path in image_files:
        if not is_valid_image(image_path):
            add_error("invalid_image_file", image_path.name, "Vietnam test image invalid")
            continue

        output_name = unique_name(image_path.name, used_names, prefix="vn_")
        output_stem = Path(output_name).stem
        shutil.copy2(image_path, dst_img_dir / output_name)

        label_path = label_files.get(image_path.stem)
        if label_path is not None:
            shutil.copy2(label_path, dst_label_dir / f"{output_stem}.txt")
        else:
            add_error("image_missing_label", image_path.name, "Vietnam test image has no matching label")


def collect_output_counts(output_root: Path) -> Counter:
    counts: Counter = Counter()
    for label_path in sorted(output_root.rglob("*.txt")):
        with open(label_path, "r", encoding="utf-8", errors="replace") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 5:
                    continue
                try:
                    cls_id = int(float(parts[0]))
                except ValueError:
                    continue
                counts[cls_id] += 1
    return counts


def write_data_yaml(output_root: Path) -> None:
    yaml_content = """train: train/images
val: valid/images

nc: 6
names: ['bus', 'car', 'motorbike', 'threewheel', 'truck', 'van']
"""
    (output_root / "data.yaml").write_text(yaml_content, encoding="utf-8")


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    ensure_dir(OUTPUT_DIR)
    ensure_dir(OUTPUT_DIR / "test_vietnam" / "images")
    ensure_dir(OUTPUT_DIR / "test_vietnam" / "labels")

    old_train_count, old_valid_count, used_names = copy_old_dataset(OUTPUT_DIR)
    vietnam_train_kept, vietnam_valid_kept, vietnam_counts = process_vietnam_dataset(OUTPUT_DIR, used_names)
    copy_vietnam_test_split(OUTPUT_DIR, used_names)

    write_data_yaml(OUTPUT_DIR)

    total_train_images = len(list((OUTPUT_DIR / "train" / "images").iterdir())) if (OUTPUT_DIR / "train" / "images").exists() else 0
    total_valid_images = len(list((OUTPUT_DIR / "valid" / "images").iterdir())) if (OUTPUT_DIR / "valid" / "images").exists() else 0

    total_counts = collect_output_counts(OUTPUT_DIR)
    class_report = {name: total_counts.get(index, 0) for index, name in OLD_CLASSES.items()}

    print(f"Dataset cũ train images: {old_train_count}")
    print(f"Dataset cũ valid images: {old_valid_count}")
    print(f"Việt Nam giữ lại train: {vietnam_train_kept}")
    print(f"Việt Nam giữ lại valid: {vietnam_valid_kept}")
    print(f"Tổng ảnh train dataset_v2: {total_train_images}")
    print(f"Tổng ảnh valid dataset_v2: {total_valid_images}")
    print("\nSố annotation theo class:")
    for class_name in ["bus", "car", "motorbike", "threewheel", "truck", "van"]:
        idx = list(OLD_CLASSES.values()).index(class_name)
        print(f"  {class_name}: {class_report.get(class_name, 0)}")

    print("\nError summary:")
    if ERRORS:
        for kind, entries in sorted(ERRORS.items()):
            print(f"- {kind}: {len(entries)}")
            for file_name, detail in entries[:10]:
                print(f"    {file_name}: {detail}")
            if len(entries) > 10:
                print(f"    ... and {len(entries) - 10} more")
    else:
        print("- No errors detected")

    print("\nDATASET V2 CREATED")
    print(f"Dataset:\n{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
