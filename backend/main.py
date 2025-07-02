from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
import base64
import io
import json
import zipfile
import shutil
import tempfile
import os
from pathlib import Path

from xmind_parser import XMindAnalyzer
from smoke_case_builder import SmokeCaseBuilder
from xmind_marker_filter import xmind_filter
import xmindparser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="XMind冒烟测试用例导出工具",
    description="上传XMind文件，分析标识符，导出冒烟测试用例",
    version="1.0.0"
)

# 配置CORS - 添加5173端口支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化分析器和构建器
xmind_analyzer = XMindAnalyzer()
smoke_builder = SmokeCaseBuilder()

# 数据模型
class ExportRequest(BaseModel):
    selected_markers: List[str]
    file_data: str  # base64编码的文件数据

class XMindExportRequest(BaseModel):
    selected_markers: List[str]
    file_data: str  # base64编码的文件数据
    test_case_titles: List[str]  # 导出的测试用例标题列表

class AnalyzeResponse(BaseModel):
    filename: str
    markers_found: List[Dict[str, Any]]
    total_nodes: int
    suitable_for_smoke: int
    file_data: str  # 添加base64编码的文件数据，供导出使用

class TestDataRequest(BaseModel):
    """测试数据请求模型"""
    test_data: Dict[str, Any]

@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "XMind冒烟测试用例导出工具API正常运行", "status": "success"}

@app.post("/api/test/analyze")
async def test_analyze(request: TestDataRequest):
    """测试分析接口，用于模拟数据验证"""
    try:
        logger.info("接收到测试分析请求")
        
        # 模拟分析结果
        test_result = {
            "filename": "test.xmind",
            "markers_found": [
                {
                    "markerId": "important",
                    "symbol": "重要 (红色叹号)",
                    "count": 1,
                    "sample_nodes": ["登录功能"]
                },
                {
                    "markerId": "priority-1", 
                    "symbol": "优先级1 (红色1)",
                    "count": 1,
                    "sample_nodes": ["用户名密码登录验证"]
                },
                {
                    "markerId": "priority-2",
                    "symbol": "优先级2 (橙色2)", 
                    "count": 1,
                    "sample_nodes": ["登录失败处理"]
                },
                {
                    "markerId": "flag-red",
                    "symbol": "红旗",
                    "count": 1, 
                    "sample_nodes": ["注册功能"]
                },
                {
                    "markerId": "star-red",
                    "symbol": "红星",
                    "count": 1,
                    "sample_nodes": ["新用户注册验证"]
                }
            ],
            "total_nodes": 10,
            "suitable_for_smoke": 5,
            "file_data": base64.b64encode(str(request.test_data).encode()).decode()
        }
        
        logger.info(f"测试分析完成，找到 {len(test_result['markers_found'])} 种标识符")
        return test_result
        
    except Exception as e:
        logger.error(f"测试分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试分析失败: {str(e)}")

