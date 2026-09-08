"""
Xử lý luồng chính của ứng dụng: Mở thẳng chương trình chính.
"""

import webbrowser
import os

def run_app():
    print("Khởi động ứng dụng Nhận diện phương tiện đường bộ...")
    # 1. Hiển thị form màn hình chính
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'view', 'live_monitor.html'))
    print(f"Mở màn hình chính: {html_path}")
    webbrowser.open(f"file://{html_path}")

if __name__ == "__main__":
    run_app()
