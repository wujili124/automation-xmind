#!/usr/bin/env python3
"""
测试XMind文件过滤API
"""
import requests
import json
import base64
import os
from pathlib import Path

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_xmind_filter_api():
    """测试XMind文件过滤API"""
    print("🚀 开始测试XMind文件过滤API...")
    
    # 1. 检查API健康状态
    print("\n1️⃣ 检查API健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"✅ API状态: {response.json()}")
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return
    
    # 2. 查找测试用的XMind文件
    print("\n2️⃣ 查找测试用的XMind文件...")
    test_files = []
    for root, dirs, files in os.walk(".."):
        for file in files:
            if file.endswith('.xmind'):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print("❌ 未找到测试用的XMind文件")
        return
    
    test_file = test_files[0]
    print(f"✅ 使用测试文件: {test_file}")
    
    # 3. 分析XMind文件
    print("\n3️⃣ 分析XMind文件...")
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
            response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
        
        if response.status_code != 200:
            print(f"❌ 分析失败: {response.text}")
            return
        
        analysis_data = response.json()
        print(f"✅ 分析完成: 发现 {len(analysis_data['markers_found'])} 种标识符")
        
        for marker in analysis_data['markers_found']:
            print(f"   • {marker['symbol']}: {marker['count']} 个节点")
    
    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        return
    
    # 4. 准备导出请求
    print("\n4️⃣ 准备导出请求...")
    if not analysis_data['markers_found']:
        print("❌ 没有找到标识符，无法测试导出")
        return
    
    # 选择第一个标识符进行测试
    selected_markers = [analysis_data['markers_found'][0]['markerId']]
    print(f"✅ 选择标识符: {selected_markers}")
    
    # 5. 测试导出冒烟用例
    print("\n5️⃣ 测试导出冒烟用例...")
    try:
        export_request = {
            "selected_markers": selected_markers,
            "file_data": analysis_data['file_data']
        }
        
        response = requests.post(f"{API_BASE_URL}/api/export", json=export_request)
        
        if response.status_code != 200:
            print(f"❌ 导出失败: {response.text}")
            return
        
        export_result = response.json()
        test_cases = export_result['smoke_test_suite']['test_cases']
        print(f"✅ 导出完成: 生成 {len(test_cases)} 个测试用例")
        
        # 提取测试用例标题
        test_case_titles = [tc['title'] for tc in test_cases]
        print(f"   测试用例标题: {test_case_titles[:3]}...")  # 显示前3个
        
    except Exception as e:
        print(f"❌ 导出过程出错: {e}")
        return
    
    # 6. 测试XMind文件过滤
    print("\n6️⃣ 测试XMind文件过滤...")
    try:
        filter_request = {
            "selected_markers": selected_markers,
            "file_data": analysis_data['file_data'],
            "test_case_titles": test_case_titles
        }
        
        response = requests.post(f"{API_BASE_URL}/api/export-xmind", json=filter_request)
        
        if response.status_code != 200:
            print(f"❌ XMind过滤失败: {response.text}")
            return
        
        filter_result = response.json()
        
        if filter_result['success']:
            print(f"✅ XMind过滤成功!")
            print(f"   原始大小: {filter_result['original_size']} bytes")
            print(f"   过滤后大小: {filter_result['filtered_size']} bytes")
            print(f"   保留节点数: {filter_result['nodes_filtered']}")
            
            # 可选：保存过滤后的文件用于验证
            filtered_data = base64.b64decode(filter_result['file_data'])
            output_file = "filtered_test_output.xmind"
            with open(output_file, 'wb') as f:
                f.write(filtered_data)
            print(f"   ✅ 过滤后文件已保存: {output_file}")
            
        else:
            print(f"❌ XMind过滤失败: {filter_result.get('message', '未知错误')}")
            return
        
    except Exception as e:
        print(f"❌ XMind过滤过程出错: {e}")
        return
    
    print("\n🎉 所有测试完成！XMind文件过滤API工作正常")

if __name__ == "__main__":
    test_xmind_filter_api() 