@app.post("/api/debug/analyze")
async def debug_analyze_xmind(file: UploadFile = File(...)):
    """
    调试分析XMind文件，显示原始标识符信息
    """
    try:
        # 验证文件格式
        if not file.filename.endswith('.xmind'):
            raise HTTPException(status_code=400, detail="只支持.xmind格式文件")
        
        # 读取文件内容
        file_content = await file.read()
        logger.info(f"调试分析文件: {file.filename}, 大小: {len(file_content)} bytes")
        
        # 使用xmindparser直接解析，查看原始结构
        file_obj = io.BytesIO(file_content)
        xmind_data = xmindparser.xmind_to_dict(file_obj)
        
        # 打印原始数据结构（用于调试）
        logger.info(f"XMind原始数据结构: {xmind_data}")
        
        # 提取所有标识符信息
        all_markers = []
        all_raw_nodes = []  # 保存所有原始节点数据
        node_count = 0
        
        def extract_markers_debug(topic, path="", level=1):
            nonlocal node_count
            if not isinstance(topic, dict):
                return
                
            title = topic.get('title', '').strip()
            if title:
                node_count += 1
                current_path = f"{path} > {title}" if path else title
                
                # 保存完整的原始节点数据
                all_raw_nodes.append({
                    "path": current_path,
                    "title": title,
                    "level": level,
                    "raw_data": topic  # 完整的原始数据
                })
                
                # 收集原始标识符信息
                markers = topic.get('markers', [])
                if markers:
                    logger.info(f"节点 '{title}' 发现标识符: {markers}")
                    for marker in markers:
                        all_markers.append({
                            "node_path": current_path,
                            "node_title": title,
                            "node_level": level,
                            "raw_marker": marker
                        })
                else:
                    # 检查是否有其他可能的标识符字段
                    possible_marker_fields = ['marker', 'flag', 'icon', 'symbol', 'priority', 'labels', 'tags']
                    for field in possible_marker_fields:
                        if field in topic and topic[field]:
                            logger.info(f"节点 '{title}' 发现可能的标识符字段 '{field}': {topic[field]}")
                
                # 递归处理子节点
                subtopics = topic.get('topics', [])
                for subtopic in subtopics:
                    extract_markers_debug(subtopic, current_path, level + 1)
        
        # 处理所有工作表
        for sheet_idx, sheet in enumerate(xmind_data):
            logger.info(f"处理工作表 {sheet_idx}: {list(sheet.keys())}")
            root_topic = sheet.get('topic', {})
            extract_markers_debug(root_topic)
        
        # 统计标识符类型
        marker_types = {}
        for marker_info in all_markers:
            marker_data = marker_info['raw_marker']
            logger.info(f"处理标识符数据: {marker_data}")
            
            if isinstance(marker_data, dict):
                marker_id = marker_data.get('markerId', 'unknown')
                marker_type = marker_data.get('markerType', 'unknown')
                
                # 记录所有可能的标识符字段
                marker_key = f"{marker_id}_{marker_type}" if marker_type != 'unknown' else marker_id
                
                if marker_key not in marker_types:
                    marker_types[marker_key] = {
                        "count": 0,
                        "examples": [],
                        "raw_data": marker_data
                    }
                marker_types[marker_key]["count"] += 1
                if len(marker_types[marker_key]["examples"]) < 3:
                    marker_types[marker_key]["examples"].append(marker_info['node_title'])
            elif isinstance(marker_data, str):
                # 字符串类型的标识符
                if marker_data not in marker_types:
                    marker_types[marker_data] = {
                        "count": 0,
                        "examples": [],
                        "raw_data": marker_data
                    }
                marker_types[marker_data]["count"] += 1
                if len(marker_types[marker_data]["examples"]) < 3:
                    marker_types[marker_data]["examples"].append(marker_info['node_title'])
        
        debug_result = {
            "filename": file.filename,
            "total_nodes": node_count,
            "total_markers": len(all_markers),
            "unique_marker_types": len(marker_types),
            "marker_types": marker_types,
            "all_markers": all_markers[:20],  # 显示前20个标识符
            "sample_raw_nodes": all_raw_nodes[:10],  # 显示前10个原始节点
            "xmind_structure_sample": xmind_data[:1] if xmind_data else [],  # 显示第一个工作表的结构
            "supported_markers": [
                {"id": "important", "name": "重要 (红色叹号)"},
                {"id": "priority-1", "name": "优先级1 (红色1)"},
                {"id": "priority-2", "name": "优先级2 (橙色2)"},
                {"id": "priority-3", "name": "优先级3 (黄色3)"},
                {"id": "priority-4", "name": "优先级4 (绿色4)"},
                {"id": "priority-5", "name": "优先级5 (灰色5)"},
                {"id": "flag-red", "name": "红旗"},
                {"id": "flag-yellow", "name": "黄旗"},
                {"id": "star-red", "name": "红星"},
                {"id": "star-yellow", "name": "黄星"}
            ]
        }
        
        logger.info(f"调试分析完成: 节点={node_count}, 标识符={len(all_markers)}, 类型={len(marker_types)}")
        logger.info(f"发现的标识符类型: {list(marker_types.keys())}")
        
        return debug_result
        
    except Exception as e:
        logger.error(f"调试分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"调试分析失败: {str(e)}")

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_xmind(file: UploadFile = File(...)):
    """
    分析XMind文件，提取标识符信息
    """
    try:
        # 验证文件格式
        if not file.filename.endswith('.xmind'):
            raise HTTPException(status_code=400, detail="只支持.xmind格式文件")
        
        # 读取文件内容
        file_content = await file.read()
        logger.info(f"接收到文件: {file.filename}, 大小: {len(file_content)} bytes")
        
        # 将文件内容转换为base64编码（供前端传递给导出接口）
        file_data_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # 分析XMind文件
        analysis_result = xmind_analyzer.analyze_markers(file_content, file.filename)
        
        # 添加file_data到返回结果
        analysis_result["file_data"] = file_data_base64
        
        logger.info(f"分析完成，找到 {len(analysis_result['markers_found'])} 种标识符")
        
        return AnalyzeResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"分析XMind文件时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")

