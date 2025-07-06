/**
 * 打包前准备工作脚本
 * 执行以下任务：
 * 1. 检查并创建Python虚拟环境
 * 2. 安装Python和npm依赖
 * 3. 确保资源文件正确包含
 * 4. 配置平台特定设置
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const { findPythonExecutable } = require('./python_finder');

// 检测当前平台
const platform = process.platform;
const isWindows = platform === 'win32';
const isMacOS = platform === 'darwin';
const isLinux = platform === 'linux';

// 路径配置
const rootDir = path.resolve(__dirname, '../..');
const frontendDir = path.join(rootDir, 'frontend');
const backendDir = path.join(rootDir, 'backend');
const resourcesDir = path.join(frontendDir, 'resources');
const buildTempDir = path.join(frontendDir, '.build-temp');

// 创建日志函数
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}`;
  console.log(logMessage);

  // 同时写入日志文件
  try {
    if (!fs.existsSync(buildTempDir)) {
      fs.mkdirSync(buildTempDir, { recursive: true });
    }
    fs.appendFileSync(path.join(buildTempDir, 'build-prep.log'), logMessage + '\n');
  } catch (err) {
    console.error('无法写入日志文件:', err);
  }
}

/**
 * 运行命令并返回Promise
 */
function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    log(`执行命令: ${command} ${args.join(' ')}`);
    
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
 * 检查环境
 */
async function checkEnvironment() {
  log('开始检查环境...');
  
  // 创建必要的目录
  if (!fs.existsSync(resourcesDir)) {
    fs.mkdirSync(resourcesDir, { recursive: true });
  }
  
  // 检查Node.js版本
  try {
    const nodeVersion = execSync('node --version').toString().trim();
    log(`Node.js版本: ${nodeVersion}`);
    
    // 检查最低版本要求
    const majorVersion = parseInt(nodeVersion.substring(1).split('.')[0]);
    if (majorVersion < 16) {
      throw new Error(`Node.js版本需要16或更高，当前版本: ${nodeVersion}`);
    }
  } catch (err) {
    log(`检查Node.js版本出错: ${err.message}`);
    throw err;
  }
  
  // 检查npm版本
  try {
    const npmVersion = execSync('npm --version').toString().trim();
    log(`npm版本: ${npmVersion}`);
  } catch (err) {
    log(`检查npm版本出错: ${err.message}`);
    throw err;
  }
  
  // 检查Python环境
  try {
    // 使用python_finder检查Python
    const pythonInfo = findPythonExecutable(
      frontendDir, 
      rootDir
    );
    
    if (!pythonInfo.executablePath) {
      log('警告: 未找到Python可执行文件，将尝试创建Python环境');
    } else {
      log(`找到Python: ${pythonInfo.executablePath} (类型: ${pythonInfo.pythonType})`);
      
      // 检查Python版本
      try {
        const pythonVersion = execSync(`"${pythonInfo.executablePath}" --version`).toString().trim();
        log(`Python版本: ${pythonVersion}`);
      } catch (err) {
        log(`检查Python版本出错: ${err.message}`);
      }
    }
  } catch (err) {
    log(`检查Python环境出错: ${err.message}`);
  }
  
  log('环境检查完成');
}

/**
 * 准备Python环境
 */
async function preparePythonEnv() {
  log('开始准备Python环境...');
  
  try {
    // 运行Python环境准备脚本
    log('运行Python环境准备脚本...');
    await runCommand('node', ['scripts/prepare_python.js'], { cwd: frontendDir });
    log('Python环境准备完成');
  } catch (err) {
    log(`准备Python环境失败: ${err.message}`);
    log('将尝试继续构建过程，但可能会导致后端无法正常工作');
  }
}

/**
 * 安装npm依赖
 */
async function installNpmDependencies() {
  log('开始安装npm依赖...');
  
  try {
    // 使用npm ci安装依赖，更加可靠用于CI环境
    log('运行npm ci...');
    await runCommand('npm', ['ci'], { cwd: frontendDir });
    log('npm依赖安装完成');
  } catch (err) {
    log(`npm ci失败，尝试npm install: ${err.message}`);
    try {
      await runCommand('npm', ['install'], { cwd: frontendDir });
      log('npm依赖安装完成(使用npm install)');
    } catch (installErr) {
      log(`安装npm依赖失败: ${installErr.message}`);
      throw installErr;
    }
  }
}

