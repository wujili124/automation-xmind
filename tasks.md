# XMind 冒烟测试用例导出工具 - 任务清单

## 项目概述
简单的XMind文件上传分析工具：上传XMind → Python解析 → 选择标识 → 导出测试用例

## 技术栈
- 前端：Vue 3 + Vue Router + Element Plus
- 后端：Python + FastAPI + xmindparser

## 标识符映射配置
```python
xmind_markers = [
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
```

---

## 功能流程
1. **上传页面** - 用户选择XMind文件
2. **分析页面** - Python解析文件，显示包含的标识符
3. **导出页面** - 用户选择标识符，点击按钮导出JSON

---

## 任务清单

### 🎯 后端开发 (Python)

#### API接口 (2个接口)
- [ ] `POST /api/analyze` - 上传并分析XMind文件
  - [ ] 接收文件流 (不保存到磁盘)
  - [ ] 解析XMind结构
  - [ ] 返回文件中存在的标识符列表

- [ ] `POST /api/export` - 导出测试用例
  - [ ] 接收选中的标识符列表
  - [ ] 筛选匹配的节点
  - [ ] 返回JSON格式的测试用例

#### 核心功能
- [ ] **XMind标识符分析器**
  ```python
  def analyze_xmind_markers(file_content):
      # 1. 解析XMind文件获取所有节点
      # 2. 提取每个节点的markerId (XMind对外开放的标识ID)
      # 3. 统计各标识符的数量和分布
      # 4. 返回可选择的标识符列表
  ```

- [ ] **冒烟用例导出器**
  ```python
  def export_smoke_test_cases(nodes, selected_markers):
      # 1. 根据选中的标识符筛选节点
      # 2. 分析节点层级结构，构建测试路径
      # 3. 按冒烟用例规范格式化输出
      # 4. 生成符合测试标准的JSON结构
  ```

#### 重点：标识ID分析逻辑
- [ ] **解析XMind原生标识**
  - [ ] 读取XMind文件的markers属性
  - [ ] 映射XMind内部markerId到自定义标识
  - [ ] 处理多标识节点的情况
  - [ ] 验证标识的有效性

- [ ] **节点分析规则**
  - [ ] 识别测试用例节点（叶子节点或特定层级）
  - [ ] 构建完整的节点父子关系路径
  - [ ] 提取节点的测试描述和期望结果
  - [ ] 判断节点是否适合作为冒烟用例

### 🎯 前端开发 (Vue3)

#### 页面路由 (3个页面)
- [ ] **上传页面** `/upload`
  - [ ] 文件选择器
  - [ ] 上传按钮
  - [ ] 上传进度提示

- [ ] **分析页面** `/analyze` 
  - [ ] 显示XMind文件信息
  - [ ] 显示检测到的标识符列表
  - [ ] 前往导出页面按钮

- [ ] **导出页面** `/export`
  - [ ] **标识符选择区域**
    - [ ] 复选框列表（用户可多选）
    - [ ] 显示每个标识符的用例数量
    - [ ] 全选/反选功能
  - [ ] **导出操作区域**
    - [ ] 导出按钮
    - [ ] 导出格式选择
  - [ ] **结果展示区域**
    - [ ] 格式化的JSON显示
    - [ ] 复制到剪贴板按钮
    - [ ] 下载JSON文件按钮

#### 核心组件
- [ ] **FileUpload.vue** - 文件上传组件
- [ ] **MarkerSelector.vue** - 标识符多选组件  
- [ ] **SmokeTestDisplay.vue** - 冒烟用例展示组件

---

## 数据结构

### 分析接口返回
```json
{
  "filename": "test.xmind", 
  "markers_found": [
    {
      "markerId": "priority-1", 
      "symbol": "优先级1 (红色1)", 
      "count": 5,
      "sample_nodes": ["登录功能", "支付流程"]
    },
    {
      "markerId": "important", 
      "symbol": "重要 (红色叹号)", 
      "count": 3,
      "sample_nodes": ["数据备份", "安全验证"]
    }
  ],
  "total_nodes": 25,
  "suitable_for_smoke": 8
}
```

### 冒烟用例规范格式
```json
{
  "smoke_test_suite": {
    "metadata": {
      "source_file": "test.xmind",
      "export_time": "2024-01-01T10:00:00Z",
      "selected_markers": ["priority-1", "important"],
      "total_cases": 8
    },
    "test_cases": [
      {
        "case_id": "SMOKE_001",
        "title": "用户登录功能验证",
        "module": "用户管理",
        "test_path": "功能测试/用户管理/登录功能",
        "priority": "P1",
        "markers": ["priority-1"],
        "steps": [
          {
            "step": 1,
            "action": "打开登录页面",
            "expected": "页面正常显示"
          },
          {
            "step": 2, 
            "action": "输入有效用户名密码",
            "expected": "成功登录系统"
          }
        ],
        "smoke_criteria": {
          "is_core_function": true,
          "affects_main_flow": true,
          "execution_time": "< 2分钟"
        }
      }
    ]
  }
}
```

---

## 冒烟用例提取规范

### 节点筛选条件
- [ ] **必须包含选中的标识符**
- [ ] **节点层级为3-5层** (不要太浅或太深)
- [ ] **节点描述包含动作词** (测试、验证、检查等)
- [ ] **非配置类节点** (排除环境配置、数据准备等)

### 用例构建规则
- [ ] **标题规范**: 动作 + 对象 + 期望
- [ ] **路径构建**: 完整的节点父子关系路径
- [ ] **步骤提取**: 子节点自动转换为测试步骤
- [ ] **优先级映射**: 根据标识符自动设置优先级

### 质量控制
- [ ] **去重处理**: 相同路径的节点合并
- [ ] **长度限制**: 单个用例步骤不超过10步
- [ ] **完整性检查**: 确保每个用例都有明确的验证点
- [ ] **可执行性验证**: 步骤描述具备可操作性

---

## 开发顺序

### 第1步：后端基础 (1天)
- [ ] 创建FastAPI项目
- [ ] 实现XMind文件解析
- [ ] 完成标识符提取逻辑

### 第2步：前端基础 (1天)  
- [ ] 创建Vue3项目
- [ ] 配置路由 (3个页面)
- [ ] 实现文件上传功能

### 第3步：核心功能 (2天)
- [ ] **重点**: 完善冒烟用例导出逻辑
- [ ] 前端多选标识符界面
- [ ] 前后端数据联调

### 第4步：界面优化 (1天)
- [ ] 冒烟用例格式化显示
- [ ] 复制和下载功能
- [ ] 错误提示和用户引导

**总计：5天**

---

## 文件结构

```
project/
├── backend/
│   ├── main.py              # FastAPI入口
│   ├── xmind_parser.py      # XMind解析逻辑
│   ├── smoke_case_builder.py # 冒烟用例构建器
│   └── requirements.txt     # 依赖列表
└── frontend/
    ├── src/
    │   ├── views/           # 3个页面
    │   ├── components/      # 3个组件
    │   └── router/          # 路由配置
    └── package.json
```

---

## 完成标准
- [ ] 可以上传XMind文件并分析标识符
- [ ] 用户可以多选标识符进行筛选
- [ ] 导出的冒烟用例符合测试规范
- [ ] JSON格式规范，包含完整的测试步骤
- [ ] 支持复制和下载功能
- [ ] 界面简洁，操作流畅 