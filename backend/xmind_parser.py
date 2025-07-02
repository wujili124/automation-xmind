import io
import logging
from typing import Dict, List, Any, Optional
from xmindparser import xmind_to_dict
import base64

logger = logging.getLogger(__name__)

class XMindAnalyzer:
    """XMind文件分析器，提取标识符和节点信息"""
    
    def __init__(self):
        # XMind标识符映射配置（与tasks.md中定义一致）
        self.xmind_markers = [
            {"symbol": "重要 (红色叹号)", "markerId": "important"},
            {"symbol": "优先级1 (红色1)", "markerId": "priority-1"},
            {"symbol": "优先级2 (橙色2)", "markerId": "priority-2"},
            {"symbol": "优先级3 (黄色3)", "markerId": "priority-3"},
            {"symbol": "优先级4 (绿色4)", "markerId": "priority-4"},
            {"symbol": "优先级5 (灰色5)", "markerId": "priority-5"},
            {"symbol": "红旗", "markerId": "flag-red"},
            {"symbol": "黄旗", "markerId": "flag-yellow"},
            {"symbol": "红星", "markerId": "star-red"},
            {"symbol": "黄星", "markerId": "star-yellow"},
        ]
        
        # 创建markerId到symbol的映射
        self.marker_id_to_symbol = {m["markerId"]: m["symbol"] for m in self.xmind_markers}
        
        # 存储解析后的节点数据，供后续导出使用
        self.parsed_nodes = []
        self.filename = ""
    
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
            
            # 将字节内容转换为文件对象
            file_obj = io.BytesIO(file_content)
            
            # 解析XMind文件
            xmind_data = xmind_to_dict(file_obj)
            logger.info("XMind文件解析成功")
            
            # 提取所有节点并分析标识符
            all_nodes = []
            marker_stats = {}
            
            for sheet in xmind_data:
                root_topic = sheet.get('topic', {})
                self._extract_nodes_recursive(root_topic, [], all_nodes, marker_stats)
            
            # 保存解析的节点数据供后续使用
            self.parsed_nodes = all_nodes
            
            # 统计适合冒烟测试的节点数量
            suitable_nodes = self._count_suitable_smoke_nodes(all_nodes)
            
            # 构建返回结果
            markers_found = []
            for marker_id, count in marker_stats.items():
                if marker_id in self.marker_id_to_symbol:
                    # 获取包含该标识符的节点示例
                    sample_nodes = [
                        node['title'] for node in all_nodes 
                        if marker_id in node.get('markers', [])
                    ][:3]  # 最多显示3个示例
                    
                    markers_found.append({
                        "markerId": marker_id,
                        "symbol": self.marker_id_to_symbol[marker_id],
                        "count": count,
                        "sample_nodes": sample_nodes
                    })
            
            result = {
                "filename": filename,
                "markers_found": markers_found,
                "total_nodes": len(all_nodes),
                "suitable_for_smoke": suitable_nodes
            }
            
            logger.info(f"分析完成: 总节点数={len(all_nodes)}, 发现标识符={len(markers_found)}, 适合冒烟测试={suitable_nodes}")
            return result
            
        except Exception as e:
            logger.error(f"XMind文件分析失败: {str(e)}")
            raise Exception(f"XMind文件分析失败: {str(e)}")
    
    def _extract_nodes_recursive(self, topic: Dict, path: List[str], all_nodes: List[Dict], marker_stats: Dict, level: int = 1):
        """
        递归提取节点信息
        
        Args:
            topic: 当前主题节点
            path: 节点路径
            all_nodes: 所有节点列表
            marker_stats: 标识符统计
            level: 节点层级
        """
        if not isinstance(topic, dict):
            return
            
        title = topic.get('title', '').strip()
        if not title:
            return
            
        current_path = path + [title]
        
        # 提取节点的标识符
        markers = self._extract_node_markers(topic)
        
        # 统计标识符
        for marker in markers:
            marker_stats[marker] = marker_stats.get(marker, 0) + 1
        
        # 构建节点信息
        node_info = {
            'title': title,
            'path': ' > '.join(current_path),
            'level': level,
            'markers': markers,
            'has_children': 'topics' in topic and len(topic.get('topics', [])) > 0,
            'raw_topic': topic  # 保存原始数据供后续处理
        }
        
        all_nodes.append(node_info)
        
        # 递归处理子节点
        subtopics = topic.get('topics', [])
        for subtopic in subtopics:
            self._extract_nodes_recursive(subtopic, current_path, all_nodes, marker_stats, level + 1)
    
    def _extract_node_markers(self, topic: Dict) -> List[str]:
        """
        提取节点的标识符
        
        Args:
            topic: XMind主题节点
            
        Returns:
            标识符ID列表
        """
        markers = []
        
        # 检查所有可能包含标识符的字段 - 添加makers字段支持
        marker_fields = ['markers', 'marker', 'makers', 'icons', 'labels', 'flags', 'priorities']
        
        for field in marker_fields:
            if field in topic and topic[field]:
                logger.debug(f"在字段'{field}'中发现数据: {topic[field]}")
                
                # XMind文件中的markers字段包含标识符信息
                marker_refs = topic[field] if isinstance(topic[field], list) else [topic[field]]
                
                for marker_ref in marker_refs:
                    logger.debug(f"处理标识符引用: {marker_ref}, 类型: {type(marker_ref)}")
                    
                    # 根据XMind的marker结构提取markerId
                    marker_id = self._map_xmind_marker_to_id(marker_ref)
                    if marker_id:
                        if marker_id not in markers:  # 避免重复
                            markers.append(marker_id)
                            logger.info(f"成功映射标识符: {marker_ref} -> {marker_id}")
                        else:
                            logger.debug(f"标识符已存在，跳过: {marker_id}")
                    else:
                        # 记录无法映射的标识符，用于调试
                        logger.warning(f"无法映射的标识符: {marker_ref} (字段: {field})")
        
        # 如果没有通过标准字段找到标识符，检查其他可能包含标识符的字段
        if not markers:
            for key, value in topic.items():
                if key not in ['title', 'topics', 'note', 'link', 'position'] and value and key not in marker_fields:
                    # 检查是否包含标识符相关数据
                    if isinstance(value, list):
                        # 处理列表类型的数据
                        for item in value:
                            if isinstance(item, str) and any(keyword in item.lower() for keyword in ['marker', 'icon', 'flag', 'star', 'priority']):
                                logger.info(f"在字段'{key}'中发现疑似标识符数据: {value}")
                                # 尝试映射这些数据
                                for marker_ref in value:
                                    marker_id = self._map_xmind_marker_to_id(marker_ref)
                                    if marker_id and marker_id not in markers:
                                        markers.append(marker_id)
                                        logger.info(f"从字段'{key}'成功映射标识符: {marker_ref} -> {marker_id}")
                                break
                    elif isinstance(value, str) and any(keyword in value.lower() for keyword in ['marker', 'icon', 'flag', 'star', 'priority']):
                        logger.info(f"在字段'{key}'中发现疑似标识符数据: {value}")
                        # 尝试映射这个字符串
                        marker_id = self._map_xmind_marker_to_id(value)
                        if marker_id and marker_id not in markers:
                            markers.append(marker_id)
                            logger.info(f"从字段'{key}'成功映射标识符: {value} -> {marker_id}")
        
        if markers:
            logger.info(f"节点 '{topic.get('title', 'unknown')}' 最终提取到的标识符: {markers}")
        
        return markers
    
    def _map_xmind_marker_to_id(self, marker_ref: Any) -> Optional[str]:
        """
        将XMind内部标识符映射到自定义ID
        
        Args:
            marker_ref: XMind标识符引用
            
        Returns:
            映射后的标识符ID，如果无法映射则返回None
        """
        if marker_ref is None:
            return None
        
        # 处理字符串类型的标识符
        if isinstance(marker_ref, str):
            return self._map_string_marker(marker_ref)
        
        # 处理字典类型的标识符
        if isinstance(marker_ref, dict):
            return self._map_dict_marker(marker_ref)
        
        # 处理数字类型的标识符
        if isinstance(marker_ref, (int, float)):
            marker_str = str(int(marker_ref))
            if marker_str in ['1', '2', '3', '4', '5']:
                return f'priority-{marker_str}'
        
        logger.debug(f"未知的标识符格式: {marker_ref} (类型: {type(marker_ref)})")
        return None
    
    def _map_string_marker(self, marker_str: str) -> Optional[str]:
        """映射字符串类型的标识符"""
        marker_str = marker_str.lower().strip()
        
        # 直接字符串映射
        string_mapping = {
            # 官方标识符
            'important': 'important',
            'priority-1': 'priority-1',
            'priority-2': 'priority-2', 
            'priority-3': 'priority-3',
            'priority-4': 'priority-4',
            'priority-5': 'priority-5',
            'flag-red': 'flag-red',
            'flag-yellow': 'flag-yellow',
            'star-red': 'star-red',
            'star-yellow': 'star-yellow',
            
            # 变体形式
            'priority_1': 'priority-1',
            'priority_2': 'priority-2',
            'priority_3': 'priority-3',
            'priority_4': 'priority-4',
            'priority_5': 'priority-5',
            'priority1': 'priority-1',
            'priority2': 'priority-2',
            'priority3': 'priority-3',
            'priority4': 'priority-4',
            'priority5': 'priority-5',
            
            # 数字形式
            '1': 'priority-1',
            '2': 'priority-2',
            '3': 'priority-3',
            '4': 'priority-4',
            '5': 'priority-5',
            
            # 旗帜变体
            'flag_red': 'flag-red',
            'flag_yellow': 'flag-yellow',
            'red_flag': 'flag-red',
            'yellow_flag': 'flag-yellow',
            'red-flag': 'flag-red',
            'yellow-flag': 'flag-yellow',
            'flagred': 'flag-red',
            'flagyellow': 'flag-yellow',
            
            # 星星变体
            'star_red': 'star-red',
            'star_yellow': 'star-yellow',
            'red_star': 'star-red',
            'yellow_star': 'star-yellow',
            'red-star': 'star-red',
            'yellow-star': 'star-yellow',
            'starred': 'star-red',
            'staryellow': 'star-yellow',
            
            # 重要性变体
            'exclamation': 'important',
            'warning': 'important',
            'alert': 'important',
            'critical': 'important',
            '!': 'important',
            '重要': 'important',
            '警告': 'important',
            '关键': 'important',
            
            # 中文标识符
            '红旗': 'flag-red',
            '黄旗': 'flag-yellow',
            '红星': 'star-red',
            '黄星': 'star-yellow',
            '优先级1': 'priority-1',
            '优先级2': 'priority-2',
            '优先级3': 'priority-3',
            '优先级4': 'priority-4',
            '优先级5': 'priority-5',
        }
        
        # 首先尝试直接映射
        if marker_str in string_mapping:
            return string_mapping[marker_str]
        
        # 模糊匹配和正则表达式匹配
        import re
        
        # 匹配优先级数字
        priority_match = re.search(r'(?:priority|优先级)[-_\s]*([1-5])', marker_str)
        if priority_match:
            return f'priority-{priority_match.group(1)}'
        
        # 匹配单独的数字1-5
        if re.match(r'^[1-5]$', marker_str):
            return f'priority-{marker_str}'
        
        # 颜色和形状匹配
        if any(word in marker_str for word in ['red', '红', 'rouge']):
            if any(word in marker_str for word in ['flag', '旗', 'drapeau']):
                return 'flag-red'
            elif any(word in marker_str for word in ['star', '星', 'étoile']):
                return 'star-red'
            else:
                return 'important'  # 红色默认为重要
        
        if any(word in marker_str for word in ['yellow', '黄', 'jaune']):
            if any(word in marker_str for word in ['flag', '旗', 'drapeau']):
                return 'flag-yellow'
            elif any(word in marker_str for word in ['star', '星', 'étoile']):
                return 'star-yellow'
        
        # 重要性关键词
        if any(word in marker_str for word in ['important', '重要', 'critical', '关键', 'urgent', '紧急']):
            return 'important'
        
        return None
    
    def _map_dict_marker(self, marker_dict: Dict) -> Optional[str]:
        """映射字典类型的标识符"""
        # XMind中marker的常见字段
        possible_id_fields = ['markerId', 'markerID', 'id', 'type', 'name', 'symbol']
        
        marker_id = None
        for field in possible_id_fields:
            if field in marker_dict:
                marker_id = marker_dict[field]
                break
        
        if not marker_id:
            # 如果没找到ID字段，尝试使用整个字典的字符串表示
            marker_id = str(marker_dict)
        
        logger.debug(f"从字典提取的标识符ID: {marker_id}")
        
        # 递归调用字符串映射
        if isinstance(marker_id, str):
            return self._map_string_marker(marker_id)
        
        return None
    
    def _count_suitable_smoke_nodes(self, all_nodes: List[Dict]) -> int:
        """
        统计适合作为冒烟测试的节点数量
        
        Args:
            all_nodes: 所有节点列表
            
        Returns:
            适合冒烟测试的节点数量
        """
        suitable_count = 0
        
        for node in all_nodes:
            if self._is_suitable_for_smoke_test(node):
                suitable_count += 1
                
        return suitable_count
    
    def _is_suitable_for_smoke_test(self, node: Dict) -> bool:
        """
        判断节点是否适合作为冒烟测试用例
        
        Args:
            node: 节点信息
            
        Returns:
            是否适合冒烟测试
        """
        # 检查是否包含标识符
        if not node.get('markers'):
            return False
            
        # 检查节点层级（3-5层比较合适）
        level = node.get('level', 0)
        if level < 3 or level > 5:
            return False
            
        # 检查节点描述是否包含测试相关的动作词
        title = node.get('title', '').lower()
        test_keywords = ['测试', '验证', '检查', '校验', '确认', '登录', '注册', '支付', '搜索', '查询']
        
        if not any(keyword in title for keyword in test_keywords):
            return False
            
        # 排除配置类节点
        config_keywords = ['配置', '环境', '数据准备', '初始化', '设置']
        if any(keyword in title for keyword in config_keywords):
            return False
            
        return True
    
    def get_parsed_nodes(self) -> List[Dict]:
        """获取已解析的节点数据"""
        return self.parsed_nodes
    
    def get_filename(self) -> str:
        """获取文件名"""
        return self.filename 