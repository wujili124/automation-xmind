#!/usr/bin/env python3
"""
测试XMind标识符筛选优化
验证当节点有标识符时，是否正确保留其所有子节点
"""

import json
import base64
import logging
from pathlib import Path
import tempfile
import zipfile
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_xmind_content():
    """
    创建测试用的XMind内容结构
    模拟以下结构：
    
    测试计划
    ├── 登录模块 [priority-1] ← 有标识符
    │   ├── 用户名密码登录 ← 子节点，无标识符
    │   ├── 验证码验证 ← 子节点，无标识符
    │   └── 登录失败处理 ← 子节点，无标识符
    ├── 注册模块 ← 无标识符
    │   ├── 邮箱注册 [priority-2] ← 子节点有标识符
    │   └── 手机注册 ← 无标识符
    └── 其他功能 ← 无标识符
        └── 普通功能 ← 无标识符
    """
    
    # 创建JSON格式的XMind内容，使用正确的字段名
    content = [
        {
            "title": "测试工作表",
            "rootTopic": {  # 使用 rootTopic 而不是 topic
                "title": "测试计划",
                "children": {  # 使用 children.attached 而不是 topics
                    "attached": [
                        {
                            "title": "登录模块",
                            "markers": [{"markerId": "priority-1"}],
                            "children": {
                                "attached": [
                                    {"title": "用户名密码登录"},
                                    {"title": "验证码验证"},
                                    {"title": "登录失败处理"}
                                ]
                            }
                        },
                        {
                            "title": "注册模块",
                            "children": {
                                "attached": [
                                    {
                                        "title": "邮箱注册",
                                        "markers": [{"markerId": "priority-2"}]
                                    },
                                    {"title": "手机注册"}
                                ]
                            }
                        },
                        {
                            "title": "其他功能",
                            "children": {
                                "attached": [
                                    {"title": "普通功能"}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    return content

def create_test_xmind_file():
    """创建测试用的XMind文件"""
    content = create_test_xmind_content()
    
    with tempfile.NamedTemporaryFile(suffix='.xmind', delete=False) as temp_file:
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 写入content.json
            zip_file.writestr('content.json', json.dumps(content, ensure_ascii=False, indent=2))
            
            # 写入基本的元数据文件
            zip_file.writestr('META-INF/manifest.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" password-hint="">
  <file-entry full-path="content.json" media-type="text/json"/>
</manifest>''')
            
            zip_file.writestr('meta.xml', '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">
  <Author>
    <Name>Test</Name>
  </Author>
</meta>''')
    
    return temp_file.name

def test_filter_optimization():
    """测试筛选优化功能"""
    
    try:
        # 创建测试文件
        test_file_path = create_test_xmind_file()
        logger.info(f"创建测试文件: {test_file_path}")
        
        # 读取文件并转换为base64
        with open(test_file_path, 'rb') as f:
            file_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 导入过滤器
        from xmind_marker_filter import xmind_filter
        
        # 测试筛选功能
        selected_markers = ["priority-1", "priority-2"]
        
        logger.info(f"开始测试筛选，选中标识符: {selected_markers}")
        
        result = xmind_filter.filter_xmind_by_markers(
            file_data=file_data,
            selected_markers=selected_markers,
            engine='lxml'
        )
        
        # 分析结果
        logger.info("=" * 50)
        logger.info("筛选结果分析:")
        logger.info(f"处理成功: {result['success']}")
        logger.info(f"处理详情: {result['processing_details']}")
        
        # 解码并分析筛选后的文件
        filtered_data = base64.b64decode(result['file_data'])
        
        # 保存筛选后的文件用于检查
        filtered_file_path = test_file_path.replace('.xmind', '_filtered.xmind')
        with open(filtered_file_path, 'wb') as f:
            f.write(filtered_data)
        
        logger.info(f"筛选后文件保存到: {filtered_file_path}")
        
        # 分析筛选后的文件内容
        analyze_filtered_content(filtered_file_path)
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # 清理临时文件
        if 'test_file_path' in locals() and os.path.exists(test_file_path):
            os.unlink(test_file_path)
        if 'filtered_file_path' in locals() and os.path.exists(filtered_file_path):
            os.unlink(filtered_file_path)

def analyze_filtered_content(file_path):
    """分析筛选后的文件内容"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # 读取content.json
            if 'content.json' in zip_file.namelist():
                content_data = zip_file.read('content.json').decode('utf-8')
                content = json.loads(content_data)
                
                logger.info("=" * 50)
                logger.info("筛选后内容分析:")
                
                def analyze_topic(topic, level=0, path=""):
                    indent = "  " * level
                    title = topic.get('title', 'untitled')
                    current_path = f"{path} > {title}" if path else title
                    
                    markers = topic.get('markers', [])
                    marker_info = f" [标识符: {[m.get('markerId', m) if isinstance(m, dict) else m for m in markers]}]" if markers else ""
                    
                    logger.info(f"{indent}- {title}{marker_info}")
                    
                    # 分析子节点 - 只处理children.attached结构
                    if 'children' in topic and 'attached' in topic['children']:
                        for subtopic in topic['children']['attached']:
                            analyze_topic(subtopic, level + 1, current_path)
                
                # 分析每个工作表 - 使用rootTopic
                for sheet in content:
                    if 'rootTopic' in sheet:
                        analyze_topic(sheet['rootTopic'])
                
                # 验证预期结果
                logger.info("=" * 50)
                logger.info("结果验证:")
                
                # 检查"登录模块"及其子节点是否都被保留
                login_module_found = False
                login_children_found = []
                
                def check_expected_nodes(topic, path=""):
                    nonlocal login_module_found, login_children_found
                    
                    title = topic.get('title', '')
                    current_path = f"{path} > {title}" if path else title
                    
                    if title == "登录模块":
                        login_module_found = True
                        logger.info(f"✅ 找到标记节点: {current_path}")
                        
                        # 检查子节点 - 只处理children.attached结构
                        if 'children' in topic and 'attached' in topic['children']:
                            for subtopic in topic['children']['attached']:
                                child_title = subtopic.get('title', '')
                                if child_title in ["用户名密码登录", "验证码验证", "登录失败处理"]:
                                    login_children_found.append(child_title)
                                    logger.info(f"✅ 找到被保留的子节点: {child_title}")
                    
                    # 递归检查 - 只处理children.attached结构
                    if 'children' in topic and 'attached' in topic['children']:
                        for subtopic in topic['children']['attached']:
                            check_expected_nodes(subtopic, current_path)
                
                for sheet in content:
                    if 'rootTopic' in sheet:
                        check_expected_nodes(sheet['rootTopic'])
                
                # 报告验证结果
                logger.info("=" * 50)
                logger.info("最终验证结果:")
                
                if login_module_found:
                    logger.info("✅ 登录模块（有标识符的节点）被正确保留")
                else:
                    logger.error("❌ 登录模块（有标识符的节点）丢失")
                
                expected_children = ["用户名密码登录", "验证码验证", "登录失败处理"]
                if len(login_children_found) == len(expected_children):
                    logger.info("✅ 所有子节点都被正确保留")
                    for child in login_children_found:
                        logger.info(f"   - {child}")
                else:
                    logger.error(f"❌ 子节点保留不完整，预期 {len(expected_children)} 个，实际 {len(login_children_found)} 个")
                    logger.error(f"   预期: {expected_children}")
                    logger.error(f"   实际: {login_children_found}")
                
    except Exception as e:
        logger.error(f"分析筛选后内容失败: {str(e)}")

if __name__ == "__main__":
    logger.info("开始测试XMind标识符筛选优化...")
    
    success = test_filter_optimization()
    
    if success:
        logger.info("✅ 测试完成")
    else:
        logger.error("❌ 测试失败") 