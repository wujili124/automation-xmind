#!/usr/bin/env python3
"""
XMind标识符注册表
管理XMind标识符映射关系和元数据
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

logger = logging.getLogger(__name__)

class MarkerRegistry:
    """XMind标识符注册表，管理标识符映射关系和元数据"""
    
    def __init__(self, config_path: str = None):
        """
        初始化标识符注册表
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        # 基础标识符映射配置
        self.base_markers = [
            {"symbol": "重要 (红色叹号)", "markerId": "important", "category": "重要性", "icon": "❗"},
            {"symbol": "优先级1 (红色1)", "markerId": "priority-1", "category": "优先级", "icon": "1️⃣"},
            {"symbol": "优先级2 (橙色2)", "markerId": "priority-2", "category": "优先级", "icon": "2️⃣"},
            {"symbol": "优先级3 (黄色3)", "markerId": "priority-3", "category": "优先级", "icon": "3️⃣"},
            {"symbol": "优先级4 (绿色4)", "markerId": "priority-4", "category": "优先级", "icon": "4️⃣"},
            {"symbol": "优先级5 (蓝色5)", "markerId": "priority-5", "category": "优先级", "icon": "5️⃣"},
            {"symbol": "优先级6 (紫色6)", "markerId": "priority-6", "category": "优先级", "icon": "6️⃣"},
            {"symbol": "优先级7 (灰色7)", "markerId": "priority-7", "category": "优先级", "icon": "7️⃣"},
            {"symbol": "优先级8 (灰色8)", "markerId": "priority-8", "category": "优先级", "icon": "8️⃣"},
            {"symbol": "优先级9 (灰色9)", "markerId": "priority-9", "category": "优先级", "icon": "9️⃣"},
            {"symbol": "是", "markerId": "yes", "category": "标记", "icon": "✅"},
            {"symbol": "否", "markerId": "no", "category": "标记", "icon": "❌"},
            {"symbol": "对号", "markerId": "check", "category": "标记", "icon": "✓"},
            {"symbol": "叉号", "markerId": "cross", "category": "标记", "icon": "✗"},
            {"symbol": "半对号", "markerId": "half-check", "category": "标记", "icon": "✓"},
            {"symbol": "问号", "markerId": "question", "category": "标记", "icon": "❓"},
            {"symbol": "感叹号", "markerId": "exclamation", "category": "标记", "icon": "❗"},
            {"symbol": "信息", "markerId": "info", "category": "标记", "icon": "ℹ️"},
            {"symbol": "注意", "markerId": "attention", "category": "标记", "icon": "⚠️"},
            {"symbol": "错误", "markerId": "error", "category": "标记", "icon": "⛔"},
            {"symbol": "暂停", "markerId": "pause", "category": "状态", "icon": "⏸️"},
            {"symbol": "停止", "markerId": "stop", "category": "状态", "icon": "⏹️"},
            {"symbol": "运行", "markerId": "running", "category": "状态", "icon": "▶️"},
            {"symbol": "等待", "markerId": "waiting", "category": "状态", "icon": "⏳"},
            {"symbol": "完成", "markerId": "done", "category": "状态", "icon": "✅"},
            {"symbol": "进行中", "markerId": "in-progress", "category": "状态", "icon": "🔄"},
            {"symbol": "未开始", "markerId": "not-started", "category": "状态", "icon": "⭕"},
            {"symbol": "延迟", "markerId": "delayed", "category": "状态", "icon": "⏰"},
            {"symbol": "风险", "markerId": "risk", "category": "风险", "icon": "🔴"},
            {"symbol": "高风险", "markerId": "high-risk", "category": "风险", "icon": "🔴"},
            {"symbol": "中风险", "markerId": "medium-risk", "category": "风险", "icon": "🟠"},
            {"symbol": "低风险", "markerId": "low-risk", "category": "风险", "icon": "🟡"},
            {"symbol": "无风险", "markerId": "no-risk", "category": "风险", "icon": "🟢"},
            {"symbol": "星标", "markerId": "star", "category": "标记", "icon": "⭐"},
            {"symbol": "旗标", "markerId": "flag", "category": "标记", "icon": "🚩"},
            {"symbol": "人物", "markerId": "people", "category": "对象", "icon": "👤"},
            {"symbol": "时钟", "markerId": "clock", "category": "时间", "icon": "🕒"},
            {"symbol": "日历", "markerId": "calendar", "category": "时间", "icon": "📅"},
            {"symbol": "邮件", "markerId": "email", "category": "通信", "icon": "📧"},
            {"symbol": "电话", "markerId": "phone", "category": "通信", "icon": "📞"}
        ]
        
        # 标识符ID到信息的映射
        self.marker_map = {}
        
        # 原始标识符到标准ID的映射
        self.raw_to_standard = {}
        
        # 自定义标识符
        self.custom_markers = []
        
        # 加载配置
        self._load_config(config_path)
        
        # 初始化映射
        self._initialize_mappings()
        
        logger.info(f"标识符注册表初始化完成，共加载 {len(self.marker_map)} 个标识符")
    
    def _load_config(self, config_path: str = None) -> None:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        # 默认配置路径
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'marker_config.json')
        
        # 如果配置文件存在，加载它
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载额外的标识符
                if 'markers' in config:
                    self.base_markers.extend(config['markers'])
                
                # 加载映射规则
                if 'mappings' in config:
                    for raw, standard in config['mappings'].items():
                        self.raw_to_standard[raw] = standard
                
                # 加载自定义标识符
                if 'custom_markers' in config:
                    self.custom_markers = config['custom_markers']
                
                logger.info(f"从 {config_path} 加载了配置")
            
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        else:
            logger.info(f"配置文件 {config_path} 不存在，使用默认配置")
    
    def _initialize_mappings(self) -> None:
        """初始化标识符映射"""
        # 初始化标准标识符映射
        for marker in self.base_markers:
            self.marker_map[marker['markerId']] = marker
        
        # 添加自定义标识符
        for marker in self.custom_markers:
            self.marker_map[marker['markerId']] = marker
        
        # 初始化一些常见的变体映射
        common_variants = {
            # 优先级变体
            'priority1': 'priority-1',
            'priority2': 'priority-2',
            'priority3': 'priority-3',
            'priority4': 'priority-4',
            'priority5': 'priority-5',
            'priority6': 'priority-6',
            'priority7': 'priority-7',
            'priority8': 'priority-8',
            'priority9': 'priority-9',
            'p1': 'priority-1',
            'p2': 'priority-2',
            'p3': 'priority-3',
            'p4': 'priority-4',
            'p5': 'priority-5',
            'p6': 'priority-6',
            'p7': 'priority-7',
            'p8': 'priority-8',
            'p9': 'priority-9',
            
            # 标记变体
            'tick': 'check',
            'checked': 'check',
            'unchecked': 'cross',
            'wrong': 'cross',
            'warning': 'attention',
            'alert': 'attention',
            'information': 'info',
            
            # 状态变体
            'pending': 'waiting',
            'blocked': 'stop',
            'completed': 'done',
            'finished': 'done',
            'started': 'in-progress',
            'ongoing': 'in-progress',
            'notstarted': 'not-started',
            'todo': 'not-started',
            'delayed': 'delayed',
            'late': 'delayed',
            
            # 风险变体
            'highrisk': 'high-risk',
            'mediumrisk': 'medium-risk',
            'lowrisk': 'low-risk',
            'norisk': 'no-risk',
            'high': 'high-risk',
            'medium': 'medium-risk',
            'low': 'low-risk',
            'none': 'no-risk'
        }
        
        # 添加到映射中
        for variant, standard in common_variants.items():
            self.raw_to_standard[variant] = standard
        
        # 添加配置中的映射
        for raw, standard in self.raw_to_standard.items():
            if standard in self.marker_map:
                logger.debug(f"添加映射: {raw} -> {standard}")
            else:
                logger.warning(f"映射目标不存在: {raw} -> {standard}")
    
    def map_marker(self, marker_ref: Any) -> Optional[str]:
        """
        将原始标识符映射到标准标识符ID
        
        Args:
            marker_ref: 原始标识符引用，可能是字符串、字典或其他类型
            
        Returns:
            标准标识符ID，如果无法映射则返回None
        """
        try:
            # 处理字典类型的标识符引用
            if isinstance(marker_ref, dict):
                # 尝试从字典中提取标识符ID
                marker_id = None
                
                # 检查常见的ID字段
                for field in ['markerId', 'id', 'marker-id', 'marker_id']:
                    if field in marker_ref and marker_ref[field]:
                        marker_id = str(marker_ref[field]).lower()
                        break
                
                # 如果没有找到ID，尝试其他字段
                if not marker_id:
                    for field in ['name', 'type', 'marker']:
                        if field in marker_ref and marker_ref[field]:
                            marker_id = str(marker_ref[field]).lower()
                            break
                
                # 如果仍然没有找到ID，返回None
                if not marker_id:
                    return None
                
                # 尝试直接映射
                if marker_id in self.marker_map:
                    return marker_id
                
                # 尝试通过变体映射
                clean_id = self._clean_marker_id(marker_id)
                if clean_id in self.raw_to_standard:
                    return self.raw_to_standard[clean_id]
                
                # 尝试模糊匹配
                return self._fuzzy_match_marker(clean_id)
            
            # 处理字符串类型的标识符引用
            elif isinstance(marker_ref, str):
                marker_id = marker_ref.lower()
                
                # 尝试直接映射
                if marker_id in self.marker_map:
                    return marker_id
                
                # 尝试通过变体映射
                clean_id = self._clean_marker_id(marker_id)
                if clean_id in self.raw_to_standard:
                    return self.raw_to_standard[clean_id]
                
                # 尝试模糊匹配
                return self._fuzzy_match_marker(clean_id)
            
            # 其他类型，尝试转换为字符串
            else:
                marker_id = str(marker_ref).lower()
                clean_id = self._clean_marker_id(marker_id)
                
                # 尝试直接映射
                if clean_id in self.marker_map:
                    return clean_id
                
                # 尝试通过变体映射
                if clean_id in self.raw_to_standard:
                    return self.raw_to_standard[clean_id]
                
                # 尝试模糊匹配
                return self._fuzzy_match_marker(clean_id)
        
        except Exception as e:
            logger.warning(f"标识符映射失败: {str(e)}")
            return None
    
    def _clean_marker_id(self, marker_id: str) -> str:
        """
        清理标识符ID，移除特殊字符
        
        Args:
            marker_id: 原始标识符ID
            
        Returns:
            清理后的标识符ID
        """
        # 移除非字母数字字符
        clean_id = re.sub(r'[^a-z0-9]', '', marker_id.lower())
        return clean_id
    
    def _fuzzy_match_marker(self, marker_id: str) -> Optional[str]:
        """
        模糊匹配标识符
        
        Args:
            marker_id: 标识符ID
            
        Returns:
            匹配到的标准标识符ID，如果无法匹配则返回None
        """
        # 如果ID为空，返回None
        if not marker_id:
            return None
        
        # 尝试匹配包含该ID的标识符
        for standard_id in self.marker_map.keys():
            if marker_id in standard_id:
                logger.debug(f"模糊匹配成功: {marker_id} -> {standard_id}")
                return standard_id
        
        # 尝试匹配变体映射
        for raw, standard in self.raw_to_standard.items():
            if marker_id in raw or raw in marker_id:
                logger.debug(f"变体模糊匹配成功: {marker_id} -> {standard}")
                return standard
        
        # 无法匹配
        return None
    
    def get_marker_info(self, marker_id: str) -> Optional[Dict]:
        """
        获取标识符信息
        
        Args:
            marker_id: 标识符ID
            
        Returns:
            标识符信息，如果不存在则返回None
        """
        return self.marker_map.get(marker_id)
    
    def get_all_markers(self) -> List[Dict]:
        """
        获取所有已知的标识符
        
        Returns:
            标识符列表
        """
        return list(self.marker_map.values())
    
    def register_custom_marker(self, marker_id: str, symbol: str, category: str = "自定义") -> Dict:
        """
        注册自定义标识符
        
        Args:
            marker_id: 标识符ID
            symbol: 显示名称
            category: 分类
            
        Returns:
            新注册的标识符信息
        """
        # 创建新的标识符
        new_marker = {
            "markerId": marker_id,
            "symbol": symbol,
            "category": category,
            "icon": "🔖",  # 默认图标
            "isCustom": True
        }
        
        # 添加到映射中
        self.marker_map[marker_id] = new_marker
        self.custom_markers.append(new_marker)
        
        logger.info(f"注册自定义标识符: {marker_id} - {symbol}")
        
        # 保存配置
        self._save_config()
        
        return new_marker
    
    def learn_marker_mapping(self, original: Any, mapped_to: str) -> bool:
        """
        学习标识符映射
        
        Args:
            original: 原始标识符
            mapped_to: 映射到的标识符ID
            
        Returns:
            是否成功学习映射
        """
        try:
            # 检查映射目标是否存在
            if mapped_to not in self.marker_map:
                logger.warning(f"映射目标不存在: {mapped_to}")
                return False
            
            # 将原始标识符转换为字符串
            if isinstance(original, dict):
                # 尝试从字典中提取ID
                for field in ['markerId', 'id', 'name', 'type', 'marker']:
                    if field in original and original[field]:
                        original_id = str(original[field]).lower()
                        break
                else:
                    original_id = str(original)
            else:
                original_id = str(original).lower()
            
            # 清理ID
            clean_id = self._clean_marker_id(original_id)
            
            # 添加映射
            self.raw_to_standard[clean_id] = mapped_to
            
            logger.info(f"学习到新的标识符映射: {clean_id} -> {mapped_to}")
            
            # 保存配置
            self._save_config()
            
            return True
            
        except Exception as e:
            logger.warning(f"学习标识符映射失败: {str(e)}")
            return False
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'marker_config.json')
            
            # 准备配置数据
            config = {
                'markers': self.base_markers,
                'mappings': self.raw_to_standard,
                'custom_markers': self.custom_markers
            }
            
            # 保存到文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已保存到 {config_path}")
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建标识符注册表
    registry = MarkerRegistry()
    
    # 测试标识符映射
    test_markers = [
        "important",
        "priority1",
        "p2",
        {"markerId": "check"},
        {"id": "question"},
        {"name": "exclamation"},
        "unknown_marker"
    ]
    
    print("测试标识符映射:")
    for marker in test_markers:
        mapped = registry.map_marker(marker)
        print(f"{marker} -> {mapped}")
        if mapped:
            info = registry.get_marker_info(mapped)
            print(f"  {info['symbol']} ({info['category']})")
    
    # 测试注册自定义标识符
    custom = registry.register_custom_marker("custom-test", "测试标识符", "测试")
    print(f"\n注册自定义标识符: {custom['markerId']} - {custom['symbol']}")
    
    # 测试学习映射
    registry.learn_marker_mapping("test_marker", "important")
    print("\n学习映射后:")
    print(f"test_marker -> {registry.map_marker('test_marker')}")
    
    # 获取所有标识符
    all_markers = registry.get_all_markers()
    print(f"\n共有 {len(all_markers)} 个标识符")
    for i, marker in enumerate(all_markers[:5]):  # 只显示前5个
        print(f"{i+1}. {marker['markerId']} - {marker['symbol']} ({marker['category']})") 