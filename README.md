# 🚗 Vehicle Detection AI - Nhận Diện Phương Tiện Đường Bộ

> **Bài Tập Lớn Trí Tuệ Nhân Tạo - Đề 20 (Nhóm 1)**  
> Chương trình ứng dụng Thị giác máy tính (Computer Vision) và Học sâu (Deep Learning) để nhận diện các phương tiện giao thông đường bộ thời gian thực.

---

## 📌 Giới Thiệu Dự Án

Hệ thống được thiết kế nhằm tự động phát hiện và phân loại các phương tiện giao thông đường bộ (ô tô, xe máy, xe buýt, xe tải,...) từ hình ảnh, video hoặc luồng camera trực tiếp. Dự án áp dụng kiến trúc **YOLOv8** tiên tiến giúp đạt tốc độ xử lý nhanh cùng độ chính xác cao.

---

## 🛠️ Công Nghệ & Thư Viện Sử Dụng

- **Python**: Ngôn ngữ lập trình chính cho toàn bộ dự án.
- **YOLOv8**: Mô hình phát hiện đối tượng (Object Detection) thế hệ mới từ Ultralytics.
- **Ultralytics**: Framework cung cấp công cụ huấn luyện, đánh giá và suy luận mô hình YOLO.
- **PyTorch**: Nền tảng Học sâu (Deep Learning) hỗ trợ tính toán và xử lý trên GPU/CPU.
- **OpenCV**: Thư viện xử lý ảnh và luồng video thời gian thực.
- **YOLO Dataset Standard**: Định dạng dữ liệu chuẩn với file cấu hình `vehicle.yaml` và các nhãn bounding box tương ứng.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
Vehicle-Detection-AI/
│
├── data/                      # Dữ liệu hình ảnh và nhãn gán chuẩn YOLO
│   ├── images/                # Thư mục ảnh (train / val)
│   ├── labels/                # Thư mục nhãn gán bounding box
│   └── vehicle.yaml           # File cấu hình tập dữ liệu (dataset config)
│
├── models/                    # Lưu trữ các checkpoint / trọng số mô hình (.pt)
│
├── notebooks/                 # Jupyter Notebooks phục vụ thử nghiệm & phân tích
│
├── src/                       # Mã nguồn chính của ứng dụng (mô hình MVC)
│   ├── controller/            # Điều khiển luồng ứng dụng (main_ctrl.py)
│   ├── model/                 # Xử lý huấn luyện & nhận diện (train.py, predict.py)
│   └── view/                  # Giao diện người dùng (login_ui.py, register_ui.py,...)
│
├── test_images/               # Ảnh/Video mẫu dùng để kiểm thử nhận diện
├── requirements.txt           # Danh sách các thư viện cần cài đặt
└── README.md                  # Tài liệu hướng dẫn dự án
```

---

## 🏷️ Các Lớp Phương Tiện Nhận Diện (Classes)

Mô hình được huấn luyện để nhận diện các lớp phương tiện chính (`data/vehicle.yaml`):

| ID | Class Name | Tên tiếng Việt |
| :-: | :--- | :--- |
| `0` | **car** | Ô tô |
| `1` | **motorbike** | Xe máy |
| `2` | **bus** | Xe buýt |
| `3` | **truck** | Xe tải |

---

## 🚀 Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Chuẩn bị môi trường

Yêu cầu **Python 3.8+** (khuyên dùng Python 3.10 hoặc 3.11).

```bash
# Clone repository (nếu chưa thực hiện)
git clone https://github.com/THL-Agent-edu/Vehicle-Detection-AI.git
cd Vehicle-Detection-AI

# Khởi tạo môi trường ảo (tùy chọn)
python -m venv venv
# Kích hoạt trên Windows:
venv\Scripts\activate
# Kích hoạt trên Linux/macOS:
source venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

*(Các thư viện chính bao gồm: `ultralytics`, `torch`, `torchvision`, `opencv-python`, `matplotlib`, `pyyaml`,...)*

---

## 🎯 Huấn Luyện & Chạy Ứng Dụng

### 🏋️ Huấn luyện mô hình (Training)

Chạy file script huấn luyện mô hình YOLOv8 trên dataset phương tiện:

```bash
python -m src.model.train
```

### 🔍 Chạy thử nghiệm nhận diện (Inference)

Chạy dự đoán trên ảnh/video kiểm thử:

```bash
python -m src.model.predict
```

### 🖥️ Khởi chạy ứng dụng giao diện (App UI)

```bash
python -m src.controller.main_ctrl
```

---

## 📝 Giấy Phép & Tác Giả

- **Bài Tập Lớn**: Trí Tuệ Nhân Tạo - Đề 20
- **Thực hiện**: Nhóm 1
