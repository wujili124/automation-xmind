#!/usr/bin/env node

// 跨平台后端启动脚本
// 自动检测操作系统并运行对应的启动脚本

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// 获取当前文件的目录路径 (ES模块中的__dirname替代)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🐍 启动Python后端服务...');

// 检测操作系统
const isWindows = process.platform === 'win32';
const backendDir = path.join(__dirname, '..', 'backend');

// 选择对应的脚本
const scriptName = isWindows ? 'start_backend.bat' : './start_backend.sh';
const scriptPath = path.join(backendDir, isWindows ? 'start_backend.bat' : 'start_backend.sh');

// 检查脚本是否存在
if (!fs.existsSync(scriptPath)) {
    console.error(`❌ 启动脚本不存在: ${scriptPath}`);
    process.exit(1);
}

console.log(`🔧 检测到系统: ${isWindows ? 'Windows' : 'Unix/Linux/macOS'}`);
console.log(`📁 运行脚本: ${scriptName}`);

// 启动后端脚本
const child = spawn(scriptName, [], {
    cwd: backendDir,
    stdio: 'inherit',
    shell: true
});

// 处理进程事件
child.on('error', (error) => {
    console.error(`❌ 启动失败: ${error.message}`);
    process.exit(1);
});

child.on('close', (code) => {
    console.log(`🛑 后端服务已停止 (退出码: ${code})`);
    process.exit(code);
});

// 处理Ctrl+C
process.on('SIGINT', () => {
    console.log('\n🛑 正在停止后端服务...');
    child.kill('SIGINT');
});

process.on('SIGTERM', () => {
    console.log('\n🛑 正在停止后端服务...');
    child.kill('SIGTERM');
}); 