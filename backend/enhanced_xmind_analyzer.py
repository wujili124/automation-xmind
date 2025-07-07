#!/usr/bin/env python3
"""
增强版XMind文件分析器
使用MarkerRegistry进行标识符识别和管理
"""

import io
import os
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Set, Tuple
from xmindparser import xmind_to_dict
from collections import defaultdict

# 导入标识符注册表
from marker_registry import MarkerRegistry

logger = logging.getLogger(__name__)

class EnhancedXMindAnalyzer:
    """增强版XMind文件分析器，提供更强大的标识符识别和管理功能"""
    
    def __init__(self):
        """初始化增强版XMind分析器"""
        # 创建标识符注册表
        self.marker_registry = MarkerRegistry()
        
        # 存储解析后的节点数据
        self.parsed_nodes = []
        self.filename = ""
        
        # 记录发现的标识符
        self.discovered_markers = set()
        self.unknown_markers = []
        
        logger.info("增强版XMind分析器初始化完成")
    
    def analyze_markers(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        分析XMind文件，提取标识符信息
        
        Args:
            file_content: XMind文件的字节内容
            filename: 文件名
            
        Returns:
            包含标识符统计信息的字典
        """
        try:
            self.filename = filename
            logger.info(f"开始分析XMind文件: {filename}")
            
            # 清空之前的数据
            self.parsed_nodes = []
            self.discovered_markers = set()
            self.unknown_markers = []
            
            # 将字节内容转换为文件对象
            file_obj = io.BytesIO(file_content)
            
            # 解析XMind文件
            xmind_data = xmind_to_dict(file_obj)
            logger.info("XMind文件解析成功")
            
            # 提取所有节点并分析标识符
            all_nodes = []
            marker_stats = defaultdict(int)
            
            # 处理所有工作表
            for sheet_idx, sheet in enumerate(xmind_data):
                root_topic = sheet.get('topic', {})
                # 使用sheet索引作为顶层索引，确保不同sheet的节点顺序正确
                sheet_base_index = sheet_idx * 10000
                self._extract_nodes_recursive(root_topic, [], all_nodes, marker_stats, 1, sheet_base_index)
            
            # 保存解析的节点数据供后续使用
            self.parsed_nodes = all_nodes
            
            # 统计适合冒烟测试的节点数量
            suitable_nodes = self._count_suitable_smoke_nodes(all_nodes)
            
            # 构建返回结果 - 支持所有发现的标识符
            markers_found = []
            for marker_id, count in marker_stats.items():
                # 获取包含该标识符的节点示例
                sample_nodes = [
                    node['title'] for node in all_nodes 
                    if marker_id in node.get('markers', [])
                ][:3]  # 最多显示3个示例
                
                # 获取标识符信息
                marker_info = self.marker_registry.get_marker_info(marker_id)
                
                if marker_info:
                    # 使用注册表中的信息
                    symbol = marker_info['symbol']
                    category = marker_info.get('category', '未分类')
                    icon = marker_info.get('icon', '🔖')
                else:
                    # 为未知标识符生成友好名称
                    symbol = self._generate_friendly_name(marker_id)
                    category = '未知'
                    icon = '❓'
                    
                    # 记录未知标识符
                    self.unknown_markers.append({
                        'markerId': marker_id,
                        'symbol': symbol,
                        'raw_samples': sample_nodes
                    })
                
                markers_found.append({
                    "markerId": marker_id,
                    "symbol": symbol,
                    "category": category,
                    "icon": icon,
                    "count": count,
                    "sample_nodes": sample_nodes
                })
            
            # 按类别和计数排序
            markers_found.sort(key=lambda x: (-x['count'], x.get('category', ''), x['markerId']))
            
            # 构建结果
            result = {
                "filename": filename,
                "markers_found": markers_found,
                "total_nodes": len(all_nodes),
                "suitable_for_smoke": suitable_nodes,
                "file_data": base64.b64encode(file_content).decode('utf-8'),  # 保留原始数据供后续使用
                "unknown_markers": self.unknown_markers,
                "categories": self._get_marker_categories(markers_found)
            }
            
            # 统计标识符类型
            known_markers = [m for m in markers_found if self.marker_registry.get_marker_info(m['markerId'])]
            unknown_count = len(markers_found) - len(known_markers)
            
            logger.info(f"分析完成: 总节点数={len(all_nodes)}, 发现标识符={len(markers_found)}, 未知标识符={unknown_count}, 适合冒烟测试={suitable_nodes}")
            
            if unknown_count > 0:
                logger.info(f"🔍 发现 {unknown_count} 个未知标识符:")
                for marker in self.unknown_markers:
                    logger.info(f"  ❓ {marker['markerId']} → {marker['symbol']}")
            
            return result
            
        except Exception as e:
            logger.error(f"XMind文件分析失败: {str(e)}")
            raise Exception(f"XMind文件分析失败: {str(e)}")
    
    def _extract_nodes_recursive(self, topic: Dict, path: List[str], all_nodes: List[Dict], marker_stats: Dict, level: int = 1, xmind_index: int = 0):
        """
        递归提取节点信息
        
        Args:
            topic: 当前主题节点
            path: 节点路径
            all_nodes: 所有节点列表
            marker_stats: 标识符统计
            level: 节点层级
            xmind_index: XMind中的原始顺序索引
        """
        if not isinstance(topic, dict):
            return
            
        title = topic.get('title', '').strip()
        if not title:
            return
            
        current_path = path + [title]
        
        # 提取节点的标识符
        markers, raw_markers = self._extract_node_markers(topic)
        
        # 统计标识符
        for marker in markers:
            marker_stats[marker] += 1
            self.discovered_markers.add(marker)
        
        # 构建节点信息
        node_info = {
            'title': title,
            'path': ' > '.join(current_path),
            'level': level,
            'markers': markers,
            'raw_markers': raw_markers,  # 保存原始标识符数据
            'has_children': self._has_children(topic),
            'xmind_index': xmind_index  # 添加XMind中的原始顺序索引
        }
        
        all_nodes.append(node_info)
        
        # 递归处理子节点
        children = self._get_children(topic)
        for idx, child in enumerate(children):
            # 为子节点生成顺序索引，确保唯一性
            child_index = xmind_index * 1000 + idx + 1
            self._extract_nodes_recursive(child, current_path, all_nodes, marker_stats, level + 1, child_index)
    
    def _extract_node_markers(self, topic: Dict) -> Tuple[List[str], List[Any]]:
        """
        提取节点的标识符
        
        Args:
            topic: XMind主题节点
            
        Returns:
            (标识符ID列表, 原始标识符数据列表)
        """
        markers = []
        raw_markers = []
        
        # 检查所有可能包含标识符的字段
        marker_fields = ['markers', 'marker', 'makers', 'icons', 'labels', 'flags', 'priorities']
        
        for field in marker_fields:
            if field in topic and topic[field]:
                logger.debug(f"在字段'{field}'中发现数据: {topic[field]}")
                
                # XMind文件中的markers字段包含标识符信息
                marker_refs = topic[field] if isinstance(topic[field], list) else [topic[field]]
                
                for marker_ref in marker_refs:
                    logger.debug(f"处理标识符引用: {marker_ref}, 类型: {type(marker_ref)}")
                    
                    # 保存原始标识符数据
                    raw_markers.append({
                        'field': field,
                        'value': marker_ref
                    })
                    
                    # 使用标识符注册表映射标识符
                    marker_id = self.marker_registry.map_marker(marker_ref)
                    if marker_id:
                        if marker_id not in markers:  # 避免重复
                            markers.append(marker_id)
                            logger.debug(f"成功映射标识符: {marker_ref} -> {marker_id}")
                        else:
                            logger.debug(f"标识符已存在，跳过: {marker_id}")
                    else:
                        # 对于无法映射的标识符，尝试生成一个唯一ID
                        unknown_id = self._generate_unknown_marker_id(marker_ref)
                        if unknown_id and unknown_id not in markers:
                            markers.append(unknown_id)
                            logger.info(f"生成未知标识符ID: {marker_ref} -> {unknown_id}")
        
        # 如果没有通过标准字段找到标识符，检查其他可能包含标识符的字段
        if not markers:
            for key, value in topic.items():
                if key not in ['title', 'topics', 'note', 'link', 'position'] and value and key not in marker_fields:
                    # 检查是否包含标识符相关数据
                    if isinstance(value, list) or isinstance(value, str):
                        logger.debug(f"在非标准字段'{key}'中发现疑似标识符数据: {value}")
                        
                        # 保存原始数据
                        raw_markers.append({
                            'field': key,
                            'value': value
                        })
                        
                        # 尝试映射
                        marker_id = self.marker_registry.map_marker(value)
                        if marker_id and marker_id not in markers:
                            markers.append(marker_id)
                            logger.info(f"从非标准字段'{key}'成功映射标识符: {value} -> {marker_id}")
        
        if markers:
            logger.debug(f"节点 '{topic.get('title', 'unknown')}' 最终提取到的标识符: {markers}")
        
        return markers, raw_markers
    
    def _generate_unknown_marker_id(self, marker_ref: Any) -> Optional[str]:
        """为未知标识符生成唯一ID"""
        try:
            if isinstance(marker_ref, dict):
                # 尝试从字典中提取ID
                for field in ['markerId', 'id', 'name', 'type']:
                    if field in marker_ref and marker_ref[field]:
                        return f"{marker_ref[field]}"
                
                # 如果没有找到合适的字段，使用字典的字符串表示
                return f"marker-{hash(str(marker_ref)) % 10000}"
            
            elif isinstance(marker_ref, str):
                # 清理字符串，移除特殊字符
                import re
                clean_str = re.sub(r'[^a-zA-Z0-9_-]', '', marker_ref.lower())
                if clean_str:
                    return f"{clean_str}"
                else:
                    return f"marker-{hash(marker_ref) % 10000}"
            
            else:
                # 其他类型
                return f"{type(marker_ref).__name__}-{hash(str(marker_ref)) % 10000}"
        
        except Exception as e:
            logger.warning(f"生成未知标识符ID失败: {e}")
            return None
    
    def _generate_friendly_name(self, marker_id: str) -> str:
        """为标识符生成友好名称"""
        # 处理特殊的标识符类型
        if 'flag' in marker_id:
            color = marker_id.replace('flag', '').replace('-', '')
            if color:
                # 颜色映射
                color_map = {
                    'red': '红',
                    'yellow': '黄',
                    'green': '绿',
                    'blue': '蓝',
                    'black': '黑',
                    'white': '白',
                    'purple': '紫',
                    'orange': '橙'
                }
                color_zh = color_map.get(color, color)
                return f"{color_zh}旗"
            return "旗标"
        
        elif 'star' in marker_id:
            color = marker_id.replace('star', '').replace('-', '')
            if color:
                # 颜色映射
                color_map = {
                    'red': '红',
                    'yellow': '黄',
                    'green': '绿',
                    'blue': '蓝',
                    'black': '黑',
                    'white': '白',
                    'purple': '紫',
                    'orange': '橙'
                }
                color_zh = color_map.get(color, color)
                return f"{color_zh}星"
            return "星标"
        
        elif 'priority' in marker_id or marker_id.isdigit():
            # 优先级
            priority = marker_id.replace('priority', '').replace('-', '')
            if priority.isdigit():
                return f"优先级{priority}"
            return "优先级"
        
        # 将连字符替换为空格，首字母大写
        name = ' '.join(word.capitalize() for word in marker_id.split('-'))
        return name
    
    def _has_children(self, topic: Dict) -> bool:
        """检查节点是否有子节点"""
        return len(self._get_children(topic)) > 0
    
    def _get_children(self, topic: Dict) -> List[Dict]:
        """获取节点的子节点列表"""
        children = []
        
        # 处理不同的XMind格式
        if 'topics' in topic and isinstance(topic['topics'], list):
            children = topic['topics']
        elif 'children' in topic:
            if isinstance(topic['children'], list):
                children = topic['children']
            elif isinstance(topic['children'], dict):
                children_data = topic['children']
                if 'attached' in children_data and isinstance(children_data['attached'], list):
                    children = children_data['attached']
                elif 'topics' in children_data and isinstance(children_data['topics'], list):
                    children = children_data['topics']
        
        return children
    
    def _count_suitable_smoke_nodes(self, all_nodes: List[Dict]) -> int:
        """统计适合作为冒烟测试的节点数量"""
        suitable_count = 0
        
        for node in all_nodes:
            if self._is_suitable_for_smoke_test(node):
                suitable_count += 1
                
        return suitable_count
    
    def _is_suitable_for_smoke_test(self, node: Dict) -> bool:
        """判断节点是否适合作为冒烟测试用例"""
        # 检查是否包含标识符
        if not node.get('markers'):
            return False
            
        # 检查节点层级（3-5层比较合适）
        level = node.get('level', 0)
        if level < 2 or level > 5:
            return False
            
        # 检查节点描述是否包含测试相关的动作词
        title = node.get('title', '').lower()
        test_keywords = ['测试', '验证', '检查', '校验', '确认', '登录', '注册', '支付', 
                        '搜索', '查询', '添加', '删除', '修改', '操作', '功能']
        
        if not any(keyword in title for keyword in test_keywords):
            return False
            
        # 排除配置类节点
        config_keywords = ['配置', '环境', '数据准备', '初始化', '设置', '安装', '部署']
        if any(keyword in title for keyword in config_keywords):
            return False
            
        return True
    
    def _get_marker_categories(self, markers_found: List[Dict]) -> Dict[str, int]:
        """统计标识符类别"""
        categories = defaultdict(int)
        
        for marker in markers_found:
            category = marker.get('category', '未知')
            categories[category] += 1
        
        return dict(categories)
    
    def get_parsed_nodes(self) -> List[Dict]:
        """获取已解析的节点数据"""
        return self.parsed_nodes
    
    def get_filename(self) -> str:
        """获取文件名"""
        return self.filename
    
    def register_custom_marker(self, marker_id: str, symbol: str, category: str = "自定义") -> Dict:
        """注册自定义标识符"""
        return self.marker_registry.register_custom_marker(marker_id, symbol, category)
    
    def get_all_markers(self) -> List[Dict]:
        """获取所有已知的标识符"""
        return self.marker_registry.get_all_markers()
    
    def get_unknown_markers(self) -> List[Dict]:
        """获取未知的标识符"""
        return self.unknown_markers
    
    def learn_marker_mappings(self, mappings: List[Dict]) -> None:
        """学习多个标识符映射"""
        for mapping in mappings:
            if 'original' in mapping and 'mappedTo' in mapping:
                self.marker_registry.learn_marker_mapping(mapping['original'], mapping['mappedTo'])


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建增强版XMind分析器
    analyzer = EnhancedXMindAnalyzer()
    
    # 测试文件路径
    test_file = "test.xmind"
    
    # 检查文件是否存在
    if os.path.exists(test_file):
        with open(test_file, 'rb') as f:
            file_content = f.read()
            
        # 分析XMind文件
        result = analyzer.analyze_markers(file_content, test_file)
        
        print(f"分析结果: 找到 {len(result['markers_found'])} 个标识符")
        for marker in result['markers_found']:
            print(f"{marker['markerId']} - {marker['symbol']} ({marker['count']}个节点)")
        
        print(f"\n未知标识符: {len(result['unknown_markers'])}个")
        for marker in result['unknown_markers']:
            print(f"{marker['markerId']} - {marker['symbol']}")
    else:
        print(f"测试文件不存在: {test_file}") 