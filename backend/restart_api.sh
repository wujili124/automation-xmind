#!/bin/bash

echo "🔄 重启XMind API服务..."

# 1. 停止现有的Python服务
echo "1️⃣ 停止现有服务..."
pkill -f "python.*main.py" 2>/dev/null || echo "   没有找到运行中的服务"
sleep 2

# 2. 确保在正确的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
echo "2️⃣ 切换到目录: $SCRIPT_DIR"

# 3. 检查main.py文件是否存在
if [ ! -f "main.py" ]; then
    echo "❌ 错误: main.py文件不存在于当前目录"
    exit 1
fi

# 4. 启动服务
echo "3️⃣ 启动新的API服务..."
python main.py &
API_PID=$!

# 5. 等待服务启动
echo "4️⃣ 等待服务启动..."
sleep 3

# 6. 测试服务是否正常
echo "5️⃣ 测试服务健康状态..."
response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/ 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ API服务启动成功！PID: $API_PID"
    echo "🌐 服务地址: http://localhost:8000"
    echo "📝 日志文件: 查看终端输出"
    echo ""
    echo "⚡ 可用的API接口:"
    echo "   - GET  /                              健康检查"
    echo "   - POST /api/analyze                   分析XMind文件"
    echo "   - POST /api/export                    标准格式导出"
    echo "   - POST /api/export-template           模版格式导出"
    echo "   - POST /api/export-hierarchical       层级合并导出"
    echo "   - POST /api/export-enhanced-hierarchical 🔥增强层级合并导出"
    echo "   - POST /api/export-xmind              过滤XMind导出"
else
    echo "❌ API服务启动失败，HTTP状态码: $response"
    echo "🔍 请检查错误日志"
    exit 1
fi 