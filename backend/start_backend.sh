#!/bin/bash

# 后端服务启动脚本
# 用于在开发环境中自动启动Python FastAPI服务

echo "🐍 启动Python后端服务..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行以下命令创建："
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 安装Python依赖..."
    pip install -r requirements.txt
fi

# 启动服务
echo "🚀 启动FastAPI服务 (http://localhost:8000)..."
python main.py 