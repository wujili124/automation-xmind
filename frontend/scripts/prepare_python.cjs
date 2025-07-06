/**
 * 此脚本用于在构建前准备Python环境
 * 它会:
 * 1. 创建一个干净的虚拟环境
 * 2. 安装必要的依赖
 * 3. 准备Python环境供Electron使用
 */

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// 路径配置
const rootDir = path.resolve(__dirname, '../..');
const backendDir = path.join(rootDir, 'backend');
const pythonEnvDir = path.join(backendDir, 'python_env');
const venvDir = path.join(pythonEnvDir, 'venv');
const requirementsPath = path.join(backendDir, 'requirements.txt');

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
 * 检查Python是否安装
 */
async function checkPythonInstallation() {
  try {
    // 检查Python版本
    const versionCmd = isWindows ? 'python --version' : 'python3 --version';
    const version = execSync(versionCmd).toString().trim();
    console.log(`检测到Python: ${version}`);
    
    // 检查pip版本
    const pipVersionCmd = isWindows ? 'pip --version' : 'pip3 --version';
    const pipVersion = execSync(pipVersionCmd).toString().trim();
    console.log(`检测到pip: ${pipVersion}`);
    
    return true;
  } catch (err) {
    console.error('未检测到Python或pip:', err.message);
    return false;
  }
}

/**
 * 创建虚拟环境
 */
async function createVirtualEnv() {
  // 确保目录存在
  if (!fs.existsSync(pythonEnvDir)) {
    fs.mkdirSync(pythonEnvDir, { recursive: true });
  }
  
  console.log(`创建Python虚拟环境: ${venvDir}`);
  
  // 如果已存在虚拟环境，先删除
  if (fs.existsSync(venvDir)) {
    console.log('删除已存在的虚拟环境...');
    fs.rmSync(venvDir, { recursive: true, force: true });
  }
  
  // 创建虚拟环境
  try {
    await runCommand(pythonCommand, ['-m', 'venv', venvDir]);
    console.log('虚拟环境创建成功');
  } catch (err) {
    console.error('创建虚拟环境失败:', err.message);
    throw err;
  }
}

/**
 * 安装依赖
 */
async function installDependencies() {
  console.log('安装Python依赖...');
  
  // 虚拟环境中的pip路径
  const pipPath = isWindows 
    ? path.join(venvDir, 'Scripts', 'pip')
    : path.join(venvDir, 'bin', 'pip');
  
  // 确保requirements.txt存在
  if (!fs.existsSync(requirementsPath)) {
    console.error(`找不到requirements.txt: ${requirementsPath}`);
    
    // 创建一个基本的requirements.txt
    const basicRequirements = 
      'fastapi==0.109.2\n' +
      'uvicorn==0.27.1\n' +
      'python-multipart==0.0.9\n' +
      'python-json-logger==2.0.7\n' +
      'openpyxl==3.1.2\n' +
      'jinja2==3.1.3\n';
    
    fs.writeFileSync(requirementsPath, basicRequirements);
    console.log(`创建了基本的requirements.txt: ${requirementsPath}`);
  }
  
  // 安装依赖
  try {
    // 使用虚拟环境中的pip安装依赖
    const activateCmd = isWindows 
      ? path.join(venvDir, 'Scripts', 'activate')
      : `. "${path.join(venvDir, 'bin', 'activate')}"`;
    
    if (isWindows) {
      // Windows上使用cmd.exe执行激活命令
      await runCommand('cmd.exe', [
        '/c', 
        `${activateCmd} && ${pipPath} install -r "${requirementsPath}"`
      ], { shell: true });
    } else {
      // macOS/Linux上使用bash执行激活命令
      await runCommand('bash', [
        '-c', 
        `${activateCmd} && ${pipPath} install -r "${requirementsPath}"`
      ]);
    }
    
    console.log('依赖安装完成');
  } catch (err) {
    console.error('安装依赖失败:', err.message);
    throw err;
  }
}

/**
 * 创建环境准备标记文件
 */
function createReadyFlag() {
  const readyFlagPath = path.join(pythonEnvDir, '.ready');
  fs.writeFileSync(readyFlagPath, new Date().toISOString());
  console.log(`创建环境准备标记: ${readyFlagPath}`);
}

/**
 * 主函数
 */
async function main() {
  console.log('开始准备Python环境...');
  
  try {
    // 检查Python安装
    const isPythonInstalled = await checkPythonInstallation();
    if (!isPythonInstalled) {
      throw new Error('未检测到Python安装，请先安装Python');
    }
    
    // 创建虚拟环境
    await createVirtualEnv();
    
    // 安装依赖
    await installDependencies();
    
    // 创建准备完成标记
    createReadyFlag();
    
    console.log('Python环境准备完成！✅');
  } catch (err) {
    console.error('Python环境准备失败:', err.message);
    process.exit(1);
  }
}

// 执行主函数
main(); 