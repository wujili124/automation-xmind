#!/usr/bin/env python3
"""
XMind文件结构直接分析工具 - 帮助理解标识符数据格式
"""

import sys
import json
from pathlib import Path

try:
    from xmindparser import xmind_to_dict
except ImportError:
    print("❌ 请先安装xmindparser库:")
    print("   cd backend && source venv/bin/activate && pip install xmindparser")
    sys.exit(1)

def analyze_xmind_structure(file_path):
    """直接分析XMind文件的数据结构"""
    print(f"🔍 直接分析XMind文件结构: {file_path}")
    print("=" * 80)
    
    try:
        # 解析XMind文件
        xmind_data = xmind_to_dict(file_path)
        
        print(f"📊 工作表数量: {len(xmind_data)}")
        print()
        
        # 分析每个工作表
        total_nodes = 0
        total_markers = 0
        marker_examples = []
        
        for sheet_idx, sheet in enumerate(xmind_data):
            print(f"📋 工作表 {sheet_idx + 1}:")
            print(f"   键: {list(sheet.keys())}")
            
            if 'topic' in sheet:
                sheet_nodes, sheet_markers = analyze_topic_recursive(
                    sheet['topic'], 
                    level=1, 
                    path="",
                    marker_examples=marker_examples
                )
                total_nodes += sheet_nodes
                total_markers += sheet_markers
                print(f"   节点数: {sheet_nodes}")
                print(f"   标识符数: {sheet_markers}")
            print()
        
        print(f"🎯 总计:")
        print(f"   总节点数: {total_nodes}")
        print(f"   总标识符数: {total_markers}")
        print()
        
        if marker_examples:
            print("🏷️  发现的标识符示例:")
            for i, example in enumerate(marker_examples[:10]):
                print(f"   {i+1}. 节点: {example['title']}")
                print(f"      路径: {example['path']}")
                print(f"      原始标识符数据: {example['marker']}")
                print(f"      数据类型: {type(example['marker'])}")
                if isinstance(example['marker'], dict):
                    print(f"      字段: {list(example['marker'].keys())}")
                print()
        else:
            print("❌ 没有发现任何标识符！")
            print()
            print("🔍 让我们检查一些节点的完整数据结构...")
            print_sample_nodes(xmind_data)
        
        # 保存完整数据结构到文件
        output_file = "xmind_structure_debug.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(xmind_data, f, ensure_ascii=False, indent=2)
        print(f"💾 完整数据结构已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()

def analyze_topic_recursive(topic, level=1, path="", marker_examples=None):
    """递归分析主题节点"""
    if not isinstance(topic, dict):
        return 0, 0
    
    nodes = 0
    markers = 0
    
    title = topic.get('title', '').strip()
    if title:
        nodes = 1
        current_path = f"{path} > {title}" if path else title
        
        # 检查标识符
        if 'markers' in topic and topic['markers']:
            topic_markers = topic['markers']
            markers += len(topic_markers)
            
            # 保存标识符示例
            if marker_examples is not None:
                for marker in topic_markers:
                    marker_examples.append({
                        'title': title,
                        'path': current_path,
                        'level': level,
                        'marker': marker
                    })
        
        # 检查其他可能的标识符字段
        check_fields = ['marker', 'flag', 'icon', 'symbol', 'priority', 'labels', 'tags', 'style']
        for field in check_fields:
            if field in topic and topic[field]:
                print(f"   🔍 节点 '{title}' 包含字段 '{field}': {topic[field]}")
        
        # 递归处理子节点
        subtopics = topic.get('topics', [])
        for subtopic in subtopics:
            sub_nodes, sub_markers = analyze_topic_recursive(
                subtopic, level + 1, current_path, marker_examples
            )
            nodes += sub_nodes
            markers += sub_markers
    
    return nodes, markers

def print_sample_nodes(xmind_data, max_nodes=5):
    """打印一些节点的完整数据结构用于调试"""
    print("📋 节点数据结构示例:")
    
    node_count = 0
    for sheet in xmind_data:
        if 'topic' in sheet:
            if print_node_structure(sheet['topic'], level=1, max_nodes=max_nodes, current_count=node_count):
                break

def print_node_structure(topic, level=1, max_nodes=5, current_count=0):
    """打印节点结构"""
    if current_count >= max_nodes or not isinstance(topic, dict):
        return current_count >= max_nodes
    
    title = topic.get('title', '').strip()
    if title:
        print(f"   节点 {current_count + 1}: {title}")
        print(f"   层级: {level}")
        print(f"   所有字段: {list(topic.keys())}")
        
        # 特别关注可能包含标识符的字段
        for key, value in topic.items():
            if key in ['markers', 'marker', 'flag', 'icon', 'symbol', 'priority', 'labels', 'tags', 'style']:
                print(f"   {key}: {value} (类型: {type(value)})")
        
        print("   " + "-" * 40)
        current_count += 1
        
        if current_count >= max_nodes:
            return True
        
        # 递归处理子节点
        subtopics = topic.get('topics', [])
        for subtopic in subtopics:
            if print_node_structure(subtopic, level + 1, max_nodes, current_count):
                return True
            current_count += 1
            if current_count >= max_nodes:
                return True
    
    return False

def main():
    """主函数"""
    print("🚀 XMind文件结构直接分析工具")
    print("直接使用xmindparser库分析文件结构，不依赖API")
    print()
    
    if len(sys.argv) != 2:
        print("使用方法:")
        print("  python analyze_xmind_structure.py <xmind文件路径>")
        print()
        print("示例:")
        print("  python analyze_xmind_structure.py ~/Documents/学习报告.xmind")
        return
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    analyze_xmind_structure(file_path)

if __name__ == "__main__":
    main() 