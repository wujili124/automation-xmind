#!/usr/bin/env python3
"""
XMind分析器适配器
将增强版XMind分析器与现有系统集成
"""

import logging
import base64
from typing import Dict, List, Any, Optional

# 导入原始和增强版分析器
from xmind_parser import XMindAnalyzer
from enhanced_xmind_analyzer import EnhancedXMindAnalyzer

logger = logging.getLogger(__name__)

class XMindAnalyzerAdapter:
    """
    XMind分析器适配器
    提供统一的接口，同时支持原始和增强版分析器
    """
    
    def __init__(self, use_enhanced: bool = True):
        """
        初始化适配器
        
        Args:
            use_enhanced: 是否使用增强版分析器
        """
        self.use_enhanced = use_enhanced
        
        # 创建分析器实例
        self.legacy_analyzer = XMindAnalyzer()
        self.enhanced_analyzer = EnhancedXMindAnalyzer()
        
        logger.info(f"XMind分析器适配器初始化完成，使用{'增强版' if use_enhanced else '原始版'}分析器")
    
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
            logger.info(f"开始分析XMind文件: {filename}，使用{'增强版' if self.use_enhanced else '原始版'}分析器")
            
            if self.use_enhanced:
                # 使用增强版分析器
                result = self.enhanced_analyzer.analyze_markers(file_content, filename)
                
                # 确保结果兼容原始API
                if 'file_data' not in result:
                    result['file_data'] = base64.b64encode(file_content).decode('utf-8')
                
                return result
            else:
                # 使用原始分析器
                result = self.legacy_analyzer.analyze_markers(file_content, filename)
                
                # 添加原始文件数据供后续使用
                result['file_data'] = base64.b64encode(file_content).decode('utf-8')
                
                return result
                
        except Exception as e:
            logger.error(f"XMind文件分析失败: {str(e)}")
            raise
    
    def get_parsed_nodes(self) -> List[Dict]:
        """获取已解析的节点数据"""
        if self.use_enhanced:
            return self.enhanced_analyzer.get_parsed_nodes()
        else:
            return self.legacy_analyzer.get_parsed_nodes()
    
    def get_filename(self) -> str:
        """获取文件名"""
        if self.use_enhanced:
            return self.enhanced_analyzer.get_filename()
        else:
            return self.legacy_analyzer.get_filename()
    
    def switch_analyzer(self, use_enhanced: bool) -> None:
        """
        切换分析器类型
        
        Args:
            use_enhanced: 是否使用增强版分析器
        """
        self.use_enhanced = use_enhanced
        logger.info(f"切换到{'增强版' if use_enhanced else '原始版'}分析器")
    
    def get_all_markers(self) -> List[Dict]:
        """获取所有已知的标识符"""
        if self.use_enhanced:
            return self.enhanced_analyzer.get_all_markers()
        else:
            # 原始分析器不支持此功能，返回基本标识符
            return [
                {"symbol": m["symbol"], "markerId": m["markerId"]} 
                for m in self.legacy_analyzer.xmind_markers
            ]
    
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
        if self.use_enhanced:
            return self.enhanced_analyzer.register_custom_marker(marker_id, symbol, category)
        else:
            # 原始分析器不支持此功能，记录警告
            logger.warning("原始分析器不支持注册自定义标识符")
            return {"markerId": marker_id, "symbol": symbol}
    
    def get_unknown_markers(self) -> List[Dict]:
        """获取未知的标识符"""
        if self.use_enhanced:
            return self.enhanced_analyzer.get_unknown_markers()
        else:
            # 原始分析器不支持此功能
            return []
    
    def learn_marker_mappings(self, mappings: List[Dict]) -> None:
        """
        学习多个标识符映射
        
        Args:
            mappings: 映射列表，每个映射包含original和mappedTo字段
        """
        if self.use_enhanced:
            self.enhanced_analyzer.learn_marker_mappings(mappings)
        else:
            # 原始分析器不支持此功能
            logger.warning("原始分析器不支持学习标识符映射")


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建适配器
    adapter = XMindAnalyzerAdapter(use_enhanced=True)
    
    # 测试切换分析器
    adapter.switch_analyzer(use_enhanced=False)
    adapter.switch_analyzer(use_enhanced=True)
    
    # 获取所有标识符
    markers = adapter.get_all_markers()
    print(f"已知标识符: {len(markers)}个")
    for marker in markers[:5]:  # 只显示前5个
        print(f"{marker['markerId']} - {marker['symbol']}") 