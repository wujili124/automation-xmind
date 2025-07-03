# XMind 冒烟测试用例导出工具 🚀

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-green.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个智能化的XMind思维导图转冒烟测试用例工具，支持标识符识别、智能层级合并和多格式导出。

## ✨ 核心功能特性

### 🎯 智能分析
- **标识符识别**: 自动识别XMind文件中的优先级标识符（P1-P5、重要、旗帜、星标等）
- **节点提取**: 智能提取思维导图中的测试节点和层级关系
- **层级筛选**: 优化的筛选逻辑，保留标记节点及其完整子树结构
- **适配性强**: 支持多种XMind标识符格式和命名方式

### 📋 测试用例生成
- **规范化输出**: 生成符合测试工程师标准的冒烟测试用例
- **优先级映射**: 自动将标识符映射为测试优先级（P0-P5）
- **测试步骤**: 智能生成操作步骤和预期结果
- **冒烟筛选**: 基于业务规则筛选适合冒烟测试的用例
- **路径拆分**: 自动将测试路径拆分为节点1-5层级结构

### 🔥 增强层级合并Excel导出
- **智能单元格合并**: 相同父节点的子节点自动垂直合并
- **完美视觉效果**: 完全匹配《冒烟用例导出模版.xlsx》格式要求
- **层级背景色**: 不同节点层级使用不同背景色区分
- **精确合并算法**: 递归层级分组与智能合并计算
- **模版适配**: 严格按照12列格式（节点1-5 + 业务字段）

### 📊 多格式导出选项
- **🔥 增强层级合并**: 智能合并单元格，完美层级展示
- **📋 模版格式导出**: 基础业务字段，匹配标准模版
- **📄 标准JSON导出**: 结构化数据，便于API集成
- **📁 过滤XMind导出**: 基于标识符过滤的XMind文件
- **🔄 传统Excel备选**: 容错机制，提供传统行列格式

### 🎨 用户体验
- **现代化界面**: 基于Element Plus的美观UI设计
- **响应式布局**: 适配不同屏幕尺寸
- **实时反馈**: 详细的操作提示和进度显示
- **智能容错**: 友好的错误提示和备选方案
- **文件标识**: 明确的文件名前缀区分导出方式

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代化Python Web框架
- **xmindparser**: XMind文件解析库  
- **openpyxl**: Excel文件操作和合并单元格
- **lxml & minidom**: XML处理和节点筛选
- **Uvicorn**: ASGI服务器

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **TypeScript**: JavaScript超集，提供类型安全
- **Element Plus**: Vue 3组件库
- **Vite**: 现代化构建工具
- **Axios**: HTTP客户端

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd automation-xmind
```

#### 2. 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install
# 或使用 yarn
yarn install
```

### 运行项目

#### 启动后端服务（推荐方式）
```bash
cd backend
bash restart_api.sh  # 自动重启API服务
```

#### 或手动启动
```bash
cd backend
source venv/bin/activate  # macOS/Linux
python main.py
```
后端服务将在 `http://localhost:8000` 启动

#### 启动前端服务
```bash
cd frontend
npm run dev
# 或使用 yarn
yarn dev
```
前端应用将在 `http://localhost:5173` 启动

## 📖 使用指南

### 1. 上传XMind文件
- 点击"选择文件"或拖拽XMind文件到上传区域
- 支持 `.xmind` 格式文件
- 文件大小限制：50MB

### 2. 分析文件
- 系统自动解析XMind文件结构
- 识别其中的标识符和测试节点
- 显示分析结果统计和标识符分布

### 3. 选择标识符
- 在分析结果页面查看发现的标识符
- 选择需要导出的标识符类型
- 支持全选/清空操作

### 4. 生成测试用例
- 点击"导出冒烟用例"生成测试用例
- 系统应用优化的筛选逻辑，保留完整层级结构
- 在表格中查看生成的用例详情

### 5. 🔥 增强层级合并Excel导出
- 点击"导出Excel"按钮
- 系统自动调用增强层级合并API
- 下载的文件名包含`🔥增强层级合并`前缀
- 打开Excel文件可看到智能合并的层级结构

