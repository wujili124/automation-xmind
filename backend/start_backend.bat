@echo off
REM 后端服务启动脚本 (Windows版本)
REM 用于在开发环境中自动启动Python FastAPI服务

echo 🐍 启动Python后端服务...

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo ❌ 未找到虚拟环境，请先运行以下命令创建：
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    exit /b 1
)

REM 激活虚拟环境
echo 📦 激活虚拟环境...
call venv\Scripts\activate

REM 检查依赖是否安装
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 📥 安装Python依赖...
    pip install -r requirements.txt
)

REM 启动服务
echo 🚀 启动FastAPI服务 (http://localhost:8000)...
python main.py 