#!/usr/bin/env python3
"""
测试冒烟用例导出功能
"""
import requests
import json
import base64
import os

# API基础URL
API_BASE_URL = "http://localhost:8000"

def test_export_functionality():
    """测试导出功能"""
    print("🚀 开始测试冒烟用例导出功能...")
    
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
    
    # 4. 测试导出功能
    print("\n4️⃣ 测试导出功能...")
    if not analysis_data['markers_found']:
        print("❌ 没有找到标识符，无法测试导出")
        return
    
    # 选择所有标识符进行导出
    selected_markers = [marker['markerId'] for marker in analysis_data['markers_found']]
    print(f"✅ 选择标识符: {selected_markers}")
    
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
        
        print(f"✅ 导出成功: 生成 {len(test_cases)} 个冒烟用例")
        
        # 5. 验证导出结果
        print("\n5️⃣ 验证导出结果...")
        if len(test_cases) > 0:
            print("✅ 成功生成测试用例")
            
            # 显示第一个测试用例的详细信息
            first_case = test_cases[0]
            print(f"\n📋 示例测试用例:")
            print(f"   用例ID: {first_case['case_id']}")
            print(f"   标题: {first_case['title']}")
            print(f"   模块: {first_case['module']}")
            print(f"   优先级: {first_case['priority']}")
            print(f"   标识符: {first_case['markers']}")
            print(f"   测试步骤数: {len(first_case['steps'])}")
            
            # 显示测试步骤
            print(f"\n📝 测试步骤:")
            for step in first_case['steps'][:3]:  # 只显示前3步
                print(f"   {step['step']}. {step['action']} -> {step['expected']}")
            
            if len(first_case['steps']) > 3:
                print(f"   ... 还有 {len(first_case['steps']) - 3} 个步骤")
        
        else:
            print("❌ 没有生成任何测试用例")
            return
        
        # 6. 保存导出结果
        print("\n6️⃣ 保存导出结果...")
        output_file = "test_export_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_result, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {output_file}")
        
        print("\n🎉 测试完成! 所有功能正常工作")
        return True
        
    except Exception as e:
        print(f"❌ 导出过程出错: {e}")
        return False

if __name__ == "__main__":
    success = test_export_functionality()
    if success:
        print("\n✅ 测试通过")
    else:
        print("\n❌ 测试失败") 