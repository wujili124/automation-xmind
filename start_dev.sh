#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}启动开发环境...${NC}"

# 检查是否存在Python虚拟环境
if [ ! -d "backend/venv" ]; then
    echo -e "${BLUE}创建Python虚拟环境...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo -e "${BLUE}使用已存在的Python虚拟环境${NC}"
fi

# 启动后端服务
echo -e "${GREEN}启动后端服务...${NC}"
cd backend
source venv/bin/activate
# 设置开发环境变量
export FRONTEND_URL="http://localhost:5173"
uvicorn main:app --reload --port 8000 &
cd ..

# 启动前端服务
echo -e "${GREEN}启动前端服务...${NC}"
cd frontend
# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}安装前端依赖...${NC}"
    npm install
fi
# 启动开发服务器
npm run dev 