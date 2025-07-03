@echo off
echo [92m启动开发环境...[0m

REM 检查是否存在Python虚拟环境
if not exist "backend\venv" (
    echo [94m创建Python虚拟环境...[0m
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
) else (
    echo [94m使用已存在的Python虚拟环境[0m
)

REM 启动后端服务
echo [92m启动后端服务...[0m
cd backend
call venv\Scripts\activate
REM 设置开发环境变量
set FRONTEND_URL=http://localhost:5173
start uvicorn main:app --reload --port 8000
cd ..

REM 启动前端服务
echo [92m启动前端服务...[0m
cd frontend
REM 安装依赖（如果需要）
if not exist "node_modules" (
    echo [94m安装前端依赖...[0m
    call npm install
)
REM 启动开发服务器
call npm run dev 