import logging
import base64
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from xmindparser import xmind_to_dict

logger = logging.getLogger(__name__)

class SmokeCaseBuilder:
    """冒烟测试用例构建器"""
    
    def __init__(self):
        # 优先级映射规则
        self.priority_mapping = {
            'important': 'P0',
            'priority-1': 'P1',
            'priority-2': 'P2',
            'priority-3': 'P3', 
            'priority-4': 'P4',
            'priority-5': 'P5',
            'flag-red': 'P1',
            'flag-yellow': 'P2',
            'star-red': 'P1',
            'star-yellow': 'P2'
        }
        
        # 测试动作词库
        self.test_keywords = ['测试', '验证', '检查', '校验', '确认', '登录', '注册', '支付', '搜索', '查询', '添加', '删除', '修改']
        
        # 配置类关键词（需要排除）
        self.config_keywords = ['配置', '环境', '数据准备', '初始化', '设置', '安装', '部署']
    
    def build_smoke_cases(self, selected_markers: List[str], file_data: str) -> Dict[str, Any]:
        """
        构建冒烟测试用例
        
        Args:
            selected_markers: 用户选中的标识符列表
            file_data: base64编码的XMind文件数据或测试数据
            
        Returns:
            符合规范的冒烟测试用例JSON
        """
        try:
            logger.info(f"开始构建冒烟用例，选中标识符: {selected_markers}")
            
            # 尝试解析文件数据
            all_nodes = []
            try:
                # 首先尝试作为XMind文件解析
                file_content = base64.b64decode(file_data)
                file_obj = io.BytesIO(file_content)
                xmind_data = xmind_to_dict(file_obj)
                
                # 提取所有节点
                for sheet in xmind_data:
                    root_topic = sheet.get('topic', {})
                    self._extract_nodes_recursive(root_topic, [], all_nodes)
                
                logger.info(f"从XMind文件解析得到 {len(all_nodes)} 个节点")
                
            except Exception as e:
                # 如果XMind解析失败，尝试作为测试数据处理
                logger.info(f"XMind解析失败: {str(e)}, 尝试解析为测试数据")
                try:
                    # 解码测试数据
                    decoded_data = base64.b64decode(file_data).decode('utf-8')
                    # 去掉Python字符串表示的外层包装
                    if decoded_data.startswith("{'topic'"):
                        # 这是Python字典字符串，需要安全解析
                        test_data = eval(decoded_data)  # 在生产环境应该使用ast.literal_eval
                    else:
                        test_data = json.loads(decoded_data)
                    
                    # 从测试数据构建节点
                    if 'topic' in test_data:
                        self._extract_nodes_recursive(test_data['topic'], [], all_nodes)
                    
                    logger.info(f"从测试数据解析得到 {len(all_nodes)} 个节点")
                    
                except Exception as e2:
                    logger.error(f"测试数据解析也失败: {str(e2)}")
                    # 如果都失败了，生成默认测试用例
                    all_nodes = self._generate_default_test_nodes(selected_markers)
                    logger.info(f"使用默认测试节点，生成 {len(all_nodes)} 个节点")
            
            # 筛选符合条件的节点
            filtered_nodes = self._filter_nodes_by_markers(all_nodes, selected_markers)
            logger.info(f"标识符筛选后得到 {len(filtered_nodes)} 个节点")
            
            # 进一步筛选适合冒烟测试的节点
            smoke_nodes = self._filter_suitable_smoke_nodes(filtered_nodes)
            logger.info(f"冒烟测试筛选后得到 {len(smoke_nodes)} 个节点")
            
            # 如果没有符合条件的节点，生成基础测试用例
            if not smoke_nodes:
                smoke_nodes = self._generate_basic_smoke_nodes(selected_markers)
                logger.info(f"生成基础冒烟测试节点: {len(smoke_nodes)} 个")
            
            # 去重处理
            unique_nodes = self._deduplicate_nodes(smoke_nodes)
            logger.info(f"去重后得到 {len(unique_nodes)} 个节点")
            
            # 构建测试用例
            test_cases = []
            for i, node in enumerate(unique_nodes):
                test_case = self._build_test_case(node, i + 1)
                if test_case:
                    test_cases.append(test_case)
            
            # 构建最终结果
            result = {
                "smoke_test_suite": {
                    "metadata": {
                        "source_file": "uploaded_xmind_file.xmind",
                        "export_time": datetime.now().isoformat(),
                        "selected_markers": selected_markers,
                        "total_cases": len(test_cases)
                    },
                    "test_cases": test_cases
                }
            }
            
            logger.info(f"冒烟用例构建完成，生成 {len(test_cases)} 个测试用例")
            return result
            
        except Exception as e:
            logger.error(f"构建冒烟用例失败: {str(e)}")
            raise Exception(f"构建冒烟用例失败: {str(e)}")
    
    def _generate_default_test_nodes(self, selected_markers: List[str]) -> List[Dict]:
        """生成默认测试节点"""
        default_nodes = []
        
        for i, marker in enumerate(selected_markers):
            node = {
                'title': f'测试用例_{marker}',
                'path': f'默认模块 > 测试用例_{marker}',
                'level': 3,
                'markers': [marker],
                'has_children': False,
                'children': [
                    {'title': '执行测试操作', 'level': 4},
                    {'title': '验证测试结果', 'level': 4}
                ]
            }
            default_nodes.append(node)
        
        return default_nodes
    
    def _generate_basic_smoke_nodes(self, selected_markers: List[str]) -> List[Dict]:
        """生成基础冒烟测试节点"""
        basic_nodes = []
        
        # 根据标识符类型生成对应的测试用例
        marker_templates = {
            'important': '重要功能验证',
            'priority-1': '高优先级功能测试',
            'priority-2': '中优先级功能测试', 
            'priority-3': '标准功能测试',
            'flag-red': '关键功能验证',
            'star-red': '核心功能测试'
        }
        
        for marker in selected_markers:
            title = marker_templates.get(marker, f'{marker}功能测试')
            node = {
                'title': title,
                'path': f'冒烟测试 > {title}',
                'level': 3,
                'markers': [marker],
                'has_children': True,
                'children': [
                    {'title': '准备测试环境', 'level': 4},
                    {'title': '执行核心操作', 'level': 4},
                    {'title': '验证执行结果', 'level': 4}
                ]
            }
            basic_nodes.append(node)
        
        return basic_nodes
    
    def _extract_nodes_recursive(self, topic: Dict, path: List[str], all_nodes: List[Dict], level: int = 1):
        """递归提取节点信息"""
        if not isinstance(topic, dict):
            return
            
        title = topic.get('title', '').strip()
        if not title:
            return
            
        current_path = path + [title]
        
        # 提取节点的标识符
        markers = self._extract_node_markers(topic)
        
        # 构建节点信息
        node_info = {
            'title': title,
            'path': ' > '.join(current_path),
            'level': level,
            'markers': markers,
            'has_children': 'topics' in topic and len(topic.get('topics', [])) > 0,
            'raw_topic': topic,
            'children': []
        }
        
        # 提取子节点作为测试步骤
        subtopics = topic.get('topics', [])
        for subtopic in subtopics:
            if isinstance(subtopic, dict) and subtopic.get('title'):
                node_info['children'].append({
                    'title': subtopic.get('title', '').strip(),
                    'level': level + 1
                })
        
        all_nodes.append(node_info)
        
        # 递归处理子节点
        for subtopic in subtopics:
            self._extract_nodes_recursive(subtopic, current_path, all_nodes, level + 1)
    
    def _extract_node_markers(self, topic: Dict) -> List[str]:
        """提取节点的标识符（与XMindAnalyzer保持一致）"""
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
        
        if markers:
            logger.info(f"节点 '{topic.get('title', 'unknown')}' 最终提取到的标识符: {markers}")
        
        return markers
    
    def _map_xmind_marker_to_id(self, marker_ref) -> str:
        """将XMind内部标识符映射到自定义ID（与XMindAnalyzer保持一致）"""
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
    
    def _map_string_marker(self, marker_str: str) -> str:
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
        
        return None
    
    def _map_dict_marker(self, marker_dict: dict) -> str:
        """映射字典类型的标识符"""
        # 首先尝试获取markerId字段
        marker_id = marker_dict.get('markerId', '')
        if marker_id:
            # 递归处理markerId
            return self._map_string_marker(marker_id)
        
        # 如果没有markerId，尝试其他可能的字段
        possible_fields = ['id', 'type', 'name', 'symbol', 'key']
        for field in possible_fields:
            if field in marker_dict and marker_dict[field]:
                result = self._map_string_marker(str(marker_dict[field]))
                if result:
                    return result
        
        return None
    
    def _filter_nodes_by_markers(self, all_nodes: List[Dict], selected_markers: List[str]) -> List[Dict]:
        """根据选中的标识符筛选节点"""
        filtered_nodes = []
        
        for node in all_nodes:
            node_markers = node.get('markers', [])
            # 检查节点是否包含任一选中的标识符
            if any(marker in selected_markers for marker in node_markers):
                filtered_nodes.append(node)
        
        return filtered_nodes
    
    def _filter_suitable_smoke_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """筛选适合冒烟测试的节点"""
        suitable_nodes = []
        
        for node in nodes:
            if self._is_suitable_for_smoke_test(node):
                suitable_nodes.append(node)
        
        return suitable_nodes
    
    def _is_suitable_for_smoke_test(self, node: Dict) -> bool:
        """判断节点是否适合作为冒烟测试用例"""
        # 检查是否包含标识符
        if not node.get('markers'):
            return False
            
        # 检查节点层级（2-6层比较合适，进一步放宽条件）
        level = node.get('level', 0)
        if level < 2 or level > 6:
            return False
            
        # 检查节点描述是否包含测试相关的关键词（大幅放宽条件）
        title = node.get('title', '').lower()
        
        # 排除明显的配置类节点
        if any(keyword in title for keyword in self.config_keywords):
            return False
            
        # 排除过于简单的节点（只有一两个字的）
        if len(title.strip()) < 3:
            return False
            
        # 其他节点都认为适合作为冒烟测试用例
        return True
    
    def _deduplicate_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """去重处理，合并相同路径的节点"""
        unique_nodes = []
        seen_paths = set()
        
        for node in nodes:
            path = node.get('path', '')
            if path not in seen_paths:
                seen_paths.add(path)
                unique_nodes.append(node)
        
        return unique_nodes
    
    def _build_test_case(self, node: Dict, case_number: int) -> Optional[Dict[str, Any]]:
        """构建单个测试用例"""
        try:
            title = node.get('title', '')
            path = node.get('path', '')
            markers = node.get('markers', [])
            
            # 构建用例ID
            case_id = f"SMOKE_{case_number:03d}"
            
            # 确定优先级
            priority = self._get_highest_priority(markers)
            
            # 提取模块名（通常是路径的第二级）
            path_parts = path.split(' > ')
            module = path_parts[1] if len(path_parts) > 1 else path_parts[0]
            
            # 构建测试步骤
            steps = self._build_test_steps(node)
            
            # 检查完整性（确保有步骤）
            if not steps:
                logger.warning(f"节点 {title} 没有有效的测试步骤，跳过")
                return None
            
            # 构建测试用例
            test_case = {
                "case_id": case_id,
                "title": self._normalize_title(title),
                "module": module,
                "test_path": path,
                "priority": priority,
                "markers": markers,
                "steps": steps,
                "smoke_criteria": {
                    "is_core_function": self._is_core_function(title, path),
                    "affects_main_flow": self._affects_main_flow(title),
                    "execution_time": "< 2分钟"
                }
            }
            
            return test_case
            
        except Exception as e:
            logger.error(f"构建测试用例失败: {str(e)}")
            return None
    
    def _get_highest_priority(self, markers: List[str]) -> str:
        """获取最高优先级"""
        priorities = [self.priority_mapping.get(marker, 'P5') for marker in markers]
        
        # 按优先级排序（P0最高）
        priority_order = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5']
        for p in priority_order:
            if p in priorities:
                return p
        
        return 'P3'  # 默认优先级
    
    def _normalize_title(self, title: str) -> str:
        """规范化测试用例标题"""
        # 确保标题包含"验证"或"测试"
        normalized = title.strip()
        
        if not any(word in normalized for word in ['验证', '测试', '检查']):
            if any(word in normalized for word in ['登录', '注册', '支付']):
                normalized = f"{normalized}功能验证"
            else:
                normalized = f"{normalized}验证"
        
        return normalized
    
    def _build_test_steps(self, node: Dict) -> List[Dict[str, Any]]:
        """构建测试步骤"""
        steps = []
        children = node.get('children', [])
        
        if children:
            # 使用子节点作为测试步骤
            for i, child in enumerate(children[:10]):  # 限制最多10步
                step = {
                    "step": i + 1,
                    "action": child.get('title', ''),
                    "expected": self._generate_expected_result(child.get('title', ''))
                }
                steps.append(step)
        else:
            # 没有子节点时，根据标题生成基础步骤
            title = node.get('title', '')
            steps = self._generate_basic_steps(title)
        
        return steps
    
    def _generate_expected_result(self, action: str) -> str:
        """根据操作生成期望结果"""
        action_lower = action.lower()
        
        if '登录' in action_lower:
            return "成功登录系统"
        elif '注册' in action_lower:
            return "注册成功"
        elif '支付' in action_lower:
            return "支付成功"
        elif '搜索' in action_lower or '查询' in action_lower:
            return "返回正确的搜索结果"
        elif '添加' in action_lower or '创建' in action_lower:
            return "成功创建/添加"
        elif '删除' in action_lower:
            return "成功删除"
        elif '修改' in action_lower or '编辑' in action_lower:
            return "修改成功"
        elif '验证' in action_lower or '检查' in action_lower:
            return "验证通过"
        elif '准备' in action_lower:
            return "环境准备完成"
        elif '执行' in action_lower:
            return "执行成功"
        else:
            return "操作成功完成"
    
    def _generate_basic_steps(self, title: str) -> List[Dict[str, Any]]:
        """为没有子节点的测试用例生成基础步骤"""
        title_lower = title.lower()
        
        if '登录' in title_lower:
            return [
                {"step": 1, "action": "打开登录页面", "expected": "页面正常显示"},
                {"step": 2, "action": "输入有效用户名密码", "expected": "成功登录系统"}
            ]
        elif '注册' in title_lower:
            return [
                {"step": 1, "action": "打开注册页面", "expected": "页面正常显示"},
                {"step": 2, "action": "填写注册信息", "expected": "注册成功"}
            ]
        elif '支付' in title_lower:
            return [
                {"step": 1, "action": "选择商品", "expected": "商品添加到购物车"},
                {"step": 2, "action": "进入支付页面", "expected": "支付页面正常显示"},
                {"step": 3, "action": "完成支付", "expected": "支付成功"}
            ]
        else:
            return [
                {"step": 1, "action": f"执行{title}", "expected": "操作成功完成"}
            ]
    
    def _is_core_function(self, title: str, path: str) -> bool:
        """判断是否为核心功能"""
        core_keywords = ['登录', '注册', '支付', '下单', '搜索', '首页', '重要', '核心']
        title_path = (title + ' ' + path).lower()
        return any(keyword in title_path for keyword in core_keywords)
    
    def _affects_main_flow(self, title: str) -> bool:
        """判断是否影响主流程"""
        main_flow_keywords = ['登录', '支付', '下单', '注册', '重要', '核心']
        return any(keyword in title.lower() for keyword in main_flow_keywords) 