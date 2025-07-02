# XMind 冒烟测试用例导出工具 🚀

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-green.svg)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个智能化的XMind思维导图转冒烟测试用例工具，支持标识符识别、用例生成和多格式导出。

## ✨ 功能特性

### 🎯 智能分析
- **标识符识别**: 自动识别XMind文件中的优先级标识符（P1-P5、重要、旗帜、星标等）
- **节点提取**: 智能提取思维导图中的测试节点和层级关系
- **适配性强**: 支持多种XMind标识符格式和命名方式

### 📋 测试用例生成
- **规范化输出**: 生成符合测试工程师标准的冒烟测试用例
- **优先级映射**: 自动将标识符映射为测试优先级（P0-P5）
- **测试步骤**: 智能生成操作步骤和预期结果
- **冒烟筛选**: 基于业务规则筛选适合冒烟测试的用例

### 📊 多格式导出
- **表格展示**: 清晰的测试用例表格界面，支持排序和筛选
- **Excel导出**: 完整的Excel工作簿，包含用例明细和汇总统计
- **JSON导出**: 结构化的JSON数据，便于集成和二次开发
- **复制功能**: 支持一键复制表格和JSON数据

### 🎨 用户体验
- **现代化界面**: 基于Element Plus的美观UI设计
- **响应式布局**: 适配不同屏幕尺寸
- **实时反馈**: 详细的操作提示和进度显示
- **错误处理**: 友好的错误提示和异常处理

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代化Python Web框架
- **xmindparser**: XMind文件解析库
- **openpyxl**: Excel文件操作
- **Uvicorn**: ASGI服务器

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **TypeScript**: JavaScript超集，提供类型安全
- **Element Plus**: Vue 3组件库
- **Vite**: 现代化构建工具
- **XLSX**: Excel文件处理库

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

#### 启动后端服务
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
- 显示分析结果统计

### 3. 选择标识符
- 在分析结果页面查看发现的标识符
- 选择需要导出的标识符类型
- 支持全选/清空操作

### 4. 导出测试用例
- 点击"导出冒烟用例"生成测试用例
- 在表格中查看生成的用例详情
- 支持Excel导出和JSON下载

### 5. 查看和使用结果
- **表格视图**: 直观查看所有测试用例
- **详情对话框**: 点击"查看详情"查看完整的测试步骤
- **Excel文件**: 包含用例列表和统计汇总两个工作表
- **JSON数据**: 结构化数据便于API集成

## 📁 项目结构

```
automation-xmind/
├── backend/                 # 后端代码
│   ├── main.py             # FastAPI应用入口
│   ├── xmind_parser.py     # XMind文件解析器
│   ├── smoke_case_builder.py # 冒烟用例构建器
│   ├── requirements.txt    # Python依赖
│   └── test_*.py          # 测试脚本
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   └── main.ts        # 应用入口
│   ├── package.json       # Node.js依赖
│   └── vite.config.ts     # Vite配置
├── README.md              # 项目文档
└── 学习报告.xmind          # 示例测试文件
```

## 🧪 测试

### 运行后端测试
```bash
cd backend
python test_export.py        # 测试导出功能
python test_excel_export.py  # 测试Excel导出
python verify_excel.py       # 验证Excel文件
```

### 测试用例覆盖
- [x] XMind文件解析
- [x] 标识符识别和映射
- [x] 冒烟用例生成
- [x] Excel导出功能
- [x] JSON数据导出
- [x] API接口测试

## 📊 功能展示

### 支持的标识符类型
| 标识符 | 映射优先级 | 描述 |
|--------|------------|------|
| important | P0 | 重要功能 |
| priority-1 | P1 | 高优先级 |
| priority-2 | P2 | 中优先级 |
| priority-3 | P3 | 标准优先级 |
| flag-red | P1 | 红色旗帜 |
| star-red | P1 | 红色星标 |

### 生成的测试用例格式
```json
{
  "case_id": "SMOKE_001",
  "title": "答题器参与课中不完成加油站验证",
  "module": "课堂互动",
  "priority": "P3",
  "markers": ["priority-3"],
  "test_path": "学习报告 > 课中数据 > 答题器参与课中不完成加油站",
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

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2025-01-02)
- ✨ 完整的XMind文件解析功能
- ✨ 智能标识符识别和映射
- ✨ 冒烟测试用例自动生成
- ✨ Excel和JSON多格式导出
- ✨ 现代化Web界面
- ✨ 完整的测试覆盖

## 🐛 问题反馈

如果您在使用过程中遇到问题，请：

1. 查看 [常见问题](FAQ.md)
2. 搜索已有的 [Issues](../../issues)
3. 创建新的 Issue 并提供详细信息

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [xmindparser](https://github.com/tobyqin/xmindparser) - XMind文件解析
- [Element Plus](https://element-plus.org/) - Vue 3 组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化API框架

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