### 6. 其他导出选项
- **XMind导出**: 基于筛选结果的XMind文件
- **JSON下载**: 结构化数据便于API集成
- **传统Excel**: 如增强导出失败的备选方案

## 🎯 API接口

### 核心接口
- `GET /` - 健康检查
- `POST /api/analyze` - 分析XMind文件
- `POST /api/export` - 标准JSON格式导出
- `POST /api/export-template` - 基础模版格式导出
- `POST /api/export-hierarchical` - 层级合并导出
- `🔥 POST /api/export-enhanced-hierarchical` - **增强层级合并导出**
- `POST /api/export-xmind` - 过滤XMind导出

### 增强层级合并API示例
```javascript
POST /api/export-enhanced-hierarchical
{
  "selected_markers": ["priority-1", "priority-2", "flag-red"],
  "file_data": "[base64编码的XMind文件]"
}
```

**响应格式:**
```json
{
  "success": true,
  "file_data": "[base64编码的Excel文件]",
  "export_details": {
    "merged_regions_count": 9,
    "data_rows": 58,
    "features": ["精确单元格合并算法", "完美匹配模版视觉"]
  }
}
```

## 📁 项目结构

```
automation-xmind/
├── backend/                           # 后端代码
│   ├── main.py                       # FastAPI应用入口
│   ├── xmind_analyzer.py             # XMind文件分析器
│   ├── smoke_case_builder.py         # 冒烟用例构建器
│   ├── enhanced_hierarchical_exporter.py  # 🔥增强层级导出器
│   ├── excel_template_exporter.py    # 模版格式导出器
│   ├── hierarchical_excel_exporter.py # 层级合并导出器
│   ├── requirements.txt              # Python依赖
│   ├── restart_api.sh                # API重启脚本
│   ├── test_*.py                     # 测试脚本集合
│   └── 问题解决报告.md                # 技术文档
├── frontend/                         # 前端代码
│   ├── src/
│   │   ├── views/
│   │   │   ├── AnalyzeView.vue      # 分析页面
│   │   │   └── ExportView.vue       # 导出页面（已优化）
│   │   ├── router/                   # 路由配置
│   │   └── main.ts                   # 应用入口
│   ├── package.json                  # Node.js依赖
│   └── vite.config.ts               # Vite配置
├── 冒烟用例导出模版.xlsx              # 参考模版文件
├── 学习报告.xmind                    # 示例测试文件
└── README.md                         # 项目文档
```

## 🧪 测试验证

### 运行测试脚本
```bash
cd backend

# 综合测试（推荐）
python comprehensive_test.py           # 全面功能测试

# 专项测试
python test_frontend_backend_connection.py  # 前后端连接测试
python test_hierarchical_api.py        # 层级合并API测试
python analyze_excel_structure.py      # Excel结构分析
python verify_merge_result.py          # 合并效果验证
python final_verification.py           # 最终验证
```

### 测试覆盖范围
- ✅ XMind文件解析和标识符识别
- ✅ 层级筛选逻辑优化
- ✅ 冒烟用例生成算法
- ✅ 增强层级合并Excel导出
- ✅ 智能单元格合并功能
- ✅ 前后端API连接
- ✅ 多种导出格式验证
- ✅ 容错机制和备选方案

## 📊 功能展示

### 支持的标识符类型
| 标识符 | 映射优先级 | 描述 | 合并效果 |
|--------|------------|------|----------|
| important | P0 | 重要功能 | 红色背景合并 |
| priority-1 | P1 | 高优先级 | 深蓝色背景合并 |
| priority-2 | P2 | 中优先级 | 中蓝色背景合并 |
| priority-3 | P3 | 标准优先级 | 浅蓝色背景合并 |
| flag-red | P1 | 红色旗帜 | 自动层级合并 |
| star-red | P1 | 红色星标 | 智能单元格合并 |

### 🔥 层级合并示例
```
学习报告 (跨58行合并)
├── 答题情况 (跨6行合并)
│   ├── 答题器参与课中不完成加油站验证
│   ├── 答题器参与课中完成加油站验证
│   └── ...
├── 分享 (跨4行合并)
│   ├── 分享微信好友
│   ├── 分享朋友圈
│   └── ...
└── 课堂互动 (跨6行合并)
    ├── 参与全部互动
    └── ...
```