@app.post("/api/export")
async def export_smoke_cases(request: ExportRequest):
    """
    根据选中的标识符导出冒烟测试用例
    """
    try:
        logger.info(f"开始导出冒烟用例，选中标识符: {request.selected_markers}")
        
        # 验证请求数据
        if not request.selected_markers:
            raise HTTPException(status_code=400, detail="请至少选择一个标识符")
        
        if not request.file_data:
            raise HTTPException(status_code=400, detail="缺少文件数据")
        
        # 构建冒烟测试用例
        smoke_cases = smoke_builder.build_smoke_cases(
            request.selected_markers,
            request.file_data
        )
        
        total_cases = smoke_cases['smoke_test_suite']['metadata']['total_cases']
        logger.info(f"导出完成，生成 {total_cases} 个冒烟用例")
        
        return smoke_cases
        
    except Exception as e:
        logger.error(f"导出冒烟用例时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@app.post("/api/export-xmind")
async def export_xmind_filtered(request: XMindExportRequest):
    """
    基于markerId精确过滤XMind文件并导出
    完全保持原始样式和结构
    """
    try:
        logger.info(f"🚀 开始基于markerId过滤XMind文件")
        logger.info(f"选中标识符: {request.selected_markers}")
        logger.info(f"测试用例数量: {len(request.test_case_titles)}")
        
        # 验证请求数据
        if not request.selected_markers:
            raise HTTPException(status_code=400, detail="请至少选择一个标识符")
        
        if not request.file_data:
            raise HTTPException(status_code=400, detail="缺少文件数据")
        
        # 验证base64数据
        try:
            file_bytes = base64.b64decode(request.file_data)
            logger.info(f"原始文件大小: {len(file_bytes):,} bytes")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"文件数据解码失败: {str(e)}")
        
        # 使用新的markerId过滤器进行精确过滤
        try:
            filter_result = xmind_filter.filter_xmind_by_markers(
                file_data=request.file_data,  # 直接传递base64数据
                selected_markers=request.selected_markers,  # 使用新的参数名
                engine='lxml'  # 使用lxml进行高性能处理
            )
            
            logger.info(f"🎉 markerId过滤完成！")
            logger.info(f"处理统计: {filter_result['processing_details']}")
            
        except Exception as e:
            logger.error(f"❌ markerId过滤失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"XMind文件过滤失败: {str(e)}")
        
        # 返回结果
        return {
            "success": True,
            "message": "XMind文件基于markerId精确过滤成功",
            "file_data": filter_result['file_data'],  # 已经是base64格式
            "filename": "filtered_markers.xmind",
            "processing_details": filter_result['processing_details']
        }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ XMind文件导出过程中发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出过程失败: {str(e)}")

def create_xmind_metadata(build_path: Path):
    """
    创建XMind文件所需的元数据文件
    """
    # 这个函数现在不再需要，因为我们直接复制原始文件的元数据

def start_server():
    """启动服务器函数"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    print("🚀 正在启动XMind冒烟测试用例导出工具API服务器...")
    start_server() 