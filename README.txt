- chạy web app:
docker build -t money-goal-app .
docker run -p 5000:5000 -v ${PWD}/data.json:/app/data.json -v ${PWD}/static:/app/static money-goal-app

- push app Flask “Geld-Ziel-App” lên Docker Hub:
🐋 Các bước đẩy app lên Docker Hub
1️⃣ Đảm bảo Dockerfile đã chuẩn
Hiện tại folder:

GELD-ZIEL-APP/
├── Dockerfile
├── app.py
├── requirements.txt
├── templates/
└── data.json

📦 Dockerfile tối thiểu:

Dockerfile

# Sử dụng Python slim
FROM python:3.11-slim

# Set thư mục làm việc
WORKDIR /app

# Copy file requirements trước để cache pip install
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose port Flask chạy
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]
2️⃣ Đăng nhập Docker Hub
✅ Trên máy:

docker login

Điền:
username Docker Hub
password hoặc token

3️⃣ Build image Docker
Giả sử Docker Hub username là hahh24
Muốn tên image là geld-ziel-app

📦 Build image:

docker build -t hahh24/geld-ziel-app:latest .
4️⃣ Test local image
Chạy thử:

docker run -p 5000:5000 hahh24/geld-ziel-app:latest
Truy cập: http://localhost:5000
✅ Nếu OK → tiếp tục.

5️⃣ Push image lên Docker Hub

docker push hahh24/geld-ziel-app:latest
6️⃣ Triển khai từ Docker Hub
Giờ bất kỳ ai cũng có thể pull app về chạy:

docker pull hahh24/geld-ziel-app:latest
docker run -p 5000:5000 hahh24/geld-ziel-app:latest
📦 Tổng kết
image public trên Docker Hub tại:
👉 https://hub.docker.com/r/hahh24/geld-ziel-app

Quy trình sau khi cập nhật code local:

Build lại image mới: docker build -t hahh24/geld-ziel-app:latest .
Push image mới lên Docker Hub: docker push hahh24/geld-ziel-app:latest

Để cập nhật code lên GitHub mỗi khi có thay đổi ở local, làm như sau:

1. Lưu thay đổi ở local

git add .
git commit -m "Nội dung cập nhật"

2. Push lên GitHub

git push origin main
(hoặc git push nếu nhánh mặc định là main)

Sau khi push xong, trang GitHub sẽ tự động cập nhật code mới nhất.

Tóm tắt:

git add .
git commit -m "..."
git push