/**
 * 配置平台特定设置
 */
async function configurePlatform() {
  log(`开始为${platform}平台配置特定设置...`);
  
  try {
    // 运行平台配置脚本
    log('运行平台配置脚本...');
    await runCommand('node', ['scripts/configure-platform.js'], { cwd: frontendDir });
    log('平台配置完成');
  } catch (err) {
    log(`平台配置失败: ${err.message}`);
    log('将尝试继续构建过程，但可能会导致应用在目标平台上无法正常工作');
  }
}

/**
 * 检查构建配置
 */
function checkBuildConfig() {
  log('检查构建配置...');
  
  try {
    // 检查package.json的build配置
    const packageJsonPath = path.join(frontendDir, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    
    const buildConfig = packageJson.build || {};
    
    // 检查必要的build配置
    if (!buildConfig.appId) {
      log('警告: 未配置appId，将使用默认值');
    }
    
    // 检查extraResources配置
    let hasBackendResource = false;
    let hasResourcesDir = false;
    
    if (Array.isArray(buildConfig.extraResources)) {
      for (const resource of buildConfig.extraResources) {
        if (typeof resource === 'object') {
          if (resource.from === '../backend') hasBackendResource = true;
          if (resource.from === 'resources') hasResourcesDir = true;
        }
      }
    }
    
    if (!hasBackendResource) {
      log('警告: 未配置backend资源目录，打包可能不会包含后端代码');
    }
    
    if (!hasResourcesDir) {
      log('警告: 未配置resources资源目录');
    }
    
    log('构建配置检查完成');
  } catch (err) {
    log(`检查构建配置失败: ${err.message}`);
  }
}

/**
 * 准备资源文件
 */
function prepareResourceFiles() {
  log('准备资源文件...');
  
  try {
    // 确保resources目录存在
    if (!fs.existsSync(resourcesDir)) {
      fs.mkdirSync(resourcesDir, { recursive: true });
    }
    
    // 创建版本信息文件
    const versionInfoPath = path.join(resourcesDir, 'version-info.json');
    const packageJson = JSON.parse(fs.readFileSync(path.join(frontendDir, 'package.json'), 'utf-8'));
    
    const versionInfo = {
      version: packageJson.version,
      buildTime: new Date().toISOString(),
      platform,
      buildBy: process.env.USER || process.env.USERNAME || 'unknown'
    };
    
    fs.writeFileSync(versionInfoPath, JSON.stringify(versionInfo, null, 2));
    log(`创建了版本信息文件: ${versionInfoPath}`);
    
    // 创建平台特定启动脚本
    if (isWindows) {
      createWindowsStartupScript();
    } else if (isMacOS) {
      createMacStartupScript();
    } else if (isLinux) {
      createLinuxStartupScript();
    }
    
    log('资源文件准备完成');
  } catch (err) {
    log(`准备资源文件失败: ${err.message}`);
  }
}

/**
 * 创建Windows启动脚本
 */
function createWindowsStartupScript() {
  const startScriptPath = path.join(resourcesDir, 'start.bat');
  const scriptContent = `@echo off
echo 正在启动 XMind冒烟测试用例导出工具...
start "" "%~dp0\\..\\XMind冒烟测试用例导出工具.exe"
exit
`;
  
  fs.writeFileSync(startScriptPath, scriptContent);
  log(`创建了Windows启动脚本: ${startScriptPath}`);
}

/**
 * 创建macOS启动脚本
 */
function createMacStartupScript() {
  const startScriptPath = path.join(resourcesDir, 'start.sh');
  const scriptContent = `#!/bin/bash
echo "正在启动 XMind冒烟测试用例导出工具..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
open "$DIR/../XMind冒烟测试用例导出工具.app"
`;
  
  fs.writeFileSync(startScriptPath, scriptContent);
  fs.chmodSync(startScriptPath, '755'); // 设置可执行权限
  log(`创建了macOS启动脚本: ${startScriptPath}`);
}

/**
 * 创建Linux启动脚本
 */
function createLinuxStartupScript() {
  const startScriptPath = path.join(resourcesDir, 'start.sh');
  const scriptContent = `#!/bin/bash
echo "正在启动 XMind冒烟测试用例导出工具..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR/../xmind-automation-tool" &
`;
  
  fs.writeFileSync(startScriptPath, scriptContent);
  fs.chmodSync(startScriptPath, '755'); // 设置可执行权限
  log(`创建了Linux启动脚本: ${startScriptPath}`);
}

/**
 * 验证构建环境
 */
function validateBuildEnvironment() {
  log('验证构建环境...');
  
  // 创建验证结果
  const validationResult = {
    success: true,
    warnings: [],
    errors: []
  };
  
  // 检查必要的目录和文件
  if (!fs.existsSync(path.join(frontendDir, 'node_modules'))) {
    validationResult.errors.push('未找到node_modules目录，请先运行npm install');
    validationResult.success = false;
  }
  
  if (!fs.existsSync(path.join(frontendDir, 'package.json'))) {
    validationResult.errors.push('未找到package.json文件');
    validationResult.success = false;
  }
  
  if (!fs.existsSync(path.join(frontendDir, 'electron.cjs'))) {
    validationResult.errors.push('未找到electron.cjs文件');
    validationResult.success = false;
  }
  
  if (!fs.existsSync(path.join(frontendDir, 'preload.cjs'))) {
    validationResult.errors.push('未找到preload.cjs文件');
    validationResult.success = false;
  }
  
  if (!fs.existsSync(path.join(frontendDir, 'src'))) {
    validationResult.errors.push('未找到src目录');
    validationResult.success = false;
  }
  
  // 检查Python相关文件
  const pythonEnvDir = path.join(backendDir, 'python_env');
  const venvDir = path.join(pythonEnvDir, 'venv');
  
  if (!fs.existsSync(backendDir)) {
    validationResult.errors.push('未找到backend目录');
    validationResult.success = false;
  } else {
    if (!fs.existsSync(path.join(backendDir, 'main.py'))) {
      validationResult.errors.push('未找到backend/main.py文件');
      validationResult.success = false;
    }
    
    if (!fs.existsSync(path.join(backendDir, 'requirements.txt'))) {
      validationResult.warnings.push('未找到requirements.txt文件，Python依赖可能不完整');
    }
    
    // 检查Python虚拟环境
    if (!fs.existsSync(venvDir)) {
      validationResult.warnings.push('未找到Python虚拟环境，请确保已运行prepare_python.js');
    } else {
      // 检查虚拟环境中的python可执行文件
      const pythonExePath = isWindows ? 
        path.join(venvDir, 'Scripts', 'python.exe') : 
        path.join(venvDir, 'bin', 'python');
        
      if (!fs.existsSync(pythonExePath)) {
        validationResult.warnings.push(`未找到Python可执行文件: ${pythonExePath}`);
      }
    }
  }
  
  // 输出验证结果
  if (validationResult.warnings.length > 0) {
    log('警告:');
    validationResult.warnings.forEach(warning => log(` - ${warning}`));
  }
  
  if (validationResult.errors.length > 0) {
    log('错误:');
    validationResult.errors.forEach(error => log(` - ${error}`));
  }
  
  if (validationResult.success) {
    log('构建环境验证通过 ✅');
  } else {
    log('构建环境验证失败 ❌');
  }
  
  return validationResult;
}

/**
 * 主函数
 */
async function main() {
  try {
    log('====== 开始打包前准备工作 ======');
    
    // 检查环境
    await checkEnvironment();
    
    // 安装npm依赖
    await installNpmDependencies();
    
    // 准备Python环境
    await preparePythonEnv();
    
    // 配置平台特定设置
    await configurePlatform();
    
    // 准备资源文件
    prepareResourceFiles();
    
    // 检查构建配置
    checkBuildConfig();
    
    // 验证构建环境
    const validation = validateBuildEnvironment();
    
    if (validation.success) {
      log('====== 打包前准备工作完成 ✅ ======');
      log('可以开始打包了，运行以下命令：');
      log(`npm run electron:build:${platform === 'win32' ? 'win' : platform === 'darwin' ? 'mac' : 'linux'}`);
      process.exit(0);
    } else {
      log('====== 打包前准备工作完成，但存在问题 ⚠️ ======');
      log('请修复上述错误后再进行打包');
      process.exit(1);
    }
  } catch (err) {
    log(`打包前准备工作失败: ${err.message}`);
    process.exit(1);
  }
}

// 运行主函数
main(); 