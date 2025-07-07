# 将Vue3+Python项目转换为Electron应用的任务清单

## 1. 环境准备与依赖安装

- [x] 安装Electron相关依赖
  ```bash
  cd frontend
  npm install --save-dev electron electron-builder
  ```

- [x] 创建Electron配置文件
  - 在frontend目录创建electron.cjs和preload.cjs (注意：使用CommonJS格式)

## 2. 主进程配置

- [x] 创建main.js (Electron主进程)
  - 配置应用窗口
  - 设置应用菜单
  - 处理应用生命周期事件
  - 实现IPC通信机制
  - 自定义开发环境检测逻辑

- [x] 创建preload.js
  - 暴露安全的API给渲染进程
  - 设置上下文隔离

## 3. 后端集成

- [x] 实现Python后端启动机制
  - 使用child_process启动Python服务
  - 处理Python进程的生命周期管理
  - 实现进程间通信

- [x] 修改后端代码适配Electron环境
  - 调整路径处理逻辑
  - 修改网络监听配置
  - 添加进程间通信支持

## 4. 前端适配

- [x] 修改Vue前端API调用
  - 将HTTP请求改为IPC通信或本地API调用
  - 调整资源路径引用

- [ ] 添加Electron特有功能
  - 文件系统访问
  - 系统对话框
  - 托盘图标

## 5. 打包配置

- [x] 配置electron-builder
  - 创建package.json打包脚本
  - 设置应用图标和元数据
  - 配置文件包含规则

- [x] 配置Python打包
  - 使用PyInstaller创建独立可执行文件
  - 或打包Python解释器和依赖

## 6. 跨平台适配

- [x] Windows适配
  - 处理路径分隔符差异
  - 配置.bat启动脚本
  - 测试打包应用

- [x] macOS适配
  - 配置签名和公证
  - 测试打包应用

- [x] Linux适配 (可选)
  - 处理权限问题
  - 测试打包应用

## 7. 资源路径处理

- [x] 实现开发和生产环境的路径解析
  - 使用`app.getAppPath()`获取应用路径
  - 处理相对路径和绝对路径

- [ ] 处理临时文件和用户数据
  - 使用`app.getPath('userData')`存储用户数据
  - 配置临时文件目录

## 8. 测试与调试

- [x] 设置开发环境调试配置
  - 配置开发者工具
  - 添加日志记录

- [ ] 测试应用功能
  - 验证XMind解析功能
  - 测试Excel导出功能
  - 检查UI交互

## 9. 优化与改进


- [ ] XMind标识符识别优化
  - 目前用户上传的XMind文件中的标识符是硬编码在代码中的，无法完全识别用户XMind中所有可能的标识符
  - 实现动态标识符识别，自动检测并提取用户上传XMind文件中包含的全部标识符
  - 改进标识符映射逻辑，提高识别准确率和兼容性
  - 添加未知标识符的展示和选择功能，提升用户体验
  - 兼容下游导出Excel选中标识符的功能，确保导出数据准确无误

- [x] Excel导出节点排序优化
  - 解决Excel导出时某些节点出现乱序的问题
  - 实现稳定的节点排序算法，保持XMind中的原始层级和顺序关系
    - 完全保留XMind中的原始顺序，不进行额外排序
    - 在XMind解析阶段记录节点的原始顺序索引，并在整个数据流程中保留
    - 在测试用例构建和Excel导出阶段使用XMind原始顺序索引进行排序
  - 优化层级合并逻辑，确保节点按照正确的顺序和层级关系展示
    - 改进节点路径解析和分组算法
    - 优化合并区域计算方法，首先按列排序，然后按XMind原始顺序排序
  - 改进合并单元格算法，处理非连续行的情况
    - 添加非连续行自动分段合并功能
    - 实现对合并区域的验证和过滤
    - 确保合并区域也遵循XMind的原始顺序
  - 优化合并单元格样式处理，确保视觉一致性
    - 自动复制合并区域首行的样式到所有合并单元格
    - 增强边框和背景色处理
  - 实现方案:
    - 在xmind_parser.py中，使用层级索引（父节点索引*1000 + 子节点序号）记录每个节点的原始位置
    - 在smoke_case_builder.py中，保留xmind_index并按它排序测试用例
    - 在enhanced_hierarchical_exporter.py中，修改_write_enhanced_hierarchical_data方法，使用xmind_index而非full_path排序
    - 确保合并区域计算和应用过程中也按照xmind_index排序


## 注意事项

- [x] 处理ES模块和CommonJS兼容性问题
  - 使用.cjs扩展名表示CommonJS模块
  - 使用自定义开发环境检测逻辑，避免依赖ES模块包

- [x] Python环境配置
  - 确保Python可执行文件路径正确
  - 处理不同操作系统下的路径差异

- [x] 打包前的准备工作
  - 创建虚拟环境并安装依赖
  - 确保所有资源文件都被正确包含

## 参考资源

- [Electron文档](https://www.electronjs.org/docs)
- [electron-builder文档](https://www.electron.build/)
- [PyInstaller文档](https://pyinstaller.org/en/stable/) 