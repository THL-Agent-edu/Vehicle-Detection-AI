"""
Xử lý luồng chính của ứng dụng: Mở form đăng nhập -> đăng nhập thành công -> chạy chương trình chính.
"""

from src.view.login_ui import show_login_ui
from src.view.register_ui import show_register_ui

def run_app():
    print("Khởi động ứng dụng Nhận diện phương tiện đường bộ...")
    # 1. Hiển thị form đăng nhập
    show_login_ui()

if __name__ == "__main__":
    run_app()
