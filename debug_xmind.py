#!/usr/bin/env python3
"""
XMind文件调试工具 - 帮助用户分析XMind文件中的标识符
"""

import sys
import requests
import json

def debug_xmind_file(file_path):
    """调试XMind文件，显示标识符信息"""
    print(f"🔍 正在分析XMind文件: {file_path}")
    print("=" * 60)
    
    try:
        # 读取文件
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/octet-stream')}
            
            # 调用调试接口
            response = requests.post('http://localhost:8000/api/debug/analyze', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print_debug_result(result)
            else:
                print(f"❌ 调试失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器，请确保服务器在运行")
        print("   启动命令: cd backend && source venv/bin/activate && python main.py")
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {str(e)}")

def print_debug_result(result):
    """打印调试结果"""
    print(f"📁 文件名: {result['filename']}")
    print(f"📊 总节点数: {result['total_nodes']}")
    print(f"🏷️  总标识符数: {result['total_markers']}")
    print(f"🎯 唯一标识符类型: {result['unique_marker_types']}")
    print()
    
    if result['total_markers'] == 0:
        print("⚠️  您的XMind文件中没有发现任何标识符！")
        print()
        print("📝 如何添加标识符:")
        print("1. 在XMind中选择要标记的节点")
        print("2. 右键选择 '标记' → '标识符'")
        print("3. 选择以下支持的标识符之一:")
        
        supported = result.get('supported_markers', [])
        for marker in supported:
            print(f"   • {marker['name']}")
        print()
        print("4. 保存文件后重新上传")
        print()
        return
    
    print("🎯 发现的标识符类型:")
    marker_types = result.get('marker_types', {})
    
    if marker_types:
        for marker_id, info in marker_types.items():
            count = info['count']
            examples = info.get('examples', [])
            print(f"   • {marker_id}: {count} 个")
            if examples:
                print(f"     示例节点: {', '.join(examples[:3])}")
        print()
    
    print("📋 支持的标识符对照表:")
    supported = result.get('supported_markers', [])
    for marker in supported:
        status = "✅ 已发现" if marker['id'] in marker_types else "❌ 未发现"
        print(f"   {status} {marker['name']} (ID: {marker['id']})")
    
    print()
    if result['total_markers'] > 0:
        print("🎉 您的文件包含标识符，可以继续进行冒烟用例导出！")
    else:
        print("💡 建议在XMind中为测试用例节点添加标识符以获得更好的导出效果")

def main():
    """主函数"""
    print("🚀 XMind文件标识符调试工具")
    print("帮助您分析XMind文件中的标识符信息")
    print()
    
    if len(sys.argv) != 2:
        print("使用方法:")
        print("  python debug_xmind.py <xmind文件路径>")
        print()
        print("示例:")
        print("  python debug_xmind.py ~/Documents/测试用例.xmind")
        return
    
    file_path = sys.argv[1]
    debug_xmind_file(file_path)

if __name__ == "__main__":
    main() 