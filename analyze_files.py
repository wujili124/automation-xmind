#!/usr/bin/env python3
"""
分析学习报告.xmind和冒烟用例导出模版.xlsx文件
"""

import json
import zipfile
import tempfile
import os
import logging
import pandas as pd
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_xmind_file(file_path):
    """分析XMind文件结构和标识符"""
    logger.info(f"🔍 分析XMind文件: {file_path}")
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # 检查文件列表
            file_list = zip_file.namelist()
            logger.info(f"📁 XMind文件包含: {file_list}")
            
            # 读取content.json
            if 'content.json' in file_list:
                content_data = zip_file.read('content.json').decode('utf-8')
                content = json.loads(content_data)
                
                logger.info("=" * 60)
                logger.info("📊 XMind内容结构分析:")
                logger.info(f"工作表数量: {len(content)}")
                
                # 分析第一个工作表
                if content:
                    sheet = content[0]
                    logger.info(f"第一个工作表标题: {sheet.get('title', 'untitled')}")
                    
                    # 统计节点和标识符
                    total_nodes = 0
                    nodes_with_markers = 0
                    marker_types = {}
                    all_markers = []
                    
                    def analyze_topic(topic, level=0, path=""):
                        nonlocal total_nodes, nodes_with_markers
                        
                        if not isinstance(topic, dict):
                            return
                        
                        total_nodes += 1
                        title = topic.get('title', 'untitled').strip()
                        current_path = f"{path} > {title}" if path else title
                        
                        # 分析标识符
                        markers = topic.get('markers', [])
                        if markers:
                            nodes_with_markers += 1
                            for marker in markers:
                                if isinstance(marker, dict):
                                    marker_id = marker.get('markerId', 'unknown')
                                    all_markers.append({
                                        'path': current_path,
                                        'title': title,
                                        'marker_id': marker_id,
                                        'marker_data': marker
                                    })
                                    
                                    if marker_id not in marker_types:
                                        marker_types[marker_id] = 0
                                    marker_types[marker_id] += 1
                                elif isinstance(marker, str):
                                    all_markers.append({
                                        'path': current_path,
                                        'title': title,
                                        'marker_id': marker,
                                        'marker_data': marker
                                    })
                                    
                                    if marker not in marker_types:
                                        marker_types[marker] = 0
                                    marker_types[marker] += 1
                        
                        # 递归处理子节点
                        if 'children' in topic and 'attached' in topic['children']:
                            for subtopic in topic['children']['attached']:
                                analyze_topic(subtopic, level + 1, current_path)
                        elif 'topics' in topic:
                            for subtopic in topic['topics']:
                                analyze_topic(subtopic, level + 1, current_path)
                    
                    # 分析根主题
                    if 'rootTopic' in sheet:
                        analyze_topic(sheet['rootTopic'])
                    elif 'topic' in sheet:
                        analyze_topic(sheet['topic'])
                    
                    logger.info("=" * 60)
                    logger.info("📈 统计信息:")
                    logger.info(f"总节点数: {total_nodes}")
                    logger.info(f"带标识符的节点数: {nodes_with_markers}")
                    logger.info(f"标识符覆盖率: {(nodes_with_markers/total_nodes*100):.1f}%")
                    
                    logger.info("=" * 60)
                    logger.info("🏷️  标识符类型统计:")
                    for marker_id, count in sorted(marker_types.items(), key=lambda x: x[1], reverse=True):
                        logger.info(f"  {marker_id}: {count} 个节点")
                    
                    logger.info("=" * 60)
                    logger.info("📝 带标识符的节点示例 (前10个):")
                    for i, marker_info in enumerate(all_markers[:10]):
                        logger.info(f"  {i+1}. [{marker_info['marker_id']}] {marker_info['title']}")
                        logger.info(f"     路径: {marker_info['path']}")
                    
                    if len(all_markers) > 10:
                        logger.info(f"     ... 还有 {len(all_markers) - 10} 个带标识符的节点")
                    
                    return {
                        'total_nodes': total_nodes,
                        'nodes_with_markers': nodes_with_markers,
                        'marker_types': marker_types,
                        'all_markers': all_markers
                    }
            
    except Exception as e:
        logger.error(f"❌ 分析XMind文件失败: {str(e)}")
        return None

def analyze_excel_template(file_path):
    """分析Excel模版文件"""
    logger.info(f"🔍 分析Excel模版文件: {file_path}")
    
    try:
        # 读取Excel文件
        xls = pd.ExcelFile(file_path)
        logger.info(f"📁 Excel文件包含工作表: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            logger.info(f"\n📊 分析工作表: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            logger.info(f"行数: {len(df)}")
            logger.info(f"列数: {len(df.columns)}")
            logger.info(f"列名: {list(df.columns)}")
            
            # 显示前几行数据
            logger.info("前5行数据:")
            logger.info(df.head().to_string())
            
            # 分析数据类型和非空情况
            logger.info("\n列信息:")
            for col in df.columns:
                non_null_count = df[col].count()
                total_count = len(df)
                data_type = df[col].dtype
                logger.info(f"  {col}: {non_null_count}/{total_count} 非空, 类型: {data_type}")
                
                # 显示一些示例值
                sample_values = df[col].dropna().head(3).tolist()
                if sample_values:
                    logger.info(f"    示例值: {sample_values}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 分析Excel文件失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("🚀 开始分析文件...")
    
    # 分析XMind文件
    xmind_path = "学习报告.xmind"
    if os.path.exists(xmind_path):
        xmind_result = analyze_xmind_file(xmind_path)
    else:
        logger.error(f"❌ XMind文件不存在: {xmind_path}")
        xmind_result = None
    
    logger.info("\n" + "=" * 80 + "\n")
    
    # 分析Excel模版
    excel_path = "冒烟用例导出模版.xlsx"
    if os.path.exists(excel_path):
        excel_result = analyze_excel_template(excel_path)
    else:
        logger.error(f"❌ Excel文件不存在: {excel_path}")
        excel_result = False
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ 分析完成！")
    
    # 生成对比建议
    if xmind_result and excel_result:
        logger.info("\n🔧 对比分析和建议:")
        logger.info("1. XMind文件包含丰富的标识符信息，可以用于筛选冒烟用例")
        logger.info("2. Excel模版定义了期望的输出格式")
        logger.info("3. 建议确保导出的数据格式与Excel模版保持一致")
        
        if xmind_result['nodes_with_markers'] > 0:
            logger.info(f"4. 发现 {xmind_result['nodes_with_markers']} 个带标识符的节点，可以生成对应数量的测试用例")
            logger.info("5. 主要标识符类型:")
            for marker_id, count in list(xmind_result['marker_types'].items())[:5]:
                logger.info(f"   - {marker_id}: {count} 个")

if __name__ == "__main__":
    main() 