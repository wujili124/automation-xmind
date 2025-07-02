#!/usr/bin/env python3
"""
测试新的基于markerId的XMind文件过滤功能
"""

import requests
import json
import base64
import os
from pathlib import Path
import tempfile

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_marker_filter_api():
    """测试基于markerId的XMind文件过滤API"""
    print("🧪 测试新的基于markerId的XMind文件过滤功能")
    print("=" * 60)
    
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
    
    # 3. 读取文件并转换为base64
    print("\n3️⃣ 读取并编码文件...")
    try:
        with open(test_file, 'rb') as f:
            file_content = f.read()
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        print(f"✅ 文件大小: {len(file_content):,} bytes")
        print(f"✅ Base64编码长度: {len(file_base64):,} 字符")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return
    
    # 4. 测试文件分析（获取markerId）
    print("\n4️⃣ 分析文件获取markerId...")
    try:
        # 先上传文件进行分析
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
            response = requests.post(f"{API_BASE_URL}/api/analyze", files=files)
        
        if response.status_code == 200:
            analysis_result = response.json()
            print(f"✅ 分析成功，发现 {len(analysis_result['markers_found'])} 种标识符:")
            
            for marker in analysis_result['markers_found']:
                print(f"   - {marker['markerId']}: {marker['symbol']} ({marker['count']}个)")
            
            # 选择第一个markerId进行测试
            selected_markers = [analysis_result['markers_found'][0]['markerId']]
            print(f"✅ 选择测试markerId: {selected_markers}")
            
        else:
            print(f"❌ 分析失败: {response.status_code} - {response.text}")
            # 使用默认的markerId进行测试
            selected_markers = ['flag-red']
            print(f"⚠️ 使用默认markerId进行测试: {selected_markers}")
            
    except Exception as e:
        print(f"❌ 文件分析失败: {e}")
        selected_markers = ['flag-red']
        print(f"⚠️ 使用默认markerId进行测试: {selected_markers}")
    
    # 5. 测试基于markerId的XMind过滤
    print("\n5️⃣ 测试基于markerId的XMind过滤...")
    try:
        filter_request = {
            "selected_markers": selected_markers,
            "file_data": file_base64,
            "test_case_titles": ["测试用例1", "测试用例2"]  # 这个参数现在不再使用，但保持兼容性
        }
        
        print(f"📤 发送过滤请求...")
        print(f"   - 选中标识符: {selected_markers}")
        print(f"   - 原始文件大小: {len(file_content):,} bytes")
        
        response = requests.post(
            f"{API_BASE_URL}/api/export-xmind",
            json=filter_request,
            timeout=120  # 增加超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 XMind过滤成功！")
            print(f"📊 处理详情:")
            
            details = result.get('processing_details', {})
            print(f"   - 原始大小: {details.get('original_size', 0):,} bytes")
            print(f"   - 过滤后大小: {details.get('filtered_size', 0):,} bytes")
            print(f"   - 压缩率: {details.get('compression_ratio', 'N/A')}")
            print(f"   - 处理引擎: {details.get('processing_engine', 'N/A')}")
            print(f"   - 工作表处理数: {details.get('sheets_processed', 0)}")
            print(f"   - 工作表删除数: {details.get('sheets_removed', 0)}")
            print(f"   - 节点删除数: {details.get('nodes_removed', 0)}")
            print(f"   - 目标标识符: {details.get('target_markers', [])}")
            
            # 6. 保存过滤后的文件进行验证
            print("\n6️⃣ 保存过滤后的文件进行验证...")
            try:
                filtered_data = base64.b64decode(result['file_data'])
                output_file = f"test_output_markers_filtered.xmind"
                
                with open(output_file, 'wb') as f:
                    f.write(filtered_data)
                
                print(f"✅ 过滤后文件已保存: {output_file}")
                print(f"✅ 文件大小: {len(filtered_data):,} bytes")
                
                # 验证文件完整性
                try:
                    import zipfile
                    with zipfile.ZipFile(output_file, 'r') as zf:
                        file_list = zf.namelist()
                        print(f"✅ 文件结构验证通过，包含 {len(file_list)} 个文件:")
                        for name in file_list[:10]:  # 显示前10个文件
                            print(f"     - {name}")
                        if len(file_list) > 10:
                            print(f"     ... 和其他 {len(file_list) - 10} 个文件")
                            
                except Exception as e:
                    print(f"⚠️ 文件结构验证失败: {e}")
                    
            except Exception as e:
                print(f"❌ 保存过滤结果失败: {e}")
            
        else:
            print(f"❌ XMind过滤失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ XMind过滤测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 基于markerId的XMind过滤功能测试完成")

if __name__ == "__main__":
    test_marker_filter_api() 