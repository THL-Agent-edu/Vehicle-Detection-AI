from __future__ import annotations

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data"
TEST_IMAGES_DIR = ROOT / "test_images"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".avi"}


def _format_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size_bytes} B"


def _normalize_status(path: Path) -> str:
    path_str = str(path).lower()
    if "valid" in path_str or "train" in path_str:
        return "Processed"
    if "test" in path_str:
        return "Processing"
    return "Failed"


def _read_file_metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    timestamp = datetime.fromtimestamp(stat.st_mtime)
    return {
        "name": path.name,
        "size": _format_size(stat.st_size),
        "time": timestamp.strftime("%H:%M"),
        "status": _normalize_status(path),
    }


def get_recent_sources(limit: int = 5) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    search_roots = [
        DATA_ROOT / "images" / "train",
        DATA_ROOT / "images" / "val",
        DATA_ROOT / "train" / "images",
        DATA_ROOT / "valid" / "images",
        TEST_IMAGES_DIR,
    ]

    for root in search_roots:
        if not root.exists():
            continue
        for item in root.iterdir():
            if not item.is_file():
                continue
            if item.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            sources.append(_read_file_metadata(item))

    sources.sort(key=lambda entry: entry["time"], reverse=True)
    return sources[:limit]


def get_data_management_payload() -> dict[str, Any]:
    recent_sources = get_recent_sources(limit=5)
    processed_count = sum(1 for item in recent_sources if item["status"] == "Processed")
    processing_count = sum(1 for item in recent_sources if item["status"] == "Processing")
    failed_count = sum(1 for item in recent_sources if item["status"] == "Failed")

    return {
        "summary": {
            "total_files": len(recent_sources),
            "processed": processed_count,
            "processing": processing_count,
            "failed": failed_count,
        },
        "recent_sources": recent_sources,
        "metrics": [
            {"label": "Vehicles detected", "value": "14,892", "delta": "+12.4%"},
            {"label": "Average confidence", "value": "96.8%", "delta": "+2.1%"},
            {"label": "Alerts requiring review", "value": "47", "delta": "5 new"},
        ],
    }


class DataManagementHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in {"/", "/data-management"}:
            payload = get_data_management_payload()
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), DataManagementHandler)
    print(f"Data Management backend running at http://{host}:{port}/data-management")
    server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backend for Data Management page.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port)
