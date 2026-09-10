# 🚗 Vehicle Detection AI - Hệ Thống Nhận Diện Phương Tiện Giao Thông

> **Bài Tập Lớn Trí Tuệ Nhân Tạo - Đề 20 (Nhóm 1)**  
> Ứng dụng Thị giác máy tính (Computer Vision) và Học sâu (Deep Learning) bằng YOLOv8 để nhận diện các phương tiện giao thông đường bộ. Dự án đi kèm với Web Dashboard trực quan (xây dựng bằng Dash).

---

## 🚀 Hướng Dẫn Cài Đặt (Installation)

### Bước 1: Chuẩn bị môi trường
Yêu cầu hệ thống phải có **Python 3.8+** (Khuyên dùng Python 3.10 hoặc 3.11).

Đầu tiên, tải mã nguồn về máy:
```bash
git clone https://github.com/THL-Agent-edu/Vehicle-Detection-AI.git
cd Vehicle-Detection-AI
```

**(Tùy chọn) Khởi tạo môi trường ảo (Virtual Environment):**
Để tránh xung đột thư viện với các dự án khác trên máy, bạn nên dùng môi trường ảo:
```bash
python -m venv venv

# Kích hoạt trên Windows (dùng PowerShell):
.\venv\Scripts\Activate.ps1

# Kích hoạt trên Linux/macOS:
source venv/bin/activate
```

### Bước 2: Cài đặt thư viện (Dependencies)
Cài đặt toàn bộ các thư viện cần thiết (YOLO, PyTorch, Dash, OpenCV...) bằng lệnh sau:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Hướng Dẫn Sử Dụng (Usage)

### 1. Chuẩn bị Dữ liệu (Dataset)
Vì tập dữ liệu ảnh rất nặng nên không được lưu trữ sẵn trên GitHub. Trước khi huấn luyện, bạn **bắt buộc** phải tự copy dữ liệu vào thư mục `data`.
Cấu trúc chuẩn sau khi copy phải như sau:
```text
Vehicle-Detection-AI/
└── data/
    ├── images/
    │   ├── train/    # (Chứa ảnh huấn luyện)
    │   └── val/      # (Chứa ảnh kiểm thử)
    ├── labels/
    │   ├── train/    # (Chứa file nhãn .txt huấn luyện)
    │   └── val/      # (Chứa file nhãn .txt kiểm thử)
    └── vehicle.yaml
```

### 2. Huấn luyện Mô hình (Training)
Sau khi đã có dataset, chạy lệnh sau để bắt đầu cho AI học (quá trình này có thể mất nhiều thời gian tùy thuộc vào cấu hình máy tính/GPU):
```bash
python -m src.model.train
```

### 3. Kiểm thử Mô hình (Inference/Predict)
Để kiểm tra độ chính xác của mô hình sau khi huấn luyện xong trên các ảnh test:
```bash
python -m src.model.predict
```

### 4. Khởi chạy Giao diện Web (Web Dashboard)
Để mở bảng điều khiển quản lý trực quan (UI Premium) trên trình duyệt, hãy chạy lệnh:
```bash
python src/ui/app.py
```
Sau đó, hãy mở trình duyệt web và truy cập vào đường dẫn: **`http://127.0.0.1:8050/`**

---

## 📁 Cấu Trúc Mã Nguồn

| Thư mục/File | Chức năng |
|---|---|
| `data/` | Chứa dữ liệu ảnh, nhãn (labels) và file cấu hình `vehicle.yaml`. |
| `models/` | Nơi lưu trữ trọng số mô hình (`.pt`) sau khi huấn luyện xong. |
| `src/model/` | Chứa code xử lý logic AI (`train.py`, `predict.py`). |
| `src/ui/` | Chứa toàn bộ mã nguồn của giao diện Web Dashboard (Dash). |
| `test_images/` | Chứa các video/ảnh mẫu để chạy thử nghiệm. |
| `requirements.txt` | Khai báo các thư viện Python cần thiết cho dự án. |

---

## 🏷️ Các Lớp Nhận Diện (Classes)
Dự án được cấu hình để nhận diện 4 loại phương tiện chính:
- `0`: **car** (Ô tô con)
- `1`: **motorbike** (Xe máy)
- `2`: **bus** (Xe buýt)
- `3`: **truck** (Xe tải)

---
*Phát triển bởi Nhóm 1 - Đề 20.*