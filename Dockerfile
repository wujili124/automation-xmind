# 多阶段构建：前端构建阶段
FROM node:18-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# 后端运行阶段
FROM python:3.9-slim
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./

# 复制前端构建产物到static目录
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建启动脚本
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}' > start.sh && chmod +x start.sh

# 暴露端口 (Render会自动设置PORT环境变量)
EXPOSE ${PORT:-8000}

# 启动命令
CMD ["./start.sh"] 