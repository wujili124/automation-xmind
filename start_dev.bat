@echo off
REM XMind冒烟测试用例导出工具 - 开发环境启动脚本 (Windows版本)
REM 同时启动前端Vue.js和后端FastAPI服务

echo 🚀 XMind冒烟测试用例导出工具 - 开发环境启动
echo ==================================================

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装，请先安装Node.js 16+
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查frontend目录
if not exist "frontend" (
    echo ❌ frontend目录不存在
    pause
    exit /b 1
)

REM 检查backend目录
if not exist "backend" (
    echo ❌ backend目录不存在
    pause
    exit /b 1
)

REM 进入frontend目录
cd frontend

REM 检查是否安装了npm依赖
if not exist "node_modules" (
    echo 📥 安装前端依赖...
    npm install
)

REM 检查是否安装了concurrently
npm list concurrently >nul 2>&1
if errorlevel 1 (
    echo 📥 安装concurrently...
    npm install --save-dev concurrently
)

echo.
echo 🌟 启动服务：
echo    🌐 前端: http://localhost:5173
echo    🐍 后端: http://localhost:8000
echo.
echo 💡 按 Ctrl+C 停止所有服务
echo.

REM 启动开发服务器
npm run dev 