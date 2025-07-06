/**
 * 此脚本使用PyInstaller打包Python后端为可执行文件
 * 它会创建一个独立的可执行文件，不需要Python解释器
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 路径配置
const rootDir = path.resolve(__dirname, '../..');
const backendDir = path.join(rootDir, 'backend');
const distDir = path.join(backendDir, 'dist');
const buildDir = path.join(backendDir, 'build');
const mainScript = path.join(backendDir, 'main.py');

// 检测操作系统
const isWindows = process.platform === 'win32';
const isMac = process.platform === 'darwin';
const pythonCommand = isWindows ? 'python' : 'python3';
const pipCommand = isWindows ? 'pip' : 'pip3';

/**
 * 运行命令并返回Promise
 */
function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    console.log(`执行命令: ${command} ${args.join(' ')}`);
    
    const proc = spawn(command, args, {
      ...options,
      stdio: 'inherit'
    });
    
    proc.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    proc.on('error', (err) => {
      reject(err);
    });
  });
}

/**
 * 检查PyInstaller是否安装，如果未安装则安装
 */
async function checkPyInstaller() {
  try {
    console.log('检查PyInstaller...');
    execSync(`${pythonCommand} -m PyInstaller --version`);
    console.log('PyInstaller已安装');
  } catch (err) {
    console.log('PyInstaller未安装，正在安装...');
    try {
      await runCommand(pythonCommand, ['-m', 'pip', 'install', 'pyinstaller']);
      console.log('PyInstaller安装成功');
    } catch (err) {
      console.error('安装PyInstaller失败:', err.message);
      throw err;
    }
  }
}

/**
 * 准备打包配置
 */
function prepareSpec() {
  // 创建spec文件
  const specPath = path.join(backendDir, 'main.spec');
  const specContent = `# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['${mainScript.replace(/\\/g, '\\\\')}'],
    pathex=['${backendDir.replace(/\\/g, '\\\\')}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='xmind_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='xmind_backend',
)
`;

  fs.writeFileSync(specPath, specContent);
  console.log(`创建spec文件: ${specPath}`);
}

/**
 * 清理旧的构建文件
 */
function cleanBuildDirs() {
  console.log('清理旧的构建文件...');
  
  // 清理dist目录
  if (fs.existsSync(distDir)) {
    fs.rmSync(distDir, { recursive: true, force: true });
  }
  
  // 清理build目录
  if (fs.existsSync(buildDir)) {
    fs.rmSync(buildDir, { recursive: true, force: true });
  }
}

/**
 * 使用PyInstaller打包
 */
async function buildWithPyinstaller() {
  console.log('使用PyInstaller打包Python后端...');
  
  try {
    // 检查主脚本是否存在
    if (!fs.existsSync(mainScript)) {
      throw new Error(`找不到主脚本: ${mainScript}`);
    }
    
    // 创建spec文件
    prepareSpec();
    
    // 执行PyInstaller
    await runCommand(pythonCommand, [
      '-m', 'PyInstaller',
      '--clean',
      '--noconfirm',
      path.join(backendDir, 'main.spec')
    ], { cwd: backendDir });
    
    console.log('PyInstaller打包完成');
    
    // 检查打包结果
    const executablePath = path.join(distDir, 'xmind_backend', isWindows ? 'xmind_backend.exe' : 'xmind_backend');
    if (!fs.existsSync(executablePath)) {
      throw new Error(`找不到打包后的可执行文件: ${executablePath}`);
    }
    
    console.log(`可执行文件位置: ${executablePath}`);
    
    // 创建一个README文件，提供使用说明
    const readmePath = path.join(distDir, 'README.txt');
    const readmeContent = `XMind冒烟测试用例导出工具后端
============================

此目录包含打包后的后端可执行文件，由PyInstaller创建。

使用方法:
1. 确保xmind_backend目录与Electron应用在同一目录下
2. Electron应用会自动启动后端服务

技术细节:
- 端口: 8000
- API路径: /api/*
- 健康检查: /health

`;
    fs.writeFileSync(readmePath, readmeContent);
  } catch (err) {
    console.error('PyInstaller打包失败:', err.message);
    throw err;
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('开始打包Python后端...');
  
  try {
    // 检查PyInstaller
    await checkPyInstaller();
    
    // 清理旧构建
    cleanBuildDirs();
    
    // 执行打包
    await buildWithPyinstaller();
    
    console.log('Python后端打包完成！✅');
    console.log(`可执行文件已生成在: ${path.join(distDir, 'xmind_backend')}`);
  } catch (err) {
    console.error('打包失败:', err.message);
    process.exit(1);
  }
}

// 执行主函数
main(); 