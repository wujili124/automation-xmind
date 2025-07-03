#!/bin/bash

# XMind冒烟测试用例导出工具 - 开发环境启动脚本
# 同时启动前端Vue.js和后端FastAPI服务

echo "🚀 XMind冒烟测试用例导出工具 - 开发环境启动"
echo "=================================================="

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js 16+"
    exit 1
fi

# 检查Python是否安装
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查frontend目录
if [ ! -d "frontend" ]; then
    echo "❌ frontend目录不存在"
    exit 1
fi

# 检查backend目录
if [ ! -d "backend" ]; then
    echo "❌ backend目录不存在"
    exit 1
fi

# 进入frontend目录
cd frontend

# 检查是否安装了npm依赖
if [ ! -d "node_modules" ]; then
    echo "📥 安装前端依赖..."
    npm install
fi

# 检查是否安装了concurrently
if ! npm list concurrently &> /dev/null; then
    echo "📥 安装concurrently..."
    npm install --save-dev concurrently
fi

echo ""
echo "🌟 启动服务："
echo "   🌐 前端: http://localhost:5173"
echo "   🐍 后端: http://localhost:8000"
echo ""
echo "💡 按 Ctrl+C 停止所有服务"
echo ""

# 启动开发服务器
npm run dev 