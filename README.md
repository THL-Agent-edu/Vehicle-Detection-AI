# Vehicle Detection AI

Hệ thống phát hiện và phân loại phương tiện giao thông bằng YOLOv8, sử dụng backend FastAPI và frontend React + TypeScript + Vite.

## 1. Tổng quan

Dự án gồm 2 phần chính:

- Backend Python/FastAPI: xử lý upload ảnh/video, gọi YOLOv8, trả về kết quả bounding box.
- Frontend React + TypeScript: giao diện quản lý dữ liệu và hiển thị kết quả phát hiện trên ảnh/video.

## 2. Công nghệ sử dụng

- Python 3.10+
- FastAPI
- Uvicorn
- Ultralytics YOLOv8
- PyTorch
- React
- TypeScript
- Vite

## 3. Cấu trúc thư mục

```text
Vehicle-Detection-AI/
├── data/
├── models/
├── src/
│   ├── backend/
│   │   └── app.py
│   ├── controller/
│   ├── model/
│   └── ui/
├── uploads/
├── runs/
├── requirements.txt
├── README.md
├── yolov8n.pt
└── .venv/
```

## 4. Yêu cầu môi trường

- Python 3.10+
- Node.js 18+
- npm
- Git

## 5. Cài đặt

### 5.1 Tạo môi trường Python

Windows PowerShell:

```powershell
cd E:\Vehicle-Detection-AI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
cd Vehicle-Detection-AI
python3 -m venv .venv
source .venv/bin/activate
```

### 5.2 Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 5.3 Cài đặt frontend dependencies

```bash
cd src/ui
npm install
```

## 6. Chạy ứng dụng

### 6.1 Chạy backend

Từ thư mục gốc:

```powershell
cd E:\Vehicle-Detection-AI
.\.venv\Scripts\Activate.ps1
python -m uvicorn src.backend.app:app --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại:

- http://127.0.0.1:8000
- health check: http://127.0.0.1:8000/health

### 6.2 Chạy frontend

Mở terminal mới:

```powershell
cd E:\Vehicle-Detection-AI\src\ui
npm run dev -- --host 0.0.0.0 --port 4179
```

Frontend sẽ chạy tại:

- http://localhost:4179/

## 7. Truy cập giao diện

Mở trình duyệt và vào:

```text
http://localhost:4179/
```

Từ đây bạn có thể:

- upload ảnh/video
- xem dữ liệu trong Data Management
- chọn file để phát hiện xe
- chạy YOLOv8 trên hình ảnh/video

## 8. Build production

```bash
cd src/ui
npm run build
```

## 9. Gỡ lỗi thường gặp

### Port đã được sử dụng

Nếu port 8000 hoặc 4179 đang bận, hãy đổi port:

```powershell
python -m uvicorn src.backend.app:app --host 0.0.0.0 --port 8001
npm run dev -- --host 0.0.0.0 --port 4180
```

### CORS lỗi kết nối frontend-backend

Đảm bảo backend đang chạy và frontend đang gọi đúng base URL:

```text
http://127.0.0.1:8000
```

### Không thấy box phát hiện

- Kiểm tra backend đã chạy
- Kiểm tra file upload đúng định dạng JPG/PNG/MP4
- Kiểm tra dữ liệu trả về từ /detect

## 10. Lưu ý

- Dự án đang dùng mô hình YOLOv8 `best.pt` trong thư mục `models/`
- Upload file thực tế sẽ được lưu trong `uploads/`
- Kết quả phát hiện sẽ được lưu trong `runs/`

## 11. License

Dự án phục vụ mục đích học tập và nghiên cứu trong khuôn khổ bài tập lớn AI/Computer Vision.