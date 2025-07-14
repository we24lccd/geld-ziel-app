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