#!/usr/bin/env python3
"""
XMind文件markerId精确过滤模块
基于lxml直接操作XML DOM，精确删除包含指定markerId的节点
完全保持原始文件样式和结构
"""

import shutil
from lxml import etree
import zipfile
import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import logging
import base64
import traceback

logger = logging.getLogger(__name__)

class XMindMarkerFilter:
    """XMind文件markerId过滤器"""
    
    def __init__(self):
        # XMind XML命名空间定义
        self.namespaces = {
            'x': 'urn:xmind:xmap:xmlns:content:2.0',
            'm': 'urn:xmind:xmap:xmlns:marker:2.0'
        }
    
    def has_target_marker(self, topic_node, target_marker_id: str) -> bool:
        """
        检查topic节点是否包含目标markerId
        
        Args:
            topic_node: XML topic节点
            target_marker_id: 目标标记ID
            
        Returns:
            bool: 是否包含目标标记
        """
        # 获取topic下的所有marker-ref元素
        marker_refs = topic_node.getElementsByTagName('marker-ref')
        for marker_ref in marker_refs:
            marker_id = marker_ref.getAttribute('marker-id')
            if marker_id == target_marker_id:
                return True
        return False
    
    def process_dom_with_minidom(self, dom, target_marker_ids: List[str]) -> Dict[str, int]:
        """
        使用xml.dom.minidom处理DOM，删除包含指定markerId的节点
        
        Args:
            dom: minidom DOM对象
            target_marker_ids: 要删除的markerId列表
            
        Returns:
            Dict: 处理统计信息
        """
        import xml.dom.minidom as minidom
        
        stats = {
            'sheets_processed': 0,
            'sheets_removed': 0,
            'nodes_removed': 0,
            'target_marker_ids': target_marker_ids
        }
        
        # 获取所有sheet
        sheets = dom.getElementsByTagName('sheet')
        sheet_nodes = []
        for i in range(sheets.length):
            sheet_nodes.append(sheets[i])
        
        sheets_to_remove = []
        
        for sheet in sheet_nodes:
            stats['sheets_processed'] += 1
            
            # 获取根topic
            rootTopics = sheet.getElementsByTagName('topic')
            if rootTopics.length == 0:
                continue
                
            rootTopic = rootTopics[0]
            
            # 检查根topic是否包含任何目标标记
            root_has_target = any(
                self.has_target_marker(rootTopic, marker_id) 
                for marker_id in target_marker_ids
            )
            
            if root_has_target:
                # 记录该sheet需要被删除
                sheets_to_remove.append(sheet)
                stats['sheets_removed'] += 1
                logger.info(f"根topic包含目标标记，将删除整个sheet")
            else:
                # 获取该根topic下的所有topic（包括自己），然后排除根topic
                allTopics = rootTopic.getElementsByTagName('topic')
                topics_to_remove = []
                
                for i in range(allTopics.length):
                    topic = allTopics[i]
                    # 跳过根topic
                    if topic == rootTopic:
                        continue
                    
                    # 检查是否包含任何目标标记
                    topic_has_target = any(
                        self.has_target_marker(topic, marker_id) 
                        for marker_id in target_marker_ids
                    )
                    
                    if topic_has_target:
                        topics_to_remove.append(topic)
                
                # 删除这些topic节点
                for topic in topics_to_remove:
                    parent = topic.parentNode
                    parent.removeChild(topic)
                    stats['nodes_removed'] += 1
                    logger.info(f"删除包含目标标记的节点")
        
        # 删除整个sheet
        for sheet in sheets_to_remove:
            parent = sheet.parentNode
            parent.removeChild(sheet)
        
        return stats
    
    def process_dom_with_lxml(self, tree, target_marker_ids: List[str]) -> Dict[str, int]:
        """
        使用lxml处理DOM，保留包含指定markerId的节点，删除其他节点
        
        Args:
            tree: lxml ElementTree对象
            target_marker_ids: 要保留的markerId列表
            
        Returns:
            Dict: 处理统计信息
        """
        stats = {
            'sheets_processed': 0,
            'sheets_removed': 0,
            'nodes_removed': 0,
            'target_marker_ids': target_marker_ids
        }
        
        root = tree.getroot()
        
        # 获取所有sheet
        sheets = root.xpath('.//sheet')
        
        for sheet in sheets:
            stats['sheets_processed'] += 1
            
            # 获取该sheet的根topic
            root_topics = sheet.xpath('.//topic')
            if not root_topics:
                continue
            
            root_topic = root_topics[0]  # 第一个topic是根topic
            
            # 递归处理整个sheet，保留包含目标标记的节点
            nodes_to_remove = []
            
            # 获取所有topic节点（除了根节点）
            all_topics = sheet.xpath('.//topic')
            for node in all_topics:
                if node == root_topic:
                    continue  # 跳过根节点，根节点始终保留
                
                # 检查是否应该保留这个节点
                should_keep = self.should_keep_xml_node(node, target_marker_ids)
                
                if not should_keep:
                    nodes_to_remove.append(node)
            
            # 删除不需要的节点
            for node in nodes_to_remove:
                parent = node.getparent()
                if parent is not None:
                    parent.remove(node)
                    stats['nodes_removed'] += 1
                    logger.info(f"删除不包含目标标记的XML节点")
        
        return stats
    
    def should_keep_xml_node(self, node, target_marker_ids: List[str]) -> bool:
        """
        判断XML节点是否应该保留
        保留包含目标markerId的节点或包含有效子节点的父节点
        """
        # 检查当前节点是否包含目标标记
        for marker_id in target_marker_ids:
            xpath = f".//marker-ref[@marker-id='{marker_id}']"
            markers = node.xpath(xpath)
            if markers:
                logger.info(f"保留包含目标标记的XML节点: markerId={marker_id}")
                return True
        
        # 检查是否有子节点包含目标标记
        for marker_id in target_marker_ids:
            xpath = f".//topic[.//marker-ref[@marker-id='{marker_id}']]"
            child_nodes_with_marker = node.xpath(xpath)
            if child_nodes_with_marker:
                logger.info(f"保留包含有效子节点的XML父节点")
                return True
        
        return False
    
    def filter_xmind_by_markers(
        self, 
        file_data: str, 
        selected_markers: List[str],
        engine: str = 'lxml'  # 'lxml' 或 'minidom'
    ) -> Dict:
        """
        根据标识符过滤XMind文件
        保留包含选中标识符的节点，删除其他节点
        
        Args:
            file_data: XMind文件的base64编码数据
            selected_markers: 要保留的标识符列表
            engine: XML处理引擎
            
        Returns:
            Dict: 包含处理结果的字典
        """
        try:
            # 验证输入参数
            if not file_data:
                raise ValueError("文件数据不能为空")
            
            if not selected_markers:
                raise ValueError("至少需要选择一个标识符")
            
            logger.info(f"开始过滤XMind文件，保留标识符: {selected_markers}")
            
            # 解码base64数据
            decoded_data = base64.b64decode(file_data)
            original_size = len(decoded_data)
            logger.info(f"原始文件大小: {original_size} bytes")
            
            # 创建临时文件来处理
            with tempfile.NamedTemporaryFile(suffix='.xmind', delete=False) as temp_file:
                temp_file.write(decoded_data)
                temp_file_path = temp_file.name
            
            try:
                # 解压XMind文件
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    with tempfile.TemporaryDirectory() as extract_dir:
                        zip_ref.extractall(extract_dir)
                        
                        # 初始化统计信息
                        stats = {
                            'original_size': original_size,
                            'sheets_processed': 0,
                            'sheets_removed': 0,
                            'nodes_removed': 0,
                            'target_markers': selected_markers,
                            'processing_engine': engine
                        }
                        
                        # 处理content.json（如果存在）
                        content_json_path = os.path.join(extract_dir, 'content.json')
                        if os.path.exists(content_json_path):
                            logger.info("处理content.json格式")
                            self.process_content_json(content_json_path, selected_markers, stats)
                        
                        # 处理content.xml（如果存在）
                        content_xml_path = os.path.join(extract_dir, 'content.xml')
                        if os.path.exists(content_xml_path):
                            logger.info(f"处理content.xml格式，使用{engine}引擎")
                            if engine == 'lxml':
                                self.process_content_xml_lxml(content_xml_path, selected_markers, stats)
                            else:
                                self.process_content_xml_minidom(content_xml_path, selected_markers, stats)
                        
                        # 重新打包XMind文件
                        with tempfile.NamedTemporaryFile(suffix='.xmind', delete=False) as new_temp_file:
                            new_temp_path = new_temp_file.name
                        
                        with zipfile.ZipFile(new_temp_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                            for root, dirs, files in os.walk(extract_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arc_path = os.path.relpath(file_path, extract_dir)
                                    new_zip.write(file_path, arc_path)
                        
                        # 读取处理后的文件
                        with open(new_temp_path, 'rb') as processed_file:
                            processed_data = processed_file.read()
                        
                        # 计算压缩统计
                        filtered_size = len(processed_data)
                        compression_ratio = f"{((original_size - filtered_size) / original_size * 100):.1f}%"
                        
                        stats.update({
                            'filtered_size': filtered_size,
                            'compression_ratio': compression_ratio
                        })
                        
                        # 编码为base64
                        processed_base64 = base64.b64encode(processed_data).decode('utf-8')
                        
                        logger.info(f"过滤完成，保留标识符 {selected_markers}")
                        logger.info(f"删除节点数: {stats['nodes_removed']}")
                        logger.info(f"删除工作表数: {stats['sheets_removed']}")
                        logger.info(f"文件大小变化: {original_size} -> {filtered_size} bytes")
                        logger.info(f"压缩率: {compression_ratio}")
                        
                        return {
                            'success': True,
                            'file_data': processed_base64,
                            'processing_details': stats
                        }
                        
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                if 'new_temp_path' in locals() and os.path.exists(new_temp_path):
                    os.unlink(new_temp_path)
                    
        except Exception as e:
            logger.error(f"过滤XMind文件时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def process_content_json(self, content_json_path: str, target_marker_ids: List[str], stats: Dict) -> Dict[str, int]:
        """
        处理content.json文件，删除包含指定markerId的节点
        
        Args:
            content_json_path: content.json文件路径
            target_marker_ids: 要删除的markerId列表
            stats: 处理统计信息
            
        Returns:
            Dict: 处理统计信息
        """
        stats['sheets_processed'] = 0
        stats['sheets_removed'] = 0
        stats['nodes_removed'] = 0
        
        try:
            # 读取JSON文件
            with open(content_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"原始content.json大小: {os.path.getsize(content_json_path)} bytes")
            
            # 处理每个工作表
            filtered_sheets = []
            for sheet in data:
                stats['sheets_processed'] += 1
                
                # 处理工作表
                filtered_sheet = self.filter_json_sheet(sheet, target_marker_ids, stats)
                if filtered_sheet:
                    filtered_sheets.append(filtered_sheet)
                else:
                    stats['sheets_removed'] += 1
                    logger.info(f"删除整个工作表，因为根topic包含目标标记")
            
            # 保存修改后的JSON
            with open(content_json_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_sheets, f, ensure_ascii=False, indent=2)
            
            logger.info(f"content.json处理完成，处理统计: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"处理content.json失败: {str(e)}")
            raise
    
    def filter_json_sheet(self, sheet: Dict, target_marker_ids: List[str], stats: Dict) -> Dict:
        """
        过滤JSON格式的工作表
        保留包含目标标记的工作表和节点
        """
        if not sheet or 'rootTopic' not in sheet:
            return None
        
        root_topic = sheet['rootTopic']
        
        # 过滤根主题
        filtered_root = self.filter_json_topic(root_topic, target_marker_ids, stats, is_root=True)
        
        if not filtered_root:
            # 如果根主题被完全过滤掉（即没有任何包含目标标记的节点），删除整个工作表
            stats['sheets_removed'] += 1
            logger.info("删除不包含目标标记的工作表")
            return None
        
        # 创建新的工作表
        filtered_sheet = sheet.copy()
        filtered_sheet['rootTopic'] = filtered_root
        
        return filtered_sheet
    
    def filter_json_topic(self, topic: Dict, target_marker_ids: List[str], stats: Dict, is_root: bool = False) -> Dict:
        """
        递归过滤JSON格式的主题节点
        保留包含目标标记的节点，删除不包含目标标记的节点
        """
        if not topic:
            return None
        
        # 检查当前节点是否包含目标标记
        has_target_marker = self.json_topic_has_target_marker(topic, target_marker_ids)
        
        # 处理子主题
        filtered_topic = topic.copy()
        filtered_children = []
        has_valid_children = False
        
        if 'children' in topic and 'attached' in topic['children']:
            for child_topic in topic['children']['attached']:
                filtered_child = self.filter_json_topic(child_topic, target_marker_ids, stats, is_root=False)
                if filtered_child:
                    filtered_children.append(filtered_child)
                    has_valid_children = True
        
        # 决策逻辑：保留包含目标标记的节点或有有效子节点的父节点
        if has_target_marker or has_valid_children or is_root:
            # 更新子主题
            if filtered_children:
                filtered_topic['children'] = {'attached': filtered_children}
            elif 'children' in filtered_topic:
                # 如果没有有效子节点，移除children字段
                del filtered_topic['children']
            
            if has_target_marker and not is_root:
                logger.info(f"保留包含目标标记的节点: {topic.get('title', 'untitled')}")
            
            return filtered_topic
        else:
            # 删除不包含目标标记且没有有效子节点的节点
            stats['nodes_removed'] += 1
            logger.info(f"删除不包含目标标记的节点: {topic.get('title', 'untitled')}")
            return None
    
    def json_topic_has_target_marker(self, topic: Dict, target_marker_ids: List[str]) -> bool:
        """
        检查JSON格式的主题节点是否包含目标标记
        """
        # 检查markers字段
        markers = topic.get('markers', [])
        for marker in markers:
            if isinstance(marker, dict):
                marker_id = marker.get('markerId', '')
                if marker_id in target_marker_ids:
                    return True
            elif isinstance(marker, str):
                if marker in target_marker_ids:
                    return True
        
        return False

    def process_content_xml_lxml(self, content_xml_path: str, target_marker_ids: List[str], stats: Dict) -> Dict[str, int]:
        """
        使用lxml处理content.xml，保留包含指定markerId的节点，删除其他节点
        
        Args:
            content_xml_path: content.xml文件路径
            target_marker_ids: 要保留的markerId列表
            stats: 处理统计信息
            
        Returns:
            Dict: 处理统计信息
        """
        stats['sheets_processed'] = 0
        stats['sheets_removed'] = 0
        stats['nodes_removed'] = 0
        
        try:
            # 使用lxml解析XML
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(content_xml_path, parser)
            
            # 获取所有sheet
            sheets = tree.getroot().xpath('.//sheet')
            
            for sheet in sheets:
                stats['sheets_processed'] += 1
                
                # 获取该sheet的根topic
                root_topics = sheet.xpath('.//topic')
                if not root_topics:
                    continue
                
                root_topic = root_topics[0]  # 第一个topic是根topic
                
                # 递归处理整个sheet，保留包含目标标记的节点
                nodes_to_remove = []
                
                # 获取所有topic节点（除了根节点）
                all_topics = sheet.xpath('.//topic')
                for node in all_topics:
                    if node == root_topic:
                        continue  # 跳过根节点，根节点始终保留
                    
                    # 检查是否应该保留这个节点
                    should_keep = self.should_keep_xml_node(node, target_marker_ids)
                    
                    if not should_keep:
                        nodes_to_remove.append(node)
                
                # 删除不需要的节点
                for node in nodes_to_remove:
                    parent = node.getparent()
                    if parent is not None:
                        parent.remove(node)
                        stats['nodes_removed'] += 1
                        logger.info(f"删除不包含目标标记的XML节点")
            
            # 保存修改后的XML
            tree.write(
                content_xml_path, 
                encoding='UTF-8', 
                xml_declaration=True, 
                pretty_print=True
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"处理content.xml失败: {str(e)}")
            raise

    def process_content_xml_minidom(self, content_xml_path: str, target_marker_ids: List[str], stats: Dict) -> Dict[str, int]:
        """
        使用minidom处理content.xml，保留包含指定markerId的节点，删除其他节点
        
        Args:
            content_xml_path: content.xml文件路径
            target_marker_ids: 要保留的markerId列表
            stats: 处理统计信息
            
        Returns:
            Dict: 处理统计信息
        """
        stats['sheets_processed'] = 0
        stats['sheets_removed'] = 0
        stats['nodes_removed'] = 0
        
        try:
            # 使用minidom解析XML
            import xml.dom.minidom as minidom
            dom = minidom.parse(content_xml_path)
            
            # 获取所有sheet
            sheets = dom.getElementsByTagName('sheet')
            sheet_nodes = []
            for i in range(sheets.length):
                sheet_nodes.append(sheets[i])
            
            for sheet in sheet_nodes:
                stats['sheets_processed'] += 1
                
                # 获取根topic
                rootTopics = sheet.getElementsByTagName('topic')
                if rootTopics.length == 0:
                    continue
                    
                rootTopic = rootTopics[0]
                
                # 获取该根topic下的所有topic（除了根topic）
                allTopics = rootTopic.getElementsByTagName('topic')
                topics_to_remove = []
                
                for i in range(allTopics.length):
                    topic = allTopics[i]
                    # 跳过根topic
                    if topic == rootTopic:
                        continue
                    
                    # 检查是否应该保留这个节点
                    should_keep = self.should_keep_minidom_node(topic, target_marker_ids)
                    
                    if not should_keep:
                        topics_to_remove.append(topic)
                
                # 删除不需要的topic节点
                for topic in topics_to_remove:
                    parent = topic.parentNode
                    parent.removeChild(topic)
                    stats['nodes_removed'] += 1
                    logger.info(f"删除不包含目标标记的XML节点（minidom）")
            
            # 保存修改后的XML
            with open(content_xml_path, 'w', encoding='utf-8') as f:
                dom.writexml(f, encoding='utf-8')
            
            return stats
            
        except Exception as e:
            logger.error(f"处理content.xml失败: {str(e)}")
            raise

    def should_keep_minidom_node(self, node, target_marker_ids: List[str]) -> bool:
        """
        判断minidom节点是否应该保留
        保留包含目标markerId的节点或包含有效子节点的父节点
        """
        # 检查当前节点是否包含目标标记
        for marker_id in target_marker_ids:
            if self.has_target_marker(node, marker_id):
                logger.info(f"保留包含目标标记的XML节点（minidom）: markerId={marker_id}")
                return True
        
        # 检查是否有子节点包含目标标记
        child_topics = node.getElementsByTagName('topic')
        for i in range(child_topics.length):
            child_topic = child_topics[i]
            if child_topic == node:
                continue  # 跳过自己
            
            for marker_id in target_marker_ids:
                if self.has_target_marker(child_topic, marker_id):
                    logger.info(f"保留包含有效子节点的XML父节点（minidom）")
                    return True
        
        return False

# 创建全局实例
xmind_filter = XMindMarkerFilter() 