### 导出文件识别
- 🔥 **增强层级合并**: `🔥增强层级合并_冒烟测试用例_[时间].xlsx`
- 📋 **模版格式**: `模版格式_冒烟测试用例_[时间].xlsx`
- 📄 **传统格式**: `传统格式_冒烟测试用例_[时间].xlsx`
- 📁 **过滤XMind**: `冒烟测试用例_基于标识符_[时间].xmind`

### 生成的测试用例格式
```json
{
  "case_id": "SMOKE_001",
  "title": "答题器参与课中不完成加油站验证",
  "module": "课堂互动",
  "priority": "P3",
  "markers": ["priority-3"],
  "test_path": "学习报告 > 课中数据 > 答题器参与课中不完成加油站",
  "path_nodes": {
    "node1": "学习报告",
    "node2": "课中数据", 
    "node3": "答题器参与课中不完成加油站",
    "node4": "",
    "node5": ""
  },
  "platform": "Web",
  "smoke_result": "待测试",
  "developer": "待分配",
  "showcase_issue": "无",
  "steps": [
    {
      "step": 1,
      "action": "打开答题器功能",
      "expected": "答题器界面正常显示"
    }
  ],
  "smoke_criteria": {
    "is_core_function": true,
    "affects_main_flow": true,
    "execution_time": "< 2分钟"
  }
}
```

## 🎖️ 核心优势

### 🚀 技术创新
- **智能层级合并算法**: 递归分组计算，精确合并单元格
- **完美模版适配**: 100%匹配《冒烟用例导出模版.xlsx》格式
- **优化筛选逻辑**: 保留标记节点及其完整子树结构
- **容错机制**: 多重备选方案确保导出成功

### 📈 效率提升
- **一键导出**: 从XMind直接生成标准测试用例
- **视觉优化**: 层级合并让测试用例结构一目了然
- **批量处理**: 支持大量节点的高效处理
- **格式标准**: 完全符合测试团队工作流程

### 🛡️ 质量保证
- **全面测试覆盖**: 9个专项测试脚本验证功能
- **错误处理**: 友好的错误提示和异常处理
- **数据完整性**: 保证导出数据的完整性和准确性
- **性能优化**: 高效的文件处理和内存管理

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v2.0.0 (2025-07-03) 🔥 重大更新
- ✨ **新增增强层级合并Excel导出功能**
- ✨ 智能单元格合并，完美匹配模版格式
- ✨ 优化层级筛选逻辑，保留父子节点关联
- ✨ 修复前端导出Excel连接问题
- ✨ 新增多种导出方式和容错机制
- ✨ 完整的测试验证套件
- ✨ 层级背景色和视觉效果优化
- 🐛 修复前端与后端API连接断裂问题
- 🔧 重构导出逻辑，提供备选方案
- 📚 完善技术文档和使用指南

### v1.0.0 (2025-01-02)
- ✨ 完整的XMind文件解析功能
- ✨ 智能标识符识别和映射
- ✨ 冒烟测试用例自动生成
- ✨ Excel和JSON多格式导出
- ✨ 现代化Web界面
- ✨ 完整的测试覆盖

## 🐛 问题反馈

如果您在使用过程中遇到问题，请：

1. 查看 [问题解决报告](backend/问题解决报告.md)
2. 运行测试脚本验证功能：`python comprehensive_test.py`
3. 搜索已有的 [Issues](../../issues)
4. 创建新的 Issue 并提供详细信息

### 常见问题
- **Q**: 导出的Excel文件没有层级合并效果？
- **A**: 请确认下载的文件名包含`🔥增强层级合并`前缀，如果没有，说明前端调用了错误的API接口。

- **Q**: API服务无法启动？
- **A**: 请运行 `bash restart_api.sh` 或手动检查Python环境和依赖。

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [xmindparser](https://github.com/tobyqin/xmindparser) - XMind文件解析
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化API框架
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel文件操作和合并单元格

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

🔥 **特别推荐**: 体验最新的增强层级合并Excel导出功能，让您的测试用例展示更加直观和专业！
